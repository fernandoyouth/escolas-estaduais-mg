# Escolas estaduais de Minas Gerais: infraestrutura, professores e resultados (2019–2025)

Dados, scripts e mapa usados no estudo sobre as 3.453 escolas estaduais de Minas Gerais em atividade em 2024. Tudo parte de dados públicos do INEP e do Ipea, e qualquer número pode ser refeito a partir daqui.

**Situação:** trabalho em andamento, sem revisão por pares. Os resultados são associações, não efeitos causais.

## Principais achados

- **Infraestrutura.** Comparando escolas diferentes, mais infraestrutura acompanha Ideb um pouco maior (cerca de 0,04 ponto por ponto numa escala de 0 a 10). Acompanhando a mesma escola de 2019 a 2025, a associação some: a estimativa fica entre −0,01 e +0,01 nas três etapas.
- **Desigualdade.** A infraestrutura é pior onde os alunos são mais pobres e nas mesorregiões do Vale do Mucuri, Norte e Jequitinhonha.
- **Professores.** A regularidade do corpo docente (permanência dos mesmos professores na escola) é o único fator escolar associado ao Ideb tanto entre escolas quanto dentro da mesma escola ao longo do tempo. No ensino médio e nos anos finais o resultado se mantém sem 2021; nos anos iniciais, não.
- **Região metropolitana.** As 510 escolas das três SREs metropolitanas de Belo Horizonte ficam entre as de pior resultado em relação ao esperado para o perfil dos alunos. A diferença está na nota de aprendizagem, não na aprovação. A menor permanência docente está associada a cerca de um quinto dela; a infraestrutura, a nada.

## Estrutura

```
scripts/              análise, na ordem de scripts/executar.sh
  baixar_dados.sh     baixa os dados brutos do INEP e do Ipea para dados/brutos/
  executar.sh         roda tudo
dados/processados/    bases finais (CSV separado por ponto e vírgula, decimal com vírgula)
  escolas_estaduais_mg_indicadores.csv   uma linha por escola: matrículas, equipamentos,
                                         infraestrutura, Ideb, rendimento, INSE, resultado esperado
  painel_escolas_2019_2025.csv           escola × etapa × ano: Ideb, escala de infraestrutura,
                                         indicadores docentes e controles
  irt_params.json                        parâmetros da escala de infraestrutura (TRI)
  panel_res.json                         coeficientes dos modelos de painel
mapa/                 mapa interativo (abrir mapa/index.html num servidor local)
```

## Como reproduzir

Requer Python 3.10+ e cerca de 1 GB livre para os dados brutos.

```bash
pip install -r requirements.txt
bash scripts/baixar_dados.sh
bash scripts/executar.sh
```

Os scripts gravam arquivos intermediários (`*.pkl`, `data.json`) na raiz do repositório.

## Fontes

| Dado | Ano | Fonte |
| --- | --- | --- |
| Microdados do Censo Escolar | 2019, 2021, 2023, 2024 | INEP |
| Ideb por escola (série 2017–2025) | 2025 | INEP |
| Taxas de rendimento e distorção idade-série por escola | 2024 | INEP |
| Indicador de Nível Socioeconômico (INSE) por escola | 2023 | INEP |
| Adequação da formação docente e regularidade do corpo docente | 2019–2025 | INEP |
| Coordenadas das escolas e limites municipais | 2023 / 2022 | geobr (Ipea), a partir do Catálogo de Escolas do INEP e do IBGE |

## Método em resumo

- **Recorte:** escolas com dependência administrativa estadual, em atividade, em Minas Gerais.
- **Escala de infraestrutura:** modelo de Teoria de Resposta ao Item de 2 parâmetros com 40 itens do Censo, calibrado em conjunto para 2019, 2021, 2023 e 2024, no espírito de Alves e Xavier (2018) e Soares Neto et al. (2013).
- **Resultado esperado:** regressão do Ideb 2025 de cada etapa sobre INSE, tamanho da escola, localização, oferta noturna e tempo integral; o resíduo é padronizado pelo desvio-padrão da etapa.
- **Painel:** Ideb de 2019 a 2025 com efeitos fixos de escola e de ano e erros-padrão agrupados por escola. O Ideb de 2025 é pareado com o Censo 2024.
- **SREs:** nomes inferidos a partir da cidade-sede de cada código de órgão regional do Censo.

## Limitações

- Desenho observacional: o painel remove diferenças fixas entre escolas, mas não estabelece causa.
- O INSE é de 2023 e fica constante no painel; cerca de 10% das escolas não têm INSE ou Ideb, em geral pequenas e rurais.
- Infraestrutura declarada pela própria escola no Censo; registra a existência do item, não a conservação.
- 2021 foi ano de pandemia; os resultados principais foram conferidos sem esse ano.
- O vínculo dos professores (efetivo ou temporário) não está nos microdados públicos.
- 111 escolas sem coordenada aparecem no mapa na sede do município.

## Referências citadas

- ALVES, M. T. G.; XAVIER, F. P. Indicadores multidimensionais para avaliação da infraestrutura escolar: o ensino fundamental. *Cadernos de Pesquisa*, v. 48, n. 169, 2018.
- PETRUS, L. *Análise dos impactos dos investimentos em infraestrutura escolar no desempenho das unidades estaduais de ensino de Minas Gerais*. Dissertação (Mestrado) – UFJF, 2013.
- PONTES, L. A. F.; SOARES, T. M. Volatilidade dos resultados de proficiência e seu impacto sobre as metas do Ideb nas escolas públicas de Minas Gerais. *Educação em Revista*, v. 33, 2017.
- SOARES NETO, J. J. et al. Uma escala para medir a infraestrutura escolar. *Estudos em Avaliação Educacional*, v. 24, n. 54, 2013.

## Licença

Código sob licença MIT. Os dados são públicos e pertencem às fontes listadas; ao reutilizá-los, cite o INEP e o Ipea.

## Autor

Fernando Costa. Comentários e correções são bem-vindos pelas *issues* do repositório.
