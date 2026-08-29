#!/usr/bin/env bash
# ============================================================
# CONFERENCIA DEPOIS DO ENVIO
#
# Olha a producao de fora, como um visitante olharia, e compara
# com o que deveria estar la. Se alguma coisa objetiva estiver
# errada, a automacao para e avisa.
#
# Confere:
#   1. as paginas do envio respondem 200 e tem o tamanho certo
#   2. o QR do PIX no ar continua sendo o oficial
#   3. HTTP vai para HTTPS, www vai para o dominio sem www
#   4. o .htaccess continua protegido
#   5. arquivos de desenvolvimento continuam fora do ar
#
# Uso: bash deploy/conferir-producao.sh
# ============================================================
set -uo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"
site="https://efbitapira.org"
escopo="${EFB_ESCOPO:-tudo}"
falhou=0

# a KingHost nao manda cabecalho de cache. sem isto, a conferencia
# pode ler a versao antiga e aprovar uma publicacao que nao chegou.
sem_cache="?conferencia=$(git -C "$raiz" rev-parse --short HEAD 2>/dev/null || echo x)"

echo "== escopo =="
echo "  $escopo"

echo "== paginas e documentos =="
mapfile -t envio < <(EFB_ESCOPO="$escopo" bash "$aqui/montar-lista.sh")
if [ "${#envio[@]}" -eq 0 ]; then
  # lista vazia aqui viraria conferencia verde sem ter conferido nada.
  echo "  FALHOU  a lista de envio veio vazia. Nada foi conferido."
  falhou=1
fi
for arq in "${envio[@]}"; do
  [ -z "$arq" ] && continue
  caminho="/${arq%index.html}"
  esperado=$(wc -c < "$raiz/$arq" | tr -d ' ')
  http=$(curl -s -o /tmp/pg.$$ -w '%{http_code}' "$site$caminho$sem_cache")
  obtido=$(wc -c < /tmp/pg.$$ | tr -d ' '); rm -f /tmp/pg.$$
  if [ "$http" = "200" ] && [ "$obtido" = "$esperado" ]; then
    echo "  ok  $caminho  HTTP $http  $obtido bytes"
  else
    echo "  FALHOU  $caminho  HTTP $http  $obtido bytes, esperados $esperado"; falhou=1
  fi
done

echo "== documentos despublicados sairam do ar =="
n=0
while IFS= read -r alvo; do
  [ -z "$alvo" ] && continue
  n=$((n + 1))
  c=$(curl -s -o /dev/null -w '%{http_code}' "$site/$alvo$sem_cache")
  if [ "$c" = "404" ] || [ "$c" = "403" ]; then
    echo "  ok  /$alvo  HTTP $c"
  else
    echo "  FALHOU  /$alvo continua no ar, HTTP $c"; falhou=1
  fi
done < <(grep -vE '^\s*(#|$)' "$aqui/remover.txt" || true)
[ "$n" -eq 0 ] && echo "  ok  nada a despublicar"

# Este bloco roda em QUALQUER escopo, inclusive quando a doacao nao foi
# enviada. E a garantia que sustenta a dispensa da conferencia do PIX no
# validar.sh: nao importa o que foi publicado, o QR que o visitante ve
# tem que continuar sendo o do banco.
echo "== PIX no ar =="
curl -s "$site/doacao/$sem_cache" -o /tmp/doa.$$
if python3 "$aqui/conferir-pix.py" /tmp/doa.$$ "$aqui/pix-oficial.txt"; then
  echo "  ok"
else
  echo "  FALHOU  o QR que esta no ar nao confere com o oficial"; falhou=1
fi
rm -f /tmp/doa.$$

echo "== redirecionamentos =="
for u in "http://efbitapira.org/" "http://www.efbitapira.org/" "https://www.efbitapira.org/"; do
  r=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "$u")
  if [ "${r%% *}" = "301" ] && [ "${r#* }" = "https://efbitapira.org/" ]; then
    echo "  ok  $u -> 301 https://efbitapira.org/"
  else
    echo "  FALHOU  $u -> $r"; falhou=1
  fi
done

echo "== .htaccess protegido =="
h=$(curl -s -o /dev/null -w '%{http_code}' "$site/.htaccess")
if [ "$h" = "403" ] || [ "$h" = "404" ]; then
  echo "  ok  HTTP $h"
else
  echo "  FALHOU  /.htaccess respondeu HTTP $h"; falhou=1
fi

echo "== arquivos de desenvolvimento fora do ar =="
for f in template.html build-home.py comum.py .pages.yml package.json audit.js CNAME README.md; do
  c=$(curl -s -o /dev/null -w '%{http_code}' "$site/$f")
  if [ "$c" = "404" ] || [ "$c" = "403" ]; then
    echo "  ok  /$f  HTTP $c"
  else
    echo "  FALHOU  /$f vazou para a producao, HTTP $c"; falhou=1
  fi
done

echo
if [ "$falhou" -eq 0 ]; then
  echo "CONFERENCIA APROVADA."
else
  echo "CONFERENCIA REPROVADA. Considere restaurar o commit anterior."
  echo "  Actions -> Publicar na KingHost -> Run workflow -> commit: <hash anterior>"
fi
exit "$falhou"
