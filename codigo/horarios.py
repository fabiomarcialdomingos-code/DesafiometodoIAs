"""Tema: ESTRUTURA DO PREGAO (horarios) -- WIN (e WDO na estatistica).
Teses: (a) momentum intradiario Gao/Han/Li/Zhou, (b) 9-10h antes do a vista, (c) abertura de NY (com horario de verao americano),
(d) pos-almoco, (e) gap da abertura (fora dos dias de rolagem).
Uso:  python3 horarios.py stats   -> analise estatistica rapida (WIN e WDO)
      python3 horarios.py sim     -> simulacoes no engine (WIN, custo 15 pts) + grade de robustez; grava tabelas em out_horarios_*.csv
Sem olhar o futuro: todo preco "p(HH:MM)" e a ABERTURA da barra de 5 min que comeca em HH:MM (= preco conhecido as HH:MM);
o sinal e emitido na barra que fecha em HH:MM e o engine entra na abertura da barra seguinte (HH:MM)."""
import sys, pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/win/grade')
from engine import load_mt5_csv, prep, simulate, report
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
HIST = '/home/claude/win/hist'
OUT = '/home/claude/win/grade'

# ---------------------------------------------------------------- calendario
def us_dst(d):
    """True se os EUA estao em horario de verao no dia d (abertura de NY = 10:30 BRT; senao 11:30 BRT).
    Brasil nao tem horario de verao desde 2019."""
    return bool(pd.Timestamp(pd.Timestamp(d).date()).tz_localize('America/New_York').replace(hour=12).dst())

def ny_open_min(d):  return 10*60+30 if us_dst(d) else 11*60+30
def cash_close_min(d): return 17*60 if us_dst(d) else 18*60   # fim do a vista (confirmado pelo IVVB11: ultima barra 16:50 / 17:50)

def win_roll_days():
    """Vencimento do WIN: quarta-feira mais proxima do dia 15 dos meses pares. Na serie contN o salto aparece
    na abertura desse dia (conferido: todos os gaps de +1,5% a +2,5% caem nessas quartas)."""
    out = set()
    for y in range(2022, 2028):
        for m in (2, 4, 6, 8, 10, 12):
            c = pd.Timestamp(y, m, 15)
            out.add([c+pd.Timedelta(days=k) for k in range(-3, 4) if (c+pd.Timedelta(days=k)).weekday() == 2][0])
    return out

def wdo_roll_days(idx):
    """WDO vira no 1o dia util do mes: exclui o 1o pregao de cada mes."""
    s = pd.Series(idx, index=idx); return set(s.groupby([idx.year, idx.month]).first().values)

# ---------------------------------------------------------------- estatistica rapida (dados diarios)
def daily(asset):
    df = load_mt5_csv(f'{HIST}/{asset}_contN_M5.csv')
    df['d'] = df.index.normalize(); df['t'] = df.index.hour*60+df.index.minute
    rows = []
    for d, g in df.groupby('d'):
        if g.t.iloc[0] != 540 or g.t.iloc[-1] < 17*60+45: continue          # dias completos
        op = dict(zip(g.t, g.open))
        def P(m):
            if m in op: return op[m]
            s = g[g.t >= m]; return s.open.iloc[0] if len(s) else np.nan
        ny, cc = ny_open_min(d), cash_close_min(d)
        r = dict(d=d, dst=us_dst(d), o9=g.open.iloc[0], last=g.close.iloc[-1], hi=g.high.max(), lo=g.low.min())
        for m in [600, 630, 660, 720, 780, 840, 960, 990, 1020, 1050, 1080]: r[f'p{m}'] = P(m)
        r.update(pcc=P(cc), pcc30=P(cc-30), pcc60=P(cc-60), pny=P(ny), pny15=P(ny+15), pny30=P(ny+30), pny90=P(ny+90))
        rows.append(r)
    D = pd.DataFrame(rows).set_index('d')
    D['pc'] = D['last'].shift(1)                                   # fechamento anterior (ultima barra do dia anterior)
    D['atr'] = (D.hi-D.lo).rolling(14).mean().shift(1)
    D['roll'] = D.index.isin(win_roll_days() if asset == 'WIN' else wdo_roll_days(D.index))
    return D

