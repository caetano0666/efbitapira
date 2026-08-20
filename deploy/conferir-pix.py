# ============================================================
# A TRAVA DO PIX
#
# Le o QR de dentro da pagina de doacao ja gerada, decodifica e
# compara o payload inteiro com o arquivo oficial guardado no
# repositorio, que veio do aplicativo do banco da Escolinha.
#
# Um QR redesenhado, estilizado, recomprimido ou com logotipo no
# meio nao passa aqui. E isso e o ponto: se o QR quebrar, a doacao
# nao chega, e ninguem descobre olhando a pagina.
#
# Uso: python3 deploy/conferir-pix.py doacao/index.html deploy/pix-oficial.txt
# ============================================================
import base64
import io
import re
import sys

from PIL import Image

pagina, oficial = sys.argv[1], sys.argv[2]

html = io.open(pagina, encoding='utf-8', errors='replace').read()
m = re.search(r'class="cartao__qr" src="data:image/png;base64,([A-Za-z0-9+/=]+)"', html)
if not m:
    print('  PIX: nao encontrei o QR embutido na pagina')
    sys.exit(1)

img = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB')

try:
    import cv2
    import numpy as np
    achado, _, _ = cv2.QRCodeDetector().detectAndDecode(
        cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
except ImportError:
    from pyzbar.pyzbar import decode
    lidos = decode(img)
    achado = lidos[0].data.decode() if lidos else ''

esperado = io.open(oficial, encoding='utf-8').read().strip()

if not achado:
    print('  PIX: o QR da pagina nao pode ser decodificado')
    sys.exit(1)
if len(achado) != 144:
    print(f'  PIX: o payload tem {len(achado)} caracteres, esperados 144')
    sys.exit(1)
if achado != esperado:
    print('  PIX: o payload MUDOU em relacao ao oficial do banco')
    sys.exit(1)

chave = re.search(r'data-chave="(\d+)"', html)
if not chave or chave.group(1) != '53300905000143':
    print('  PIX: a chave do botao de copiar nao e o CNPJ da Escolinha')
    sys.exit(1)

print(f'  PIX: payload identico ao oficial, {len(achado)} caracteres, chave {chave.group(1)}')
