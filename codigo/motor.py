"""agenteE -- motor do M2-A ("Acao atrasada"), streaming por papel (serve para 60 ou 600 papeis).

Convencoes (sem look-ahead), herdadas do agenteC/core.py e da rodada 3 do GPT (executavel.py):
- slot = barra M5 pelo horario de ABERTURA; slots das acoes 0..95 = 10:00..17:55; WIN alinhado nos mesmos slots.
- Acoes: barras >= 18:00 descartadas e barras >= fechamento do a vista (17:00 em horario de verao dos EUA, 18:00 no resto).
  Barra sem negocio = ultimo fechamento (ffill); 'traded' marca barras com negocio real.
- gap = abertura D1 / fechamento D1 anterior - 1 (|gap| >= 15% descartado); se o leilao saiu na barra 10:00 exijo que a
  abertura M5 dessa barra bata com o D1 (0,2%).
- r_WIN ate 10:00 = fech. barra 9:55 / fech. 16:55 ou 17:55 do dia anterior; r_1h = 9:00 -> 10:00. Dias de vencimento fora.
- beta = cov/var de 60 pregoes (min 40) do gap contra r_WIN ate 10:00, shift(1). ATRd = media 14d de (max-min), shift(1).
- lag = (beta*r_WIN_ate_10 - gap)/ATRd. Sinal: lo <= |lag| <= hi, sinal(lag) = sinal(r_1h), |r_1h| >= wmin * media 60d.
- liquidez = media 60d de volume*fechamento (R$) ATE ONTEM (shift 1).
- coorte 'cedo': leilao na barra 10:00 -> entrada na abertura da 10:05 (+atraso). coorte 'tarde': 1o negocio na barra 10:05
  -> entrada na abertura da 10:10 (+atraso). A entrada exige negocio real na barra de entrada.
- Execucao (como o executavel do GPT): acoes inteiras q = floor(risco/(k*ATRd*preco)); stop checado no FECHAMENTO de cada
  barra sobre o P&L marcado (acao + hedge teorico beta); saida na ABERTURA da proxima barra com negocio. Saida por tempo na
  abertura da barra 'fim+1' (fim=80 -> 16:45) ou na proxima com negocio; sem negocio ate o fim do pregao = fechamento (proxy).
- Custos: taxa_acao (fracao do nocional ida+volta) + hedge 15 pts por WIN (R$3/contrato ida+volta), fracionario por operacao.
  O hedge inteiro agregado por dia e calculado a parte (hedge_inteiro)."""
import numpy as np, pandas as pd, warnings, os
warnings.filterwarnings('ignore')

WINP = '/home/claude/win/hist21/WIN_contN_M5.csv'
T0 = 10*60; NS = 96; WT0 = 9*60; WNS = 114
WIN_PV = 0.20; WIN_COST_PTS = 15.0
LO_MIN, HI_MAX = 0.05, 3.0            # superconjunto gravado; os filtros finos sao aplicados depois


# ------------------------------------------------------------------ utilitarios de dados
def load_mt5_csv(path):
    df = pd.read_csv(path, sep=';')
    df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')
    df = df.set_index('time').sort_index(); df = df[~df.index.duplicated()]
    df['volume'] = df.real_volume.where(df.real_volume > 0, df.tick_volume)
    return df[['open', 'high', 'low', 'close', 'volume']].astype(float)


def us_dst(d):
    return bool(pd.Timestamp(pd.Timestamp(d).date()).tz_localize('America/New_York').replace(hour=12).dst())


def win_roll_days():
    out = set()
    for y in range(2020, 2030):
        for m in (2, 4, 6, 8, 10, 12):
            c = pd.Timestamp(y, m, 15)
            out.add([c + pd.Timedelta(days=k) for k in range(-3, 4) if (c + pd.Timedelta(days=k)).weekday() == 2][0])
    return out


