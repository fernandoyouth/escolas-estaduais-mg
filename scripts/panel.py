import pandas as pd, numpy as np, json
U='dados/brutos/'
files={2019:U+'hist/mg_estaduais_2019.csv',2021:U+'hist/mg_estaduais_2021.csv',2023:U+'hist/mg_estaduais_2023.csv',2025:U+'mg_estaduais_2025.csv'}
C=[]
for y,f in files.items():
    d=pd.read_csv(f,sep=';',dtype=str); d=d[d.TP_SITUACAO_FUNCIONAMENTO=='1']
    n=lambda c: pd.to_numeric(d[c],errors='coerce').fillna(0)
    C.append(pd.DataFrame({'id':d.CO_ENTIDADE.astype(int),'ano_c':y,'mat':n('QT_MAT_BAS'),'mat_em':n('QT_MAT_MED'),'mat_em_int':n('QT_MAT_MED_INT'),
      'mat_fund':n('QT_MAT_FUND_AI')+n('QT_MAT_FUND_AF'),'mat_fund_int':n('QT_MAT_FUND_INT'),'mat_not':n('QT_MAT_BAS_N'),'rural':(d.TP_LOCALIZACAO=='2').astype(int),'meso':d.get('NO_MESORREGIAO')}))
C=pd.concat(C); C['ano']=C.ano_c.replace({2024:2025})
S=pd.read_pickle('infra_scale.pkl'); S['ano']=S.ano.replace({2024:2025})
H=pd.read_pickle('ideb_hist.pkl'); H=H[H.ano>=2019]
D=pd.read_pickle('docentes.pkl'); D=D[D.ano.isin([2019,2021,2023,2025])]
P=H.merge(S,on=['id','ano']).merge(C.drop(columns='ano_c'),on=['id','ano']).merge(D,on=['id','ano'],how='left')
P['log_mat']=np.log1p(P.mat); P['noturno']=(P.mat_not>0).astype(int)
P['integral']=np.where(P.etapa=='em',P.mat_em_int/P.mat_em.replace(0,np.nan),P.mat_fund_int/P.mat_fund.replace(0,np.nan)); P['integral']=P.integral.fillna(0).clip(0,1)
P['afd']=np.select([P.etapa=='em',P.etapa=='af'],[P.afd_em,P.afd_af],P.afd_ai)/10  # por 10 p.p.
P=P.dropna(subset=['ideb'])
P.to_pickle('panel.pkl')
def fe(df,y,xs,fe_school=True):
    df=df.dropna(subset=[y]+xs).copy()
    yrs=pd.get_dummies(df.ano,prefix='a',drop_first=True,dtype=float)
    X=pd.concat([df[xs],yrs],axis=1); Y=df[y]
    if fe_school:
        g=df.id; X=X-X.groupby(g).transform('mean'); Y=Y-Y.groupby(g).transform('mean')
        keep=df.groupby('id').id.transform('size')>1; X,Y,df=X[keep],Y[keep],df[keep]
    else:
        X=pd.concat([pd.Series(1.0,index=X.index,name='c'),X],axis=1)
    Xv=X.values.astype(float); b,*_=np.linalg.lstsq(Xv,Y.values,rcond=None); r=Y.values-Xv@b
    XtXi=np.linalg.pinv(Xv.T@Xv); meat=np.zeros((Xv.shape[1],)*2)
    for gid,idx in df.groupby('id').indices.items():
        s=(Xv[idx]*r[idx,None]).sum(0); meat+=np.outer(s,s)
    se=np.sqrt(np.diag(XtXi@meat@XtXi))
    return pd.DataFrame({'b':b,'se':se,'t':b/se},index=X.columns).loc[xs],len(df),df.id.nunique()
out={}
for et in ['em','af','ai']:
    d=P[P.etapa==et]
    for spec,xs in {'geral':['esc_geral','log_mat','noturno','integral'],'dims':['esc_estab','esc_ensino','esc_equid','log_mat','noturno','integral'],
                    'geral+doc':['esc_geral','log_mat','noturno','integral','afd','ird']}.items():
        for fs in [False,True]:
            t,n,ns=fe(d,'ideb',xs+([] if fs else ['rural']),fs)
            key=f'{et}|{spec}|{"FE" if fs else "pooled"}'; out[key]=t.round(4).to_dict('index')
            print(f'\n{key}  n={n} escolas={ns}'); print(t.round(3).to_string())
    # excluding 2021
    t,n,ns=fe(d[d.ano!=2021],'ideb',['esc_geral','log_mat','noturno','integral','afd','ird'],True); print(f'\n{et}|sem2021|FE n={n}'); print(t.round(3).to_string())
    out[f'{et}|sem2021|FE']=t.round(4).to_dict('index')
json.dump(out,open('panel_res.json','w'))
print('\nSD esc_geral', P.esc_geral.std().round(2), 'within-school SD', (P.esc_geral-P.groupby("id").esc_geral.transform("mean")).std().round(2))
