"""Recorta as escolas estaduais de MG (CO_UF=31, TP_DEPENDENCIA=2) de um microdado do Censo Escolar.
Uso: python3 scripts/filtrar_censo.py <microdados_ed_basica_ANO.csv> <saida.csv>"""
import csv, sys
src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding='latin-1') as f, open(dst, 'w', encoding='utf-8', newline='') as out:
    r = csv.reader(f, delimiter=';'); h = next(r)
    iu, idp = h.index('CO_UF'), h.index('TP_DEPENDENCIA')
    w = csv.writer(out, delimiter=';'); w.writerow(h); n = 0
    for row in r:
        if row[iu] == '31' and row[idp] == '2':
            w.writerow(row); n += 1
print(dst, n)
