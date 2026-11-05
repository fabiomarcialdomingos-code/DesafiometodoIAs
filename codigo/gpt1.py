from lab2 import *
import io,contextlib
def S(**kw):
    with contextlib.redirect_stdout(io.StringIO()): return run2('_',**kw)
def Sd(**kw):
    with contextlib.redirect_stdout(io.StringIO()): return run('_',**kw)
b=S(); ext=S(fill=(-99,0)); part=S(fill=(0,1.0001))
a=Sd(times=(790,),mode='dev',gmin=0.2,gmax=1.0); a=a[~a.d.isin(set(b.d))]
alld=pd.to_datetime(pd.Series(days)); alld=alld[alld>='2022-01-01']
def daily(t): return t.groupby(pd.to_datetime(t.d)).brl.sum().reindex(alld,fill_value=0)
base=daily(b); dobra=daily(pd.concat([ext,part.assign(brl=part.brl*2)])); v2=daily(pd.concat([ext,part.assign(brl=part.brl*2),a]))
print('== 1) atribuicao: base',round(base.sum()),'| +dobra',round(dobra.sum()-base.sum()),'| +tarde',round(v2.sum()-dobra.sum()))
# 2) tarde por motivo da manha ficar de fora
A_=A; reasons={}
for d in a.d:
    ix=idx[d]; o9=O[ix[540]]; p=pc[d]; ie=first_at(ix,600); aa=A_[ie]; c=C[ie-1]; gap=o9-p; z=abs(gap)/aa
    if d in roll: r='vencimento'
    elif z<0.10: r='gap pequeno'
    elif z>1.0: r='gap grande'
    elif (c-p)*np.sign(gap)<=0: r='gap ja fechou'
    elif 0.3*aa*0.2>200: r='teto R$200'
    else: r='outro'
    reasons[d]=r
a['mot']=a.d.map(reasons)
print('== 2) tarde por motivo:'); print(a.groupby('mot').brl.agg(['count','sum',f]).round(2))
# 3) sensibilidade do corte f perto de zero (em pontos)
print('== 3) corte do preenchimento deslocado em pontos')
def fpts(t):
    out=[]
    for _,r in t.iterrows():
        d=r.d; ix=idx[d]; o9=O[ix[540]]; ie=first_at(ix,600); c=C[ie-1]; gap=o9-pc[d]
        out.append((o9-c)*np.sign(gap))   # >0 = ja voltou (pts)
    return np.array(out)
bb=b.copy(); bb['fp']=fpts(b)
for sh in [-50,-25,-5,0,5,25,50]:
    w=np.where(bb.fp>=sh,2,1); x=bb.brl*w; d_=pd.Series(x.values,index=pd.to_datetime(bb.d)).groupby(level=0).sum().reindex(alld,fill_value=0)
    print(f'   corte {sh:+d} pts: R$ {x.sum():.0f} PF {f(x):.2f} contratos {w.sum()}')
# 4) controle: segundo contrato em dias aleatorios (mesmo numero)
rng=np.random.default_rng(1); k=(bb.fp>=0).sum(); real=(bb.brl[bb.fp>=0]).sum(); sims=[]
for _ in range(5000): sims.append(bb.brl.values[rng.choice(len(bb),k,replace=False)].sum())
sims=np.array(sims); print(f'== 4) 2o contrato nos dias f>=0: R$ {real:.0f} | aleatorio media R$ {sims.mean():.0f} p95 {np.percentile(sims,95):.0f} | p-valor {(sims>=real).mean():.4f}')
# 5) bootstrap em blocos do ganho incremental diario (v2-base)
def bboot(x,L=10,B=5000):
    n=len(x); m=[]
    for _ in range(B):
        idxs=[]
        while len(idxs)<n:
            s=rng.integers(0,n); l=rng.geometric(1/L); idxs+=list(range(s,min(n,s+l)))
        m.append(x[np.array(idxs[:n])].mean())
    return np.percentile(m,[2.5,50,97.5])
inc=(v2-base).values
for L in [5,10,20]: print(f'== 5) incremento v2-base R$/pregao, bloco {L}: IC95 {np.round(bboot(inc,L),2)}')
inc2=(dobra-base).values; print('   so a dobra bloco 10:',np.round(bboot(inc2,10),2)); inc3=(v2-dobra).values; print('   so a tarde bloco 10:',np.round(bboot(inc3,10),2))
# 6) custo estressado
for cst in [15,30,45]:
    adj=lambda t,m=1: (t.brl-(cst-15)*0.2*m)
    tot=pd.concat([adj(ext),adj(part,1)*2,adj(a)]); bt=adj(b)
    print(f'== 6) custo {cst} pts: base R$ {bt.sum():.0f} PF {f(bt):.2f} | v2 R$ {tot.sum():.0f} PF {f(tot):.2f}')
