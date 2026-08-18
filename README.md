# Site da Escolinha de Futebol Batista de Itapira

Site institucional publicado em **efbitapira.org**.

## Como o site é feito

O site é um único arquivo HTML autocontido: fontes, logotipos e fotografias
ficam embutidos dentro do próprio arquivo. Não há servidor, banco de dados,
plataforma fechada nem painel administrativo. Qualquer profissional com
conhecimento de HTML e CSS consegue mantê-lo.

- `template.html` — arquivo fonte. É aqui que se edita conteúdo e design.
- `build-home.py` — gera o site a partir do template, das fotos e dos logotipos.
- `fotos/` — fotografias originais, em alta resolução.
- `escolinha-batista-home.html` — arquivo gerado pelo build.
- `index.html` — cópia exata do gerado, com o nome que a hospedagem exige.

**Nunca edite `escolinha-batista-home.html` ou `index.html` diretamente.**
Eles são gerados e qualquer alteração feita neles se perde na próxima build.

## Como reconstruir o site

Requer Python 3 com a biblioteca Pillow, e Node.js para baixar as fontes.

```
npm install @fontsource/archivo @fontsource/inter
python3 build-home.py
cp escolinha-batista-home.html index.html
```

## Publicação

Hospedado no GitHub Pages, a partir da branch `main`, pasta raiz.
O domínio efbitapira.org é registrado e pertence à Escolinha.

---

Desenvolvimento: Creative Marketing Digital + IAieu.
