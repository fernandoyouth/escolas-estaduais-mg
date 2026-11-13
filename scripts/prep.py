import json, unicodedata, re, collections, random
import geopandas as gpd
from shapely.geometry import Point, mapping
random.seed(1)
SRE={'00001':'Metropolitana (BH/Contagem/Betim)','00002':'Metropolitana (BH/Sabará/Nova Lima)','00041':'Metropolitana (BH/Ribeirão das Neves/Santa Luzia)',
'00003':'Barbacena','00004':'Caratinga','00005':'Diamantina','00006':'Divinópolis','00007':'Governador Valadares','00008':'Itajubá','00009':'Januária',
'00010':'Juiz de Fora','00011':'Manhuaçu','00012':'Montes Claros','00013':'Muriaé','00014':'Nova Era','00015':'Ouro Preto','00016':'Paracatu','00017':'Passos',
'00018':'Patos de Minas','00019':'Poços de Caldas','00020':'Ponte Nova','00021':'São João del-Rei','00022':'São Sebastião do Paraíso','00023':'Sete Lagoas',
'00024':'Teófilo Otoni','00025':'Uberaba','00026':'Uberlândia','00027':'Varginha','00028':'Ubá','00029':'Almenara','00030':'Coronel Fabriciano',
'00031':'Conselheiro Lafaiete','00032':'Ituiutaba','00033':'Patrocínio','00034':'Monte Carmelo','00035':'Campo Belo','00036':'Leopoldina','00037':'Pouso Alegre',
'00038':'Curvelo','00039':'Guanhães','00040':'Carangola','00042':'Caxambu','00043':'Araçuaí','00044':'Janaúba','00045':'Pará de Minas','00046':'Pirapora','00047':'Unaí'}
def norm(s): return re.sub(r'[^a-z]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
mun=gpd.read_file('dados/brutos/31municipality_2022_simplified.gpkg').to_crs(4326)
mun['k']=mun.name_muni.map(norm)
mk=dict(zip(mun.k,mun.index)); mk[norm('Barão do Monte Alto')]=mk.get(norm('Barão de Monte Alto'), mk.get(norm('Barão do Monte Alto')))
d=json.load(open('dados/brutos/escolas_mg.json'))
nomatch=set(); fixed=0; approx=0
cnt=collections.defaultdict(collections.Counter)
for x in d:
    i=mk.get(norm(x['NO_MUNICIPIO']))
    if i is None: nomatch.add(x['NO_MUNICIPIO']); x['aprox']=0; continue
    cnt[i][x['CO_ORGAO_REGIONAL']]+=1
    geom=mun.geometry[i]
    ok = x['lat'] is not None and geom.buffer(0.03).contains(Point(x['lon'],x['lat']))
    if not ok:
        if x['lat'] is None: approx+=1
        else: fixed+=1
        p=geom.representative_point()
        x['lon']=round(p.x+random.uniform(-.01,.01),5); x['lat']=round(p.y+random.uniform(-.01,.01),5); x['aprox']=1
    else: x['aprox']=0
print('nomatch',nomatch,'sem coord->sede',approx,'fora do muni->sede',fixed)
mun['sre']=[cnt[i].most_common(1)[0][0] if cnt[i] else None for i in mun.index]
# fill missing via neighbors
for _ in range(5):
    for i in mun.index[mun.sre.isna()]:
        nb=mun[(mun.geometry.distance(mun.geometry[i])<0.01) & mun.sre.notna() & (mun.index!=i)]
        if len(nb): mun.loc[i,'sre']=nb.sre.mode()[0]
print('munis sem sre',mun.sre.isna().sum(), 'munis sem escola estadual', sum(1 for i in mun.index if not cnt[i]))
m2=mun.copy(); m2['geometry']=m2.geometry.simplify(0.006,preserve_topology=True)
from shapely.geometry import Polygon, MultiPolygon
def clean(g,minarea=0.002):
    g=g.buffer(0.002).buffer(-0.002)
    ps=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
    ps=[Polygon(p.exterior,[h for h in p.interiors if Polygon(h).area>minarea]) for p in ps if p.area>minarea]
    return (MultiPolygon(ps) if len(ps)>1 else ps[0]).simplify(0.008,preserve_topology=True)
sreg=mun.dissolve('sre').reset_index(); sreg['geometry']=sreg.geometry.map(clean)
state=mun.dissolve().geometry.map(clean)
def rnd(geo):
    def r(c):
        if isinstance(c,(list,tuple)) and c and isinstance(c[0],(int,float)): return [round(c[0],3),round(c[1],3)]
        return [r(y) for y in c]
    g=mapping(geo); return {'type':g['type'],'coordinates':r(g['coordinates'])}
geo={'mun':{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'n':r.name_muni,'s':r.sre},'geometry':rnd(r.geometry)} for r in m2.itertuples()]},
     'sre':{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'s':r.sre},'geometry':rnd(r.geometry)} for r in sreg.itertuples()]},
     'uf':rnd(state.iloc[0])}
K=['NO_ENTIDADE','CO_ENTIDADE','NO_MUNICIPIO','CO_ORGAO_REGIONAL','TP_LOCALIZACAO','lat','lon','aprox']
Q=[k for k in d[0] if k.startswith(('QT_','IN_'))]
addr=lambda x: ', '.join(p for p in [x['DS_ENDERECO']+(' '+x['NU_ENDERECO'] if x['NU_ENDERECO'] else ''),x['NO_BAIRRO']] if p)
tel=lambda x: f"({x['NU_DDD']}) {x['NU_TELEFONE']}" if x['NU_TELEFONE'] else ''
rows=[[x[k] for k in K]+[addr(x),tel(x)]+[x[k] for k in Q] for x in d]
out={'cols':K+['END','TEL']+Q,'rows':rows,'sre':SRE,'geo':geo}
json.dump(out,open('data.json','w'),ensure_ascii=False,separators=(',',':'))
import os; print('size',os.path.getsize('data.json'))
