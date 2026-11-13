import pandas as pd, numpy as np, json
M=pd.read_pickle('M2.pkl')
M['log_mat']=np.log1p(M.QT_MAT_BAS.fillna(0))
M['rural']=(M.TP_LOCALIZACAO==2).astype(int)
M['noturno']=(M.QT_MAT_BAS_N.fillna(0)>0).astype(int)
M['integral_em']=(M.QT_MAT_MED_INT.fillna(0)/M.QT_MAT_MED.replace(0,np.nan)).fillna(0)
M['integral_fund']=(M.QT_MAT_FUND_INT.fillna(0)/(M.QT_MAT_FUND_AI.fillna(0)+M.QT_MAT_FUND_AF.fillna(0)).replace(0,np.nan)).fillna(0)
X={'em':['inse','log_mat','rural','noturno','integral_em'],'af':['inse','log_mat','rural','noturno','integral_fund'],'ai':['inse','log_mat','rural','integral_fund']}
out={}
for et,xs in X.items():
    y='ideb_'+et; s=M[[y]+xs].dropna()
    A=np.c_[np.ones(len(s)),s[xs].values]; b,*_=np.linalg.lstsq(A,s[y].values,rcond=None)
    pred=A@b; res=s[y].values-pred; sd=res.std(ddof=len(xs)+1)
    r2=1-((res**2).sum()/((s[y]-s[y].mean())**2).sum())
    # simple-model r2 for comparison
    A0=np.c_[np.ones(len(s)),s.inse]; b0,*_=np.linalg.lstsq(A0,s[y],rcond=None); r0=1-(((s[y]-A0@b0)**2).sum()/((s[y]-s[y].mean())**2).sum())
    se=np.sqrt(np.diag(sd**2*np.linalg.inv(A.T@A)))
    print(et,'n',len(s),'R2 só INSE',round(r0,3),'R2 completo',round(r2,3),'sd res',round(sd,3))
    for n_,bb,ss in zip(['const']+xs,b,se): print(f'   {n_:14s} {bb:7.3f}  (t={bb/ss:5.1f})')
    M.loc[s.index,'z_'+et]=np.round(res/sd,2)
    out[et]={'n':len(s),'r2':round(r2,3),'r2_inse':round(r0,3),'coef':dict(zip(['const']+xs,np.round(b,3).tolist()))}
M['z']=M.z_em.fillna(M.z_af).fillna(M.z_ai)
M['z_et']=np.where(M.z_em.notna(),'médio',np.where(M.z_af.notna(),'anos finais',np.where(M.z_ai.notna(),'anos iniciais',None)))
print('abaixo (z<=-1)',(M.z<=-1).sum(),'acima (z>=1)',(M.z>=1).sum(),'dentro',((M.z>-1)&(M.z<1)).sum(),'sem',M.z.isna().sum())
print(M.groupby('z_et').z.agg(['count',lambda s:(s<=-1).sum(),lambda s:(s>=1).sum()]))
# compare with old classification
old=M.res<=-.4; new=M.z<=-1; print('overlap old/new abaixo',(old&new).sum(),'old',old.sum(),'new',new.sum())
pri=(M.inse<M.inse.quantile(.25))&(M.infra<=3); print('prioridade',pri.sum(),'e abaixo',(pri&new).sum())
M.to_pickle('M3.pkl'); json.dump(out,open('model2.json','w'),ensure_ascii=False)
