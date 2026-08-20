#!/usr/bin/env bash
# ============================================================
# A LISTA DO QUE VAI PARA A PRODUCAO
#
# Sai desta lista, e de mais lugar nenhum:
#   - os caminhos fixos de lista-de-envio.txt
#   - os PDFs que existirem em transparencia/arquivos/
#
# Os PDFs entram por varredura porque quem publica pela web nao
# edita arquivo nenhum do repositorio: manda o PDF pelo painel e
# ele aparece ali. A varredura e restrita a essa pasta e so aceita
# .pdf. Nada mais entra por descoberta automatica.
#
# Uso: bash deploy/montar-lista.sh
# ============================================================
set -euo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"

grep -vE '^\s*(#|$)' "$aqui/lista-de-envio.txt"

if [ -d "$raiz/transparencia/arquivos" ]; then
  find "$raiz/transparencia/arquivos" -maxdepth 1 -type f -name '*.pdf' -print \
    | sed "s|^$raiz/||" | sort
fi
