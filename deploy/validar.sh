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
#   2. o escopo do envio, e que ele nao ficou vazio
#   3. que cada pagina do envio existe e tem tamanho plausivel
#   4. que o QR do PIX continua sendo o do banco, com 144 caracteres
#   5. que a lista de envio nao contem nada proibido
#
# Regra que amarra tudo: confere-se O QUE VAI SER ENVIADO, e nao uma
# lista fixa escrita a mao noutro lugar. Se o escopo mudar amanha, as
# conferencias mudam junto, sem ninguem precisar lembrar.
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
# 2. O ESCOPO E A LISTA
#
#    A lista e montada UMA vez e todo o resto deste script se apoia
#    nela. Quem decide o que entra e o montar-lista.sh, que le o
#    EFB_ESCOPO. Aqui nao se decide nada, so se confere.
# ------------------------------------------------------------
escopo="${EFB_ESCOPO:-tudo}"
echo "ESCOPO: $escopo"
[ "$escopo" = "transparencia" ] && \
  echo "        publicacao disparada pelo painel. So sai o que esta sob transparencia/."

mapfile -t envio < <(bash "$aqui/montar-lista.sh")
if [ "${#envio[@]}" -eq 0 ]; then
  echo "ESCOPO: FALHOU  a lista de envio ficou vazia. Nada a publicar."
  exit 1
fi

esta_no_envio() {
  local alvo="$1" item
  for item in "${envio[@]}"; do [ "$item" = "$alvo" ] && return 0; done
  return 1
}

# ------------------------------------------------------------
# 3. CADA ARQUIVO DO ENVIO EXISTE E TEM TAMANHO PLAUSIVEL
#
#    As paginas tem minimo conhecido. Os PDFs da Transparencia nao:
#    o tamanho de um demonstrativo nao e previsivel, entao deles se
#    confere apenas que existem e nao estao vazios.
# ------------------------------------------------------------
minimo_de() {
  case "$1" in
    index.html)               echo 1500000 ;;
    doacao/index.html)        echo  400000 ;;
    transparencia/index.html) echo  250000 ;;
    equipe/index.html)        echo  500000 ;;
    *)                        echo       1 ;;
  esac
}
for arq in "${envio[@]}"; do
  if [ ! -f "$raiz/$arq" ]; then
    echo "ARQUIVOS: FALHOU  $arq esta na lista mas nao existe"; falhou=1; continue
  fi
  minimo=$(minimo_de "$arq")
  tam=$(wc -c < "$raiz/$arq" | tr -d ' ')
  if [ "$tam" -lt "$minimo" ]; then
    echo "ARQUIVOS: FALHOU  $arq tem $tam bytes, abaixo do minimo $minimo"; falhou=1
  else
    echo "ARQUIVOS: ok  $arq  $tam bytes"
  fi
done

# ------------------------------------------------------------
# 4. A TRAVA DO PIX
#    O erro mais caro possivel e um QR quebrado: a doacao deixa de
#    chegar e ninguem percebe. Conferimos o payload inteiro.
#
#    So se aplica quando a pagina de doacao esta no envio. Fora do
#    escopo dela, o arquivo no servidor nao e tocado e o QR no ar nao
#    muda, entao reprovar aqui seria travar a publicacao do William
#    por causa de uma pagina que ninguem esta publicando. A garantia
#    continua existindo: o conferir-producao.sh le o QR do site no ar
#    depois de todo envio, em qualquer escopo.
# ------------------------------------------------------------
if ! esta_no_envio "doacao/index.html"; then
  echo "PIX: nao se aplica  a pagina de doacao nao esta neste envio"
else
set +e
python3 "$aqui/conferir-pix.py" "$raiz/doacao/index.html" "$aqui/pix-oficial.txt"
codigo_pix=$?
set -e
case "$codigo_pix" in
  0)
    echo "PIX: ok" ;;
  3)
    # a conferencia nao rodou. isso nao e a mesma coisa que o QR estar errado,
    # e a mensagem precisa dizer qual das duas e. de qualquer forma nada sai
    # daqui: publicar sem conferir o QR e o risco que esta trava existe para cobrir.
    echo "PIX: NAO CONFERIDO  falta um leitor de QR neste computador."
    echo "     O QR pode estar perfeito. Ninguem olhou. A linha acima diz o que instalar."
    falhou=1 ;;
  *)
    echo "PIX: FALHOU  o QR da pagina de doacao nao confere com o oficial"
    falhou=1 ;;
esac
fi

# ------------------------------------------------------------
# 5. NADA PROIBIDO NA LISTA DE ENVIO
#    A automacao envia lista fechada, nunca espelha. Esta conferencia
#    existe para o caso de alguem mexer na lista no futuro.
# ------------------------------------------------------------
proibidos='(^|/)(\.htaccess|template.*\.html|.*\.py|audit\.js|package.*\.json|\.pages\.yml|CNAME|README\.md|qr-pix-oficial.*\.png|logo-.*)$'
lista_ruim=0
quantos_envio=0
for arq in "${envio[@]}"; do
  [ -z "$arq" ] && continue
  quantos_envio=$((quantos_envio + 1))
  if printf '%s' "$arq" | grep -qE "$proibidos"; then
    echo "LISTA: FALHOU  arquivo proibido na lista de envio: $arq"
    lista_ruim=1; falhou=1
  elif [ "$escopo" = "transparencia" ] && [ "${arq#transparencia/}" = "$arq" ]; then
    # cinto e suspensorio: no escopo do painel, nada fora de
    # transparencia/ pode passar, nem se a lista for adulterada.
    echo "LISTA: FALHOU  fora do escopo transparencia: $arq"
    lista_ruim=1; falhou=1
  fi
done
[ "$lista_ruim" -eq 0 ] && echo "LISTA: ok  $quantos_envio arquivos, nenhum proibido"

# ------------------------------------------------------------
# 6. A DESPUBLICACAO SO ALCANCA PDF DA TRANSPARENCIA
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
