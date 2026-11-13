#!/usr/bin/env bash
# Baixa os dados públicos usados no estudo e monta a pasta dados/brutos/.
# Rodar a partir da raiz do repositório: bash scripts/baixar_dados.sh
set -euo pipefail
B=dados/brutos; mkdir -p $B/ind $B/hist/ind tmp
INEP=https://download.inep.gov.br
IND=$INEP/informacoes_estatisticas/indicadores_educacionais

# Censo Escolar 2024 (todas as escolas) e recorte MG estadual
curl -L -o tmp/censo2024.zip $INEP/dados_abertos/microdados_censo_escolar_2024.zip
unzip -o -j tmp/censo2024.zip "*/dados/microdados_ed_basica_2024.csv" -d $B

# Censos 2019, 2021, 2023 (painel): só o recorte MG estadual é mantido
for y in 2019 2021 2023; do
  curl -L -o tmp/censo$y.zip $INEP/dados_abertos/microdados_censo_escolar_$y.zip
  unzip -o -j tmp/censo$y.zip "*/dados/microdados_ed_basica_$y.csv" -d tmp
  python3 scripts/filtrar_censo.py tmp/microdados_ed_basica_$y.csv $B/hist/mg_estaduais_$y.csv
  rm tmp/microdados_ed_basica_$y.csv
done

# Coordenadas das escolas e limites municipais (geobr/Ipea)
curl -L -o $B/schools_2023.gpkg https://www.ipea.gov.br/geobr/data_gpkg/schools/2023/schools_2023.gpkg
curl -L -o $B/31municipality_2022_simplified.gpkg https://www.ipea.gov.br/geobr/data_gpkg/municipality/2022/31municipality_2022_simplified.gpkg

# Ideb 2025 por escola (contém a série 2017-2025)
for e in anos_iniciais anos_finais ensino_medio; do
  curl -L -o tmp/ideb_$e.zip $INEP/ideb/resultados/divulgacao_${e}_escolas_2025.zip
  unzip -o -j tmp/ideb_$e.zip "*.xlsx" -d $B/ind
done

# Rendimento e distorção idade-série 2024, INSE 2023
curl -L -o tmp/rend.zip $IND/2024/tx_rend_escolas_2024.zip && unzip -o -j tmp/rend.zip "*.xlsx" -d $B/ind
curl -L -o tmp/tdi.zip $IND/2024/TDI_2024_ESCOLAS.zip && unzip -o -j tmp/tdi.zip "*.xlsx" -d $B/ind
curl -L -o $B/ind/INSE_2023_escolas.xlsx $IND/2023/nivel_socioeconomico/INSE_2023_escolas.xlsx

# Adequação da formação docente (AFD) e regularidade docente (IRD) por escola
for y in 2019 2021 2023 2024 2025; do
  for k in AFD IRD; do
    curl -L -o tmp/${k}_$y.zip $IND/$y/${k}_${y}_ESCOLAS.zip
    unzip -o -j tmp/${k}_$y.zip "*.xlsx" -d $B/hist/ind
  done
done
echo "Pronto. Arquivos em $B"
