"""Nucleo do M2 v2 generico (agenteA). Reusa engine.simulate e as convencoes de m2vol/lab.py e lab2.py.

FUTUROS (WIN, IND, WDO) -- m2v2_fut():
  manha: gap = abertura 9:00 - fechamento anterior (ultima barra M5 do dia anterior); ATRd = engine.prep (14d de max-min, ate ontem).
         10:00: se gmin <= |gap|/ATRd <= gmax e o fechamento da barra 9:55 ainda do lado do gap -> entra contra o gap na
         abertura da barra 10:00; stop k*ATRd; sem alvo; sai no fechamento da barra 17:00 (=17:05). Pula vencimento.
         Pula se stop*valor_ponto > teto. Tamanho: f=(abertura-preco 9:55)/gap; f>=0 -> 2 contratos, f<0 -> 1.
  tarde: so nos dias SEM entrada de manha; 13:10: se pm_gmin <= |preco 13:05-fech.ant|/ATRd <= pm_gmax entra contra o desvio,
         stop k*ATRd (mesmo teto), saida 17:05. 1 contrato.
ACOES/ETFs -- m2_acao(): gap = abertura oficial (leilao 10:00, D1) - fechamento oficial anterior (D1); mesma logica com
  entrada em ent_min (10:30/11:00) exigindo gap aberto E f>=0; saida no fechamento da barra 16:50 (=16:55).
  Custo 0,03% por lado. Tamanho: R$ RISK de risco por operacao (acoes = RISK/(k*ATRd), fracionario).
Sem olhar o futuro: tudo usa barras ja fechadas; entrada na abertura da barra seguinte ao sinal."""
import sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/win/grade')
from engine import load_mt5_csv, prep, simulate
import horarios as Hm

def pf(x):
    if not len(x): return np.nan
    l = -x[x < 0].sum()
    return round(x[x > 0].sum()/l, 2) if l > 0 else np.inf

def first_at(ix, m):
    ks = [k for k in ix if k >= m]; return ix[min(ks)] if ks else None

class Fut:
    def __init__(self, path, roll):
        self.df = prep(load_mt5_csv(path)); df = self.df
        self.days = df.d.unique(); self.pc = df.groupby('d').close.last().shift(1)
        self.idx = {d: dict(zip(g.t.values, np.flatnonzero(df.d.values == d))) for d, g in df.groupby('d')}
        self.roll = roll(self.days) if callable(roll) else roll
        self.O, self.C, self.A, self.D = df.open.values, df.close.values, df.atr_d.values, df.d.values

