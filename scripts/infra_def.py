"""Teste de robustez: três definições alternativas de infraestrutura (Censo 2024) e o gradiente por nível socioeconômico.

Entrada: M3.pkl (de model2.py) e dados/brutos/mg_estaduais_2024.csv. Saída: M4.pkl.
"""
import pandas as pd, numpy as np

R = pd.read_csv('dados/brutos/mg_estaduais_2024.csv', sep=';', dtype=str)
R = R[R.TP_SITUACAO_FUNCIONAMENTO == '1'].copy(); R['id'] = R.CO_ENTIDADE.astype(int)
M = pd.read_pickle('M3.pkl').set_index('id'); R = R.set_index('id').loc[M.index]
f = lambda c: pd.to_numeric(R[c], errors='coerce').fillna(0)

# A: serviços básicos completos
A = (f('IN_AGUA_POTAVEL') == 1) & (f('IN_ENERGIA_REDE_PUBLICA') == 1) & ((f('IN_ESGOTO_REDE_PUBLICA') == 1) | (f('IN_ESGOTO_FOSSA_SEPTICA') == 1)) \
    & (f('IN_BANHEIRO') == 1) & (f('IN_COZINHA') == 1)
# B: básica + pedagógica
B = A & ((f('IN_BIBLIOTECA') == 1) | (f('IN_BIBLIOTECA_SALA_LEITURA') == 1)) & (f('IN_QUADRA_ESPORTES') == 1) \
    & (f('IN_INTERNET_ALUNOS') == 1) & (f('IN_ACESSIBILIDADE_INEXISTENTE') == 0)
# C: contagem de 28 itens
items = ['IN_AGUA_POTAVEL','IN_ENERGIA_REDE_PUBLICA','IN_ESGOTO_REDE_PUBLICA','IN_LIXO_SERVICO_COLETA','IN_BANHEIRO','IN_BANHEIRO_PNE','IN_COZINHA','IN_REFEITORIO',
         'IN_BIBLIOTECA','IN_SALA_LEITURA','IN_LABORATORIO_CIENCIAS','IN_LABORATORIO_INFORMATICA','IN_QUADRA_ESPORTES_COBERTA','IN_PATIO_COBERTO','IN_AUDITORIO',
         'IN_SALA_PROFESSOR','IN_SALA_ATENDIMENTO_ESPECIAL','IN_ACESSIBILIDADE_RAMPAS','IN_ACESSIBILIDADE_CORRIMAO','IN_INTERNET_ALUNOS','IN_BANDA_LARGA',
         'IN_EQUIP_MULTIMIDIA','IN_DESKTOP_ALUNO','IN_COMP_PORTATIL_ALUNO','IN_EQUIP_IMPRESSORA','IN_AREA_VERDE','IN_ALMOXARIFADO','IN_SECRETARIA']
C = sum((f(c) == 1).astype(int) for c in items)

M['infA'] = A.astype(int).values; M['infB'] = B.astype(int).values; M['infC'] = C.values
M['q'] = pd.qcut(M.inse, 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
print(M.groupby('q', observed=True)[['infA', 'infB', 'infC', 'infra']].mean().round(3))
print(M[M.rural == 0].groupby('q', observed=True)[['infA', 'infB', 'infC']].mean().round(3))
M.to_pickle('M4.pkl')  # índice = código INEP
