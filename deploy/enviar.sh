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
  # a conexao e aberta pelo roteiro, e nao pela linha de comando.
  # assim a senha nao aparece na lista de processos do servidor.
  echo "open -u \"$KH_FTP_USER,$KH_FTP_PASS\" \"ftp://$KH_FTP_HOST\""
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

# a senha vive so no roteiro temporario, que o mktemp cria fechado
# e o trap apaga no fim. nunca vai para o log nem para o argv.
if lftp -f "$roteiro"; then
  echo "ENVIO: concluido."
else
  echo "ENVIO: FALHOU."
  echo "  Confira, nesta ordem:"
  echo "   1. a POLITICA DE IPS do FTP no painel da KingHost. Precisa estar"
  echo "      em 'Sem nenhum bloqueio', senao o IP do GitHub e recusado."
  echo "   2. usuario e senha do Secret, se o erro foi 530."
  echo "   3. se a conta de FTP nao foi desabilitada na aba Seguranca."
  exit 1
fi