def _t(x, y, lab, out):
    m = x.notna() & y.notna(); x, y = x[m], y[m]; pay = np.sign(x)*y
    r = dict(teste=lab, n=len(x), corr=round(np.corrcoef(x, y)[0, 1], 3), acerto=round((pay > 0).mean(), 3),
             media_pts=round(pay.mean(), 1), t=round(pay.mean()/pay.std()*np.sqrt(len(pay)), 2))
    for yy in sorted(set(pay.index.year)): r[f'm_{yy}'] = round(float(pay[pay.index.year == yy].mean()), 1)
    out.append(r)

def stats(asset):
    D = daily(asset); out = []
    for per, S in [('2024-26', D[(D.index >= '2024-01-01') & ~D.roll]), ('2023', D[(D.index.year == 2023) & ~D.roll])]:
        res = []
        yl = S['last']-S.p1020
        _t(S.p630-S.pc, yl, '(a) pc->10:30 => 17:00->fech', res)
        _t(S.p720-S.pc, yl, '(a) pc->12:00 => 17:00->fech', res)
        _t(S.p1020-S.pc, yl, '(a) pc->17:00 => 17:00->fech', res)
        _t(S.p1020-S.o9, yl, '(a) 9:00->17:00 => 17:00->fech', res)
        _t(S.pcc60-S.pc, S.pcc-S.pcc60, '(a) pc->(fim a vista-60) => ultima hora do a vista', res)
        _t(S.pcc30-S.pc, S.pcc-S.pcc30, '(a) pc->(fim a vista-30) => ultima meia hora do a vista', res)
        _t(S.p600-S.o9, S.p720-S.p600, '(b) 9->10 => 10->12', res)
        _t(S.p600-S.o9, S.p1020-S.p600, '(b) 9->10 => 10->17', res)
        _t(S.p600-S.pc, S.p1020-S.p600, '(b) pc->10 => 10->17', res)
        _t(S.pny30-S.pny, S.p1020-S.pny30, '(c) NY..NY+30 => NY+30->17', res)
        _t(S.pny15-S.pny, S.p1020-S.pny15, '(c) NY..NY+15 => NY+15->17', res)
        _t(S.pny-S.o9, S.p1020-S.pny, '(c) 9->NY => NY->17', res)
        _t(S.p720-S.o9, S.p840-S.p720, '(d) 9->12 => 12->14', res)
        _t(S.p840-S.p720, S.p1020-S.p840, '(d) 12->14 => 14->17', res)
        _t(S.p720-S.o9, S.p1020-S.p840, '(d) 9->12 => 14->17', res)
        lim = 0.04 if asset == 'WIN' else 0.02                           # descarta gaps absurdos (eleicao 2026)
        S2 = S[(S.o9/S.pc-1).abs() < lim]; g = S2.o9-S2.pc
        _t(g, S2.p600-S2.o9, '(e) gap => 9->10 (continua>0)', res)
        _t(g, S2.p720-S2.p600, '(e) gap => 10->12 (continua>0)', res)
        _t(g, S2['last']-S2.p600, '(e) gap => 10->fech (continua>0)', res)
        gz = (g/S2.atr).abs()
        for lo, hi in [(0, .1), (.1, .2), (.2, .35), (.35, .6), (.6, 9), (.1, 9)]:
            m = (gz >= lo) & (gz < hi); X = S2[m]; gg = g[m]
            _t(gg, X.p600-X.o9, f'(e) |gap| {lo}-{hi} ATR: 9->10 (continua>0)', res)
            _t(gg, X.p720-X.p600, f'(e) |gap| {lo}-{hi} ATR: 10->12 (continua>0)', res)
            _t(gg, X['last']-X.p600, f'(e) |gap| {lo}-{hi} ATR: 10->fech (continua>0)', res)
            res[-1]['fill_no_dia'] = round(float(np.where(gg > 0, X.lo <= X.pc, X.hi >= X.pc).mean()), 2)
        for r in res: r['periodo'] = per; r['ativo'] = asset
        out += res
    return pd.DataFrame(out)

# ---------------------------------------------------------------- sinais para o engine (barras M5 preparadas)
def _day_tables(df):
    """indices por dia e por minuto, fechamento anterior, rolagem."""
    days = df.d.unique()
    last = df.groupby('d').close.last(); pc = last.shift(1)
    roll = win_roll_days()
    idx = {d: dict(zip(g.t.values, np.flatnonzero(df.d.values == d))) for d, g in df.groupby('d')}
    return days, pc, roll, idx

