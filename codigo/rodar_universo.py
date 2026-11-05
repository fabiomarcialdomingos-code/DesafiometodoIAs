#!/usr/bin/env python3
"""rodar_universo.py -- M2-A ("Acao atrasada") num universo grande de acoes, sem look-ahead, com walk-forward.

Entrada: uma pasta com {TICKER}_M5.csv e {TICKER}_D1.csv (sep ';', colunas time;open;high;low;close;tick_volume;real_volume,
         time no formato 'YYYY.MM.DD HH:MM'), mais o WIN M5 continuo (padrao /home/claude/win/hist21/WIN_contN_M5.csv).

O que faz:
 1. Le papel a papel (memoria constante) e gera o superconjunto de operacoes do M2-A (|lag| >= 0,10, alinhado com o WIN
    9-10h) nos cenarios base, stop 0,8/1,2 ATRd, entrada 5 min atrasada e +1 tick (motor.py).
 2. Liquidez = media 60d de volume*fechamento ATE ONTEM (shift 1). Filtro e tiers usam so isso (sem look-ahead).
    Custo por liquidez historica: >= R$150M/dia 0,06%; R$10-150M 0,10%; < R$10M 0,15% (ida e volta) + 15 pts/WIN no hedge.
 3. Walk-forward: grade (lo, wmin, coortes, stop k, piso e teto de liquidez) escolhida SO no treino (padrao 2022-23) com o
    criterio: n >= 200, PF >= 1,2, todos os anos >= 1,0, atraso 5 min >= 1,1, e os vizinhos lo x0,8 e x1,2 tambem com
    PF >= 1,15 e atraso >= 1,05 (robustez). Entre as que passam, maior R$ no treino. Mede no teste (padrao 2024+).
    Tambem mede a configuracao CONGELADA do agenteE (V6: lo 0,25, wmin 0, coorte cedo, k 1,0, liquidez R$5-300M).
 4. Tabelas por tier de liquidez x ano, por ano, por papel e o hedge inteiro agregado por dia.

Uso:
  python3 -I rodar_universo.py --pasta /caminho/acoes --saida /caminho/saida [--win WIN_M5.csv] [--jobs 2]
        [--treino_fim 2024-01-01] [--excluir BOVA11,SMAL11,...] [--reusar]
Saidas em --saida: superconjunto.pkl, wf_grade.csv, tier_ano_<cfg>.csv, ano_<cfg>.csv, papeis_<cfg>.csv,
                   hedge_inteiro_<cfg>.csv, resumo.md"""
import sys, os, glob, argparse, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motor as M, numpy as np, pandas as pd
from itertools import product
from multiprocessing import Pool

ETF_INDICE = {'BOVA11', 'BOVB11', 'BOVV11', 'SMAL11', 'SMAC11', 'IVVB11', 'BRAX11', 'ECOO11', 'DIVO11', 'FIND11', 'GOVE11',
              'MATB11', 'PIBB11', 'XBOV11', 'SPXI11', 'HASH11', 'GOLD11', 'NASD11', 'ACWI11', 'BBSD11', 'XFIX11', 'IMAB11'}
TIERS = [0, 5e6, 15e6, 40e6, 100e6, 300e6, np.inf]
NOMES = ['<5M', '5-15M', '15-40M', '40-100M', '100-300M', '>=300M']
CEN_UNIV = {k: M.CENARIOS[k] for k in ('base', 'k0.8', 'k1.2', 'atraso5', 'tick')}
CUSTO = M.custo_liquidez(((150e6, 0.0006), (10e6, 0.0010), (0, 0.0015)))
# V6 do agenteE + faixa de liquidez R$5M-300M/dia (acima de 300M a vantagem bruta some, ~2-5 bps; abaixo de 5M o custo real
# e incerto). ATENCAO: essa faixa foi decidida com os 61 papeis de 2022-26; so e fora da amostra para papeis NOVOS.
CONGELADA = dict(lo=0.25, hi=1.2, wmin=0.0, coortes=('cedo',), k=1.0, liq_min=5e6, liq_max=300e6)
_W = None


