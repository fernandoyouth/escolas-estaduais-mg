"""Junta as tabelas do Censo Escolar 2025 num só arquivo, só com as escolas estaduais de MG.

A partir de 2025 o INEP publica o Censo em tabelas separadas (Escola, Matrícula, Turma, Docente...),
todas com uma linha por escola e ligadas por CO_ENTIDADE. Este script lê as quatro tabelas de dentro do
zip, mantém CO_UF = 31 e TP_DEPENDENCIA = 2 e grava uma linha por escola com todas as colunas.

Uso: python3 scripts/juntar_censo_2025.py <microdados_censo_escolar_2025_.zip> <saida.csv>
"""
import sys, zipfile
import pandas as pd

zf = zipfile.ZipFile(sys.argv[1])
nomes = {n.split('/')[-1].split('_2025')[0]: n for n in zf.namelist() if n.lower().endswith('.csv') and '/dados/' in n}
base = None
for tab in ['Tabela_Escola', 'Tabela_Matricula', 'Tabela_Turma', 'Tabela_Docente']:
    partes = []
    with zf.open(nomes[tab]) as f:
        for ch in pd.read_csv(f, sep=';', encoding='latin-1', dtype=str, chunksize=50000):
            partes.append(ch[(ch.CO_UF == '31') & (ch.TP_DEPENDENCIA == '2')])
    t = pd.concat(partes)
    print(tab, len(t), 'escolas,', t.shape[1], 'colunas')
    if base is None:
        base = t
    else:
        novas = [c for c in t.columns if c not in base.columns]
        base = base.merge(t[['CO_ENTIDADE'] + novas], on='CO_ENTIDADE', how='left')
base.to_csv(sys.argv[2], sep=';', index=False, encoding='utf-8')
print('gravado', sys.argv[2], base.shape)
