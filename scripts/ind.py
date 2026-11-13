import pandas as pd, json, numpy as np
P='dados/brutos/ind/'
def num(s): return pd.to_numeric(s.astype(str).str.replace(',','.'),errors='coerce')
def ideb(f,tag):
    d=pd.read_excel(P+f,header=9,engine='calamine',dtype=str)
    d=d[(d.SG_UF=='MG')&(d.REDE=='Estadual')]
    o=pd.DataFrame({'id':d.ID_ESCOLA.astype(int)})
    o[f'ideb_{tag}']=num(d.VL_OBSERVADO_2025).values
    o[f'ideb23_{tag}']=num(d.VL_OBSERVADO_2023).values
    o[f'mat_{tag}']=num(d.VL_NOTA_MATEMATICA_2025).values
    o[f'por_{tag}']=num(d.VL_NOTA_PORTUGUES_2025).values
    return o.set_index('id')
I=[ideb('divulgacao_anos_iniciais_escolas_2025.xlsx','ai'),ideb('divulgacao_anos_finais_escolas_2025.xlsx','af'),ideb('divulgacao_ensino_medio_escolas_2025.xlsx','em')]
r=pd.read_excel(P+'tx_rend_escolas_2024.xlsx',header=8,engine='calamine',dtype=str); r=r[(r.SG_UF=='MG')&(r.NO_DEPENDENCIA=='Estadual')]
R=pd.DataFrame({'id':r.CO_ENTIDADE.astype(int),'aband_ai':num(r['3_CAT_FUN_AI']).values,'aband_af':num(r['3_CAT_FUN_AF']).values,'aband_em':num(r['3_CAT_MED']).values,
  'reprov_af':num(r['2_CAT_FUN_AF']).values,'reprov_em':num(r['2_CAT_MED']).values}).set_index('id')
t=pd.read_excel(P+'TDI_ESCOLAS_2024.xlsx',header=8,engine='calamine',dtype=str); t=t[(t.SG_UF=='MG')&(t.NO_DEPENDENCIA=='Estadual')]
T=pd.DataFrame({'id':t.CO_ENTIDADE.astype(int),'tdi_ai':num(t.FUN_AI_CAT_0).values,'tdi_af':num(t.FUN_AF_CAT_0).values,'tdi_em':num(t.MED_CAT_0).values}).set_index('id')
n=pd.read_excel(P+'INSE_2023_escolas.xlsx',engine='calamine',dtype=str); n=n[(n.SG_UF=='MG')&(n.TP_TIPO_REDE=='2')]
N=pd.DataFrame({'id':n.ID_ESCOLA.astype(int),'inse':num(n.MEDIA_INSE).values,'inse_nivel':n.INSE_CLASSIFICACAO.str.replace('Nível ','').values}).set_index('id')
A=pd.concat(I+[R,T,N],axis=1)
print(A.shape); print(A.notna().sum())
A.reset_index().to_csv('indicadores_mg.csv',index=False)
