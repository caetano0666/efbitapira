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
- `index.html` — o site pronto, gerado pelo build. É o único arquivo publicado.

**Nunca edite `index.html` diretamente.** Ele é gerado e qualquer alteração
feita nele se perde na próxima build. Existe um único arquivo de saída, de
propósito: não há segunda cópia para esquecer de sincronizar.

Até 17/08/2026 o build gerava `escolinha-batista-home.html` e uma cópia manual
virava `index.html`. As duas eram idênticas, e manter isso dependia de disciplina.
A saída foi unificada. As versões antigas continuam no histórico deste repositório.

## Como reconstruir o site

Requer Python 3 com a biblioteca Pillow, e Node.js para baixar as fontes.

```
npm install @fontsource/archivo @fontsource/inter
python3 build-home.py
```

## Publicação

Hospedado no GitHub Pages, a partir da branch `main`, pasta raiz.
O domínio efbitapira.org é registrado e pertence à Escolinha.

---

Desenvolvimento: Creative Marketing Digital + IAieu.
