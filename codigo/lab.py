import sys; sys.path.insert(0,'/home/claude/win/grade'); import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
from engine import load_mt5_csv, prep, simulate
import horarios as Hm
f=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2) if len(x) else np.nan
df=prep(load_mt5_csv('/home/claude/win/hist21/WIN_contN_M5.csv')); T=Hm._day_tables(df)
days,pc,roll,idx=T; O=df.open.values; C=df.close.values; A=df.atr_d.values; Dv=df.d.values
def first_at(ix,m):
    ks=[k for k in ix if k>=m]; return ix[min(ks)] if ks else None
def sigs(times=(600,), gmin=0.10, gmax=1.0, k=0.3, cap=200, capmode='skip', tmax=17*60, dev_min=None, need_open=True, mode='gap', exit_fill=False):
    """mode='gap': referencia = gap da abertura; 'dev': desvio do preco atual vs fech.ant (sem exigir gap)."""
    s=[]
    for d in days:
        ix=idx[d]
        if d in roll or 540 not in ix or pd.isna(pc.get(d)): continue
        o9=O[ix[540]]; p=pc[d]; gap=o9-p
        for tm in times:
            ie=first_at(ix,tm)
            if ie is None or ie<1 or Dv[ie-1]!=d or np.isnan(A[ie]): continue
            a=A[ie]; c=C[ie-1]
            if mode=='gap':
                z=abs(gap)/a
                if not (gmin<=z<=gmax): continue
                if need_open and (c-p)*np.sign(gap)<=0: continue
                dirn=-int(np.sign(gap))
            else:
                dv=c-p; z=abs(dv)/a
                if not (gmin<=z<=gmax): continue
                dirn=-int(np.sign(dv))
            rp=k*a
            if rp*0.2>cap:
                if capmode=='skip': continue
                rp=cap/0.2
            e=O[ie]
            s.append(dict(i=ie-1,dir=dirn,stop=e-dirn*rp,target=(p if exit_fill else None),tmax=tmax))
    return s
def run(lab,maxd=1,**kw):
    t=simulate(df,sigs(**kw),15,flat_min=Hm.FLAT,max_per_day=maxd); t['brl']=t.pts*0.2
    t=t[pd.to_datetime(t.d)>='2022-01-01']; y=t.groupby(pd.to_datetime(t.d).dt.year).brl
    py=y.apply(f); n=len(t)
    print(f"{lab:55s} n={n:4d} ({n/(4.83*52):.2f}/sem) PF {f(t.brl):.2f} R$ {t.brl.sum():7.0f} min PF ano {py.min():.2f} | "+' '.join(f"{k%100}:{v:.2f}" for k,v in py.items()))
    return t
if __name__=='__main__':
    run('BASE (10h, 0.10-1.0, k0.3, teto 200 skip)')
