import base64, io, re, sys, pathlib
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

root = pathlib.Path('.')

# ============================================================
# FONTES
# ============================================================
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
 "gal1":     ("f15.jpg", 4/5,  1000, 0.24, 0.50, "Disputa de bola entre dois atletas durante partida de futebol de base", 74),
 "gal2":     ("f05.jpg", 3/2,   900, 0.30, 0.50, "Atleta da Escolinha conduzindo a bola em campo aberto", 74),
 "gal3":     ("f24.jpg", 3/2,   950, 0.50, 0.50, "Equipes perfiladas no campo antes do início da partida", 74),
 "gal4":     ("f14.jpg", 3/2,   900, 0.30, 0.50, "Atleta da Escolinha dominando a bola durante o jogo", 74),
 "gal5":     ("f22.jpg", 3/2,   900, 0.28, 0.50, "Atleta da Escolinha com o troféu recebido em competição", 74),
 "gal6":     ("f11.jpg", 3/2,   900, 0.42, 0.50, "Professor da Escolinha no campo antes da atividade", 74),
}

PH = re.compile(r'<div class="ph[^"]*">.*?</div>', re.S)

def troca(html, slot, novo_html):
    m = re.search(r'data-slot="%s"' % slot, html)
    if not m: raise SystemExit("slot ausente: " + slot)
    t = html[m.end():]; m2 = PH.search(t)
    if not m2: raise SystemExit("placeholder ausente: " + slot)
    return html[:m.end()+m2.start()] + novo_html + html[m.end()+m2.end():]

logo_b64 = base64.b64encode((root/'logo-escolinha-batista.png').read_bytes()).decode()
base = (root/'template.html').read_text(encoding='utf-8').replace('/*FONTS*/', "\n".join(fontcss))
base = base.replace('LOGO_SRC', 'data:image/png;base64,' + logo_b64)
print('logo oficial embutido:', len(logo_b64)*3//4//1024, 'KB por instancia')

# assinatura de colaboracao: logos oficiais adaptados para fundo escuro
for chave, arq in (('CREATIVE_SRC','logo-creative-branco.png'), ('IAIEU_SRC','logo-iaieu-branco.png')):
    b = base64.b64encode((root/arq).read_bytes()).decode()
    base = base.replace(chave, 'data:image/png;base64,' + b)
    print(f'{chave}: {arq}  {len(b)*3//4//1024} KB')

comuns = {}
for slot, (arq, ratio, larg, fy, fx, alt, q) in FOTOS.items():
    data, size = recorta(arq, ratio, larg, fy, fx, q)
    b64 = base64.b64encode(data).decode()
    comuns[slot] = (f'<img src="data:image/jpeg;base64,{b64}" alt="{alt}" '
                    f'width="{size[0]}" height="{size[1]}" decoding="async">', len(data), arq, size)

html = base
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
# arquivo unico de producao. o nome index.html e o que a hospedagem serve na raiz.
# nao existe segunda copia: nada para esquecer de sincronizar.
out = root/'index.html'
out.write_text(html, encoding='utf-8')
print(f'HERO: desktop {hs[0]}x{hs[1]} {len(hd)//1024} KB | mobile {ms[0]}x{ms[1]} {len(hm)//1024} KB')
print(f'arquivo oficial: {out.name}  {out.stat().st_size//1024} KB')
print('---')
for slot, (tag, n, arq, size) in comuns.items():
    print(f'  {slot:9s} {arq}  {size[0]}x{size[1]}  {n//1024} KB')

# ============================================================
# PAGINA DE DOACAO  ->  doacao/index.html
# reaproveita o mesmo CSS, cabecalho, menu e rodape do site,
# extraidos do proprio template ja processado. nada e duplicado.
# ============================================================
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

qr_bytes = (root/'qr-pix-oficial.png').read_bytes()
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
print(f'  qr       qr-pix-oficial.png  {qr_img.size[0]}x{qr_img.size[1]}  {len(qr_bytes)//1024} KB')
