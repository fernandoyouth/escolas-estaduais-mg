#!/usr/bin/env bash
# Roda a análise inteira na ordem certa, a partir da raiz do repositório.
# Pré-requisito: bash scripts/baixar_dados.sh
set -euo pipefail
S=scripts
python3 $S/build.py        # recorte MG estadual 2024 + coordenadas
python3 $S/prep.py         # base do mapa (data.json), SREs, limites
python3 $S/ind.py          # Ideb 2025, rendimento, distorção, INSE por escola
python3 $S/ana.py          # retrato 2024-2025: INSE x infraestrutura x Ideb
python3 $S/add.py          # indicadores no mapa
python3 $S/model2.py       # resultado esperado por etapa (z)
python3 $S/infra_def.py    # definições alternativas de infraestrutura
python3 $S/reg.py          # infraestrutura por mesorregião
python3 $S/reg2.py         # itens x Ideb com efeitos de mesorregião
python3 $S/ideb_hist.py    # série do Ideb 2017-2025
python3 $S/doc_ind.py      # adequação e regularidade docente 2019-2025
python3 $S/scale.py        # itens de infraestrutura por ano
python3 $S/irt.py          # escala de infraestrutura por TRI (2PL)
python3 $S/panel.py        # painel com efeitos fixos de escola e ano
python3 $S/rmbh.py         # mesorregião Metropolitana
python3 $S/metro_sre.py    # região metropolitana pelas 3 SREs
