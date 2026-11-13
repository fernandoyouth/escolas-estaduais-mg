import pandas as pd, numpy as np, json
M=pd.read_pickle('M.pkl')
for y in ['ideb_em','ideb_af','ideb_ai']:
    s=M[[y,'inse']].dropna(); b=np.polyfit(s.inse,s[y],1); M['res_'+y[5:]]=M[y]-np.polyval(b,M.inse); print(y,b.round(3),'sd res',M['res_'+y[5:]].std().round(2))
M['res']=M.res_em.fillna(M.res_af).fillna(M.res_ai)
M['ideb_ref']=M.ideb_em.fillna(M.ideb_af).fillna(M.ideb_ai)
M['ideb_ref_et']=np.where(M.ideb_em.notna(),'EM',np.where(M.ideb_af.notna(),'AF',np.where(M.ideb_ai.notna(),'AI','')))
print(M.res.describe().round(2)); print((M.res<-0.4).sum(),(M.res>0.4).sum())
pri=(M.inse_q=='Q1 mais pobre')&(M.infra<=3); print('prioridade',pri.sum(), 'com res<0',(pri&(M.res<0)).sum())
# stats for panel
tab={}
for col in ['ideb_em','ideb_af','aband_em']:
    p=M.pivot_table(index='inse_q',columns='infra_g',values=col,aggfunc='mean',observed=False).round(2)
    c=M.pivot_table(index='inse_q',columns='infra_g',values=col,aggfunc='count',observed=False)
    tab[col]={'rows':list(map(str,p.index)),'cols':list(map(str,p.columns)),'v':p.values.tolist(),'n':c.values.tolist()}
print('inse quartis cortes',M.inse.quantile([.25,.5,.75]).round(2).tolist())
cols=['ideb_ai','ideb_af','ideb_em','ideb23_ai','ideb23_af','ideb23_em','mat_em','por_em','mat_af','por_af','aband_ai','aband_af','aband_em','reprov_af','reprov_em','tdi_ai','tdi_af','tdi_em','inse','inse_nivel','infra','res']
d=json.load(open('data.json'))
ids=[int(r[d['cols'].index('CO_ENTIDADE')]) for r in d['rows']]
X=M.set_index('id')[cols]
def cl(v):
    if isinstance(v,float) and np.isnan(v): return None
    if isinstance(v,(float,np.floating)): return round(float(v),2)
    if isinstance(v,(np.integer,)): return int(v)
    return v if v==v else None
for i,r in zip(ids,d['rows']): r.extend(cl(X.at[i,c]) for c in cols)
d['cols']+=cols; d['cross']=tab
d['inse_cuts']=M.inse.quantile([.25,.5,.75]).round(2).tolist()
json.dump(d,open('data.json','w'),ensure_ascii=False,separators=(',',':'))
M.to_pickle('M2.pkl')
print('ok', len(d['cols']))