def _um(args):
    pasta, t = args
    try:
        s, G = M.carrega_acao(f'{pasta}/{t}_M5.csv', f'{pasta}/{t}_D1.csv', _W)
        T = M.trades_papel(t, s, G, _W, CEN_UNIV)
        if not len(T): return t, None, None
        T = T[T.lagA >= 0.10]
        for c in ('lagA', 'wa', 'beta', 'atrf', 'gap', 'rs', 'rw'): T[c] = T[c].astype('float32')
        liq = s.vol_rs.describe()[['count', '50%']].to_dict()
        return t, T, dict(t=t, dias_com_dado=int(s.op.notna().sum()), liq_mediana=liq['50%'],
                          leilao_10h=float(np.nanmean(G['traded'][:, 0][s.op.notna().values])) if s.op.notna().any() else np.nan)
    except Exception as e:
        return t, None, dict(t=t, erro=str(e))


def superconjunto(pasta, W, jobs, excluir):
    global _W; _W = W
    ts = sorted(os.path.basename(p)[:-7] for p in glob.glob(f'{pasta}/*_M5.csv'))
    ts = [t for t in ts if os.path.exists(f'{pasta}/{t}_D1.csv') and t not in excluir]
    print(f'{len(ts)} papeis em {pasta}', flush=True)
    out, info = [], []; t0 = time.time()
    with Pool(jobs) as pool:
        for i, (t, T, inf) in enumerate(pool.imap_unordered(_um, [(pasta, t) for t in ts], chunksize=4)):
            if T is not None: out.append(T)
            if inf: info.append(inf)
            if (i + 1) % 25 == 0: print(f'  {i+1}/{len(ts)} ({time.time()-t0:.0f}s)', flush=True)
    return (pd.concat(out, ignore_index=True) if out else pd.DataFrame()), pd.DataFrame(info)


def sel(T, c, cen='base'):
    return M.filtra(T, lo=c['lo'], hi=c.get('hi', 1.2), wmin=c['wmin'], cen=cen, coortes=c['coortes'],
                    liq_min=c['liq_min'], liq_max=c['liq_max'])


def run_cfg(T, c, ini=None, fim=None):
    cen = {0.8: 'k0.8', 1.0: 'base', 1.2: 'k1.2'}[c['k']]
    X = sel(T, c, cen)
    if ini is not None: X = X[X.d >= ini]
    if fim is not None: X = X[X.d < fim]
    X = M.pnl(X, CUSTO)
    Xa = sel(T, c, 'atraso5'); Xa = Xa[Xa.set_index(['d', 't', 'coorte']).index.isin(X.set_index(['d', 't', 'coorte']).index)]
    Xa = M.pnl(Xa, CUSTO)
    return X, Xa


def metr(X, Xa, ini, fim):
    if not len(X): return dict(n=0, PF=np.nan, min_ano=np.nan, atraso=np.nan, RS=0, op_sem=0)
    py = X.groupby(X.d.dt.year).brl.apply(M.pf)
    return dict(n=len(X), op_sem=round(len(X)/M.semanas(ini, fim), 1), PF=M.pf(X.brl), PF_bruto=M.pf(X.brl_bruto),
                min_ano=py.min(), atraso=M.pf(Xa.brl) if len(Xa) else np.nan, RS=round(X.brl.sum()),
                DD=round(M.dd_diario(X)), papeis=X.t.nunique())


