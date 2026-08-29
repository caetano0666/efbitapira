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
# ------------------------------------------------------------
# O ESCOPO
#
# Uma publicacao pode ser disparada por duas pessoas diferentes,
# e elas nao tem a mesma autoridade.
#
#   tudo           Caetano, no botao, tendo digitado PUBLICAR.
#                  Publica o site inteiro.
#
#   transparencia  O painel do William. Ele sobe um PDF ou apaga um
#                  documento, a pagina de Transparencia se refaz
#                  sozinha e o site entra no ar sem ninguem digitar
#                  nada. Publica SOMENTE o que esta sob
#                  transparencia/.
#
# Sem essa separacao, uma acao do cliente publicava o repositorio
# inteiro: qualquer coisa commitada na main ia ao ar no proximo PDF
# que ele subisse, semanas depois, sem ninguem olhando. O escopo
# fecha isso na origem, e nao no gatilho: nao importa quantos
# gatilhos existam, o que sai daqui e o que pode ser enviado.
#
# O escopo vem da variavel de ambiente EFB_ESCOPO. Valor
# desconhecido nao vira "tudo" por descuido: para o processo.
#
# Uso: bash deploy/montar-lista.sh
#      EFB_ESCOPO=transparencia bash deploy/montar-lista.sh
# ============================================================
set -euo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"

escopo="${EFB_ESCOPO:-tudo}"
case "$escopo" in
  tudo|transparencia) ;;
  *)
    echo "ESCOPO: valor desconhecido: '$escopo'." >&2
    echo "        Use tudo ou transparencia. Nada sera enviado." >&2
    exit 1 ;;
esac

montar() {
  grep -vE '^\s*(#|$)' "$aqui/lista-de-envio.txt"

  if [ -d "$raiz/transparencia/arquivos" ]; then
    find "$raiz/transparencia/arquivos" -maxdepth 1 -type f -name '*.pdf' -print \
      | sed "s|^$raiz/||" | sort
  fi
}

if [ "$escopo" = "transparencia" ]; then
  # a restricao e uma so, e e literal: caminho dentro de transparencia/.
  # index.html, doacao e equipe nao passam por aqui de jeito nenhum.
  montar | grep '^transparencia/' || true
else
  montar
fi
