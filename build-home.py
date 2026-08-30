# ============================================================
# BUILD DA HOME E DA PAGINA DE DOACAO
#
# Gera index.html e doacao/index.html.
# Precisa da pasta fotos/, que nao vive no repositorio publico.
#
# A pagina de Transparencia sai de build-transparencia.py, chamado
# no fim deste arquivo, para que rodar este comando continue
# gerando as tres paginas como sempre.
#
# Rodar: python3 build-home.py
# ============================================================
import base64, io
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from comum import root, base, troca, estilo_base, cabecalho, gaveta, rodape, script, raiz

def abrir(nome):
    return ImageOps.exif_transpose(Image.open(root/'fotos'/nome)).convert("RGB")

def jpg(im, q):
    b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True, progressive=True)
    return b.getvalue()

def recorta(nome, ratio, larg, fy=0.5, fx=0.5, q=74):
    im = abrir(nome); w, h = im.size
    alvo_h = w / ratio
    if alvo_h <= h:
        nh = int(alvo_h); nw = w; top = int((h-nh)*fy); left = 0
    else:
        nw = int(h*ratio); nh = h; left = int((w-nw)*fx); top = 0
    im = im.crop((left, top, left+nw, top+nh))
    if im.size[0] > larg:
        im = im.resize((larg, max(1,int(larg/ratio))), Image.LANCZOS)
    return jpg(im, q), im.size

