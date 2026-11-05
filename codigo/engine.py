"""Laboratorio da grade: testa metodos intraday em barras de 5 min (WIN/WDO/BOVA11).
Entrada sempre na abertura da barra seguinte ao sinal; stop antes do alvo no mesmo candle (conservador);
custo fixo por operacao em pontos (inclui taxas + escorregamento)."""
import pandas as pd, numpy as np

def load_mt5_csv(path):
    df=pd.read_csv(path,sep=';'); df['time']=pd.to_datetime(df['time'],format='%Y.%m.%d %H:%M')
    df=df.set_index('time').sort_index(); df=df[~df.index.duplicated()]
    df['volume']=df.real_volume.where(df.real_volume>0,df.tick_volume)
    return df[['open','high','low','close','volume']].astype(float)

def prep(df, day_start='09:00'):
    df=df.copy(); df['d']=df.index.normalize(); df['t']=df.index.hour*60+df.index.minute
    tp=(df.high+df.low+df.close)/3; v=df.volume.replace(0,np.nan).fillna(1)
    g=df.d
    df['vwap']=(tp*v).groupby(g).cumsum()/v.groupby(g).cumsum()
    df['vsd']=np.sqrt(((tp**2*v).groupby(g).cumsum()/v.groupby(g).cumsum()-df.vwap**2).clip(lower=0))
    tr=pd.concat([df.high-df.low,(df.high-df.close.shift()).abs(),(df.low-df.close.shift()).abs()],axis=1).max(axis=1)
    df['atr']=tr.rolling(14).mean()
    dd=df.groupby('d').agg(h=('high','max'),l=('low','min'))
    df['atr_d']=df.d.map((dd.h-dd.l).rolling(14).mean().shift(1))
    df['dopen']=df.groupby('d').open.transform('first')
    return df

def simulate(df, signals, cost_pts, flat_min=17*60+30, max_per_day=99):
    """signals: lista de dict(i, dir, stop, target(None), tmax(min do dia p/ sair, opcional), trail_vwap(bool))"""
    out=[]; busy=-1; per_day={}
    O=df.open.values; H=df.high.values; L=df.low.values; C=df.close.values; T=df.t.values; D=df.d.values; VW=df.vwap.values
    n=len(df)
    for s in sorted(signals,key=lambda x:x['i']):
        i=s['i']
        if i+1>=n or i<=busy or D[i+1]!=D[i]: continue
        if per_day.get(D[i],0)>=max_per_day: continue
        dirn=s['dir']; e=O[i+1]; stop=s['stop']; tgt=s.get('target'); tmax=min(s.get('tmax',flat_min),flat_min)
        if (e-stop)*dirn<=0: continue
        R=abs(e-stop); j=i+1; px=None; why='hora'
        while j<n and D[j]==D[i]:
            adv=L[j] if dirn==1 else H[j]; fav=H[j] if dirn==1 else L[j]
            if (adv-stop)*dirn<=0: px=stop if (O[j]-stop)*dirn>0 else O[j]; why='stop'; break
            if tgt is not None and (fav-tgt)*dirn>=0: px=tgt if (O[j]-tgt)*dirn<0 else O[j]; why='alvo'; break
            if T[j]>=tmax or j+1>=n or D[j+1]!=D[i]: px=C[j]; why='hora'; break
            if s.get('trail_vwap') and (C[j]-VW[j])*dirn<0: px=C[j]; why='vwap'; break
            if s.get('be_at') and (C[j]-e)*dirn>=s['be_at']*R and (e-stop)*dirn>0: stop=e
            j+=1
        if px is None: px=C[j-1]
        out.append(dict(dt=df.index[i],d=D[i],dir=dirn,pts=(px-e)*dirn-cost_pts,R=((px-e)*dirn-cost_pts)/R,why=why))
        busy=j; per_day[D[i]]=per_day.get(D[i],0)+1
    return pd.DataFrame(out)

def report(tr, lab, point_value=0.2):
    if tr.empty: return dict(metodo=lab,n=0)
    p=tr.pts; f=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2)
    yrs=tr.groupby(pd.to_datetime(tr.d).dt.year).pts
    eq=p.cumsum(); weeks=max(1,(pd.to_datetime(tr.d).max()-pd.to_datetime(tr.d).min()).days/7)
    r=dict(metodo=lab,n=len(p),por_semana=round(len(p)/weeks,1),acerto=round((p>0).mean(),2),PF=f(p),
           total_RS=round(p.sum()*point_value),dd_RS=round((eq-eq.cummax()).min()*point_value))
    for y,s in yrs: r[f'PF_{y}']=f(s); r[f'RS_{y}']=round(s.sum()*point_value)
    return r