def _grid(M, t0, ns, days, cut=None):
    d = M.index.normalize(); m = M.index.hour*60 + M.index.minute
    k = ((m - t0)//5).values; ok = (k >= 0) & (k < ns)
    if cut is not None: ok &= m.values < cut.reindex(d).fillna(0).values
    di = pd.Index(days).get_indexer(d); ok &= di >= 0
    A = {c: np.full((len(days), ns), np.nan) for c in ['open', 'high', 'low', 'close', 'volume']}
    for c in A: A[c][di[ok], k[ok]] = M[c].values[ok]
    first = ~np.isnan(A['close'])
    C = pd.DataFrame(A['close']).ffill(axis=1).values
    miss = np.isnan(A['close']) & ~np.isnan(C)
    for c in ['open', 'high', 'low', 'close']: A[c] = np.where(miss, C, A[c])
    A['volume'] = np.where(np.isnan(A['volume']), 0, A['volume'])
    A['traded'] = first
    return A


def carrega_win(path=WINP):
    Wm = load_mt5_csv(path)
    days = pd.DatetimeIndex(sorted(Wm.index.normalize().unique()))
    G = _grid(Wm, WT0, WNS, days)
    dst = np.array([us_dst(d) for d in days])
    cc = np.where(dst, (16*60 + 55 - WT0)//5, (17*60 + 55 - WT0)//5)
    w = pd.DataFrame(index=days)
    w['o9'] = G['open'][:, 0]; w['p10'] = G['close'][:, 11]
    w['cc'] = G['close'][np.arange(len(days)), cc]; w['cc_prev'] = w.cc.shift(1)
    w['roll'] = days.isin(pd.DatetimeIndex(sorted(win_roll_days())))
    w['r_night'] = w.o9/w.cc_prev - 1; w['r_1h'] = w.p10/w.o9 - 1; w['r_to10'] = w.p10/w.cc_prev - 1
    w['p1005'] = G['open'][:, 13]                                        # WIN na abertura da barra 10:05
    w['r_to1005'] = w.p1005/w.cc_prev - 1
    w.loc[w.roll | w.o9.isna() | w.p10.isna(), ['r_night', 'r_1h', 'r_to10', 'r_to1005']] = np.nan
    w['wa'] = w.r_1h.abs()/w.r_1h.abs().rolling(60, min_periods=20).mean().shift(1)
    WG = {c: G[c][:, 12:12 + NS] for c in ['open', 'high', 'low', 'close']}
    cut = pd.Series(np.where(dst, 17*60, 18*60), index=days)
    return dict(w=w, WG=WG, days=days, dst=dst, cut=cut)


def carrega_acao(m5, d1, W, beta_win=60):
    days = W['days']; w = W['w']
    M = load_mt5_csv(m5); M = M[M.index.hour < 18]
    D = load_mt5_csv(d1); D.index = D.index.normalize(); D = D[~D.index.duplicated()].reindex(days)
    G = _grid(M, T0, NS, days, cut=W['cut'])
    s = pd.DataFrame(index=days)
    s['op'] = D.open
    s['pc'] = D.close.ffill().shift(1).where(D.open.notna())
    s['atr'] = (D.high - D.low).rolling(14, min_periods=10).mean().shift(1)
    s['atrf'] = s.atr/s.pc
    s['gap'] = s.op/s.pc - 1
    s['vol_rs'] = (D.volume*D.close).rolling(60, min_periods=20).mean().shift(1)
    x = w.r_to10; y = s.gap.where(x.notna()); x = x.where(y.notna())
    mp = int(beta_win*2/3)
    cov = (x*y).rolling(beta_win, min_periods=mp).mean() - x.rolling(beta_win, min_periods=mp).mean()*y.rolling(beta_win, min_periods=mp).mean()
    s['beta'] = (cov/x.rolling(beta_win, min_periods=mp).var(ddof=0)).shift(1)
    s['lag'] = (s.beta*w.r_to10 - s.gap)/s.atrf
    # variante para a coorte tarde: WIN ate a abertura da barra 10:05 (aprox. o horario do 1o negocio)
    s['lag5'] = (s.beta*w.r_to1005 - s.gap)/s.atrf
    return s, G


# ------------------------------------------------------------------ simulacao
def simula(G, WG, rows, start, dirs, atrf, beta, k, end=80, slip_in=0, slip_out=0):
    """Retorna dict com retornos por nocional (acao e hedge teorico), slot de saida real e flags."""
    n = len(rows)
    O = G['open'][rows, start] + dirs*0.01*slip_in
    Cc = G['close'][rows][:, start:end + 1]
    W0 = WG['open'][rows, start]; WC = WG['close'][rows][:, start:end + 1]
    mark = dirs[:, None]*(Cc/O[:, None] - 1) - dirs[:, None]*beta[:, None]*(WC/W0[:, None] - 1)
    hit = mark <= -(k*atrf)[:, None]
    stop = hit.any(1)
    efrom = np.where(stop, start + hit.argmax(1) + 1, end + 1)
    tr = G['traded'][rows]
    poss = (np.arange(NS)[None, :] >= efrom[:, None]) & tr
    can = poss.any(1); ex = np.where(can, poss.argmax(1), end)
    ii = np.arange(n)
    px = np.where(can, G['open'][rows, ex], G['close'][rows, end]) - dirs*0.01*slip_out
    wx = np.where(can, WG['open'][rows, ex], WG['close'][rows, end])
    rs = dirs*(px/O - 1); rw = -dirs*beta*(wx/W0 - 1)
    exs = np.where(can, ex, end + 1)                    # slot em que a posicao deixa de existir (para o hedge inteiro)
    return dict(entry=O, rs=rs, rw=rw, stop=stop, ex=exs, proxy=~can, W0=W0, Wx=wx)


# cenarios: nome -> (atraso em barras, k, slip_in, slip_out, fim)
CENARIOS = {
    'base':      (0, 1.0, 0, 0, 80),
    'k0.8':      (0, 0.8, 0, 0, 80),
    'k1.2':      (0, 1.2, 0, 0, 80),
    'atraso5':   (1, 1.0, 0, 0, 80),
    'tick':      (0, 1.0, 1, 0, 80),
    'tick2':     (0, 1.0, 1, 1, 80),
    'fim1655':   (0, 1.0, 0, 0, 82),
}


def trades_papel(t, s, G, W, cenarios=CENARIOS, coortes=('cedo', 'tarde')):
    """Superconjunto de operacoes de um papel: |lag| em [LO_MIN, HI_MAX], alinhado com o WIN 9-10h, qualquer wmin."""
    w = W['w']; WG = W['WG']; days = W['days']; out = []
    base_ok = (np.abs(s.gap.values) < 0.15) & ~w.roll.values & np.isfinite(w.r_to10.values) & \
              (s.atrf.values > 0) & np.isfinite(s.beta.values) & np.isfinite(w.wa.values)
    tr0 = G['traded'][:, 0]; tr1 = G['traded'][:, 1]
    # coerencia D1 x M5 no leilao das 10:00
    coer = ~tr0 | (np.abs(G['open'][:, 0]/s.op.values - 1) < 0.002)
    for coorte in coortes:
        for lagcol in (('lag',) if coorte == 'cedo' else ('lag', 'lag5')):
            lag = s[lagcol].values
            ok = base_ok & np.isfinite(lag) & (np.abs(lag) >= LO_MIN) & (np.abs(lag) <= HI_MAX) & \
                 (np.sign(lag) == np.sign(w.r_1h.values))
            ok &= (tr0 & coer) if coorte == 'cedo' else (~tr0 & tr1)
            rows0 = np.flatnonzero(ok)
            if not len(rows0): continue
            s0 = 1 if coorte == 'cedo' else 2
            for nome, (atr_, k, si, so, fim) in cenarios.items():
                if coorte == 'tarde' and nome == 'fim1655': continue
                if coorte == 'tarde' and lagcol == 'lag5' and nome != 'base': continue
                st = s0 + atr_
                rows = rows0[G['traded'][rows0, st] & np.isfinite(WG['open'][rows0, st])]
                if not len(rows): continue
                dirs = np.sign(lag[rows]); a = s.atrf.values[rows]; b = s.beta.values[rows]
                R = simula(G, WG, rows, st, dirs, a, b, k, end=fim, slip_in=si, slip_out=so)
                out.append(pd.DataFrame(dict(
                    d=days[rows], t=t, coorte=coorte if lagcol == 'lag' else 'tarde5', cen=nome, k=k, start=st,
                    dir=dirs, lagA=np.abs(lag[rows]), wa=w.wa.values[rows], vol_rs=s.vol_rs.values[rows],
                    beta=b, atrf=a, gap=s.gap.values[rows], entry=R['entry'], rs=R['rs'], rw=R['rw'], stop=R['stop'],
                    ex=R['ex'], proxy=R['proxy'], W0=R['W0'], Wx=R['Wx'])))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def roda_pasta(pasta, W, tickers=None, cenarios=CENARIOS, coortes=('cedo', 'tarde'), verbose=True, beta_win=60):
    """Le {T}_M5.csv / {T}_D1.csv de uma pasta, papel a papel (memoria constante)."""
    import glob
    ts = sorted(os.path.basename(p)[:-7] for p in glob.glob(f'{pasta}/*_M5.csv'))
    if tickers is not None: ts = [t for t in ts if t in tickers]
    out = []
    for i, t in enumerate(ts):
        d1 = f'{pasta}/{t}_D1.csv'
        if not os.path.exists(d1): continue
        try:
            s, G = carrega_acao(f'{pasta}/{t}_M5.csv', d1, W, beta_win=beta_win)
            T = trades_papel(t, s, G, W, cenarios, coortes)
        except Exception as e:
            print(f'  {t}: ERRO {e}'); continue
        if len(T): out.append(T)
        if verbose and (i % 10 == 0): print(f'  {i+1}/{len(ts)} {t}: {len(T)} linhas', flush=True)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


# ------------------------------------------------------------------ P&L, selecao e metricas
def filtra(T, lo=0.25, hi=1.2, wmin=0.5, cen='base', coortes=('cedo',), liq_min=0.0, liq_max=np.inf, tickers=None, inicio=None, fim=None):
    m = (T.cen == cen) & T.coorte.isin(coortes) & (T.lagA >= lo) & (T.lagA <= hi) & (T.wa >= wmin) & \
        (T.vol_rs >= liq_min) & (T.vol_rs < liq_max)
    if tickers is not None: m &= T.t.isin(tickers)
    if inicio is not None: m &= T.d >= inicio
    if fim is not None: m &= T.d < fim
    return T[m].copy()


def pnl(X, custo, risco=80.0, cost_mult=1.0, fator=None):
    """custo: funcao(DataFrame)->taxa ida+volta por operacao. fator: escala de risco por operacao (limite diario)."""
    X = X.copy()
    r = risco*(1.0 if fator is None else fator)
    q = np.floor(r/(X.k*X.atrf*X.entry)); X['q'] = q
    X['notional'] = q*X.entry
    X['risk'] = X.notional*X.k*X.atrf
    X['taxa'] = custo(X)
    X['brl_bruto'] = X.notional*(X.rs + X.rw)
    X['custo_rs'] = cost_mult*(X.taxa*X.notional + WIN_COST_PTS*np.abs(X.beta)*X.notional/X.W0)
    X['brl'] = X.brl_bruto - X.custo_rs
    X['brl_semhedge'] = X.notional*X.rs - cost_mult*X.taxa*X.notional
    X['R'] = X.brl/80.0
    return X[X.q > 0]


def custo_rotulo(taxas):
    """taxas: dict papel -> taxa; padrao 0,10%."""
    return lambda X: X.t.map(taxas).fillna(0.0010).values


def custo_liquidez(faixas=((150e6, 0.0006), (10e6, 0.0010), (0, 0.0015))):
    """taxa pela liquidez historica (R$/dia, ate ontem): >=150M 0,06%; 10-150M 0,10%; <10M 0,15%."""
    def f(X):
        v = X.vol_rs.values; out = np.full(len(v), faixas[-1][1])
        for lim, tx in reversed(faixas): out = np.where(v >= lim, tx, out)
        return out
    return f


def pf(x):
    x = np.asarray(x, float); l = -x[x < 0].sum()
    return round(x[x > 0].sum()/l, 3) if l > 0 else np.inf


def semanas(ini, fim):
    return max(1.0, (pd.Timestamp(fim) - pd.Timestamp(ini)).days/7)


def dd_diario(X, col='brl', calendario=None):
    d = X.groupby('d')[col].sum()
    if calendario is not None: d = d.reindex(calendario, fill_value=0.0)
    e = np.r_[0, d.sort_index().cumsum().values]
    return float((e - np.maximum.accumulate(e)).min())


def icc(X, col='R'):
    """correlacao media entre pares de operacoes do MESMO dia (correlacao intra-classe)."""
    x = X[col].values - X[col].mean(); v = (x**2).mean()
    g = pd.DataFrame(dict(d=X.d.values, x=x)).groupby('d').x
    s1 = g.sum(); s2 = g.apply(lambda z: (z**2).sum()); n = g.size()
    num = (s1**2 - s2).sum(); den = (n*(n - 1)).sum()
    return float(num/den/v) if den > 0 else np.nan


def resumo(X, lab, ini, fim, calendario=None, extra=None):
    if X is None or len(X) == 0: return dict(teste=lab, n=0)
    y = X.d.dt.year
    py = X.groupby(y).brl.apply(pf)
    dia = X.groupby('d').brl.sum()
    r = dict(teste=lab, n=len(X), op_sem=round(len(X)/semanas(ini, fim), 1), dias=X.d.nunique(),
             PF=pf(X.brl), PF_bruto=pf(X.brl_bruto), RS=round(X.brl.sum()), RS_bruto=round(X.brl_bruto.sum()),
             RS_op=round(X.brl.mean(), 2), DD=round(dd_diario(X, calendario=calendario)), PF_dia=pf(dia),
             pior_dia=round(dia.min()), acerto=round((X.brl > 0).mean(), 3), stops=round(X.stop.mean(), 3))
    for yy, v in py.items(): r[f'PF{yy}'] = v
    r['minPF_ano'] = py.min()
    if extra: r.update(extra)
    return r


def linha(r):
    if not r.get('n'): return f"{r['teste']:46s} n=0"
    anos = ' '.join(f"{k[4:]}:{v:.2f}" for k, v in r.items() if k.startswith('PF2'))
    return (f"{r['teste']:46s} n={r['n']:5d} ({r['op_sem']:5.1f}/sem) PF {r['PF']:.2f} (bruto {r['PF_bruto']:.2f}) "
            f"R$ {r['RS']:7.0f} DD {r['DD']:6.0f} | {anos}")


def hedge_inteiro(X, W, cost_mult=1.0):
    """Hedge agregado do dia em contratos INTEIROS, rebalanceado a cada abertura de barra conforme as pernas entram/saem.
    Retorna DataFrame diario: n, acao (liq. de custo), futuro (liq.), net, bruto, pico de contratos."""
    days = W['days']; Wo = W['WG']['open']; di = pd.Index(days).get_indexer(X.d)
    h = -X.dir.values*X.beta.values*X.notional.values/(WIN_PV*X.W0.values)       # contratos (fracionarios)
    E = np.zeros((len(days), NS + 1))
    np.add.at(E, (di, X.start.values), h); np.add.at(E, (di, np.minimum(X.ex.values, NS)), -h)
    E = np.cumsum(E, axis=1)[:, :NS]
    pos = np.sign(E)*np.floor(np.abs(E) + 0.5)
    pos[:, -1] = 0
    Wf = pd.DataFrame(Wo).ffill(axis=1).values
    dW = np.nan_to_num(np.diff(Wf, axis=1))
    fut_bruto = (pos[:, :-1]*dW).sum(1)*WIN_PV
    trade = np.abs(np.diff(np.c_[np.zeros(len(days)), pos], axis=1)).sum(1)
    fut_custo = trade*WIN_PV*WIN_COST_PTS/2*cost_mult
    acao_b = np.bincount(di, weights=X.notional.values*X.rs.values, minlength=len(days))
    acao_c = np.bincount(di, weights=cost_mult*X.taxa.values*X.notional.values, minlength=len(days))
    F = pd.DataFrame(dict(d=days, n=np.bincount(di, minlength=len(days)), bruto=acao_b + fut_bruto,
                          net=acao_b - acao_c + fut_bruto - fut_custo, pico=np.abs(pos).max(1),
                          risco=np.bincount(di, weights=X.risk.values, minlength=len(days)),
                          nocional=np.bincount(di, weights=X.notional.values, minlength=len(days))))
    return F


def resumo_inteiro(F, lab):
    F = F[F.n > 0]
    y = F.d.dt.year; e = np.r_[0, F.net.cumsum().values]
    r = dict(teste=lab, dias=len(F), n=int(F.n.sum()), PF_dia=pf(F.net), PF_dia_bruto=pf(F.bruto), RS=round(F.net.sum()),
             DD=round((e - np.maximum.accumulate(e)).min()), pico_ctr_med=round(F.pico.mean(), 2), pico_ctr_max=int(F.pico.max()))
    for yy, g in F.groupby(y): r[f'PF{yy}'] = pf(g.net)
    return r
