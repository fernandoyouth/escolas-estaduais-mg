import pandas as pd, numpy as np
U='dados/brutos/'
files={2017:U+'hist/mg_estaduais_2017.csv',2019:U+'hist/mg_estaduais_2019.csv',2021:U+'hist/mg_estaduais_2021.csv',2023:U+'hist/mg_estaduais_2023.csv',2024:U+'mg_estaduais_2024.csv'}
DIM={'estab':['IN_AGUA_POTAVEL','IN_ENERGIA_REDE_PUBLICA','IN_ESGOTO_REDE_PUBLICA','IN_LIXO_SERVICO_COLETA','IN_BANHEIRO','IN_BANHEIRO_FUNCIONARIOS','IN_BANHEIRO_CHUVEIRO','IN_COZINHA','IN_DESPENSA','IN_ALMOXARIFADO','IN_REFEITORIO','IN_PATIO_COBERTO','IN_AREA_VERDE','IN_SALA_DIRETORIA','IN_SALA_PROFESSOR','IN_SECRETARIA','IN_AUDITORIO'],
 'ensino':['IN_BIBLIOTECA','IN_SALA_LEITURA','IN_LABORATORIO_CIENCIAS','IN_LABORATORIO_INFORMATICA','IN_QUADRA_ESPORTES','IN_QUADRA_ESPORTES_COBERTA','IN_SALA_ATELIE_ARTES','IN_SALA_MUSICA_CORAL','IN_SALA_MULTIUSO','IN_COMPUTADOR','IN_EQUIP_COPIADORA','IN_EQUIP_IMPRESSORA','IN_EQUIP_IMPRESSORA_MULT','IN_EQUIP_SCANNER','IN_EQUIP_MULTIMIDIA','IN_EQUIP_LOUSA_DIGITAL','IN_EQUIP_TV','IN_EQUIP_SOM','IN_DESKTOP_ALUNO','IN_COMP_PORTATIL_ALUNO','IN_TABLET_ALUNO','IN_INTERNET','IN_INTERNET_ALUNOS','IN_INTERNET_APRENDIZAGEM','IN_BANDA_LARGA','IN_MATERIAL_PED_MULTIMIDIA','IN_MATERIAL_PED_CIENTIFICO','IN_MATERIAL_PED_DESPORTIVA','IN_MATERIAL_PED_JOGOS'],
 'equid':['IN_BANHEIRO_PNE','IN_SALA_ATENDIMENTO_ESPECIAL','IN_ACESSIBILIDADE_RAMPAS','IN_ACESSIBILIDADE_CORRIMAO','IN_ACESSIBILIDADE_ELEVADOR','IN_ACESSIBILIDADE_PISOS_TATEIS','IN_ACESSIBILIDADE_VAO_LIVRE','IN_ACESSIBILIDADE_SINAL_SONORO','IN_ACESSIBILIDADE_SINAL_TATIL','IN_ACESSIBILIDADE_SINAL_VISUAL']}
allit=sum(DIM.values(),[])
frames=[]
for y,f in files.items():
    d=pd.read_csv(f,sep=';',dtype=str); d=d[d.TP_SITUACAO_FUNCIONAMENTO=='1']
    o=d[['CO_ENTIDADE']].copy(); o['ano']=y
    for c in allit: o[c]=pd.to_numeric(d[c],errors='coerce') if c in d else np.nan
    frames.append(o)
A=pd.concat(frames,ignore_index=True); A['id']=A.CO_ENTIDADE.astype(int)
cov=A.groupby('ano')[allit].apply(lambda g:g.notna().mean()).T; prev=A.groupby('ano')[allit].mean().T
keep=[c for c in allit if cov.loc[c].min()>0.9 and 0.02<A[c].mean()<0.98]
print('dropped (coverage<90% some year or near-constant):',[c for c in allit if c not in keep])
print(pd.concat([cov.min(axis=1).rename('cov_min'),prev.round(2)],axis=1).loc[keep].to_string())
A.to_pickle('infra_items.pkl'); pd.Series(keep).to_json('keep.json')
import json; json.dump({k:[c for c in v if c in keep] for k,v in DIM.items()},open('dims.json','w'))