def _first_at(ix, m):
    """indice da primeira barra com t>=m (ix: dict t->i)."""
    ks = [k for k in ix if k >= m]; return ix[min(ks)] if ks else None

def sig_momentum(df, T, sig_min=12*60, ent_min=17*60, k_stop=0.5, base='pc', min_abs=0.0):
    """(a) Gao et al.: r = p(sig_min) - fechamento anterior (base='pc') ou - abertura 9:00 (base='o9').
    Na abertura da barra de ent_min entra a favor de sign(r); stop = k_stop*ATRdiario; sai no fim do pregao (flat)."""
    s = []; days, pc, roll, idx = T
    O = df.open.values; A = df.atr_d.values
    for d in days:
        ix = idx[d]
        if d in roll or 540 not in ix or pd.isna(pc.get(d)): continue
        i0 = _first_at(ix, sig_min); ie = _first_at(ix, ent_min)
        if i0 is None or ie is None or ie < 1 or df.d.values[ie-1] != d or np.isnan(A[ie]): continue
        ref = pc[d] if base == 'pc' else O[ix[540]]
        r = O[i0]-ref
        if r == 0 or abs(r) < min_abs*A[ie]: continue
        dirn = int(np.sign(r)); e = O[ie]
        s.append(dict(i=ie-1, dir=dirn, stop=e-dirn*k_stop*A[ie], target=None))
    return s

def sig_gapfade(df, T, ent_min=10*60, gmin=0.10, gmax=1.0, k_stop=0.5, tmax=17*60, target='pc'):
    """(e) gap = abertura 9:00 - fechamento anterior. Fora do dia de rolagem, se gmin <= |gap|/ATRd <= gmax e o gap
    ainda esta aberto as ent_min (preco ainda do lado do gap), entra CONTRA o gap na abertura de ent_min.
    Stop = k_stop*ATRd; alvo = fechamento anterior (gap preenchido); saida por tempo em tmax."""
    s = []; days, pc, roll, idx = T
    O = df.open.values; C = df.close.values; A = df.atr_d.values
    for d in days:
        ix = idx[d]
        if d in roll or 540 not in ix or pd.isna(pc.get(d)): continue
        ie = _first_at(ix, ent_min)
        if ie is None or df.d.values[ie-1] != d or np.isnan(A[ie]): continue
        o9 = O[ix[540]]; p = pc[d]; gap = o9-p; z = abs(gap)/A[ie]
        if not (gmin <= z <= gmax): continue
        c = C[ie-1]                                   # fechamento da barra anterior a entrada (conhecido)
        if (c-p)*np.sign(gap) <= 0: continue          # gap ja fechou -> sem operacao
        dirn = -int(np.sign(gap)); e = O[ie]
        tg = p if target == 'pc' else None
        s.append(dict(i=ie-1, dir=dirn, stop=e-dirn*k_stop*A[ie], target=tg, tmax=tmax))
    return s

def sig_9a10(df, T, k_stop=0.5, tmax=17*60, mode='cont'):
    """(b) movimento 9:00->10:00; entra 10:00 a favor (cont) ou contra (rev); sai tmax."""
    s = []; days, pc, roll, idx = T; O = df.open.values; A = df.atr_d.values
    for d in days:
        ix = idx[d]
        if 540 not in ix or 600 not in ix: continue
        ie = ix[600]; r = O[ie]-O[ix[540]]
        if r == 0 or np.isnan(A[ie]): continue
        dirn = int(np.sign(r))*(1 if mode == 'cont' else -1); e = O[ie]
        s.append(dict(i=ie-1, dir=dirn, stop=e-dirn*k_stop*A[ie], target=None, tmax=tmax))
    return s

