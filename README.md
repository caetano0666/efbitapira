# Site da Escolinha de Futebol Batista de Itapira

Site institucional publicado em **efbitapira.org**.

## Como o site é feito

O site é um único arquivo HTML autocontido: fontes, logotipos e fotografias
ficam embutidos dentro do próprio arquivo. Não há servidor, banco de dados,
plataforma fechada nem painel administrativo. Qualquer profissional com
conhecimento de HTML e CSS consegue mantê-lo.

- `template.html` — arquivo fonte. É aqui que se edita conteúdo e design.
- `build-home.py` — gera o site a partir do template, das fotos e dos logotipos.
- `index.html` — o site pronto, gerado pelo build. É o único arquivo publicado.

**Nunca edite `index.html` diretamente.** Ele é gerado e qualquer alteração
feita nele se perde na próxima build. Existe um único arquivo de saída, de
propósito: não há segunda cópia para esquecer de sincronizar.

Até 17/08/2026 o build gerava `escolinha-batista-home.html` e uma cópia manual
virava `index.html`. As duas eram idênticas, e manter isso dependia de disciplina.
A saída foi unificada.

## A pasta `fotos/` não está neste repositório

As fotografias originais são de crianças e adolescentes. Por decisão de
17/08/2026, elas não ficam expostas publicamente. A pasta `fotos/` está no
`.gitignore` e foi removida também do histórico deste repositório.

As 10 fotografias que aparecem no site continuam dentro do `index.html`,
embutidas. **O site publicado não depende da pasta `fotos/`.**

O que depende dela é a reconstrução. Sem a pasta `fotos/` no lugar, o
`build-home.py` não roda até o fim.

**Para reconstruir o site é obrigatório ter a pasta `fotos/`**, com os
arquivos `f01.jpg` a `f25.jpg`, na raiz do projeto, ao lado do
`build-home.py`. Ela é entregue em separado, por canal privado, a quem for
assumir a manutenção. Quem precisar dela deve pedir ao responsável pelo
projeto.

Sem as fotos ainda é possível editar texto, cor, tipografia, estrutura e
layout no `template.html`. Só não é possível gerar o `index.html` final.

## Como reconstruir o site

Requer Python 3 com a biblioteca Pillow, Node.js para baixar as fontes, e a
pasta `fotos/` no lugar.

```
npm install @fontsource/archivo @fontsource/inter
python3 build-home.py
```

## Painel da Transparência: risco residual conhecido

A página de Transparência é editada por um painel administrativo, o Pages CMS,
que grava direto neste repositório. O painel só expõe a lista de documentos e a
pasta de PDFs, e a restrição é verificada no servidor, não apenas na tela.

Existe um risco residual conhecido, aceito por decisão do responsável pelo
projeto em 19/08/2026: a validação de caminho do Pages CMS compara o início do
caminho, sem marcar a fronteira da pasta. Na prática, quem tem acesso ao painel
pode criar arquivos, restritos à extensão configurada, em uma pasta vizinha cujo
nome comece igual ao da pasta autorizada.

O que esse risco NAO alcança, verificado no código do Pages CMS:
home, página de doação, QR do PIX, arquivos de código, template, automação do
GitHub Actions e o próprio .pages.yml. Todos esses são recusados pelo servidor
antes de qualquer escrita.

A falha foi reportada ao projeto Pages CMS pelo canal privado de vulnerabilidade.
Enquanto não houver correção do fornecedor, a conduta é: conferir de tempos em
tempos se surgiu pasta inesperada perto de transparencia/arquivos.

## Publicação

Hospedado no GitHub Pages, a partir da branch `main`, pasta raiz.
O domínio efbitapira.org é registrado e pertence à Escolinha.

---

Desenvolvimento: Creative Marketing Digital + IAieu.
