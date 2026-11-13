import pandas as pd, numpy as np
P='dados/brutos/ind/'
num=lambda s: pd.to_numeric(s.astype(str).str.replace(',','.'),errors='coerce')
out=[]
for f,et in [('divulgacao_anos_iniciais_escolas_2025.xlsx','ai'),('divulgacao_anos_finais_escolas_2025.xlsx','af'),('divulgacao_ensino_medio_escolas_2025.xlsx','em')]:
    d=pd.read_excel(P+f,header=9,engine='calamine',dtype=str); d=d[(d.SG_UF=='MG')&(d.REDE=='Estadual')]
    for y in [2017,2019,2021,2023,2025]:
        o=pd.DataFrame({'id':d.ID_ESCOLA.astype(int).values,'etapa':et,'ano':y,
          'ideb':num(d[f'VL_OBSERVADO_{y}']).values,'nota':num(d[f'VL_NOTA_MEDIA_{y}']).values,'rend':num(d[f'VL_INDICADOR_REND_{y}']).values})
        out.append(o)
H=pd.concat(out); H.to_pickle('ideb_hist.pkl')
print(H.groupby(['etapa','ano']).ideb.agg(['count','mean']).round(2))