# ============================================================
# COMPOSICAO DE HERO
# fundo: a propria foto ampliada, desfocada e escurecida
# frente: a foto inteira, sem corte, posicionada pelo ponto focal
# ============================================================
def compoe(nome, W, H, altura_frac, subj, alvo, q=76, desfoque=None, veu=None):
    src = abrir(nome)
    # fundo
    bg = ImageOps.fit(src, (W, H), Image.LANCZOS, centering=(0.5, 0.4))
    bg = bg.filter(ImageFilter.GaussianBlur(desfoque or max(18, W//26)))
    bg = ImageEnhance.Brightness(bg).enhance(0.52)
    bg = ImageEnhance.Color(bg).enhance(0.6)
    # frente
    fh = int(H*altura_frac); fw = int(src.size[0]*fh/src.size[1])
    fg = src.resize((fw, fh), Image.LANCZOS)
    x = int(alvo[0]*W - subj[0]*fw)
    y = int(alvo[1]*H - subj[1]*fh)
    # mascara com bordas suaves
    m = Image.new("L", (fw, fh), 255)
    px = m.load()
    fx_ = max(8, int(fw*0.10)); fy_ = max(8, int(fh*0.07))
    for i in range(fx_):
        v = int(255*i/fx_)
        for j in range(fh):
            px[i, j] = min(px[i, j], v); px[fw-1-i, j] = min(px[fw-1-i, j], v)
    for j in range(fy_):
        v = int(255*j/fy_)
        for i in range(fw):
            px[i, j] = min(px[i, j], v); px[i, fh-1-j] = min(px[i, fh-1-j], v)
    canvas = bg.copy()
    canvas.paste(fg, (x, y), m)
    if veu:
        ini, forca = veu
        escuro = Image.new("RGB", (W, H), (6, 30, 56))
        mk = Image.new("L", (1, H), 0); mp = mk.load()
        for j in range(H):
            t = (j/H - ini) / max(1e-6, (1 - ini))
            mp[0, j] = 0 if t <= 0 else int(255 * forca * (t ** 1.6))
        canvas = Image.composite(escuro, canvas, mk.resize((W, H)))
    return jpg(canvas, q), (W, H)

# ============================================================
# HEROS A e B
# ============================================================
HERO = {
 "desk": dict(nome="f10.jpg", W=1920, H=1080, altura_frac=1.02, subj=(0.46,0.50), alvo=(0.72,0.52)),
 "mob":  dict(nome="f10.jpg", W=1080, H=1620, altura_frac=0.56, subj=(0.46,0.46), alvo=(0.52,0.30), veu=(0.40,0.86)),
 "alt":  "Atleta da Escolinha de Futebol Batista ajoelhado no gramado durante a partida",
}

# ============================================================
# DEMAIS FOTOS, IGUAIS NOS DOIS
# ============================================================
FOTOS = {
 "treino":   ("f13.jpg", 3/2,  1400, 0.50, 0.50, "Equipes da Escolinha reunidas no campo ao entardecer, com as famílias", 72),
 "historia": ("f16.jpg", 4/5,   900, 0.42, 0.50, "Time da Escolinha reunido em roda comemorando com a comissão técnica", 74),
 "trofeu":   ("f03.jpg", 1/1,  1000, 0.52, 0.50, "Equipe da Escolinha de Futebol Batista com o troféu conquistado", 74),
}

# ============================================================
# A GALERIA
#
# Aqui NAO se corta. A funcao so reduz, e a proporcao original
# atravessa intacta ate o HTML: retrato continua retrato, paisagem
# continua paisagem. Na pagina a faixa da a todas a mesma altura e
# deixa a largura variar, entao nenhuma cabeca precisa ser decepada
# para a foto caber numa caixa.
#
# A galeria antiga fazia o oposto. Forcava 3/2 em f05, f14, f22 e
# f11, que sao retratos. A f22 tem 1280 de altura e aparecia com
# 529: 59 por cento da fotografia ficava fora, escolhido por um
# ponto focal chutado.
#
# CAIXA e o lado maior depois da reducao. Serve as duas leituras: a
# miniatura da faixa, com cerca de 320 pixels de altura, e a
# ampliacao, que chega a 86vh. Nao ha duas copias de cada foto
# porque tudo aqui e base64 no proprio HTML: duas copias seriam duas
# vezes o peso, e nao metade.
#
# Acrescentar fotografia e acrescentar uma linha nesta lista.
# Nem o CSS nem o JavaScript da pagina precisam saber.
# ============================================================
GAL_CAIXA, GAL_Q = 1000, 72

def inteira(nome, caixa=GAL_CAIXA, q=GAL_Q):
    im = abrir(nome); w, h = im.size
    e = min(caixa / w, caixa / h, 1.0)
    if e < 1:
        im = im.resize((round(w * e), round(h * e)), Image.LANCZOS)
    return jpg(im, q), im.size

# ordem da faixa. paisagem e retrato alternados para a faixa nao
# ficar aos bloces. os seis primeiros textos vem da galeria antiga,
# preservados; os das fotos novas descrevem so o que se ve nelas.
GALERIA = [
 ("f31.jpg", "Dois atletas de times diferentes disputando a bola em velocidade"),
 ("f15.jpg", "Disputa de bola entre dois atletas durante partida de futebol de base"),
 ("f27.jpg", "Goleiro caído no gramado segurando a bola com as duas mãos"),
 ("f22.jpg", "Atleta da Escolinha com o troféu recebido em competição"),
 ("f28.jpg", "Atleta de uniforme verde dominando a bola com o pé, perto da bandeira de escanteio"),
 ("f05.jpg", "Atleta da Escolinha conduzindo a bola em campo aberto"),
 ("f29.jpg", "Equipe de uniforme azul comemorando com o troféu erguido no campo"),
 ("f14.jpg", "Atleta da Escolinha dominando a bola durante o jogo"),
 ("f24.jpg", "Equipes perfiladas no campo antes do início da partida"),
 ("f26.jpg", "Goleiro de uniforme verde e luvas em pé no gramado"),
 ("f30.jpg", "Atleta com troféu ao lado de dois adultos, diante do painel da Escolinha"),
 ("f11.jpg", "Professor da Escolinha no campo antes da atividade"),
]

comuns = {}
for slot, (arq, ratio, larg, fy, fx, alt, q) in FOTOS.items():
    data, size = recorta(arq, ratio, larg, fy, fx, q)
    b64 = base64.b64encode(data).decode()
    comuns[slot] = (f'<img src="data:image/jpeg;base64,{b64}" alt="{alt}" '
                    f'width="{size[0]}" height="{size[1]}" decoding="async">', len(data), arq, size)

# ------------------------------------------------------------
# CREDENCIAL PESSOAL DO WILLIAM, NA SECAO HISTORIA
# O logotipo entra reduzido a tres vezes o tamanho de exibicao.
# Nao faz sentido carregar 900 pixels de altura para mostrar 32.
# ------------------------------------------------------------
adc = Image.open(root/'logo-atletas-de-cristo.png')
adc_h = 110
adc = adc.resize((round(adc.size[0]*adc_h/adc.size[1]), adc_h), Image.LANCZOS)
_b = io.BytesIO(); adc.save(_b, 'PNG', optimize=True)
adc_bytes = _b.getvalue()

html = base
html = html.replace('ADC_SRC', 'data:image/png;base64,' + base64.b64encode(adc_bytes).decode())
hd, hs = compoe(**HERO["desk"])
hm, ms = compoe(**HERO["mob"])
pic = ('<picture>'
       f'<source media="(max-width:700px)" srcset="data:image/jpeg;base64,{base64.b64encode(hm).decode()}">'
       f'<img src="data:image/jpeg;base64,{base64.b64encode(hd).decode()}" alt="{HERO["alt"]}" '
       f'width="{hs[0]}" height="{hs[1]}" fetchpriority="high" decoding="async">'
       '</picture>')
html = troca(html, "hero", pic)
for slot, (tag, n, arq, size) in comuns.items():
    html = troca(html, slot, tag)

# ---- a faixa da galeria ----
# a primeira nao e lazy: e a unica que ja pode estar na tela quando
# a secao entra. as outras esperam a rolagem.
figuras, peso_gal = [], 0
for k, (arq, alt) in enumerate(GALERIA):
    dados, (gw, gh) = inteira(arq)
    peso_gal += len(dados)
    figuras.append(
        '<figure class="gal__i" role="listitem">'
        f'<button class="gal__b" type="button" aria-label="Ampliar: {alt}">'
        f'<img src="data:image/jpeg;base64,{base64.b64encode(dados).decode()}" '
        f'alt="{alt}" width="{gw}" height="{gh}" '
        f'{"" if k == 0 else "loading=\"lazy\" "}decoding="async">'
        '</button></figure>'
    )
if '<!--GALERIA-->' not in html:
    raise SystemExit('placeholder <!--GALERIA--> ausente no template')
html = html.replace('<!--GALERIA-->', ''.join(figuras))
# arquivo unico de producao. o nome index.html e o que a hospedagem serve na raiz.
# nao existe segunda copia: nada para esquecer de sincronizar.
out = root/'index.html'
out.write_text(html, encoding='utf-8')
print(f'HERO: desktop {hs[0]}x{hs[1]} {len(hd)//1024} KB | mobile {ms[0]}x{ms[1]} {len(hm)//1024} KB')
print(f'arquivo oficial: {out.name}  {out.stat().st_size//1024} KB')
print('---')
for slot, (tag, n, arq, size) in comuns.items():
    print(f'  {slot:9s} {arq}  {size[0]}x{size[1]}  {n//1024} KB')
print(f'  galeria   {len(GALERIA)} fotos, caixa {GAL_CAIXA}px q{GAL_Q}, {peso_gal//1024} KB'
      f' ({peso_gal*4//3//1024} KB ja em base64)')

# ============================================================
# PAGINA DE DOACAO  ->  doacao/index.html
# reaproveita o mesmo CSS, cabecalho, menu e rodape do site,
# extraidos do proprio template ja processado. nada e duplicado.
# ============================================================
qr_bytes = (root/'qr-pix-oficial-2026-08-18.png').read_bytes()
qr_img = Image.open(io.BytesIO(qr_bytes))
qr_b64 = base64.b64encode(qr_bytes).decode()

# f10.jpg e a fotografia original do menino ajoelhado no campo.
# o recorte apenas ajusta o enquadramento ao layout e deixa de fora
# a faixa da direita onde fica a marca do fotografo. a foto nao e alterada.
foto_menino, tam_menino = recorta("f10.jpg", 1.15, 980, 0.50, 0.25, 74)
img_menino = (f'<img src="data:image/jpeg;base64,{base64.b64encode(foto_menino).decode()}" '
              f'alt="Menino da Escolinha de Futebol Batista ajoelhado no gramado durante a partida" '
              f'width="{tam_menino[0]}" height="{tam_menino[1]}" decoding="async">')

doa = (root/'template-doacao.html').read_text(encoding='utf-8')
doa = doa.replace('/*ESTILO_BASE*/', estilo_base)
doa = doa.replace('<!--CABECALHO-->', raiz(cabecalho))
doa = doa.replace('<!--GAVETA-->', raiz(gaveta))
doa = doa.replace('<!--RODAPE-->', raiz(rodape))
doa = doa.replace('<!--SCRIPT-->', script)
doa = doa.replace('QR_SRC', 'data:image/png;base64,' + qr_b64)
doa = doa.replace('QR_W', str(qr_img.size[0])).replace('QR_H', str(qr_img.size[1]))
doa = troca(doa, "menino", img_menino)

destino = root/'doacao'
destino.mkdir(exist_ok=True)
(destino/'index.html').write_text(doa, encoding='utf-8')
print('---')
print(f'doacao/index.html  {(destino/"index.html").stat().st_size//1024} KB')
print(f'  foto     f10.jpg  {tam_menino[0]}x{tam_menino[1]}  {len(foto_menino)//1024} KB')
print(f'  qr       qr-pix-oficial-2026-08-18.png  {qr_img.size[0]}x{qr_img.size[1]}  {len(qr_bytes)//1024} KB')

# ============================================================
# a pagina de Transparencia sai do seu proprio arquivo, que nao
# depende das fotos. rodar build-home.py continua gerando as tres.
# ============================================================
import runpy
runpy.run_path(str(root / 'build-transparencia.py'), run_name='__main__')
