# ============================================================
# RETRATOS DA EQUIPE
#
# Le as fotos originais de _entrada/equipe e escreve os retratos
# prontos em fotos/equipe. As duas pastas ficam fora do git.
#
# Rodar: python3 build-retratos.py
#
# Regra do cliente, 29/08/2026:
#   - nenhum pixel do rosto e inventado. Sem mascara de nitidez, sem
#     realce local, sem retoque, sem correcao tonal. So corte,
#     reamostragem Lanczos e conversao para cinza.
#   - enquadramento por CABECA, nao por olhos, para nunca cortar o topo.
#   - mesma proporcao de rosto para todos, ate onde a foto de origem deixa.
import os, json
from PIL import Image, ImageOps, ImageEnhance

RAIZ = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(RAIZ, "_entrada", "equipe")     # fotos originais, fora do git
SAI  = os.path.join(RAIZ, "fotos", "equipe")        # retratos prontos, fora do git
LARG, ALT = 300, 375          # 4 por 5
ROSTO_ALVO = 0.42             # largura do rosto sobre a largura do quadro
ROSTO_POR_FOTO = {            # excecoes ditadas pela foto de origem
 # professores: rosto mais fechado, para os tres ficarem iguais entre si e
 # para aproximar o Bruno do centro. Na foto dele a cabeca encosta na borda
 # esquerda, entao so fechando o quadro ele sai do canto.
 "prof-ed-fisica-bruno-brevis.jpeg": 0.55,
 "prof-ed-fisica-michel-cabral-SEM-FILHO.jpeg": 0.55,
 "prof-ed-fisica-viniciau-pelizar.jpeg": 0.55,
}
# correcao tonal global, sem retoque local, so onde a foto original esta lavada
TOM = {}   # nenhuma foto recebe correcao tonal. decisao do cliente em 29/08
FOLGA_TOPO = 0.10             # espaco acima do cabelo, em fracao da altura

# rosto medido a mao em cada foto: (x, y, largura, altura) do rosto,
# do inicio do cabelo ate o queixo quando indicado.
ROSTOS = {
 "equip-adm-presidente-william-maia.jpeg":          (547,  95, 152, 152),   # conferido com caixa desenhada sobre a foto
 "equip-adm-vp-rodrigo-godoy.jpeg":                 (235, 310,  65,  85),
 "equip-adm-secretaria-eliane-godoy.jpeg":          (396, 403, 538, 538),
 "equip-adm-tesoureiro-Andre-olo.jpeg":             (400, 620, 240, 300),
 "equip-adm-conselho-fiscal-claudenir-machado.jpeg":(372, 574, 479, 479),
 "equip-adm-conselho-fiscal-PAtricia-maia.jpeg":    (155, 335, 400, 480),
 "comissao-tecnica-rodrigo-godoi.jpeg":             (100,  90, 100, 110),
 "comissao-tecnica-prof-helio.jpeg":                (405, 225,  70,  90),
 "Juridico-oab-Daniela-mesquita.jpeg":              (155, 150, 365, 365),
 "juridico-oab-GAbriela-Albano.jpeg":               (250,  55, 100, 120),
 "prof-ed-fisica-bruno-brevis.jpeg":                ( 29, 143, 325, 325),
 "prof-ed-fisica-michel-cabral-SEM-FILHO.jpeg":     (341,  84, 129, 129),   # foto composta, o filho saiu do fundo
 "prof-ed-fisica-viniciau-pelizar.jpeg":            (219, 287, 442, 442),
 # Departamento Medico, 09/09/2026. As tres primeiras medidas a mao e
 # conferidas na imagem. A do Dr. Mauro veio da deteccao Haar: das tres
 # caixas encontradas, a de 311px e o rosto; as outras duas caem num movel
 # desfocado ao fundo e no colarinho.
 "Dr_Mauro_Xavier_De_Sousa_Filho_3.jpg":            (525, 165, 311, 311),
 "Dra_Caroline_Prado_De_Souza_Xavier.jpeg":         (168, 129, 202, 202),
 "Carolina_Bizon_Bressaglia.jpeg":                  (428, 187, 240, 240),
 "Paola Maia.jpeg":                                 (386, 179, 260, 260),
}
# faixa util, para fotos com tarja preta ou vizinho no quadro
UTIL = {
 "equip-adm-tesoureiro-Andre-olo.jpeg":  {"y0":190, "y1":1400},
}
PESSOAS = [
 ("Administração","equip-adm-presidente-william-maia.jpeg","William Maia da Silva","Presidente"),
 ("Administração","comissao-tecnica-rodrigo-godoi.jpeg","Rodrigo Godoy","Vice-presidente"),
 ("Administração","equip-adm-secretaria-eliane-godoy.jpeg","Eliane Godoy","Secretária"),
 ("Administração","equip-adm-tesoureiro-Andre-olo.jpeg","André Olo","Tesoureiro"),
 ("Conselho fiscal","equip-adm-conselho-fiscal-claudenir-machado.jpeg","Claudenir Machado","Conselho fiscal"),
 ("Conselho fiscal","equip-adm-conselho-fiscal-PAtricia-maia.jpeg","Patrícia Maia","Conselho fiscal"),
 ("Corpo técnico","comissao-tecnica-prof-helio.jpeg","Professor Hélio","Comissão técnica"),
 ("Corpo jurídico","Juridico-oab-Daniela-mesquita.jpeg","Daniela Mesquita","Jurídico"),
 ("Corpo jurídico","juridico-oab-GAbriela-Albano.jpeg","Gabriela Albano","Jurídico"),
 ("Professores","prof-ed-fisica-bruno-brevis.jpeg","Bruno Brevis","Educação física"),
 ("Professores","prof-ed-fisica-michel-cabral-SEM-FILHO.jpeg","Michel Cabral","Educação física"),
 ("Professores","prof-ed-fisica-viniciau-pelizar.jpeg","Vinicius Pelizar","Educação física"),
 ("Departamento Médico","Dr_Mauro_Xavier_De_Sousa_Filho_3.jpg","Dr. Mauro Xavier de Sousa Filho","Generalista"),
 ("Departamento Médico","Dra_Caroline_Prado_De_Souza_Xavier.jpeg","Dra. Caroline Prado de Souza Xavier","Ortopedista e Traumatologista"),
 ("Departamento Médico","Carolina_Bizon_Bressaglia.jpeg","Carolina Bizon Bressaglia","Psicóloga"),
 ("Departamento Médico","Paola Maia.jpeg","Paola Maia","Estagiária de Psicologia"),
]

