# ============================================================
# BASE COMUM DAS BUILDS
#
# Aqui ficam as fontes, os logotipos e os blocos que todas as
# paginas do site compartilham: o CSS, o cabecalho, o menu, o
# rodape e o script. Tudo e extraido do proprio template.html,
# entao o site continua com uma unica fonte de verdade.
#
# Este arquivo NAO depende da pasta fotos/. E de proposito:
# assim a pagina de Transparencia pode ser gerada sozinha, num
# servidor, sem que as fotografias das criancas precisem sair
# do computador da Escolinha.
# ============================================================
import base64, pathlib, re

root = pathlib.Path(__file__).resolve().parent

# ------------------------------------------------------------
# FONTES
# ------------------------------------------------------------
faces = [
 ("Archivo", 600, "@fontsource/archivo/files/archivo-latin-600-normal.woff2"),
 ("Archivo", 700, "@fontsource/archivo/files/archivo-latin-700-normal.woff2"),
 ("Archivo", 800, "@fontsource/archivo/files/archivo-latin-800-normal.woff2"),
 ("Inter", 400, "@fontsource/inter/files/inter-latin-400-normal.woff2"),
 ("Inter", 500, "@fontsource/inter/files/inter-latin-500-normal.woff2"),
 ("Inter", 600, "@fontsource/inter/files/inter-latin-600-normal.woff2"),
]
fontcss = []
for fam, w, rel in faces:
    d = base64.b64encode((root/'node_modules'/rel).read_bytes()).decode()
    fontcss.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(data:font/woff2;base64,{d}) format('woff2');}}")

# ------------------------------------------------------------
# TEMPLATE COM FONTES E LOGOTIPOS EMBUTIDOS
# ------------------------------------------------------------
logo_b64 = base64.b64encode((root/'logo-escolinha-batista.png').read_bytes()).decode()
base = (root/'template.html').read_text(encoding='utf-8').replace('/*FONTS*/', "\n".join(fontcss))
base = base.replace('LOGO_SRC', 'data:image/png;base64,' + logo_b64)

# assinatura de colaboracao: logos oficiais adaptados para fundo escuro
for chave, arq in (('CREATIVE_SRC','logo-creative-branco.png'), ('IAIEU_SRC','logo-iaieu-branco.png')):
    b = base64.b64encode((root/arq).read_bytes()).decode()
    base = base.replace(chave, 'data:image/png;base64,' + b)

# ------------------------------------------------------------
# BLOCOS COMPARTILHADOS, TIRADOS DO PROPRIO TEMPLATE
# ------------------------------------------------------------
def bloco(txt, ini, fim, inclusive=True):
    a = txt.index(ini)
    b = txt.index(fim, a) + (len(fim) if inclusive else 0)
    return txt[a:b]

estilo_base = bloco(base, '<style>', '</style>')[len('<style>'):-len('</style>')]
cabecalho   = bloco(base, '<header class="topo"', '</header>')
gaveta      = bloco(base, '<div class="gaveta"', '</div>\n\n<main>', inclusive=False) + '</div>'
rodape      = bloco(base, '<footer class="pe">', '</footer>')
script      = bloco(base, '<script>\n(function(){\n  var topo', '</script>')

# fora da home os ancoras precisam voltar para a raiz
def raiz(t): return t.replace('href="#', 'href="/#')

# ------------------------------------------------------------
# TROCA DE PLACEHOLDER POR CONTEUDO
# ------------------------------------------------------------
PH = re.compile(r'<div class="ph[^"]*">.*?</div>', re.S)

def troca(html, slot, novo_html):
    m = re.search(r'data-slot="%s"' % slot, html)
    if not m: raise SystemExit("slot ausente: " + slot)
    t = html[m.end():]; m2 = PH.search(t)
    if not m2: raise SystemExit("placeholder ausente: " + slot)
    return html[:m.end()+m2.start()] + novo_html + html[m.end()+m2.end():]