def m2v2_fut(F, pv, cost, cap=200, k=0.3, gmin=0.10, gmax=1.0, pm_t=790, pm_gmin=0.2, pm_gmax=1.0, tmax=17*60,
             t_ent=600, sizing=True, tarde=True, need_f=None, start='2022-01-01', skip=None, flat=Hm.FLAT):
    """skip(d, atr) -> True para pular o dia (teto alternativo). cap em R$ por contrato (None = sem teto)."""
    O, C, A, Dv, pc, idx = F.O, F.C, F.A, F.D, F.pc, F.idx
    capok = lambda a, d: (cap is None or k*a*pv <= cap) and (skip is None or not skip(d, a))
    ms, fmap = [], {}
    for d in F.days:
        ix = idx[d]
        if d in F.roll or 540 not in ix or pd.isna(pc.get(d)): continue
        ie = first_at(ix, t_ent)
        if ie is None or ie < 1 or Dv[ie-1] != d or np.isnan(A[ie]): continue
        o9 = O[ix[540]]; p = pc[d]; gap = o9 - p; a = A[ie]; c = C[ie-1]; sg = np.sign(gap)
        if not (gmin <= abs(gap)/a <= gmax) or (c - p)*sg <= 0: continue
        fr = (o9 - c)/gap
        if need_f is not None and not (fr >= 0) == need_f: continue
        if not capok(a, d): continue
        e = O[ie]; dirn = -int(sg)
        ms.append(dict(i=ie-1, dir=dirn, stop=e - dirn*k*a, target=None, tmax=tmax)); fmap[d] = fr
    tm = simulate(F.df, ms, cost, flat_min=flat, max_per_day=1)
    if len(tm):
        tm['f'] = tm.d.map(fmap); tm['ctr'] = np.where((tm.f >= 0) & sizing, 2, 1); tm['leg'] = 'manha'
    out = [tm]
    if tarde:
        mdays = set(tm.d) if len(tm) else set(); ps = []
        for d in F.days:
            ix = idx[d]
            if d in F.roll or d in mdays or 540 not in ix or pd.isna(pc.get(d)): continue
            ie = first_at(ix, pm_t)
            if ie is None or ie < 1 or Dv[ie-1] != d or np.isnan(A[ie]): continue
            a = A[ie]; dv = C[ie-1] - pc[d]
            if not (pm_gmin <= abs(dv)/a <= pm_gmax) or not capok(a, d): continue
            e = O[ie]; dirn = -int(np.sign(dv))
            ps.append(dict(i=ie-1, dir=dirn, stop=e - dirn*k*a, target=None, tmax=tmax))
        tp = simulate(F.df, ps, cost, flat_min=flat, max_per_day=1)
        if len(tp): tp['f'] = np.nan; tp['ctr'] = 1; tp['leg'] = 'tarde'; out.append(tp)
    t = pd.concat([x for x in out if len(x)], ignore_index=True)
    t = t[pd.to_datetime(t.d) >= start].copy()
    t['gpts'] = t.pts + cost                                  # pontos brutos por contrato
    t['brl'] = t.pts*pv*t.ctr; t['brl_bruto'] = t.gpts*pv*t.ctr
    return t.sort_values('dt').reset_index(drop=True)

# ------------------------------------------------------------------ acoes / ETFs
ACOES = '/home/claude/win/proj/WIN_WDO/export/acoes'
TICK = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'BBAS3', 'B3SA3', 'PRIO3', 'BOVA11', 'SMAL11', 'WEGE3', 'ABEV3']
COSTF = 0.0003; RISK = 100.0

def load_acao(t):
    M = load_mt5_csv(f'{ACOES}/{t}_M5.csv'); M = M[M.index.hour < 18]
    D = load_mt5_csv(f'{ACOES}/{t}_D1.csv'); D.index = D.index.normalize()
    D['pc'] = D.close.shift(1); D['atr_d'] = (D.high - D.low).rolling(14).mean().shift(1)
    return M, D

def load_m5_only(path):
    """Para ETF sem D1 (IVVB11): diario montado do M5. abertura = open da 1a barra; fech.ant = close da ultima barra."""
    M = load_mt5_csv(path); M = M[M.index.hour < 18]; g = M.groupby(M.index.normalize())
    D = pd.DataFrame({'open': g.open.first(), 'high': g.high.max(), 'low': g.low.min(), 'close': g.close.last()})
    D['pc'] = D.close.shift(1); D['atr_d'] = (D.high - D.low).rolling(14).mean().shift(1)
    return M, D

def _path(P, m, ie, dirn, e, stop, tmax):
    O, H, L, C = P.open.values, P.high.values, P.low.values, P.close.values
    for j in range(ie, len(P)):
        adv = L[j] if dirn == 1 else H[j]
        if (adv - stop)*dirn <= 0: return (stop if (O[j] - stop)*dirn > 0 else O[j]), 'stop'
        if m[j] >= tmax: return C[j], 'hora'
    return C[-1], 'hora'