def tabelas(T, W, c, nome, saida, ini, fim, teste_ini):
    X, Xa = run_cfg(T, c)
    X['tier'] = pd.cut(X.vol_rs, TIERS, labels=NOMES, right=False); Xa['tier'] = pd.cut(Xa.vol_rs, TIERS, labels=NOMES, right=False)
    X['ano'] = X.d.dt.year; Xa['ano'] = Xa.d.dt.year
    def bloco(g, ga):
        return pd.Series(dict(n=len(g), papeis=g.t.nunique(), PF=M.pf(g.brl), PF_bruto=M.pf(g.brl_bruto),
                              bps_bruto=round(1e4*g.brl_bruto.sum()/g.notional.sum(), 1) if len(g) else np.nan,
                              PF_atraso5=M.pf(ga.brl) if len(ga) else np.nan, RS=round(g.brl.sum())))
    ta = []
    for (tr, an), g in X.groupby(['tier', 'ano'], observed=True):
        ga = Xa[(Xa.tier == tr) & (Xa.ano == an)]; ta.append(bloco(g, ga).rename((tr, an)))
    for tr, g in X.groupby('tier', observed=True):
        ta.append(bloco(g, Xa[Xa.tier == tr]).rename((tr, 'total')))
    TA = pd.DataFrame(ta); TA.index = pd.MultiIndex.from_tuples(TA.index, names=['tier', 'ano']); TA.to_csv(f'{saida}/tier_ano_{nome}.csv')
    an = pd.DataFrame([bloco(g, Xa[Xa.ano == a]).rename(a) for a, g in X.groupby('ano')]); an.to_csv(f'{saida}/ano_{nome}.csv')
    pp = X.groupby('t').agg(n=('brl', 'size'), PF=('brl', M.pf), RS=('brl', 'sum'), liq_med=('vol_rs', 'median')).sort_values('RS')
    pp.to_csv(f'{saida}/papeis_{nome}.csv')
    F = M.hedge_inteiro(X, W); F[F.n > 0].to_csv(f'{saida}/hedge_inteiro_{nome}.csv', index=False)
    tot = metr(X, Xa, ini, fim); te = X[X.d >= teste_ini]; tea = Xa[Xa.d >= teste_ini]
    oos = metr(te, tea, teste_ini, fim)
    Fi = F[(F.n > 0)]; tot['PF_dia_hedge_inteiro'] = M.pf(Fi.net)
    Xt = sel(T, c, 'tick' if c['k'] == 1.0 else {0.8: 'k0.8', 1.2: 'k1.2'}[c['k']])
    if c['k'] == 1.0:
        Xt = M.pnl(Xt[Xt.set_index(['d', 't', 'coorte']).index.isin(X.set_index(['d', 't', 'coorte']).index)], CUSTO)
        tot['PF_tick'] = M.pf(Xt.brl); oos['PF_tick'] = M.pf(Xt[Xt.d >= teste_ini].brl)
    else:
        tot['PF_tick'] = oos['PF_tick'] = np.nan          # cenario de tick so foi simulado com k = 1,0
    return TA, an, pp, tot, oos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pasta', required=True); ap.add_argument('--saida', required=True)
    ap.add_argument('--win', default=M.WINP); ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--inicio', default='2022-03-01'); ap.add_argument('--treino_fim', default='2024-01-01')
    ap.add_argument('--fim', default='2026-12-31'); ap.add_argument('--excluir', default=','.join(sorted(ETF_INDICE)))
    ap.add_argument('--reusar', action='store_true', help='reusa superconjunto.pkl da pasta de saida')
    ap.add_argument('--pf_min_treino', type=float, default=1.2,
                    help='PF minimo no treino (nos 61 papeis o PF caiu ~0,10-0,15 do treino para o teste; 1,35 e mais prudente)')
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    W = M.carrega_win(a.win)
    pk = f'{a.saida}/superconjunto.pkl'
    if a.reusar and os.path.exists(pk):
        T, info = pickle.load(open(pk, 'rb'))
    else:
        T, info = superconjunto(a.pasta, W, a.jobs, set(x for x in a.excluir.split(',') if x))
        pickle.dump((T, info), open(pk, 'wb'))
    info.to_csv(f'{a.saida}/papeis_info.csv', index=False)
    T = T[(T.d >= a.inicio) & (T.d < a.fim)]
    fim_real = str(T.d.max().date()); IS0, IS1 = a.inicio, a.treino_fim
    print(f'superconjunto: {len(T)} linhas, {T.t.nunique()} papeis, {T.d.min().date()} a {fim_real}', flush=True)

    # ------------------------------ walk-forward
    G = []
    grade = list(product((0.15, 0.20, 0.25, 0.30), (0.0, 0.5), (('cedo',), ('cedo', 'tarde')), (0.8, 1.0, 1.2),
                         (0.0, 5e6, 15e6), (300e6, np.inf)))
    cache = {}
    def is_metr(c):
        key = (c['lo'], c['wmin'], c['coortes'], c['k'], c['liq_min'], c['liq_max'])
        if key not in cache:
            X, Xa = run_cfg(T, c, IS0, IS1); Y, Ya = run_cfg(T, c, IS1, None)
            cache[key] = (metr(X, Xa, IS0, IS1), metr(Y, Ya, IS1, fim_real))
        return cache[key]
    for lo, wmin, coortes, k, lmin, lmax in grade:
        c = dict(lo=lo, hi=1.2, wmin=wmin, coortes=coortes, k=k, liq_min=lmin, liq_max=lmax)
        mi, mo = is_metr(c)
        viz = [is_metr({**c, 'lo': round(lo*f, 3)})[0] for f in (0.8, 1.2)]
        ok_viz = all((v['n'] > 0) and v['PF'] >= 1.15 and v['atraso'] >= 1.05 for v in viz)
        passa = (mi['n'] >= 200) and mi['PF'] >= a.pf_min_treino and mi['min_ano'] >= 1.0 and mi['atraso'] >= 1.1 and ok_viz
        G.append(dict(lo=lo, wmin=wmin, coortes='+'.join(coortes), k=k, liq_min=lmin, liq_max=lmax, passa_treino=passa,
                      **{f'{x}_treino': v for x, v in mi.items()}, **{f'{x}_teste': v for x, v in mo.items()}))
    G = pd.DataFrame(G); G.to_csv(f'{a.saida}/wf_grade.csv', index=False)
    ok = G[G.passa_treino].sort_values('RS_treino', ascending=False)
    md = [f'# M2-A em universo grande: {T.t.nunique()} papeis ({a.pasta})', '',
          f'Treino {IS0} a {IS1}; teste {IS1} a {fim_real}. Custo por liquidez historica (0,06% / 0,10% / 0,15%), R$80 por operacao.', '']
    cfgs = {'congelada_V6': CONGELADA}
    if len(ok):
        b = ok.iloc[0]
        cfgs['escolhida_treino'] = dict(lo=b.lo, hi=1.2, wmin=b.wmin, coortes=tuple(b.coortes.split('+')), k=b.k, liq_min=b.liq_min, liq_max=b.liq_max)
        md += [f'## Walk-forward (PF minimo no treino {a.pf_min_treino})', f'{len(ok)} de {len(G)} configuracoes passam no treino (com vizinhos lo x0,8/x1,2).',
               f'- Teste das que passam: PF mediano {ok.PF_teste.median():.2f}; {(ok.PF_teste >= 1.2).mean():.0%} com PF >= 1,2; '
               f'{((ok.PF_teste >= 1.2) & (ok.min_ano_teste >= 1) & (ok.atraso_teste >= 1.1)).mean():.0%} passam tudo no teste.',
               f'- Correlacao PF treino x teste (grade toda): {G.PF_treino.corr(G.PF_teste):.2f}', '',
               ok.head(10)[['lo', 'wmin', 'coortes', 'k', 'liq_min', 'liq_max', 'n_treino', 'PF_treino', 'atraso_treino', 'RS_treino',
                            'n_teste', 'op_sem_teste', 'PF_teste', 'min_ano_teste', 'atraso_teste', 'RS_teste']].round(2).to_markdown(index=False), '']
    else:
        md += ['## Walk-forward', 'NENHUMA configuracao passa no treino.', '']
    for nome, c in cfgs.items():
        TA, an, pp, tot, oos = tabelas(T, W, c, nome, a.saida, IS0, fim_real, IS1)
        md += [f'## {nome}: {c}', '',
               f"- Periodo todo: n {tot['n']} ({tot['op_sem']}/sem), {tot['papeis']} papeis, PF {tot['PF']:.2f} (bruto {tot['PF_bruto']:.2f}), "
               f"pior ano {tot['min_ano']:.2f}, atraso 5 min {tot['atraso']:.2f}, +1 tick {tot['PF_tick']:.2f}, R$ {tot['RS']}, DD {tot['DD']}, PF diario c/ hedge inteiro {tot['PF_dia_hedge_inteiro']:.2f}",
               f"- Teste ({IS1}+): n {oos['n']} ({oos['op_sem']}/sem), PF {oos['PF']:.2f}, pior ano {oos['min_ano']:.2f}, atraso {oos['atraso']:.2f}, +1 tick {oos['PF_tick']:.2f}, R$ {oos['RS']}", '',
               '### Por ano', an.round(2).to_markdown(), '', '### Por tier de liquidez (R$/dia, media 60d ate ontem)',
               TA.xs('total', level='ano').round(2).to_markdown(), '',
               '### Tier x ano (PF)', TA.PF.unstack('ano').round(2).to_markdown(), '',
               f'### Papeis: {(pp.PF > 1).mean():.0%} com PF > 1; 5 piores e 5 melhores por R$',
               pd.concat([pp.head(5), pp.tail(5)]).round(2).to_markdown(), '']
        print(f"{nome}: n {tot['n']} ({tot['op_sem']}/sem) PF {tot['PF']:.2f} pior ano {tot['min_ano']:.2f} atraso {tot['atraso']:.2f} R$ {tot['RS']}"
              f" | teste PF {oos['PF']:.2f} atraso {oos['atraso']:.2f}", flush=True)
    open(f'{a.saida}/resumo.md', 'w').write('\n'.join(md))
    print(f'ok -> {a.saida}/resumo.md')


if __name__ == '__main__':
    main()
