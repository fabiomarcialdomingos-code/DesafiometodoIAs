from lab import *
Hh=df.high.values; Ll=df.low.values; V=df.volume.values; Tt=df.t.values
dl=df.groupby('d').agg(h=('high','max'),l=('low','min'))
ph=dl.h.shift(1); pl=dl.l.shift(1)
# volume 9:00-9:55 / media 20d
vm=df[(df.t>=540)&(df.t<600)].groupby('d').volume.sum(); vr=(vm/vm.rolling(20).mean().shift(1))
dow=pd.Series(pd.to_datetime(days).dayofweek,index=days)
prevday=pd.Series(pd.to_datetime(days),index=days).shift(1)
gapdays=(pd.Series(pd.to_datetime(days),index=days)-prevday).dt.days
def sigs2(t_ent=600,gmin=0.10,gmax=1.0,k=0.3,cap=200,stop='atr',buf=0.05,smin=0.15,grp=None,fill=None,small_ext=None,vol_max=None,mon=None,tmax=17*60):
    s=[]
    for d in days:
        ix=idx[d]
        if d in roll or 540 not in ix or pd.isna(pc.get(d)): continue
        ie=first_at(ix,t_ent)
        if ie is None or Dv[ie-1]!=d or np.isnan(A[ie]): continue
        o9=O[ix[540]]; p=pc[d]; gap=o9-p; a=A[ie]; c=C[ie-1]; z=abs(gap)/a; sg=np.sign(gap)
        if small_ext is not None:     # gap pequeno mas desvio grande as 10h, mesmo sentido
            dv=(c-p)
            if not (z<gmin and abs(dv)/a>=small_ext and np.sign(dv)==sg and sg!=0): continue
        else:
            if not (gmin<=z<=gmax): continue
            if (c-p)*sg<=0: continue
        if fill is not None:
            fr=(o9-c)/gap if gap!=0 else 0   # fracao do gap ja preenchida
            if not (fill[0]<=fr<fill[1]): continue
        if grp is not None:
            g='dentro' if pl[d]<=o9<=ph[d] else 'fora'
            if g!=grp: continue
        if vol_max is not None and not (vr.get(d,np.nan)<vol_max): continue
        if mon is not None and ((gapdays.get(d,1)>1)!=mon): continue
        dirn=-int(sg); e=O[ie]
        if stop=='atr': rp=k*a
        else:
            bars=range(ix[540],ie)
            ext=max(Hh[j] for j in bars) if sg>0 else min(Ll[j] for j in bars)
            rp=abs(ext-e)+buf*a; rp=min(max(rp,smin*a),k*a)
        if rp*0.2>cap: continue
        s.append(dict(i=ie-1,dir=dirn,stop=e-dirn*rp,target=None,tmax=tmax))
    return s
def run2(lab,**kw):
    t=simulate(df,sigs2(**kw),15,flat_min=Hm.FLAT,max_per_day=1); t['brl']=t.pts*0.2
    t=t[pd.to_datetime(t.d)>='2022-01-01']; y=t.groupby(pd.to_datetime(t.d).dt.year).brl; py=y.apply(f); n=len(t)
    print(f"{lab:58s} n={n:4d} ({n/(4.83*52):.2f}/sem) PF {f(t.brl):.2f} R$ {t.brl.sum():7.0f} minPF {py.min():.2f} | "+' '.join(f"{k%100}:{v:.2f}" for k,v in py.items()))
    return t
if __name__=='__main__':
    b=run2('BASE')
    print('--- stop estrutural (extremo 9:00-9:55 + buf, entre smin e 0.3 ATR)')
    for buf in [0.0,0.05,0.10]:
        for smin in [0.10,0.15]: run2(f'stop estrutural buf {buf} min {smin}',stop='struct',buf=buf,smin=smin)
    run2('estrutural buf .05 min .15, teto 300',stop='struct',cap=300)
    print('--- grupos do gap (dentro/fora do range anterior)')
    run2('so dentro',grp='dentro'); run2('so fora',grp='fora')
    for g0 in [0.03,0.05]: run2(f'dentro com gmin {g0}',grp='dentro',gmin=g0)
    print('--- fracao preenchida ate 9:55')
    for a_,b_ in [(-9,0),(0,0.3),(0.3,0.6),(0.6,1.0)]: run2(f'fill {a_}-{b_}',fill=(a_,b_))
    print('--- gap pequeno + extensao 1a hora (dias que o M2 descarta)')
    for x in [0.2,0.25,0.3,0.4]: run2(f'gap<0.10 e desvio10h>={x}',small_ext=x,k=0.25)
    print('--- volume da 1a hora')
    for vmx in [1.0,1.2,1.5]: run2(f'vol rel <{vmx}',vol_max=vmx)
    for vmx in [1.0,1.2]: run2(f'vol rel <{vmx} faixa 0.05-1.5',vol_max=vmx,gmin=0.05,gmax=1.5)
    print('--- segunda/pos feriado')
    run2('so dias apos fim de semana/feriado',mon=True); run2('so dias normais',mon=False)
    run2('pos-fds faixa 0.15-1.5',mon=True,gmin=0.15,gmax=1.5)
