import pandas as pd, numpy as np
R=pd.read_csv('dados/brutos/mg_estaduais_2025.csv',sep=';',dtype=str)
R24=pd.read_csv('dados/brutos/mg_estaduais_2024.csv',sep=';',dtype=str,usecols=['CO_MUNICIPIO','NO_MESORREGIAO']).drop_duplicates('CO_MUNICIPIO')
R=R.merge(R24,on='CO_MUNICIPIO',how='left')  # Censo 2025 não traz mesorregião; vem do município
R=R[R.TP_SITUACAO_FUNCIONAMENTO=='1'].copy(); R['id']=R.CO_ENTIDADE.astype(int); R=R.set_index('id')
M=pd.read_pickle('M4.pkl'); M=M.join(R[['NO_MESORREGIAO','NO_REGIAO_GEOG_INTERM']],how='left')
f=lambda c: pd.to_numeric(R.loc[M.index,c],errors='coerce').fillna(0).values
comp=M[['QT_DESKTOP_ALUNO','QT_COMP_PORTATIL_ALUNO','QT_TABLET_ALUNO']].fillna(0).sum(axis=1)
IT={'Água potável':f('IN_AGUA_POTAVEL')==1,'Esgoto da rede pública':f('IN_ESGOTO_REDE_PUBLICA')==1,'Coleta de lixo':f('IN_LIXO_SERVICO_COLETA')==1,
'Banheiro acessível (PNE)':f('IN_BANHEIRO_PNE')==1,'Refeitório':f('IN_REFEITORIO')==1,'Biblioteca ou sala de leitura':(f('IN_BIBLIOTECA')==1)|(f('IN_BIBLIOTECA_SALA_LEITURA')==1)|(f('IN_SALA_LEITURA')==1),
'Laboratório de ciências':f('IN_LABORATORIO_CIENCIAS')==1,'Laboratório de informática':f('IN_LABORATORIO_INFORMATICA')==1,'Quadra coberta':f('IN_QUADRA_ESPORTES_COBERTA')==1,
'Auditório':f('IN_AUDITORIO')==1,'Sala de professores':f('IN_SALA_PROFESSOR')==1,'Sala de AEE':f('IN_SALA_ATENDIMENTO_ESPECIAL')==1,
'Rampas de acessibilidade':f('IN_ACESSIBILIDADE_RAMPAS')==1,'Internet para alunos':f('IN_INTERNET_ALUNOS')==1,'Banda larga':f('IN_BANDA_LARGA')==1,
'Até 15 alunos por computador':(M.QT_MAT_BAS/comp.replace(0,np.nan)).fillna(999).values<=15,'Projetor multimídia':f('IN_EQUIP_MULTIMIDIA')==1,'Salas climatizadas (alguma)':M.QT_SALAS_UTILIZA_CLIMATIZADAS.fillna(0).values>0}
for k,v in IT.items(): M[k]=np.asarray(v).astype(int)
meso=M.NO_MESORREGIAO
print(meso.value_counts())
T=M.groupby('NO_MESORREGIAO')[list(IT)+['infC']].mean()
T['n']=M.groupby('NO_MESORREGIAO').size(); T['ideb_em']=M.groupby('NO_MESORREGIAO').ideb_em.mean(); T['ideb_af']=M.groupby('NO_MESORREGIAO').ideb_af.mean(); T['inse']=M.groupby('NO_MESORREGIAO').inse.mean(); T['rural']=M.groupby('NO_MESORREGIAO').rural.mean()
pd.set_option('display.width',250)
print((T[['n','inse','rural','ideb_em','ideb_af','infC']]).sort_values('infC').round(2))
P=(T[list(IT)]*100).round(0).T; print(P.to_string())
rng=(T[list(IT)].max()-T[list(IT)].min()).sort_values(ascending=False)*100; print('amplitude entre mesos (p.p.)\n',rng.round(0))
M.to_pickle('M5.pkl'); import json; json.dump(list(IT),open('items.json','w'),ensure_ascii=False)
