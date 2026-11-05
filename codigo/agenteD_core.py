"""agenteD - nucleo M1 para o WIN.
Matrizes dia x minuto (09:00..18:35) com NaN onde nao ha barra. Convencoes iguais a grade/engine.py + m2vol/lab*.py:
  - pc = fechamento da ultima barra do pregao anterior; ATRd = media 14d de (max-min) do dia, ate ontem.
  - abertura 9:00 = open da 1a barra com t em [9:00, 9:05) (equivale a barra M5 das 9:00).
  - sinal com barras FECHADAS: "preco em m" = close da ultima barra com t < m; entrada = open da 1a barra com t >= m.
  - stop checado barra a barra (inclusive na barra de entrada); se a barra abre alem do stop, sai na abertura.
  - saida por horario: close da ultima barra com t < tmax (tmax=17:05 -> close da barra 17:04 = mesmo preco do M5).
  - custo 15 pts ida+volta por contrato, R$0,20/pt. Vencimento (quarta mais proxima do dia 15 dos meses pares) pulado.
Nada aqui envia ordens: e so backtest em CSV local."""
import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/win/grade')
from engine import load_mt5_csv
import horarios as Hm

PV, COST, CAP = 0.2, 15.0, 200.0
M0, M1_ = 540, 1116          # colunas: minuto 540 (9:00) .. 1115 (18:35)
NM = M1_ - M0
START = pd.Timestamp('2022-01-01')

def hm(h, m=0): return h*60 + m
def col(m): return m - M0

def us_dst(x):
    y = x.year; m = pd.Timestamp(y, 3, 1); s = m + pd.Timedelta(days=(6 - m.weekday()) % 7 + 7)
    n = pd.Timestamp(y, 11, 1); e = n + pd.Timedelta(days=(6 - n.weekday()) % 7)
    return s <= x < e

class Win:
    def __init__(self, path='/home/claude/win/hist21/WIN_contN_M1.csv'):
        df = load_mt5_csv(path)
        d = df.index.normalize(); t = df.index.hour*60 + df.index.minute
        df = df[(t >= M0) & (t < M1_)]; d = df.index.normalize(); t = (df.index.hour*60 + df.index.minute).values
        self.days = pd.DatetimeIndex(d.unique()); nd = len(self.days)
        di = self.days.get_indexer(d); ci = t - M0
        self.O, self.H, self.L, self.C, self.V = [np.full((nd, NM), np.nan) for _ in range(5)]
        for M, s in [(self.O, 'open'), (self.H, 'high'), (self.L, 'low'), (self.C, 'close'), (self.V, 'volume')]:
            M[di, ci] = df[s].values
        self.has = ~np.isnan(self.C)
        # close forward-filled (preco "em m" = Cf[:, col(m)-1])
        self.Cf = pd.DataFrame(self.C).ffill(axis=1).values
        # proxima barra existente com t>=m: indice de coluna
        idx = np.where(self.has, np.arange(NM)[None, :], NM)
        self.nxt = np.minimum.accumulate(idx[:, ::-1], axis=1)[:, ::-1]
        g = df.groupby(d)
        dh, dl, dc = g.high.max().values, g.low.min().values, g.close.last().values
        self.pc = np.r_[np.nan, dc[:-1]]
        self.atr = pd.Series(dh - dl).rolling(14).mean().shift(1).values
        first9 = np.where(self.has[:, :5].any(1), self.nxt[:, 0], NM)
        self.o9 = np.array([self.O[k, j] if j < 5 else np.nan for k, j in enumerate(first9)])
        roll = Hm.win_roll_days(); self.roll = np.array([x in roll for x in self.days])
        self.dst = np.array([us_dst(x) for x in self.days])
        self.ok = (~self.roll) & ~np.isnan(self.o9) & ~np.isnan(self.pc) & ~np.isnan(self.atr)
        self.insample = self.days >= START
        self.last_col = np.array([np.flatnonzero(r)[-1] if r.any() else -1 for r in self.has])
        # fechamento do a vista: 17:55 (call ate 18:00) fora do horario de verao dos EUA; 16:55 (ate 17:00) dentro
        self.cc = np.where(self.dst, hm(17, 0), hm(18, 0))

    def price_at(self, m):
        """preco em m (close da ultima barra com t<m) por dia; NaN se nao ha barra antes de m no dia."""
        m = np.broadcast_to(np.asarray(m), (len(self.days),))
        out = self.Cf[np.arange(len(self.days)), np.clip(m - M0 - 1, 0, NM-1)]
        return np.where(m - M0 - 1 >= 0, out, np.nan)

    def entry_col(self, m):
        m = np.broadcast_to(np.asarray(m), (len(self.days),))
        return self.nxt[np.arange(len(self.days)), np.clip(m - M0, 0, NM-1)]

