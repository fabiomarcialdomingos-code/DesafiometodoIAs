"""agenteC -- nucleo: painel dias x barras M5 para WIN e acoes, beta movel, simulador vetorizado.

Convencoes (sem look-ahead):
- slot = barra M5 identificada pelo horario de ABERTURA. "preco as HH:MM" = abertura da barra HH:MM
  (= fechamento da barra anterior). Entrada "10:05" = abertura da barra 10:05. Saida "11:00" = fechamento da barra 10:55;
  "13:00" = fechamento da 12:55; "16:55" = fechamento da 16:50.
- acoes: barras >= 18:00 descartadas e barras >= fechamento do a vista do dia (17:00 no horario de verao dos EUA,
  18:00 no resto) descartadas. Barras faltantes: preenchidas com o ultimo fechamento (sem negocio = preco parado).
- gap da acao = abertura oficial (D1, leilao das 10:00) / fechamento oficial anterior (D1) - 1.
- WIN "fechamento do a vista anterior" = fechamento da barra 16:55 (ou 17:55) do dia anterior; "WIN as 10:00" = fech. 9:55.
  Dias de vencimento do WIN (salto da serie contN) sao excluidos (o retorno do WIN fica contaminado pela rolagem).
- ATRd = media 14d de (max-min) diario ate ontem (como m2core). beta = cov/var movel de 60 dias, shift(1).
"""
import sys, os, pickle, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/win/grade')
from engine import load_mt5_csv
from horarios import us_dst, win_roll_days

OUT = '/home/claude/win/m2vol/agenteC'
SMALL = '/home/claude/win/m2vol/small/dados'
BLUE = '/home/claude/win/proj/WIN_WDO/export/acoes'
WINP = '/home/claude/win/hist21/WIN_contN_M5.csv'
BLUE_T = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'BBAS3', 'B3SA3', 'PRIO3', 'BOVA11', 'SMAL11', 'WEGE3', 'ABEV3']
ADR = {'PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3'}
COST = {'blue': 0.0006, 'small': 0.0010}          # ida e volta, fracao do nocional
WIN_PV = 0.20; WIN_COST_PTS = 15.0; RISK = 80.0

SETOR = {  # setor economico (classificacao manual, aproximada)
 'PETR4': 'petroleo', 'PRIO3': 'petroleo', 'BRAV3': 'petroleo', 'RECV3': 'petroleo', 'CSAN3': 'petroleo', 'RAIZ4': 'petroleo',
 'VALE3': 'mineracao_siderurgia', 'CSNA3': 'mineracao_siderurgia', 'USIM5': 'mineracao_siderurgia', 'GOAU4': 'mineracao_siderurgia',
 'CMIN3': 'mineracao_siderurgia', 'BRKM5': 'mineracao_siderurgia',
 'ITUB4': 'bancos_fin', 'BBDC4': 'bancos_fin', 'BBAS3': 'bancos_fin', 'B3SA3': 'bancos_fin', 'IRBR3': 'bancos_fin',
 'CYRE3': 'construcao', 'MRVE3': 'construcao', 'EZTC3': 'construcao', 'DIRR3': 'construcao', 'TEND3': 'construcao',
 'CURY3': 'construcao', 'JHSF3': 'construcao',
 'MGLU3': 'varejo_consumo', 'LREN3': 'varejo_consumo', 'AZZA3': 'varejo_consumo', 'VIVA3': 'varejo_consumo',
 'GMAT3': 'varejo_consumo', 'ASAI3': 'varejo_consumo', 'PCAR3': 'varejo_consumo', 'VULC3': 'varejo_consumo',
 'ABEV3': 'varejo_consumo', 'CVCB3': 'varejo_consumo', 'PGMN3': 'varejo_consumo',
 'COGN3': 'educacao_saude', 'YDUQ3': 'educacao_saude', 'ANIM3': 'educacao_saude', 'HAPV3': 'educacao_saude',
 'ONCO3': 'educacao_saude', 'FLRY3': 'educacao_saude',
 'ALOS3': 'shoppings_imob', 'MULT3': 'shoppings_imob', 'IGTI11': 'shoppings_imob', 'LOGG3': 'shoppings_imob',
 'MOVI3': 'transporte_locacao', 'VAMO3': 'transporte_locacao', 'SIMH3': 'transporte_locacao', 'ECOR3': 'transporte_locacao',
 'AURE3': 'utilidades', 'ENEV3': 'utilidades', 'SAPR11': 'utilidades', 'CSMG3': 'utilidades',
 'SMTO3': 'agro', 'SLCE3': 'agro', 'TTEN3': 'agro',
 'WEGE3': 'industria', 'POMO4': 'industria', 'RAPT4': 'industria', 'INTB3': 'industria',
 'LWSA3': 'tecnologia',
 'BOVA11': 'etf', 'SMAL11': 'etf',
}

