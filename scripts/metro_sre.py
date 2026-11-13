"""Região metropolitana pelo recorte das três SREs metropolitanas (códigos 00001, 00002, 00041),
decomposição da diferença e separação entre nota (aprendizagem) e rendimento (aprovação).

Entrada: M6.pkl (de rmbh.py) e ideb_hist.pkl (de ideb_hist.py).
"""
import pandas as pd, numpy as np

M = pd.read_pickle('M6.pkl')
M['metro'] = M.CO_ORGAO_REGIONAL.isin(['00001', '00002', '00041']).astype(int)
M['turma'] = M.QT_MAT_BAS / M.QT_TUR_BAS.replace(0, np.nan)
H = pd.read_pickle('ideb_hist.pkl'); h = H[H.ano == 2025]
for et in ['em', 'af']:
    M = M.join(h[h.etapa == et].set_index('id')[['nota', 'rend']].add_suffix('_' + et))

def coef(y, xs):
    s = M[[y] + xs].dropna(); X = np.c_[np.ones(len(s)), s[xs].values.astype(float)]
    b, *_ = np.linalg.lstsq(X, s[y].values, rcond=None)
    r = s[y].values - X @ b; se = np.sqrt(np.diag((r @ r) / (len(s) - X.shape[1]) * np.linalg.inv(X.T @ X)))
    return round(b[1], 3), round(se[1], 3)

print('escolas:', M.metro.sum(), '| municípios:', M[M.metro == 1].NO_MUNICIPIO.nunique())
print(M.groupby('metro')[['inse', 'ird', 'esc_geral', 'turma', 'z']].mean().round(2))
for y, ic, af in [('ideb_em', 'integral_em', 'afd_em'), ('ideb_af', 'integral_fund', 'afd_af')]:
    ctx = ['inse', 'log_mat', 'rural', 'noturno', ic]
    for name, xs in [('bruto', []), ('+INSE', ['inse']), ('+contexto', ctx), ('+infra', ctx + ['esc_geral']),
                     ('+professores', ctx + ['esc_geral', 'ird', af]), ('+turma', ctx + ['esc_geral', 'ird', af, 'turma'])]:
        print(y, name, coef(y, ['metro'] + xs))
for et, ic in [('em', 'integral_em'), ('af', 'integral_fund')]:
    for v in ['nota_', 'rend_']:
        print(et, v, coef(v + et, ['metro', 'inse', 'log_mat', 'rural', 'noturno', ic]))
print(M.groupby('NO_MESORREGIAO').z.mean().round(2).sort_values())