def corta(arq):
    im = ImageOps.exif_transpose(Image.open(os.path.join(ORIG,arq))).convert("RGB")
    u = UTIL.get(arq, {})
    x0,y0 = u.get("x0",0), u.get("y0",0)
    x1,y1 = u.get("x1",im.width), u.get("y1",im.height)
    fx,fy,fw,fh = ROSTOS[arq]
    topo_cabelo = fy - 0.45*fh
    cx = fx + fw/2

    largura = fw/ROSTO_POR_FOTO.get(arq, ROSTO_ALVO)
    largura = min(largura, x1-x0, (y1-y0)/1.25)     # nao pode passar da foto
    altura  = largura*1.25
    esq = cx - largura/2
    top = topo_cabelo - FOLGA_TOPO*altura
    esq = max(x0, min(esq, x1-largura))
    top = max(y0, min(top, y1-altura))
    rec = im.crop((round(esq),round(top),round(esq+largura),round(top+altura)))
    rec = rec.resize((LARG,ALT), Image.LANCZOS)
    if TOM.get(arq):
        rec = ImageEnhance.Contrast(ImageOps.autocontrast(rec, cutoff=2)).enhance(1.10)
    return rec, LARG/largura, fw/largura

def sem_ext(nome):
    # o Dr. Mauro chegou com extensao .jpg e conteudo PNG. a Pillow abre
    # pelo conteudo, mas o nome de saida precisa aceitar as tres formas.
    for e in (".jpeg", ".jpg", ".png"):
        if nome.lower().endswith(e):
            return nome[:-len(e)]
    return nome

def pb(im):
    return ImageEnhance.Contrast(ImageOps.grayscale(im).convert("RGB")).enhance(1.03)

if __name__ == "__main__":
    os.makedirs(SAI, exist_ok=True)
    rel=[]
    for g,arq,nome,cargo in PESSOAS:
        im, fator, ratio = corta(arq)
        b = g[:4].lower()+"-"+sem_ext(arq)
        pb(im).save(os.path.join(SAI, b+".jpg"), quality=88, optimize=True)
        rel.append((g,nome,cargo,b,round(fator,2),round(ratio,2)))
        marca = "amplia" if fator>1.05 else "reduz "
        print(f"{nome:24s} {marca} {fator:4.2f}x   rosto ocupa {ratio*100:4.1f}% do quadro")
    json.dump(rel, open(os.path.join(SAI,"equipe.json"),"w"), ensure_ascii=False, indent=1)
    print(f"\n{len(rel)} retratos em fotos/equipe")
