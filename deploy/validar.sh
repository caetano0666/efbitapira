#!/usr/bin/env bash
# ============================================================
# VALIDACAO ANTES DO ENVIO
#
# Se qualquer coisa aqui reprovar, nada e enviado e a producao
# nem chega a ser tocada. E a diferenca entre uma automacao e um
# acidente automatizado.
#
# Confere:
#   1. a TRAVA
#   2. que os tres arquivos existem e tem tamanho plausivel
#   3. que o QR do PIX continua sendo o do banco, com 144 caracteres
#   4. que a lista de envio nao contem nada proibido
#
# Uso: bash deploy/validar.sh
# ============================================================
set -euo pipefail

aqui="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
raiz="$(dirname "$aqui")"
falhou=0

# ------------------------------------------------------------
# 1. A TRAVA
# ------------------------------------------------------------
trava="$(tr -d '[:space:]' < "$aqui/TRAVA")"
echo "TRAVA: $trava"
if [ "$trava" != "LIBERADO" ]; then
  echo "TRAVA: o deploy esta BLOQUEADO. Nada sera enviado."
  echo "       Para liberar, o dono do projeto troca o conteudo de"
  echo "       deploy/TRAVA de BLOQUEADO para LIBERADO, em commit proprio."
  exit 78
fi

# ------------------------------------------------------------
# 2. OS ARQUIVOS QUE VAO PARA A PRODUCAO
# ------------------------------------------------------------
declare -a esperados=(
  "index.html:1500000"
  "doacao/index.html:400000"
  "transparencia/index.html:250000"
)
for par in "${esperados[@]}"; do
  arq="${par%%:*}"; minimo="${par##*:}"
  if [ ! -f "$raiz/$arq" ]; then
    echo "ARQUIVOS: FALHOU  $arq nao existe"; falhou=1; continue
  fi
  tam=$(wc -c < "$raiz/$arq" | tr -d ' ')
  if [ "$tam" -lt "$minimo" ]; then
    echo "ARQUIVOS: FALHOU  $arq tem $tam bytes, abaixo do minimo $minimo"; falhou=1
  else
    echo "ARQUIVOS: ok  $arq  $tam bytes"
  fi
done

# ------------------------------------------------------------
# 3. A TRAVA DO PIX
#    O erro mais caro possivel e um QR quebrado: a doacao deixa de
#    chegar e ninguem percebe. Conferimos o payload inteiro.
# ------------------------------------------------------------
if python3 "$aqui/conferir-pix.py" "$raiz/doacao/index.html" "$aqui/pix-oficial.txt"; then
  echo "PIX: ok"
else
  echo "PIX: FALHOU  o QR da pagina de doacao nao confere com o oficial"
  falhou=1
fi

# ------------------------------------------------------------
# 4. NADA PROIBIDO NA LISTA DE ENVIO
#    A automacao envia lista fechada, nunca espelha. Esta conferencia
#    existe para o caso de alguem mexer na lista no futuro.
# ------------------------------------------------------------
proibidos='(^|/)(\.htaccess|template.*\.html|.*\.py|audit\.js|package.*\.json|\.pages\.yml|CNAME|README\.md|qr-pix-oficial.*\.png|logo-.*)$'
lista_ruim=0
quantos_envio=0
while IFS= read -r arq; do
  [ -z "$arq" ] && continue
  quantos_envio=$((quantos_envio + 1))
  if printf '%s' "$arq" | grep -qE "$proibidos"; then
    echo "LISTA: FALHOU  arquivo proibido na lista de envio: $arq"
    lista_ruim=1; falhou=1
  elif [ ! -f "$raiz/$arq" ]; then
    echo "LISTA: FALHOU  na lista mas nao existe: $arq"
    lista_ruim=1; falhou=1
  fi
done < <(bash "$aqui/montar-lista.sh")
[ "$lista_ruim" -eq 0 ] && echo "LISTA: ok  $quantos_envio arquivos, nenhum proibido"

# ------------------------------------------------------------
# 5. A DESPUBLICACAO SO ALCANCA PDF DA TRANSPARENCIA
#    Apagar arquivo em producao e a unica operacao destrutiva que
#    esta automacao consegue fazer. Fica presa a uma pasta e a uma
#    extensao, e so ao que estiver escrito a mao em remover.txt.
# ------------------------------------------------------------
quantos=0
while IFS= read -r alvo; do
  [ -z "$alvo" ] && continue
  quantos=$((quantos + 1))
  if ! printf '%s' "$alvo" | grep -qE '^transparencia/arquivos/[^/]+\.pdf$'; then
    echo "REMOVER: FALHOU  fora do permitido: $alvo"
    echo "         so PDF direto em transparencia/arquivos/"
    falhou=1
  else
    echo "REMOVER: sera despublicado: $alvo"
  fi
done < <(grep -vE '^\s*(#|$)' "$aqui/remover.txt" || true)
[ "$quantos" -eq 0 ] && echo "REMOVER: ok  nada a despublicar"

[ "$falhou" -eq 0 ] || { echo; echo "VALIDACAO REPROVADA. Producao intacta."; exit 1; }
echo; echo "VALIDACAO APROVADA."
