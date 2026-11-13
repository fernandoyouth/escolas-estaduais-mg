"""Vínculo dos professores (Censo 2025, primeiro ano com o dado por escola nos microdados públicos):
percentual de docentes contratados temporariamente, relação com a regularidade docente e com o Ideb.

Entrada: M6.pkl (de rmbh.py) e dados/brutos/mg_estaduais_2025.csv.
"""
import pandas as pd, numpy as np

M = pd.read_pickle('M6.pkl')
R = pd.read_csv('dados/brutos/mg_estaduais_2025.csv', sep=';', dtype=str)
R = R[R.TP_SITUACAO_FUNCIONAMENTO == '1'].copy(); R['id'] = R.CO_ENTIDADE.astype(int); R = R.set_index('id')
n = lambda c: pd.to_numeric(R[c], errors='coerce')
tot = n('QT_DOC_BAS_VINCULO_CONCUR').fillna(0) + n('QT_DOC_BAS_VINCULO_CONTRA').fillna(0) + n('QT_DOC_BAS_VINCULO_TERCEIR').fillna(0) + n('QT_DOC_BAS_VINCULO_CLT').fillna(0)
R['pct_contrat'] = 100 * n('QT_DOC_BAS_VINCULO_CONTRA').fillna(0) / tot.replace(0, np.nan)
M = M.join(R[['pct_contrat']])
M['metro'] = M.CO_ORGAO_REGIONAL.isin(['00001', '00002', '00041']).astype(int)

print('docentes na rede (soma por escola):', int(tot.sum()), '| contratados:', int(n('QT_DOC_BAS_VINCULO_CONTRA').sum()),
      f"({100 * n('QT_DOC_BAS_VINCULO_CONTRA').sum() / tot.sum():.1f}%)")
print('média por escola, % contratados:', round(M.pct_contrat.mean(), 1))
print('correlação com regularidade docente:', round(M[['pct_contrat', 'ird']].corr().iloc[0, 1], 2))
print(M.groupby('metro').pct_contrat.mean().round(1).to_dict())
print(M.groupby('NO_MESORREGIAO').pct_contrat.mean().round(1).sort_values().to_dict())
M['q_inse'] = pd.qcut(M.inse, 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
print(M.groupby('q_inse', observed=True).pct_contrat.mean().round(1).to_dict())

def ols(y, xs):
    s = M[[y] + xs].dropna(); X = np.c_[np.ones(len(s)), s[xs].values.astype(float)]
    b, *_ = np.linalg.lstsq(X, s[y].values, rcond=None)
    r = s[y].values - X @ b; se = np.sqrt(np.diag((r @ r) / (len(s) - X.shape[1]) * np.linalg.inv(X.T @ X)))
    return pd.DataFrame({'b': b, 'se': se}, index=['c'] + xs).round(4), len(s)

for y, ic in [('ideb_em', 'integral_em'), ('ideb_af', 'integral_fund')]:
    ctx = ['inse', 'log_mat', 'rural', 'noturno', ic, 'esc_geral']
    t, n_ = ols(y, ctx + ['pct_contrat']); print(y, 'pct_contrat (por 10 p.p.):', round(10 * t.loc['pct_contrat', 'b'], 3), '±', round(10 * t.loc['pct_contrat', 'se'], 3), 'n', n_)
    t, _ = ols(y, ctx + ['pct_contrat', 'ird']); print(y, '  com ird:', round(10 * t.loc['pct_contrat', 'b'], 3), '| ird', t.loc['ird', 'b'])
    t, _ = ols(y, ['metro'] + ctx + ['ird', 'pct_contrat']); print(y, '  metro com ird+contrat:', t.loc['metro', 'b'])
M.to_pickle('M7.pkl')
