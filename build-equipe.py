# ============================================================
# BUILD DA PAGINA DA EQUIPE
#
# Gera equipe/index.html a partir de:
#   template-equipe.html       o desenho da pagina
#   fotos/equipe/equipe.json   nome, cargo e grupo de cada pessoa
#   fotos/equipe/*.jpg         os retratos, prontos por build-retratos.py
#   comum.py                   CSS, cabecalho, menu e rodape do site
#
# Os retratos entram embutidos em base64, como o resto do site.
# Nenhum arquivo externo.
#
# A pasta fotos/ nao vive no repositorio publico, entao esta pagina
# so pode ser gerada aqui, com as fotos em maos. E de proposito.
#
# Rodar: python3 build-equipe.py
# ============================================================
from comum import root, estilo_base, cabecalho, gaveta, rodape, script, raiz

import base64, json, html as _html

def _esc(s): return _html.escape(str(s), quote=True)

pasta = root / 'fotos' / 'equipe'
indice = pasta / 'equipe.json'
if not indice.exists():
    raise SystemExit('fotos/equipe/equipe.json nao existe. Rode build-retratos.py antes.')

# a ordem dos grupos e a ordem em que aparecem no equipe.json,
# que e a ordem definida pelo cliente. nada e reordenado aqui.
pessoas = json.loads(indice.read_text(encoding='utf-8'))

# Uma linha de texto embaixo dos retratos de um grupo, quando o grupo
# precisa dizer algo que nao cabe num retrato. Hoje existe uma so.
#
# William e Rodrigo tem retrato apenas na Administracao. No corpo
# tecnico eles entram por texto, sem foto. E deliberado: ninguem
# aparece duas vezes com retrato.
NOTAS = {
    'Corpo técnico': 'William Maia da Silva e Rodrigo Godoy também integram a comissão técnica.',
}

grupos = []
for grupo, nome, cargo, base, _fator, _ratio in pessoas:
    arq = pasta / (base + '.jpg')
    if not arq.exists():
        raise SystemExit(f'retrato ausente: {arq.name}. Rode build-retratos.py antes.')
    if not grupos or grupos[-1][0] != grupo:
        grupos.append((grupo, []))
    grupos[-1][1].append((nome, cargo, arq))

def monta():
    saida, peso = [], 0
    for grupo, gente in grupos:
        cartoes = []
        for nome, cargo, arq in gente:
            b = arq.read_bytes(); peso += len(b)
            cartoes.append(
                '<div class="eq-pessoa">'
                f'<img src="data:image/jpeg;base64,{base64.b64encode(b).decode()}" '
                f'alt="{_esc(nome)}" '
                'width="300" height="375" loading="lazy" decoding="async">'
                f'<h3 class="eq-pessoa__n">{_esc(nome)}</h3>'
                f'<p class="eq-pessoa__c">{_esc(cargo)}</p>'
                '</div>'
            )
        # grupo de quatro respira melhor em duas linhas de dois
        classe = 'eq-pessoas eq-pessoas--duplas' if len(gente) == 4 else 'eq-pessoas'
        nota = NOTAS.get(grupo)
        saida.append(
            '<div class="eq-grupo">'
            f'<h2 class="eq-grupo__t">{_esc(grupo)}</h2>'
            f'<div class="{classe}">{"".join(cartoes)}</div>'
            + (f'<p class="eq-grupo__nota">{_esc(nota)}</p>' if nota else '')
            + '</div>'
        )
    return '\n'.join(saida), peso

corpo, peso_fotos = monta()

eq = (root / 'template-equipe.html').read_text(encoding='utf-8')
eq = eq.replace('/*ESTILO_BASE*/', estilo_base)
eq = eq.replace('<!--CABECALHO-->', raiz(cabecalho))
eq = eq.replace('<!--GAVETA-->', raiz(gaveta))
eq = eq.replace('<!--RODAPE-->', raiz(rodape))
eq = eq.replace('<!--SCRIPT-->', script)
eq = eq.replace('<!--GRUPOS-->', corpo)

destino = root / 'equipe'
destino.mkdir(exist_ok=True)
(destino / 'index.html').write_text(eq, encoding='utf-8')

print('---')
print(f'equipe/index.html  {(destino/"index.html").stat().st_size//1024} KB')
for grupo, gente in grupos:
    print(f'  {grupo:18s} {len(gente)} pessoas')
print(f'  {sum(len(g) for _, g in grupos)} retratos, {peso_fotos//1024} KB de foto')
