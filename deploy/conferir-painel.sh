#!/usr/bin/env bash
# ============================================================
# CONFERENCIA DO PAINEL, OLHANDO DE FORA
#
# Confere que o painel respondeu, que o config nao e legivel e,
# principalmente, que o site continua exatamente como estava.
# ============================================================
set -uo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"
site="https://efbitapira.org"
v="?c=$RANDOM"
falhou=0

echo "== o painel responde =="
c=$(curl -s -o /tmp/painel.$$ -w '%{http_code}' "$site/admin/$v")
if [ "$c" = "200" ] && grep -qi "senha" /tmp/painel.$$; then
  echo "  ok  /admin/ HTTP $c, pede senha"
else
  echo "  FALHOU  /admin/ HTTP $c"; falhou=1
fi
rm -f /tmp/painel.$$

echo "== o que nao pode ser lido =="
for alvo in admin/config.php admin/config.exemplo.php admin/lib/github.php admin/lib/auth.php; do
  c=$(curl -s -o /tmp/x.$$ -w '%{http_code}' "$site/$alvo$v")
  corpo=$(head -c 40 /tmp/x.$$ 2>/dev/null); rm -f /tmp/x.$$
  if [ "$c" = "403" ] || [ "$c" = "404" ] || [ -z "$corpo" ]; then
    echo "  ok  /$alvo  HTTP $c, sem codigo-fonte"
  else
    echo "  FALHOU  /$alvo devolveu conteudo, HTTP $c"; falhou=1
  fi
done

echo "== o site continua intacto =="
for par in "/:$(wc -c < "$raiz/index.html" | tr -d ' ')" \
           "/doacao/:$(wc -c < "$raiz/doacao/index.html" | tr -d ' ')" \
           "/transparencia/:$(wc -c < "$raiz/transparencia/index.html" | tr -d ' ')"; do
  p="${par%%:*}"; esperado="${par##*:}"
  obtido=$(curl -s "$site$p$v" | wc -c | tr -d ' ')
  if [ "$obtido" = "$esperado" ]; then echo "  ok  $p  $obtido bytes"
  else echo "  FALHOU  $p  $obtido bytes, esperados $esperado"; falhou=1; fi
done
h=$(curl -s -o /dev/null -w '%{http_code}' "$site/.htaccess")
[ "$h" = "403" ] && echo "  ok  /.htaccess protegido" || { echo "  FALHOU  /.htaccess HTTP $h"; falhou=1; }

echo
[ "$falhou" -eq 0 ] && echo "PAINEL APROVADO." || echo "PAINEL REPROVADO."
exit "$falhou"
