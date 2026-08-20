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

**Linha de base vigente desde 20 de agosto de 2026.**

O site é hospedado na **KingHost**, no servidor `191.6.209.227`, e responde em
**https://efbitapira.org**. O domínio é registrado na GoDaddy e pertence à
Escolinha, mas o **DNS é administrado pela KingHost**, pelos nameservers
dns1 a dns6.kinghost.com.br.

Certificado Let's Encrypt ativo, válido para `efbitapira.org` e
`*.efbitapira.org`, com renovação automática pela KingHost.

Um arquivo `.htaccess` na raiz do site cuida de duas coisas, e só delas:
todo acesso em HTTP é redirecionado com 301 para HTTPS, e todo acesso pelo
`www` é redirecionado com 301 para o domínio sem www. Caminho e query string
são preservados, num único salto.

Estrutura publicada: `/`, `/doacao/` e `/transparencia/`.

### O GitHub NAO e mais a hospedagem

Ate 20/08/2026 o site era publicado pelo GitHub Pages. **Deixou de ser.**

Este repositorio continua sendo a fonte do projeto: o template, o gerador, as
fotografias, os logotipos e o painel da Transparencia vivem aqui, e o historico
inteiro esta preservado. Mas o que o visitante enxerga vem da KingHost.

Depois de gerar uma versao nova com `build-home.py`, e preciso **enviar os
arquivos para a KingHost por FTP**. Publicar so no GitHub nao muda o site no ar.

Nao apague este repositorio, nao apague o historico e nao reative o GitHub Pages
como producao.

---

Desenvolvimento: Creative Marketing Digital + IAieu.

## Decisão definitiva: o GitHub Pages foi desativado

20 de agosto de 2026, por decisão de Caetano Zammataro.

| | |
|---|---|
| KingHost | **única hospedagem de produção** |
| GitHub | repositório, histórico e base de automação |
| GitHub Pages | **desativado neste repositório** |

O GitHub Pages continuava ligado depois da migração e reconstruía o site a cada
push, reivindicando o domínio `efbitapira.org` dentro do GitHub. Era uma segunda
hospedagem que ninguém usava e que ninguém conseguia acessar. Foi desligado.

O que **não** mudou: o repositório, o histórico, os arquivos, o workflow da
Transparência, o painel do Pages CMS, o DNS, o SSL, o `.htaccess` e o site no ar.
O Pages CMS nunca dependeu do GitHub Pages. São coisas diferentes com nomes
parecidos: um é hospedagem do GitHub, o outro é um editor que grava arquivos
neste repositório.

O arquivo `CNAME` foi mantido de propósito. Ele não faz nada com o Pages
desligado. **Se o GitHub Pages for reativado algum dia, esse arquivo faz o GitHub
reivindicar o domínio de novo, sozinho.** Não reative sem saber disso.

## Como enviar para a KingHost

Comprovado em 20 de agosto de 2026, depois de uma publicação que falhou pela metade.

| | |
|---|---|
| host FTP | `ftp.web1137.kinghost.net` |
| usuário | `efbitapira` |
| pasta | o login já entra na raiz pública |

**Não acrescente `/www/` ao caminho.** O host `ftp.efbitapira.org` recusou o envio
da raiz e da pasta `transparencia`.

A KingHost não envia cabeçalho de cache. Para conferir uma publicação, abra o
endereço com `?cache=0` no fim, senão o navegador mostra a versão antiga.
