import pandas as pd, numpy as np, json
M=pd.read_pickle('M5.pkl'); IT=json.load(open('items.json'))
IT2=[i for i in IT if i not in ('Água potável','Banda larga','Projetor multimídia')]  # quase sem variação
def ols(y,X):
    s=pd.concat([y,X],axis=1).dropna(); yy=s.iloc[:,0].values; XX=np.c_[np.ones(len(s)),s.iloc[:,1:].values.astype(float)]
    b,*_=np.linalg.lstsq(XX,yy,rcond=None); r=yy-XX@b; n,k=XX.shape
    # cluster-robust by meso
    g=M.loc[s.index,'NO_MESORREGIAO'].values; XtXi=np.linalg.pinv(XX.T@XX); meat=np.zeros((k,k))
    for gg in np.unique(g):
        sc=(XX[g==gg]*r[g==gg,None]).sum(0); meat+=np.outer(sc,sc)
    V=XtXi@meat@XtXi; se=np.sqrt(np.diag(V)); hc=np.sqrt(np.diag(XtXi*(r@r)/(n-k)))
    return pd.DataFrame({'b':b,'se_cl':se,'se':hc},index=['const']+list(s.columns[1:])),n,1-(r@r)/((yy-yy.mean())@(yy-yy.mean()))
D=pd.get_dummies(M.NO_MESORREGIAO,drop_first=True,dtype=float)
D=D.drop(columns=[c for c in D if 'Metropolitana' in c],errors='ignore'); D=pd.get_dummies(M.NO_MESORREGIAO,dtype=float).drop(columns=['Metropolitana de Belo Horizonte'])
res={}
for et,ctl in {'em':['inse','log_mat','rural','noturno','integral_em'],'af':['inse','log_mat','rural','noturno','integral_fund']}.items():
    y=M['ideb_'+et]
    t,n,r2=ols(y,pd.concat([M[ctl+IT2],D],axis=1))
    t['t_cl']=t.b/t.se_cl
    print(f'\n=== {et} n={n} R2={r2:.3f} (controles + itens + mesorregião)')
    print(t.loc[IT2].sort_values('b').round(3).to_string())
    res[et]=t.loc[IT2,['b','se_cl']].round(4).to_dict('index')
    # regional decomposition
    s=pd.concat([y,M[ctl+IT2],D],axis=1).dropna()
    m0,_,_=ols(s[y.name],D.loc[s.index])
    m1,_,_=ols(s[y.name],pd.concat([s[['inse']],D.loc[s.index]],axis=1))
    m2,_,_=ols(s[y.name],pd.concat([s[ctl],D.loc[s.index]],axis=1))
    m3,_,_=ols(s[y.name],pd.concat([s[ctl+IT2],D.loc[s.index]],axis=1))
    G=pd.DataFrame({'bruto':m0.b[D.columns],'+INSE':m1.b[D.columns],'+contexto':m2.b[D.columns],'+infra':m3.b[D.columns]}).round(2)
    print('diferença vs Metropolitana BH'); print(G.sort_values('bruto').to_string())
    res[et+'_gap']=G.to_dict('index')
json.dump(res,open('reg_res.json','w'),ensure_ascii=False)