# ---------------------------------------------------------------- simulacao de uma operacao
def sim_trade(W, k, j0, dirn, rp, tmax, target=None, part=0.0, be=None, be_lock=0.0, trail=None, trail_on=0.0,
              tstop=None, path=False):
    """k=dia, j0=coluna de entrada (open), rp=distancia do stop em pts, tmax=minuto (exclusivo) de saida por horario.
    target: preco de parcial (fracao `part` sai la; part=1 => alvo cheio). be: move stop p/ entrada+be_lock*R quando um
    fechamento atinge +be R. trail: distancia de trailing (pts) a partir do melhor extremo, ativa apos +trail_on R.
    Retorna (pontos brutos por contrato (media ponderada das fracoes), motivo, coluna de saida, mtm-path opcional)."""
    O, H, L, C = W.O[k], W.H[k], W.L[k], W.C[k]
    jx = col(tmax); e = O[j0]; stop = e - dirn*rp; R = rp
    simple = target is None and be is None and trail is None
    if simple and not path:
        js = np.arange(j0, jx); js = js[W.has[k, js]]
        if len(js) == 0: return np.nan, 'nada', j0, None
        adv = (L[js] if dirn == 1 else H[js]); hit = (adv - stop)*dirn <= 0
        if hit.any():
            j = js[np.argmax(hit)]; px = stop if (O[j] - stop)*dirn > 0 else O[j]
            return (px - e)*dirn, 'stop', j, None
        return (C[js[-1]] - e)*dirn, 'hora', js[-1], None
    rem = 1.0; acc = 0.0; best = e; mtm = np.full(NM, np.nan) if path else None; why = 'hora'; jl = j0
    for j in range(j0, jx):
        if not W.has[k, j]:
            if path: mtm[j] = acc + rem*(W.Cf[k, j] - e)*dirn
            continue
        jl = j
        adv = L[j] if dirn == 1 else H[j]; fav = H[j] if dirn == 1 else L[j]
        if (adv - stop)*dirn <= 0:
            px = stop if (O[j] - stop)*dirn > 0 else O[j]; acc += rem*(px - e)*dirn; rem = 0; why = 'stop'
            if path: mtm[j:] = acc
            break
        if target is not None and rem > 0 and part > 0 and (fav - target)*dirn >= 0 and rem > 1 - part + 1e-9:
            px = target if (O[j] - target)*dirn < 0 else O[j]; acc += part*(px - e)*dirn; rem -= part
            if rem <= 1e-9:
                why = 'alvo'
                if path: mtm[j:] = acc
                break
        if trail is not None:
            best = max(best, fav) if dirn == 1 else min(best, fav)
            if (best - e)*dirn >= trail_on*R:
                ns = best - dirn*trail
                if (ns - stop)*dirn > 0: stop = ns
        if be is not None and (C[j] - e)*dirn >= be*R:
            ns = e + dirn*be_lock*R
            if (ns - stop)*dirn > 0: stop = ns
        if path: mtm[j] = acc + rem*(C[j] - e)*dirn
    else:
        acc += rem*(C[jl] - e)*dirn; rem = 0
    if rem > 0: acc += rem*(C[jl] - e)*dirn
    return acc, why, jl, mtm

# ---------------------------------------------------------------- M2 v2
def m2_morning(W, t_sig=600, t_ent=None, gmin=0.10, gmax=1.0, k=0.3, cap=CAP, tmax=hm(17, 5), anchor=None, sizing=True,
               mgmt=None, path=False, fcut=0.0):
    """t_sig: minuto em que se le o preco (close da barra anterior). t_ent: minuto da entrada (default = t_sig).
    anchor: array alternativo de 'fechamento anterior' (default W.pc)."""
    t_ent = t_sig if t_ent is None else t_ent
    pc = W.pc if anchor is None else anchor
    c = W.price_at(t_sig); j0s = W.entry_col(t_ent); rows = []; paths = {}
    for kd in np.flatnonzero(W.ok & ~np.isnan(pc)):
        o9, p, a = W.o9[kd], pc[kd], W.atr[kd]; gap = o9 - p; sg = np.sign(gap)
        if sg == 0 or not (gmin <= abs(gap)/a <= gmax): continue
        if np.isnan(c[kd]) or (c[kd] - p)*sg <= 0: continue
        if k*a*PV > cap: continue
        j0 = j0s[kd]
        if j0 >= col(tmax) or j0 == 0: continue
        dirn = -int(sg); f = (o9 - c[kd])/gap; ctr = 2 if (sizing and f >= fcut) else 1
        kw = dict(mgmt or {})
        if kw.get('target') == 'pc': kw['target'] = p
        if 'part_by_ctr' in kw:                 # parcial so quando ha 2 contratos (1 de 2 sai no alvo)
            pb = kw.pop('part_by_ctr'); kw['part'] = pb[ctr]
            if kw['part'] == 0: kw.pop('target', None); kw.pop('part')
        g, why, jx, mt = sim_trade(W, kd, j0, dirn, k*a, tmax, path=path, **kw)
        if np.isnan(g): continue
        rows.append(dict(k=kd, d=W.days[kd], leg='manha', dir=dirn, e=W.O[kd, j0], R=k*a, gross=g, why=why,
                         ctr=ctr, f=f, z=abs(gap)/a, tent=j0 + M0, txit=jx + M0))
        if path: paths[kd] = mt
    t = _fin(pd.DataFrame(rows))
    return (t, paths) if path else t

