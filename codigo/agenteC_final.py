"""Final -- regra ATRASADA com risco real de R$80 (stop 1,0 ATRd, tamanho R$80/(1,0*ATRd)), grade +-20% incluindo o stop,
walk-forward (escolhe parametros so em 2022-23 e mede 2024-26), metades do periodo, carteira com o M2 do WIN.
Uso: python3 -I final.py  -> final_out.txt, final_grade.csv, trades_final.csv"""
import sys; sys.path.insert(0, '/home/claude/win/m2vol/agenteC')
import core as C, numpy as np, pandas as pd
from p2b_regra import trades_lag

FIN = dict(kinds=('small',), lo=0.25, hi=1.2, wmin=0.5, ent='10:05', ext='16:55', k=1.0, hedge=True)

if __name__ == '__main__':
    P = C.add_beta(C.build()); m2 = C.m2_win_daily(); G = []
    def run(lab, **ch):
        T = trades_lag(P, **{**FIN, **ch}); r = C.resumo(T, lab, m2); G.append(r); print(C.linha(r), flush=True); return T
    print('=== FINAL: small caps, |lag| 0,25-1,2 ATRd, |WIN 9-10h| >= 0,5x media, atrasada na direcao do WIN, 10:05 -> 16:55, hedge, stop 1,0 ATRd ===')
    T = run('FINAL base'); T.to_csv(f'{C.OUT}/trades_final.csv', index=False)
    print('--- grade +-20% ---')
    for lab, ch in [('lo=0.20', {'lo': 0.20}), ('lo=0.30', {'lo': 0.30}), ('hi=0.96', {'hi': 0.96}), ('hi=1.44', {'hi': 1.44}),
                    ('wmin=0.40', {'wmin': 0.40}), ('wmin=0.60', {'wmin': 0.60}), ('stop 0.8', {'k': 0.8}), ('stop 1.2', {'k': 1.2})]:
        run(f'FINAL {lab}', **ch)
    for bw in (48, 72):
        C.add_beta(P, win=bw); run(f'FINAL beta {bw}d'); C.add_beta(P, win=60)
    print('--- variacoes / estresses ---')
    run('FINAL saida 13:00', ext='13:00'); run('FINAL saida 11:00', ext='11:00'); run('FINAL sem hedge', hedge=False)
    run('FINAL custo x1,5 (0,15%)', cost_mult=1.5); run('FINAL custo x2 (0,20%)', cost_mult=2.0)
    run('FINAL +1 tick na entrada', extra_ticks=1); run('FINAL entrada 10:10', ent='10:10'); run('FINAL entrada 10:15', ent='10:15')
    run('FINAL stop 0,3 ATRd (como M2)', k=0.3)
    pd.DataFrame(G).to_csv(f'{C.OUT}/final_grade.csv', index=False)

    print('\n--- walk-forward: escolhe (lo, wmin, saida) pelo PF em 2022-23 (n>=150) e mede 2024-26 ---')
    W = []
    for lo in (0.15, 0.20, 0.25, 0.30, 0.40):
        for wmin in (0.0, 0.5, 1.0):
            for ext in ('11:00', '13:00', '16:55'):
                X = trades_lag(P, **{**FIN, 'lo': lo, 'wmin': wmin, 'ext': ext})
                a = X[X.d < '2024-01-01']; b = X[X.d >= '2024-01-01']
                W.append(dict(lo=lo, wmin=wmin, ext=ext, n_is=len(a), PF_is=C.pf(a.brl), n_oos=len(b), PF_oos=C.pf(b.brl),
                              RS_oos=round(b.brl.sum())))
    W = pd.DataFrame(W); W.to_csv(f'{C.OUT}/final_walkforward.csv', index=False)
    best = W[W.n_is >= 150].sort_values('PF_is', ascending=False)
    print(best.head(8).to_string(index=False))
    print('mediana do PF fora da amostra entre TODAS as 45 combinacoes:', round(W.PF_oos.median(), 2), '| % com PF_oos>1:', f'{(W.PF_oos > 1).mean():.0%}',
          '| % com PF_oos>=1,2:', f'{(W.PF_oos >= 1.2).mean():.0%}')

    print('\n--- metades e trimestres ---')
    T['q'] = pd.to_datetime(T.d).dt.to_period('Q')
    q = T.groupby('q').brl.agg(['size', 'sum', C.pf]); q.columns = ['n', 'RS', 'PF']
    print('trimestres com R$>0:', (q.RS > 0).sum(), 'de', len(q)); print(q.round(2).T.to_string())

    print('\n--- carteira: M2 v2 do WIN + FINAL (R$ por dia) ---')
    dd = T.groupby('d').brl.sum()
    j = pd.concat([dd.rename('final'), m2], axis=1).fillna(0); j = j[(j.index >= '2022-02-01') & (j.index <= '2026-10-01')]
    for c in ['m2', 'final']:
        e = j[c].cumsum(); print(f'{c:6s} R$ {j[c].sum():8.0f}  DD {(e - e.cummax()).min():8.0f}')
    s = j.m2 + j.final; e = s.cumsum(); print(f'soma   R$ {s.sum():8.0f}  DD {(e - e.cummax()).min():8.0f}   corr diaria {j.m2.corr(j.final):.2f}'
                                                 f' | corr nos dias em que os dois operam {j[(j.m2 != 0) & (j.final != 0)].corr().iloc[0, 1]:.2f}')
    y = j.groupby(j.index.year).sum(); print(y.round(0).to_string())