T0 = 10*60; NS = 96                       # slots das acoes: 10:00 .. 17:55
SLOT = lambda hh, mm: (hh*60 + mm - T0)//5
WT0 = 9*60; WNS = 114                     # slots do WIN: 9:00 .. 18:25


def _grid(M, t0, ns, days, cut=None):
    """M5 -> arrays (ndias, ns) de open/high/low/close; faltantes = ultimo fechamento do dia (ffill); antes do 1o negocio = NaN."""
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
    A['traded'] = first                              # houve negocio na barra
    A['seen'] = ~np.isnan(A['close'])                # ja houve algum negocio no dia ate esta barra
    return A


def load_win():
    W = load_mt5_csv(WINP)
    days = pd.DatetimeIndex(sorted(W.index.normalize().unique()))
    G = _grid(W, WT0, WNS, days)
    dst = np.array([us_dst(d) for d in days])
    cc = np.where(dst, SLOT(16, 55) + 12, SLOT(17, 55) + 12)       # slot WIN da barra 16:55/17:55
    close_cash = G['close'][np.arange(len(days)), cc]
    roll = pd.DatetimeIndex(sorted(win_roll_days()))
    w = pd.DataFrame(index=days)
    w['dst'] = dst
    w['o9'] = G['open'][:, 0]
    w['p10'] = G['close'][:, 11]                                   # fech. barra 9:55
    w['cc'] = close_cash
    w['cc_prev'] = w.cc.shift(1)
    w['roll'] = days.isin(roll)
    w['r_night'] = w.o9/w.cc_prev - 1                              # fech. a vista anterior -> 9:00
    w['r_1h'] = w.p10/w.o9 - 1                                     # 9:00 -> 10:00
    w['r_to10'] = w.p10/w.cc_prev - 1
    w.loc[w.roll | w.o9.isna() | w.p10.isna(), ['r_night', 'r_1h', 'r_to10']] = np.nan
    # grade do WIN alinhada nos slots das acoes (10:00..17:55): slot WIN = slot acao + 12
    WG = {c: G[c][:, 12:12 + NS] for c in ['open', 'high', 'low', 'close']}
    return w, WG, days


def load_stock(t, kind, days):
    base = BLUE if kind == 'blue' else SMALL
    M = load_mt5_csv(f'{base}/{t}_M5.csv'); M = M[M.index.hour < 18]
    D = load_mt5_csv(f'{base}/{t}_D1.csv'); D.index = D.index.normalize()
    D = D.reindex(days)
    cut = pd.Series(np.where([us_dst(x) for x in days], 17*60, 18*60), index=days)
    G = _grid(M, T0, NS, days, cut=cut)
    s = pd.DataFrame(index=days)
    s['op'] = D.open; s['cl'] = D.close; s['pc'] = D.close.shift(1)
    s.loc[D.open.isna(), 'pc'] = np.nan
    # pc = fechamento oficial do ultimo pregao em que a acao negociou (D1 alinhado ao calendario do WIN)
    s['pc'] = D.close.ffill().shift(1).where(D.open.notna())
    s['atr'] = (D.high - D.low).rolling(14, min_periods=10).mean().shift(1)
    s['atrf'] = s.atr/s.pc
    s['gap'] = s.op/s.pc - 1
    s['vol_rs'] = (D.volume*D.close).rolling(60, min_periods=20).mean().shift(1)   # liquidez R$ ate ontem
    return s, G


def build(force=False):
    pk = f'{OUT}/painel.pkl'
    if os.path.exists(pk) and not force:
        return pickle.load(open(pk, 'rb'))
    w, WG, days = load_win()
    L = pd.read_csv(f'{SMALL}/smallcaps_lista.csv', sep=';'); L = L[L.exportado == 'sim']
    S = {}
    for t in BLUE_T: S[t] = ('blue',) + load_stock(t, 'blue', days)
    for t in L.papel:
        if t in S: continue
        S[t] = ('small',) + load_stock(t, 'small', days)
    P = dict(w=w, WG=WG, days=days, S=S)
    pickle.dump(P, open(pk, 'wb'))
    return P


def add_beta(P, win=60, minp=40, col='r_to10'):
    """beta_t = cov(gap, r_WIN)/var(r_WIN) em [t-win, t-1]."""
    w = P['w']
    for t, (kind, s, G) in P['S'].items():
        x = w[col]; y = s.gap.where(x.notna()); x = x.where(y.notna())
        cov = (x*y).rolling(win, min_periods=minp).mean() - x.rolling(win, min_periods=minp).mean()*y.rolling(win, min_periods=minp).mean()
        var = x.rolling(win, min_periods=minp).var(ddof=0)
        s['beta'] = (cov/var).shift(1)
        s['resid'] = s.gap - s.beta*w.r_to10
        s['residA'] = s.resid/s.atrf                      # |resid| em unidades de ATRd
        s['gapA'] = s.gap/s.atrf
    return P


