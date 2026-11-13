import pandas as pd, json, numpy as np
d=json.load(open('data.json')); E=pd.DataFrame(d['rows'],columns=d['cols']); E['id']=E.CO_ENTIDADE.astype(int)
A=pd.read_csv('indicadores_mg.csv')
M=E.merge(A,on='id',how='left')
print('escolas no mapa',len(M),'com INSE',M.inse.notna().sum(),'com ideb EM',M.ideb_em.notna().sum(),'AF',M.ideb_af.notna().sum(),'AI',M.ideb_ai.notna().sum())
comp=M[['QT_DESKTOP_ALUNO','QT_COMP_PORTATIL_ALUNO','QT_TABLET_ALUNO']].fillna(0).sum(1)
ratio=M.QT_MAT_BAS/comp.replace(0,np.nan)
items={'internet_alunos':M.IN_INTERNET_ALUNOS==1,'quadra_coberta':M.IN_QUADRA_ESPORTES_COBERTA==1,'lab_ciencias':M.IN_LABORATORIO_CIENCIAS==1,
 'lab_informatica':M.IN_LABORATORIO_INFORMATICA==1,'biblioteca':(M.IN_BIBLIOTECA==1)|(M.IN_BIBLIOTECA_SALA_LEITURA==1),'acessibilidade':M.IN_ACESSIBILIDADE_INEXISTENTE==0,'ate15_alunos_por_pc':ratio<=15}
M['infra']=sum(v.astype(int) for v in items.values())
print('infra dist',M.infra.value_counts().sort_index().to_dict())
M['inse_q']=pd.qcut(M.inse,4,labels=['Q1 mais pobre','Q2','Q3','Q4 menos pobre'])
M['infra_g']=pd.cut(M.infra,[-1,3,5,7],labels=['baixa (0-3)','média (4-5)','alta (6-7)'])
for col in ['ideb_em','ideb_af','ideb_ai','aband_em','tdi_em']:
    print('\n==',col); print(M.pivot_table(index='inse_q',columns='infra_g',values=col,aggfunc='mean',observed=False).round(2))
    print(M.pivot_table(index='inse_q',columns='infra_g',values=col,aggfunc='count',observed=False))
print('\ncorr', M[['infra','inse','ideb_em','ideb_af','ideb_ai','aband_em','tdi_em']].corr().round(2))
print('\ninfra média por quartil INSE', M.groupby('inse_q',observed=False).infra.mean().round(2))
# regression ideb_em ~ inse + infra
for y in ['ideb_em','ideb_af']:
    s=M[[y,'inse','infra']].dropna(); X=np.c_[np.ones(len(s)),s.inse,s.infra]; b=np.linalg.lstsq(X,s[y],rcond=None)[0]; print(y,'coef const,inse,infra',b.round(3),len(s))
M.to_pickle('M.pkl')
