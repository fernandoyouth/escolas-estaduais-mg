import pandas as pd, numpy as np, glob, re
P='dados/brutos/hist/ind/'
num=lambda s: pd.to_numeric(s.astype(str).str.replace(',','.'),errors='coerce')
rows=[]
for f in sorted(glob.glob(P+'IRD_ESCOLAS_*.xlsx')):
    y=int(re.search(r'20\d\d',f.split('/')[-1]).group()); d=pd.read_excel(f,header=None,skiprows=11,engine='calamine',dtype=str)
    d=d[(d[2]=='MG')&(d[8]=='Estadual')]; rows.append(pd.DataFrame({'id':d[5].astype(int).values,'ano':y,'ird':num(d[9]).values}))
IRD=pd.concat(rows)
rows=[]
for f in sorted(glob.glob(P+'AFD_ESCOLAS_*.xlsx')):
    y=int(re.search(r'20\d\d',f.split('/')[-1]).group()); d=pd.read_excel(f,header=None,skiprows=11,engine='calamine',dtype=str)
    d=d[(d[2]=='MG')&(d[8]=='Estadual')]; rows.append(pd.DataFrame({'id':d[5].astype(int).values,'ano':y,'afd_ai':num(d[19]).values,'afd_af':num(d[24]).values,'afd_em':num(d[29]).values}))
AFD=pd.concat(rows)
DOC=AFD.merge(IRD,on=['id','ano'],how='outer'); DOC.to_pickle('docentes.pkl')
print(DOC.groupby('ano')[['afd_af','afd_em','ird']].agg(['count','mean']).round(2))
