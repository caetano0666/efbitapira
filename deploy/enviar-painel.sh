#!/usr/bin/env bash
# ============================================================
# ENVIO DO PAINEL PARA A KINGHOST
#
# Manda os arquivos do painel para /admin/ no servidor, um por um.
# Nao espelha, nao apaga nada e nao alcanca nenhum arquivo do site.
#
# O painel vive numa pasta propria. index.html, doacao/,
# transparencia/, .htaccess e favicons nao aparecem em lugar
# nenhum desta lista.
# ============================================================
set -euo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"

: "${KH_FTP_HOST:?falta KH_FTP_HOST}"
: "${KH_FTP_USER:?falta KH_FTP_USER}"
: "${KH_FTP_PASS:?falta KH_FTP_PASS}"

cd "$raiz"
mapfile -t arquivos < <(
  find admin -type f \
    \( -name '*.php' -o -name '*.css' -o -name '*.woff2' -o -name '*.png' -o -name '.htaccess' \) \
    -not -name 'config.exemplo.php' | sort
)
[ "${#arquivos[@]}" -gt 0 ] || { echo "PAINEL: nada a enviar."; exit 1; }

# trava: nada fora de admin/ entra nesta lista, nunca
for arq in "${arquivos[@]}"; do
  case "$arq" in
    admin/*) : ;;
    *) echo "PAINEL: RECUSADO, arquivo fora de admin/: $arq"; exit 1 ;;
  esac
done

roteiro="$(mktemp)"
trap 'rm -f "$roteiro"' EXIT
{
  echo "open -u \"$KH_FTP_USER,$KH_FTP_PASS\" \"ftp://$KH_FTP_HOST\""
  echo "set ftp:ssl-allow no"
  echo "set ftp:passive-mode true"
  echo "set net:max-retries 2"
  echo "set net:timeout 30"
  echo "set xfer:clobber true"
  for arq in "${arquivos[@]}"; do
    pasta="$(dirname "$arq")"
    echo "mkdir -p -f \"$pasta\""
    echo "put -O \"$pasta\" \"$raiz/$arq\""
  done
  echo "bye"
} > "$roteiro"

echo "PAINEL: ${#arquivos[@]} arquivos para /admin/"
for arq in "${arquivos[@]}"; do echo "   -> $arq"; done

if lftp -f "$roteiro"; then
  echo "PAINEL: envio concluido."
else
  echo "PAINEL: envio FALHOU."
  exit 1
fi