def m2_afternoon(W, t_sig=hm(13, 10), gmin=0.2, gmax=1.0, k=0.3, cap=CAP, tmax=hm(17, 5), skip_days=(), anchor=None,
                 mgmt=None, only_days=None, dirmode='fade', rng=None):
    pc = W.pc if anchor is None else anchor
    c = W.price_at(t_sig); j0s = W.entry_col(t_sig); rows = []; skip = set(skip_days)
    for kd in np.flatnonzero(W.ok & ~np.isnan(pc)):
        if kd in skip or (only_days is not None and kd not in only_days): continue
        p, a = pc[kd], W.atr[kd]
        if np.isnan(c[kd]): continue
        dv = c[kd] - p
        if not (gmin <= abs(dv)/a <= gmax) or k*a*PV > cap: continue
        j0 = j0s[kd]
        if j0 >= col(tmax): continue
        dirn = -int(np.sign(dv))
        if dirmode == 'random': dirn = int(rng.choice([-1, 1]))
        g, why, jx, _ = sim_trade(W, kd, j0, dirn, k*a, tmax, **(mgmt or {}))
        if np.isnan(g): continue
        rows.append(dict(k=kd, d=W.days[kd], leg='tarde', dir=dirn, e=W.O[kd, j0], R=k*a, gross=g, why=why, ctr=1,
                         f=np.nan, z=abs(dv)/a, tent=j0 + M0, txit=jx + M0))
    return _fin(pd.DataFrame(rows))

def _fin(t):
    if len(t) == 0: return pd.DataFrame(columns=['k', 'd', 'leg', 'dir', 'e', 'R', 'gross', 'why', 'ctr', 'pts', 'brl', 'Rm'])
    t['pts'] = t.gross - COST                      # por contrato
    t['brl'] = t.pts*PV*t.ctr; t['Rm'] = t.pts/t.R
    return t

def m2v2(W, morning_kw=None, aft_kw=None, aft_all=False):
    m = m2_morning(W, **(morning_kw or {}))
    a = m2_afternoon(W, skip_days=() if aft_all else set(m.k), **(aft_kw or {}))
    t = pd.concat([m, a], ignore_index=True)
    return t[t.d >= START].sort_values(['d', 'leg']).reset_index(drop=True)

# ---------------------------------------------------------------- estatistica
def pf(x):
    x = np.asarray(x, float); l = -x[x < 0].sum()
    return round(x[x > 0].sum()/l, 2) if l > 0 else np.inf

def all_days(W): return W.days[W.insample]

def daily(W, t):
    return t.groupby('d').brl.sum().reindex(all_days(W), fill_value=0.0)

def stats(W, t, lab=''):
    if t is None or len(t) == 0: return dict(teste=lab, n=0)
    dd = daily(W, t); eq = dd.cumsum(); weeks = (all_days(W)[-1] - all_days(W)[0]).days/7
    r = dict(teste=lab, n=len(t), sem=round(len(t)/weeks, 2), ctr=int(t.ctr.sum()), PF=pf(t.brl), RS=round(t.brl.sum()),
             DD=round((eq - eq.cummax()).min()), acerto=round((t.brl > 0).mean(), 2))
    py = t.groupby(t.d.dt.year).brl.apply(pf)
    for y, v in py.items(): r[f'PF{y}'] = v
    r['minPF'] = py.min()
    return r

def bboot(x, L=10, B=5000, seed=7):
    """bootstrap em blocos moveis de tamanho fixo L; IC95 da media diaria."""
    x = np.asarray(x, float); n = len(x); rng = np.random.default_rng(seed); nb = int(np.ceil(n/L))
    st = rng.integers(0, n - L + 1, size=(B, nb)); ix = (st[:, :, None] + np.arange(L)[None, None, :]).reshape(B, -1)[:, :n]
    m = x[ix].mean(1)
    return np.percentile(m, [2.5, 97.5]), x.mean()

def compare(W, t, base, lab):
    """estatisticas + incremento diario vs base nos mesmos pregoes."""
    r = stats(W, t, lab); inc = (daily(W, t) - daily(W, base)).values
    (lo, hi), mu = bboot(inc)
    r.update(inc_dia=round(mu, 2), ic_lo=round(lo, 2), ic_hi=round(hi, 2), inc_RS=round(inc.sum()))
    return r

def fmt(rows, cols=None):
    df = pd.DataFrame(rows)
    if cols: df = df[[c for c in cols if c in df]]
    return df.to_string(index=False)

COLS = ['teste', 'n', 'sem', 'ctr', 'PF', 'RS', 'DD', 'PF2022', 'PF2023', 'PF2024', 'PF2025', 'PF2026', 'minPF',
        'inc_dia', 'ic_lo', 'ic_hi']
