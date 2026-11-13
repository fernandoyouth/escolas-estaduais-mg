"""Grava as bases finais em dados/processados/ (CSV com ponto e vírgula e decimal com vírgula).

Entradas: M7.pkl (de vinculo.py), panel.pkl (de panel.py), data.json (de prep.py), irt_params.json, panel_res.json.
"""
import json, os, shutil
import numpy as np
import pandas as pd

os.makedirs('dados/processados', exist_ok=True)
M = pd.read_pickle('M7.pkl')
SRE = json.load(open('data.json', encoding='utf-8'))['sre']
M['SRE'] = M.CO_ORGAO_REGIONAL.map(SRE)
M['localizacao_aproximada'] = M.aprox.fillna(0).astype(int)
M['indice_infra_0a7'] = M.infra
M['situacao_vs_esperado'] = np.select([M.z <= -1, M.z >= 1, M.z.notna()], ['abaixo', 'acima', 'dentro'], 'sem dado')
ren = {'z_em': 'z_esperado_em', 'z_af': 'z_esperado_af', 'z_ai': 'z_esperado_ai', 'z': 'z_esperado', 'z_et': 'z_etapa_usada',
       'ird': 'regularidade_docente_2025', 'pct_contrat': 'pct_docentes_temporarios_2025', 'esc_geral': 'escala_infra_0a10',
       'NO_MESORREGIAO': 'mesorregiao', 'metro': 'sre_metropolitana'}
base = ['NO_ENTIDADE', 'CO_ENTIDADE', 'NO_MUNICIPIO', 'SRE', 'CO_ORGAO_REGIONAL', 'NO_MESORREGIAO', 'metro', 'TP_LOCALIZACAO',
        'lat', 'lon', 'localizacao_aproximada', 'END', 'TEL']
qt_in = [c for c in M.columns if c.startswith(('QT_', 'IN_'))]
ind = ['ideb_ai', 'ideb23_ai', 'mat_ai', 'por_ai', 'ideb_af', 'ideb23_af', 'mat_af', 'por_af', 'ideb_em', 'ideb23_em', 'mat_em', 'por_em',
       'aband_ai', 'aband_af', 'aband_em', 'reprov_af', 'reprov_em', 'tdi_ai', 'tdi_af', 'tdi_em', 'inse', 'inse_nivel',
       'indice_infra_0a7', 'esc_geral', 'ird', 'pct_contrat', 'log_mat', 'rural', 'noturno', 'integral_em', 'integral_fund',
       'z_em', 'z_af', 'z_ai', 'z', 'z_et', 'situacao_vs_esperado']
out = M[base + qt_in + ind].rename(columns=ren)
out.to_csv('dados/processados/escolas_estaduais_mg_indicadores.csv', sep=';', decimal=',', index=False, encoding='utf-8-sig')
P = pd.read_pickle('panel.pkl')
P.to_csv('dados/processados/painel_escolas_2019_2025.csv', sep=';', decimal=',', index=False, encoding='utf-8-sig')
for f in ['irt_params.json', 'panel_res.json']:
    shutil.copy(f, 'dados/processados/' + f)
print('escolas:', len(out), '| linhas do painel:', len(P))
print(out.situacao_vs_esperado.value_counts().to_dict())
