#!/usr/bin/env bash
# ============================================================
# A LISTA DO QUE VAI PARA A PRODUCAO
#
# Sai desta lista, e de mais lugar nenhum:
#   - os caminhos fixos de lista-de-envio.txt
#   - os PDFs marcados "publicado" em transparencia/documentos.json
#
# ------------------------------------------------------------
# POR QUE O documentos.json, E NAO A PASTA
#
# Ate 14/09/2026 esta lista varria transparencia/arquivos/ e mandava
# todo PDF que encontrasse. A pagina, por outro lado, sempre obedeceu
# o campo "publicado" do documentos.json. Eram duas fontes de verdade
# sobre o mesmo documento, e elas discordavam no caso que mais importa:
# um PDF despublicado sumia da pagina e continuava no ar, alcancavel
# por quem tivesse guardado o endereco direto.
#
# A Regra de Publicacao de 18/08/2026, secao 8, trata despublicar como
# a contencao imediata de um incidente, feita pelo financeiro sozinho.
# Contencao que nao tira o arquivo do ar nao contem nada.
#
# Agora existe uma fonte de verdade so: o documentos.json manda, aqui
# e na pagina. O arquivo continua no repositorio quando despublicado,
# que e o que permite republicar. O que muda e o que fica no servidor.
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

# ------------------------------------------------------------
# OS PDFS AUTORIZADOS
#
# Le o documentos.json e devolve o caminho de cada documento com
# "publicado" verdadeiro. Tres decisoes deliberadas:
#
#   1. Arquivo ausente e estado legitimo, nao erro. E o estado de
#      hoje: nenhum documento foi publicado ainda. Devolve lista
#      vazia e o processo segue.
#
#   2. Arquivo ilegivel ou com estrutura inesperada PARA O PROCESSO.
#      Nao devolve lista vazia. Esta lista decide tambem o que e
#      apagado da producao, entao "nao consegui ler" jamais pode
#      virar "nao ha nada autorizado".
#
#   3. Cada caminho e conferido contra a mesma expressao que o painel
#      usa em gh_caminho_permitido. O documentos.json e escrito pelo
#      cliente, por dois programas diferentes. Ele nao manda em qual
#      caminho a automacao escreve ou apaga.
# ------------------------------------------------------------
pdfs=""
if [ -f "$raiz/transparencia/documentos.json" ]; then
  if ! pdfs="$(python3 - "$raiz" <<'PY'
import json, os, re, sys

raiz = sys.argv[1]
alvo = os.path.join(raiz, "transparencia", "documentos.json")
ok = re.compile(r"^transparencia/arquivos/[a-z0-9][a-z0-9._-]{0,90}\.pdf$")

try:
    with open(alvo, encoding="utf-8") as f:
        dados = json.load(f)
except Exception as e:
    print("AUTORIZADOS: documentos.json ilegivel: %s" % e, file=sys.stderr)
    sys.exit(1)

vistos = []
try:
    for per in dados.get("periodos", []) or []:
        for doc in per.get("documentos", []) or []:
            if not doc.get("publicado"):
                continue
            caminho = str(doc.get("arquivo") or "").lstrip("/")
            if not caminho:
                print("AUTORIZADOS: documento publicado sem arquivo: %r"
                      % doc.get("titulo"), file=sys.stderr)
                sys.exit(1)
            if not ok.match(caminho):
                print("AUTORIZADOS: caminho fora das areas autorizadas: %r"
                      % caminho, file=sys.stderr)
                sys.exit(1)
            if caminho not in vistos:
                vistos.append(caminho)
except AttributeError as e:
    print("AUTORIZADOS: estrutura inesperada no documentos.json: %s" % e,
          file=sys.stderr)
    sys.exit(1)

for caminho in sorted(vistos):
    print(caminho)
PY
  )"; then
    echo "LISTA: FALHOU  nao consegui apurar os PDFs autorizados." >&2
    echo "       Nada sera enviado e nada sera apagado da producao." >&2
    exit 1
  fi
fi

montar() {
  grep -vE '^\s*(#|$)' "$aqui/lista-de-envio.txt"
  [ -n "$pdfs" ] && printf '%s\n' "$pdfs"
  return 0
}

if [ "$escopo" = "transparencia" ]; then
  # a restricao e uma so, e e literal: caminho dentro de transparencia/.
  # index.html, doacao e equipe nao passam por aqui de jeito nenhum.
  montar | grep '^transparencia/' || true
else
  montar
fi
