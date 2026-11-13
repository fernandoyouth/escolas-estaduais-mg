"""Etapa 1: filtra as escolas estaduais de MG no Censo Escolar 2024 e junta as coordenadas do geobr.

Entradas (em dados/brutos/):
  microdados_ed_basica_2024.csv  (de microdados_censo_escolar_2024.zip, INEP)
  schools_2023.gpkg              (geobr/Ipea: https://www.ipea.gov.br/geobr/data_gpkg/schools/2023/schools_2023.gpkg)
Saídas: dados/brutos/mg_estaduais_2024.csv e dados/brutos/escolas_mg.json
"""
import csv, sqlite3, struct, json

B = 'dados/brutos/'

# 1) recorte MG (CO_UF=31) e rede estadual (TP_DEPENDENCIA=2)
with open(B + 'microdados_ed_basica_2024.csv', encoding='latin-1') as f, \
     open(B + 'mg_estaduais_2024.csv', 'w', encoding='utf-8', newline='') as out:
    r = csv.reader(f, delimiter=';'); h = next(r)
    iu, idp = h.index('CO_UF'), h.index('TP_DEPENDENCIA')
    w = csv.writer(out, delimiter=';'); w.writerow(h)
    for row in r:
        if row[iu] == '31' and row[idp] == '2':
            w.writerow(row)

# 2) coordenadas (geometria GeoPackage: cabeçalho + WKB de ponto)
c = sqlite3.connect(B + 'schools_2023.gpkg')
coords = {}
for code, g in c.execute("select code_school, geom from schools_2023 where abbrev_state='MG'"):
    if not g:
        continue
    env = (g[3] >> 1) & 7
    wkb = g[8 + [0, 32, 48, 48, 64][env]:]
    bo = '<' if wkb[0] == 1 else '>'
    x, y = struct.unpack(bo + 'dd', wkb[5:21])
    if x == x and y == y and x != 0:
        coords[int(code)] = (round(y, 5), round(x, 5))

F = ['NO_ENTIDADE','CO_ENTIDADE','NO_MUNICIPIO','CO_ORGAO_REGIONAL','TP_LOCALIZACAO','DS_ENDERECO','NU_ENDERECO','NO_BAIRRO','CO_CEP','NU_DDD','NU_TELEFONE',
     'QT_MAT_BAS','QT_MAT_FUND_AI','QT_MAT_FUND_AF','QT_MAT_MED','QT_MAT_PROF','QT_MAT_EJA','QT_MAT_ESP','QT_MAT_FUND_INT','QT_MAT_MED_INT','QT_MAT_BAS_N','QT_DOC_BAS','QT_TUR_BAS',
     'QT_DESKTOP_ALUNO','QT_COMP_PORTATIL_ALUNO','QT_TABLET_ALUNO','QT_EQUIP_MULTIMIDIA','QT_EQUIP_LOUSA_DIGITAL','QT_EQUIP_TV','QT_EQUIP_SOM','QT_EQUIP_DVD',
     'IN_EQUIP_IMPRESSORA','IN_EQUIP_IMPRESSORA_MULT','IN_EQUIP_COPIADORA','IN_EQUIP_SCANNER','IN_EQUIP_PARABOLICA','IN_INTERNET','IN_INTERNET_ALUNOS','IN_INTERNET_APRENDIZAGEM','IN_BANDA_LARGA',
     'IN_BIBLIOTECA','IN_BIBLIOTECA_SALA_LEITURA','IN_LABORATORIO_CIENCIAS','IN_LABORATORIO_INFORMATICA','IN_QUADRA_ESPORTES','IN_QUADRA_ESPORTES_COBERTA','IN_REFEITORIO','IN_AUDITORIO',
     'IN_SALA_ATENDIMENTO_ESPECIAL','IN_ACESSIBILIDADE_INEXISTENTE','IN_AGUA_POTAVEL','IN_ESGOTO_REDE_PUBLICA',
     'QT_SALAS_UTILIZADAS','QT_SALAS_UTILIZA_CLIMATIZADAS','QT_PROF_PSICOLOGO','QT_PROF_ASSIST_SOCIAL','QT_PROF_BIBLIOTECARIO','QT_TRANSP_RESP_EST']

def num(v):
    if v in ('', None):
        return None
    try:
        n = int(float(v))
    except ValueError:
        return None
    return None if n >= 88888 else n

rows = []
for d in csv.DictReader(open(B + 'mg_estaduais_2024.csv', encoding='utf-8'), delimiter=';'):
    if d['TP_SITUACAO_FUNCIONAMENTO'] != '1':   # só escolas em atividade
        continue
    ll = coords.get(int(d['CO_ENTIDADE']))
    o = {'lat': ll[0] if ll else None, 'lon': ll[1] if ll else None}
    for k in F:
        o[k] = num(d[k]) if (k.startswith(('QT_', 'IN_')) or k == 'TP_LOCALIZACAO') else d[k].strip()
    rows.append(o)
json.dump(rows, open(B + 'escolas_mg.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('escolas em atividade:', len(rows))
