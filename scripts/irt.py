import pandas as pd, numpy as np, json, warnings; warnings.filterwarnings('ignore')
from girth import twopl_mml, ability_eap
A=pd.read_pickle('infra_items.pkl'); A=A[A.ano>=2019].copy()
dims=json.load(open('dims.json'))
drop=['IN_MATERIAL_PED_MULTIMIDIA','IN_MATERIAL_PED_CIENTIFICO','IN_MATERIAL_PED_DESPORTIVA','IN_MATERIAL_PED_JOGOS','IN_AGUA_POTAVEL','IN_BANHEIRO']
dims={k:[c for c in v if c not in drop] for k,v in dims.items()}
allit=sum(dims.values(),[])
A[allit]=A[allit].clip(0,1).fillna(0).astype(int)
res={}
def fit(items,name):
    X=A[items].values.T
    est=twopl_mml(X); a,b=est['Discrimination'],est['Difficulty']
    th=ability_eap(X,b,a)
    res[name]=pd.DataFrame({'a':a,'b':b},index=items)
    return th
for name,items in list(dims.items())+[('geral',allit)]:
    A['th_'+name]=fit(items,name)
# 0-10 transform on pooled
for c in [c for c in A if c.startswith('th_')]:
    lo,hi=A[c].quantile(.001),A[c].quantile(.999); A['esc_'+c[3:]]=((A[c]-lo)/(hi-lo)*10).clip(0,10)
print(res['geral'].sort_values('b').round(2).to_string())
print(A.groupby('ano')[[c for c in A if c.startswith('esc_')]].mean().round(2))
print('corr com contagem simples:',np.corrcoef(A.th_geral,A[allit].sum(axis=1))[0,1].round(3))
A[['id','ano']+[c for c in A if c.startswith(('th_','esc_'))]].to_pickle('infra_scale.pkl')
json.dump({k:v.round(3).reset_index().values.tolist() for k,v in res.items()},open('irt_params.json','w'))
