import pandas as pd, numpy as np, json
M=pd.read_pickle('M5.pkl')
D=pd.read_pickle('docentes.pkl'); D25=D[D.ano==2025].set_index('id'); D24=D[D.ano==2024].set_index('id')
S=pd.read_pickle('infra_scale.pkl'); S24=S[S.ano==2025].set_index('id')  # Censo 2025
H=pd.read_pickle('ideb_hist.pkl')
M=M.join(D25[['ird','afd_af','afd_em']]).join(S24[['esc_geral','esc_estab','esc_ensino','esc_equid']])
M['rmbh']=(M.NO_MESORREGIAO=='Metropolitana de Belo Horizonte').astype(int)
M['bh']=(M.NO_MUNICIPIO=='Belo Horizonte').astype(int)
# volatility: sd of ideb_em across 2017-2025
v=H[H.etapa=='em'].pivot_table(index='id',columns='ano',values='ideb'); M['vol_em']=v.std(axis=1); M['delta_em']=v[2025]-v[2019]
cols=['inse','QT_MAT_BAS','noturno','integral_em','rural','ird','afd_em','esc_geral','vol_em','delta_em','ideb_em']
print(M.groupby('rmbh')[cols].mean().round(2).T)
print('BH capital vs resto RMBH:'); print(M[M.rmbh==1].groupby('bh')[cols].mean().round(2).T)
def ols(df,y,xs):
    s=df[[y]+xs].dropna(); X=np.c_[np.ones(len(s)),s[xs].values.astype(float)]; b,*_=np.linalg.lstsq(X,s[y].values,rcond=None)
    r=s[y].values-X@b; se=np.sqrt(np.diag((r@r)/(len(s)-X.shape[1])*np.linalg.inv(X.T@X))); return pd.DataFrame({'b':b,'se':se},index=['c']+xs),len(s)
specs=[['rmbh'],['rmbh','inse'],['rmbh','inse','log_mat','rural','noturno','integral_em'],['rmbh','inse','log_mat','rural','noturno','integral_em','esc_geral'],['rmbh','inse','log_mat','rural','noturno','integral_em','esc_geral','ird','afd_em']]
for et in ['em','af']:
    y='ideb_'+et; sp=[[c.replace('integral_em','integral_fund') if et=='af' else c for c in s] for s in specs]
    sp=[[c.replace('afd_em','afd_af') if et=='af' else c for c in s] for s in sp]
    print('\n==',et)
    for s in sp:
        t,n=ols(M,y,s); print(f"{'+'.join(s[1:]) or 'bruto':70s} RMBH {t.loc['rmbh','b']:+.3f} (se {t.loc['rmbh','se']:.3f}) n={n}" + (f"  ird {t.loc['ird','b']:+.3f}" if 'ird' in s else ''))
M.to_pickle('M6.pkl')
