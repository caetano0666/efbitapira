#!/usr/bin/env bash
# ============================================================
# ENVIO PARA A KINGHOST, POR FTP
#
# Envia EXATAMENTE os arquivos da lista, um por um.
# Nao espelha, nao sincroniza pasta, nao apaga por conta propria.
#
# O usuario efbitapira01 cai direto na raiz publica do site.
# NAO se acrescenta /www ao caminho.
#
# Credenciais chegam por variavel de ambiente e nunca sao impressas:
#   KH_FTP_HOST   ftp.web1137.kinghost.net
#   KH_FTP_USER   usuario exclusivo de deploy
#   KH_FTP_PASS   senha desse usuario
#
# Uso: bash deploy/enviar.sh
# ============================================================
set -euo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"

: "${KH_FTP_HOST:?falta KH_FTP_HOST}"
: "${KH_FTP_USER:?falta KH_FTP_USER}"
: "${KH_FTP_PASS:?falta KH_FTP_PASS}"

mapfile -t arquivos < <(bash "$aqui/montar-lista.sh")
[ "${#arquivos[@]}" -gt 0 ] || { echo "ENVIO: a lista esta vazia. Nada a fazer."; exit 1; }

mapfile -t remover < <(grep -vE '^\s*(#|$)' "$aqui/remover.txt" || true)

roteiro="$(mktemp)"
trap 'rm -f "$roteiro"' EXIT

{
  echo "set ftp:passive-mode true"
  echo "set net:max-retries 2"
  echo "set net:timeout 30"
  echo "set xfer:clobber true"
  echo "set ftp:use-mdtm false"

  for arq in "${arquivos[@]}"; do
    pasta="$(dirname "$arq")"
    [ "$pasta" != "." ] && echo "mkdir -p -f \"$pasta\""
    echo "put -O \"${pasta#.}\" \"$raiz/$arq\""
  done

  # despublicacao: so o que estiver escrito em remover.txt, e so PDFs
  # da Transparencia. Nunca vem de espelhamento nem de comparacao
  # automatica de pastas.
  for alvo in "${remover[@]}"; do
    echo "rm -f \"$alvo\""
  done

  echo "bye"
} > "$roteiro"

echo "ENVIO: ${#arquivos[@]} arquivos para $KH_FTP_HOST"
for arq in "${arquivos[@]}"; do echo "   -> $arq"; done
if [ "${#remover[@]}" -gt 0 ]; then
  echo "ENVIO: ${#remover[@]} arquivos a despublicar"
  for alvo in "${remover[@]}"; do echo "   xx $alvo"; done
fi

# a senha entra so aqui, pela variavel, e nunca aparece no log
if lftp -u "$KH_FTP_USER,$KH_FTP_PASS" "ftp://$KH_FTP_HOST" -f "$roteiro"; then
  echo "ENVIO: concluido."
else
  echo "ENVIO: FALHOU."
  echo "  Se a conexao nem abriu, a causa provavel e a POLITICA DE IPS do FTP"
  echo "  na KingHost, hoje em 'Liberar acesso nacional'. Os servidores do"
  echo "  GitHub Actions ficam fora do Brasil."
  exit 1
fi