# --------------------------------------------------------------------------- simulador
def sim(G, rows, ent, ext, dirs, stopf, WG=None, hedge=None, intrabar=True):
    """rows: indices de dia; ent: slot de entrada (abertura); ext: slot cujo fechamento e a saida;
    dirs: +1/-1; stopf: distancia de stop como fracao do preco de entrada (np.inf = sem stop).
    hedge: None ou array h = beta (vende h*nocional em WIN quando compra a acao). Com hedge o stop e checado no
    fechamento de cada barra sobre o P&L combinado (em fracao do nocional da acao).
    Retorna (ret_acao_bruto, ret_win_bruto_por_nocional_acao, saiu_por_stop)."""
    rows = np.asarray(rows); n = len(rows)
    if n == 0: return np.array([]), np.array([]), np.array([], bool)
    sl = np.arange(ent, ext + 1)
    O = G['open'][rows, ent]; Hh = G['high'][rows][:, sl]; Ll = G['low'][rows][:, sl]; Cc = G['close'][rows][:, sl]
    d = np.asarray(dirs, float); sf = np.broadcast_to(np.asarray(stopf, float), (n,))
    if WG is None or hedge is None:
        if not intrabar: Hh = Ll = Cc
        adv = np.where(d[:, None] > 0, (Ll/O[:, None] - 1), -(Hh/O[:, None] - 1))     # pior excursao por barra
        hit = adv <= -sf[:, None]
        first = np.where(hit.any(1), hit.argmax(1), -1)
        r = d*(Cc[:, -1]/O - 1)
        st = first >= 0
        if st.any():
            j = first[st]; ii = np.flatnonzero(st)
            # se a barra abriu alem do stop (gap intrabar), sai na abertura dessa barra
            ob = G['open'][rows[ii], ent + j]
            ro = d[ii]*(ob/O[ii] - 1)
            r[ii] = np.where(ro <= -sf[ii], ro, -sf[ii])
        return r, np.zeros(n), st
    WO = WG['open'][rows, ent]; WC = WG['close'][rows][:, sl]
    h = np.asarray(hedge, float)
    rs = d[:, None]*(Cc/O[:, None] - 1); rw = -d[:, None]*h[:, None]*(WC/WO[:, None] - 1)
    tot = rs + rw
    hit = tot <= -sf[:, None]
    first = np.where(hit.any(1), hit.argmax(1), tot.shape[1] - 1)
    ii = np.arange(n)
    return rs[ii, first], rw[ii, first], hit.any(1)


def pf(x):
    x = np.asarray(x); l = -x[x < 0].sum()
    return round(x[x > 0].sum()/l, 2) if l > 0 else np.inf


def m2_win_daily():
    t = pd.read_csv('/home/claude/win/m2vol/agenteA/trades_win.csv')
    t['d'] = pd.to_datetime(t.d)
    return t.groupby('d').brl.sum().rename('m2')


def resumo(T, lab, m2=None, col='brl', colb='brl_bruto'):
    """T: DataFrame com colunas d (data), brl, brl_bruto."""
    if T is None or len(T) == 0: return dict(teste=lab, n=0)
    d = pd.to_datetime(T.d); y = d.dt.year
    dd = T.groupby('d')[col].sum(); eq = dd.cumsum()
    wk = max(1, (d.max() - d.min()).days/7)
    r = dict(teste=lab, n=len(T), op_sem=round(len(T)/wk, 1), PF=pf(T[col]), PF_bruto=pf(T[colb]),
             RS=round(T[col].sum()), RS_bruto=round(T[colb].sum()), DD=round((eq - eq.cummax()).min()),
             acerto=round((T[col] > 0).mean(), 2))
    py = T.groupby(y)[col].apply(pf)
    for yy, v in py.items(): r[f'PF{yy}'] = v
    r['minPF_ano'] = py.min()
    if m2 is not None:
        j = pd.concat([dd.rename('x'), m2], axis=1).fillna(0)
        j = j[(j.index >= dd.index.min()) & (j.index <= dd.index.max())]
        r['corr_M2'] = round(j.x.corr(j.m2), 2)
    r['APROVA'] = bool(r['PF'] >= 1.2 and py.min() >= 1.0 and r['n'] >= 300)
    return r


def linha(r):
    if not r.get('n'): return f"{r['teste']:60s} n=0"
    anos = ' '.join(f"{k[4:]}:{v:.2f}" for k, v in r.items() if k.startswith('PF2'))
    return (f"{r['teste']:60s} n={r['n']:5d} ({r['op_sem']:5.1f}/sem) PF {r['PF']:.2f} (bruto {r['PF_bruto']:.2f}) "
            f"R$ {r['RS']:8.0f} (bruto {r['RS_bruto']:8.0f}) DD {r['DD']:7.0f} | {anos} | c={r.get('corr_M2', np.nan)}"
            f" {'APROVA' if r['APROVA'] else '-'}")