def sig_ny_orb(df, T, rng_min=30, win_min=120, tgt_mult=1.5, tmax=17*60, stop='mid'):
    """(c) faixa de NY_open .. NY_open+rng_min (NY_open = 10:30 BRT com horario de verao americano, 11:30 sem).
    Primeiro fechamento de 5 min fora da faixa ate NY_open+win_min -> entra no rompimento.
    Stop = meio da faixa (ou lado oposto), alvo = tgt_mult*faixa, saida por tempo tmax."""
    s = []; days, pc, roll, idx = T; H = df.high.values; L = df.low.values; C = df.close.values
    for d in days:
        ix = idx[d]; ny = ny_open_min(d)
        rb = [ix[m] for m in range(ny, ny+rng_min, 5) if m in ix]
        if len(rb) < rng_min//5: continue
        mx = H[rb].max(); mn = L[rb].min(); rg = mx-mn
        if rg <= 0: continue
        for m in range(ny+rng_min, ny+win_min, 5):
            if m not in ix: continue
            i = ix[m]
            if C[i] > mx: s.append(dict(i=i, dir=1, stop=(mx+mn)/2 if stop == 'mid' else mn, target=C[i]+tgt_mult*rg, tmax=tmax)); break
            if C[i] < mn: s.append(dict(i=i, dir=-1, stop=(mx+mn)/2 if stop == 'mid' else mx, target=C[i]-tgt_mult*rg, tmax=tmax)); break
    return s

def sig_almoco(df, T, k_stop=0.5, tmax=17*60, mode='cont'):
    """(d) movimento 12:00->14:00; entra 14:00 a favor (cont) ou contra (rev); sai tmax."""
    s = []; days, pc, roll, idx = T; O = df.open.values; A = df.atr_d.values
    for d in days:
        ix = idx[d]
        if 720 not in ix or 840 not in ix: continue
        ie = ix[840]; r = O[ie]-O[ix[720]]
        if r == 0 or np.isnan(A[ie]): continue
        dirn = int(np.sign(r))*(1 if mode == 'cont' else -1); e = O[ie]
        s.append(dict(i=ie-1, dir=dirn, stop=e-dirn*k_stop*A[ie], target=None, tmax=tmax))
    return s

# ---------------------------------------------------------------- execucao
COLS = ['metodo', 'n', 'por_semana', 'acerto', 'PF', 'total_RS', 'dd_RS', 'PF_2024', 'PF_2025', 'PF_2026', 'RS_2024', 'RS_2025', 'RS_2026']
FLAT = 18*60+15        # ultima barra completa do pregao do WIN (18:15-18:20)

def run(df, sig, lab, cost=15, pv=0.2):
    tr = simulate(df, sig, cost, flat_min=FLAT, max_per_day=1)
    tr = tr[pd.to_datetime(tr.d) >= '2024-01-01']
    r = report(tr, lab, pv)
    if r.get('n'):
        r['aprovado'] = bool(r['PF'] >= 1.2 and all(r.get(f'PF_{y}', 0) > 1.0 for y in (2024, 2025, 2026)) and r['por_semana'] >= 1.5)
    return r, tr

