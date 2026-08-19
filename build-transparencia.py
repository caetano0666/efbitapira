# ============================================================
# BUILD DA PAGINA DE TRANSPARENCIA
#
# Gera transparencia/index.html a partir de:
#   template-transparencia.html      o desenho da pagina
#   transparencia/documentos.json    a lista de documentos
#   comum.py                         CSS, cabecalho, menu e rodape do site
#
# NAO usa a pasta fotos/. E isso que permite que o painel
# administrativo regenere a pagina sozinho, num servidor,
# sem que as fotografias das criancas saiam daqui.
#
# Rodar: python3 build-transparencia.py
# ============================================================
from comum import root, estilo_base, cabecalho, gaveta, rodape, script, raiz

import json, html as _html

def _esc(s): return _html.escape(str(s), quote=True)

def _peso(caminho):
    f = root / caminho.lstrip('/')
    if not f.exists(): return None
    b = f.stat().st_size
    return f'{b/1048576:.1f} MB' if b >= 1048576 else f'{max(1, b//1024)} KB'

def monta_periodos(dados):
    saida = []
    for per in dados.get('periodos', []):
        ano = _esc(per.get('ano', ''))
        titulo = _esc(per.get('titulo', '') or f'Exercício de {ano}')
        docs = [d for d in per.get('documentos', []) if d.get('publicado')]
        docs.sort(key=lambda d: d.get('ordem', 0))

        if docs:
            linhas = []
            for d in docs:
                arq = d.get('arquivo', '')
                meta = [m for m in (_esc(d.get('descricao', '')), _peso(arq)) if m]
                linhas.append(
                    '<li class="tr-doc"><a href="%s" target="_blank" rel="noopener">'
                    '<span class="tr-doc__txt">'
                    '<span class="tr-doc__nome">%s</span>'
                    '<span class="tr-doc__meta">%s</span>'
                    '</span>'
                    '<span class="tr-doc__ir">Abrir PDF'
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                    '<path d="M5 12h14M13 6l6 6-6 6"/></svg></span></a></li>'
                    % (_esc(arq), _esc(d.get('titulo', 'Documento')), ' &middot; '.join(meta))
                )
            corpo = '<ul class="tr-docs">%s</ul>' % ''.join(linhas)
        else:
            titulo_e = _esc(per.get('espera_titulo', 'Demonstrativo em preparação.'))
            texto_e = _esc(per.get('espera_texto',
                'Será publicado aqui quando o fechamento do período for concluído pela Escolinha.'))
            marcos = per.get('marcos', [])
            lis = ''.join(
                '<li class="tr-marco%s"><span class="tr-marco__q">%s</span>'
                '<p class="tr-marco__o">%s</p></li>'
                % (' tr-marco--vivo' if mk.get('vivo') else '',
                   _esc(mk.get('quando', '')), _esc(mk.get('o_que', '')))
                for mk in marcos
            )
            lista = '<ul class="tr-marcos">%s</ul>' % lis if lis else ''
            corpo = ('<div class="tr-espera">'
                     '<p class="tr-espera__tag">Em preparação</p>'
                     '<p class="tr-espera__t">%s</p>'
                     '<p class="tr-espera__p">%s</p>%s</div>'
                     % (titulo_e, texto_e, lista))

        saida.append(
            '<div class="tr-ano">'
            '<div class="tr-ano__marca"><span class="tr-ano__n">%s</span>'
            '<p class="tr-ano__t">%s</p></div>'
            '<div>%s</div></div>' % (ano, titulo, corpo)
        )
    return '\n'.join(saida)

pasta_tr = root / 'transparencia'
pasta_tr.mkdir(exist_ok=True)
indice = pasta_tr / 'documentos.json'
dados = json.loads(indice.read_text(encoding='utf-8')) if indice.exists() else {'periodos': []}

tr = (root / 'template-transparencia.html').read_text(encoding='utf-8')
tr = tr.replace('/*ESTILO_BASE*/', estilo_base)
tr = tr.replace('<!--CABECALHO-->', raiz(cabecalho))
tr = tr.replace('<!--GAVETA-->', raiz(gaveta))
tr = tr.replace('<!--RODAPE-->', raiz(rodape))
tr = tr.replace('<!--SCRIPT-->', script)
tr = tr.replace('<!--PERIODOS-->', monta_periodos(dados))
(pasta_tr / 'index.html').write_text(tr, encoding='utf-8')

_pub = sum(len([d for d in per.get('documentos', []) if d.get('publicado')])
           for per in dados.get('periodos', []))
print('---')
print(f'transparencia/index.html  {(pasta_tr/"index.html").stat().st_size//1024} KB')
print(f'  periodos {len(dados.get("periodos", []))}  |  documentos publicados {_pub}')