def m2_acao(M, D, ent_min=630, gmin=0.10, gmax=1.0, k=0.3, tmax=16*60+50, need_f=True, tarde=False, manha=True,
            pm_t=790, pm_gmin=0.2, pm_gmax=1.0, risk=RISK, costf=COSTF, ext_signal=None, start=None):
    """need_f: True exige f>=0; None nao filtra (= M2 original). ext_signal: dict d->(dir) para usar o sinal de outro ativo
    (ideia 5: sinal do WIN); nesse caso a entrada e em ent_min sem checar o gap da propria acao (so o sentido)."""
    out = []; mdays = set()
    groups = {d: P for d, P in M.groupby(M.index.normalize())}
    def rec(d, leg, dirn, e, px, why, a, extra=None):
        sh = risk/(k*a); g = (px - e)*dirn; c = costf*(e + px)
        r = dict(d=d, leg=leg, dir=dirn, e=e, px=px, why=why, ret_gross=g/e, ret=(g - c)/e, brl_bruto=sh*g, brl=sh*(g - c),
                 notional=sh*e)
        if extra: r.update(extra)
        out.append(r)
    for d, P in groups.items():
        if d not in D.index: continue
        p, op, a = D.pc[d], D.open[d], D.atr_d[d]
        if pd.isna(p) or pd.isna(a) or a <= 0: continue
        m = (P.index.hour*60 + P.index.minute).values
        if manha:
            ie = int(np.argmax(m >= ent_min))
            if m[ie] >= ent_min and (ie >= 1 or ext_signal is not None):
                c = P.close.values[ie-1] if ie >= 1 else np.nan; gap = op - p; sg = np.sign(gap); ok = False
                if ext_signal is not None:
                    if d in ext_signal and sg == -ext_signal[d] and sg != 0: ok = True; dirn = int(ext_signal[d])
                elif gmin <= abs(gap)/a <= gmax and (c - p)*sg > 0:
                    fr = (op - c)/gap
                    ok = need_f is None or ((fr >= 0) == need_f); dirn = -int(sg)
                if ok:
                    e = P.open.values[ie]; stop = e - dirn*k*a; px, why = _path(P, m, ie, dirn, e, stop, tmax)
                    rec(d, 'manha', dirn, e, px, why, a); mdays.add(d)
        if tarde and d not in mdays:
            ie = int(np.argmax(m >= pm_t))
            if m[ie] >= pm_t and ie >= 1:
                dv = P.close.values[ie-1] - p
                if pm_gmin <= abs(dv)/a <= pm_gmax:
                    dirn = -int(np.sign(dv)); e = P.open.values[ie]; stop = e - dirn*k*a
                    px, why = _path(P, m, ie, dirn, e, stop, tmax); rec(d, 'tarde', dirn, e, px, why, a)
    t = pd.DataFrame(out)
    if len(t) and start: t = t[pd.to_datetime(t.d) >= start]
    return t

# ------------------------------------------------------------------ relatorio
def resumo(t, lab, col='brl', colb='brl_bruto', w='ctr'):
    if t is None or len(t) == 0: return dict(teste=lab, n=0)
    y = pd.to_datetime(t.d).dt.year; dd = t.groupby('d')[col].sum(); eq = dd.cumsum()
    r = dict(teste=lab, n=len(t), contratos=int(t[w].sum()) if w in t else len(t), PF=pf(t[col]), PF_bruto=pf(t[colb]),
             RS=round(t[col].sum()), RS_bruto=round(t[colb].sum()), DD=round((eq - eq.cummax()).min()),
             acerto=round((t[col] > 0).mean(), 2))
    py = t.groupby(y)[col].apply(pf)
    for yy, v in py.items(): r[f'PF{yy}'] = v
    r['minPF_ano'] = py.min()
    r['APROVA'] = bool(r['PF'] >= 1.2 and py.min() >= 1.0 and r['n'] >= 100 and r['RS'] > 0 and r['RS_bruto'] > 0)
    return r

def linha(r):
    if not r.get('n'): return f"{r['teste']:52s} n=0"
    anos = ' '.join(f"{k[2:]}:{v:.2f}" for k, v in r.items() if k.startswith('PF2'))
    return (f"{r['teste']:52s} n={r['n']:4d} PF {r['PF']:.2f} (bruto {r['PF_bruto']:.2f}) R$ {r['RS']:8.0f} (bruto {r['RS_bruto']:8.0f}) "
            f"DD {r['DD']:7.0f} | {anos} | {'APROVA' if r['APROVA'] else '-'}")