def sim():
    df = load_mt5_csv(f'{HIST}/WIN_contN_M5.csv'); df = prep(df[df.index >= '2023-11-01'])
    T = _day_tables(df); res = []
    H = lambda h, m=0: h*60+m
    # ---- regras base (uma por tese, parametros escolhidos pela logica, antes da grade)
    base = [
        ('A1 momentum pc->12:00 => 17:00-fech', sig_momentum(df, T, sig_min=H(12))),
        ('A2 momentum pc->10:30 => 17:00-fech', sig_momentum(df, T, sig_min=H(10, 30))),
        ('A3 momentum pc->17:00 => 17:00-fech', sig_momentum(df, T, sig_min=H(17))),
        ('A4 momentum 9:00->17:00 => 17:00-fech', sig_momentum(df, T, sig_min=H(17), base='o9')),
        ('B1 9-10h continua (10h->17h)', sig_9a10(df, T, mode='cont')),
        ('B2 9-10h reverte (10h->17h)', sig_9a10(df, T, mode='rev')),
        ('C1 ORB NY 15min (stop meio, alvo 1.5x)', sig_ny_orb(df, T, rng_min=15)),
        ('C2 ORB NY 30min (stop meio, alvo 1.5x)', sig_ny_orb(df, T, rng_min=30)),
        ('D1 almoco 12-14h continua (14h->17h)', sig_almoco(df, T, mode='cont')),
        ('D2 almoco 12-14h reverte (14h->17h)', sig_almoco(df, T, mode='rev')),
        ('E1 fade do gap 10:00 (0.10-1.0 ATR, stop 0.5 ATR, alvo fech.ant, sai 17h)', sig_gapfade(df, T)),
        ('E2 fade do gap 9:05 (idem, entra apos 1a barra)', sig_gapfade(df, T, ent_min=H(9, 5))),
    ]
    trades = {}
    for lab, sg in base:
        r, tr = run(df, sg, lab); res.append(r); trades[lab] = tr
    B = pd.DataFrame(res)
    # ---- grades de robustez (+-20% em cada parametro principal, um de cada vez) para as duas teses com efeito
    grid = []
    g_mom = [('base', {}),
             ('sinal 11:24 (-20% de 9h->12h)', dict(sig_min=H(11, 24))), ('sinal 12:36 (+20%)', dict(sig_min=H(12, 36))),
             ('entrada 16:45 (-20% do periodo)', dict(ent_min=H(16, 45))), ('entrada 17:15 (+20%)', dict(ent_min=H(17, 15))),
             ('stop 0.4 ATR', dict(k_stop=0.4)), ('stop 0.6 ATR', dict(k_stop=0.6))]
    for lab, kw in g_mom:
        r, _ = run(df, sig_momentum(df, T, **kw), f'A1 grade: {lab}'); grid.append(r)
    g_gap = [('base', {}),
             ('gmin 0.08', dict(gmin=0.08)), ('gmin 0.12', dict(gmin=0.12)),
             ('gmax 0.8', dict(gmax=0.8)), ('gmax 1.2', dict(gmax=1.2)),
             ('stop 0.4 ATR', dict(k_stop=0.4)), ('stop 0.6 ATR', dict(k_stop=0.6)),
             ('saida 15:36 (-20% de 10h->17h)', dict(tmax=H(15, 36))), ('saida 18:15 (+20%: fim do pregao)', dict(tmax=H(18, 15))),
             ('entrada 9:45', dict(ent_min=H(9, 45))), ('entrada 10:15', dict(ent_min=H(10, 15))),
             ('sem alvo (so tempo/stop)', dict(target=None))]
    for lab, kw in g_gap:
        r, tr = run(df, sig_gapfade(df, T, **kw), f'E1 grade: {lab}'); grid.append(r)
    # combinacoes extremas (todos os parametros +-20% juntos) para o fade
    for lab, kw in [('gmin.08 gmax.8 stop.4 saida15:36', dict(gmin=.08, gmax=.8, k_stop=.4, tmax=H(15, 36))),
                    ('gmin.12 gmax1.2 stop.6 saida18:15', dict(gmin=.12, gmax=1.2, k_stop=.6, tmax=H(18, 15))),
                    ('gmin.12 gmax.8 stop.4 saida18:15', dict(gmin=.12, gmax=.8, k_stop=.4, tmax=H(18, 15))),
                    ('gmin.08 gmax1.2 stop.6 saida15:36', dict(gmin=.08, gmax=1.2, k_stop=.6, tmax=H(15, 36)))]:
        r, _ = run(df, sig_gapfade(df, T, **kw), f'E1 grade (combinado): {lab}'); grid.append(r)
    # ---- E3 = E1 sem alvo (saida so por tempo/stop). ATENCAO: variante achada DEPOIS de ver a grade do E1 (pos-hoc);
    #      recebe sua propria grade +-20% e o teste no periodo virgem de 2023 (fora da amostra usada para escolher).
    g_e3 = [('base', {}),
            ('gmin 0.08', dict(gmin=0.08)), ('gmin 0.12', dict(gmin=0.12)),
            ('gmax 0.8', dict(gmax=0.8)), ('gmax 1.2', dict(gmax=1.2)),
            ('stop 0.4 ATR', dict(k_stop=0.4)), ('stop 0.6 ATR', dict(k_stop=0.6)),
            ('saida 15:36', dict(tmax=H(15, 36))), ('saida 18:15', dict(tmax=H(18, 15))),
            ('entrada 9:45', dict(ent_min=H(9, 45))), ('entrada 10:15', dict(ent_min=H(10, 15))),
            ('comb gmin.08 gmax.8 stop.4 saida15:36', dict(gmin=.08, gmax=.8, k_stop=.4, tmax=H(15, 36))),
            ('comb gmin.12 gmax1.2 stop.6 saida18:15', dict(gmin=.12, gmax=1.2, k_stop=.6, tmax=H(18, 15))),
            ('comb gmin.12 gmax.8 stop.4 saida18:15', dict(gmin=.12, gmax=.8, k_stop=.4, tmax=H(18, 15))),
            ('comb gmin.08 gmax1.2 stop.6 saida15:36', dict(gmin=.08, gmax=1.2, k_stop=.6, tmax=H(15, 36)))]
    for lab, kw in g_e3:
        kw = dict(kw, target=None); r, tr = run(df, sig_gapfade(df, T, **kw), f'E3 grade: {lab}'); grid.append(r)
        if lab == 'base': trades['E3'] = tr
    G = pd.DataFrame(grid)
    # ---- checagem em 2023 (fev-dez; nao usado para escolher nada) das regras base + E3
    df23 = prep(load_mt5_csv(f'{HIST}/WIN_contN_M5.csv')); df23 = df23[df23.index < '2024-01-01']; T23 = _day_tables(df23)
    chk = []
    for lab, fn in [('A1', lambda: sig_momentum(df23, T23, sig_min=H(12))), ('A3', lambda: sig_momentum(df23, T23, sig_min=H(17))),
                    ('B1', lambda: sig_9a10(df23, T23)), ('C2', lambda: sig_ny_orb(df23, T23)), ('D1', lambda: sig_almoco(df23, T23)),
                    ('E1', lambda: sig_gapfade(df23, T23)), ('E3', lambda: sig_gapfade(df23, T23, target=None))]:
        tr = simulate(df23, fn(), 15, flat_min=FLAT, max_per_day=1); tr = tr[pd.to_datetime(tr.d) >= '2023-02-01']
        chk.append(report(tr, f'{lab} em 2023 (fev-dez)', 0.2))
    C23 = pd.DataFrame(chk); C23.to_csv(f'{OUT}/out_horarios_2023.csv', index=False)
    # ---- detalhes do E1: motivo de saida, por semestre, por direcao, por tamanho do gap
    tr = trades[base[10][0]].copy(); tr['d'] = pd.to_datetime(tr.d)
    det = dict(why=tr.groupby('why').pts.agg(['count', 'mean']).round(1),
               dirn=tr.groupby('dir').pts.agg(['count', 'mean', lambda x: x[x > 0].sum()/-x[x < 0].sum()]).round(2),
               sem=tr.groupby(tr.d.dt.year.astype(str)+'H'+((tr.d.dt.month > 6)+1).astype(str)).pts.agg(
                   ['count', 'sum', lambda x: x[x > 0].sum()/-x[x < 0].sum()]).round(2))
    B.to_csv(f'{OUT}/out_horarios_base.csv', index=False); G.to_csv(f'{OUT}/out_horarios_grade.csv', index=False)
    tr.to_csv(f'{OUT}/out_horarios_E1_trades.csv', index=False)
    t3 = trades['E3'].copy(); t3['d'] = pd.to_datetime(t3.d); t3.to_csv(f'{OUT}/out_horarios_E3_trades.csv', index=False)
    det['E3_why'] = t3.groupby('why').pts.agg(['count', 'mean']).round(1)
    det['E3_dir'] = t3.groupby('dir').pts.agg(['count', 'mean', lambda x: x[x > 0].sum()/-x[x < 0].sum()]).round(2)
    det['E3_sem'] = t3.groupby(t3.d.dt.year.astype(str)+'H'+((t3.d.dt.month > 6)+1).astype(str)).pts.agg(
        ['count', 'sum', lambda x: x[x > 0].sum()/-x[x < 0].sum()]).round(2)
    det['E3_dst'] = t3.assign(dst=t3.d.map(us_dst)).groupby('dst').pts.agg(['count', 'mean', lambda x: x[x > 0].sum()/-x[x < 0].sum()]).round(2)
    det['2023'] = C23
    return B, G, det

if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'sim'
    if what == 'stats':
        S = pd.concat([stats('WIN'), stats('WDO')]); S.to_csv(f'{OUT}/out_horarios_stats.csv', index=False)
        print(S.to_string(index=False))
    else:
        B, G, det = sim(); c = COLS+['aprovado']
        print(B[c].to_string(index=False)); print(); print(G[c].to_string(index=False))
        for k, v in det.items(): print('\n', k); print(v)
