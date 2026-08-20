# Publicacao automatica na KingHost

Este diretorio leva os arquivos ja gerados ate o site no ar, sem depender do
computador de ninguem.

**Hoje ele esta desligado.** O arquivo `TRAVA` diz `BLOQUEADO`, e enquanto disser
isso o processo roda, confere tudo e para antes de tocar na producao.

## Como o envio funciona

| | |
|---|---|
| protocolo | FTP, porta 21 |
| host | `ftp.web1137.kinghost.net` |
| usuario | `efbitapira01`, exclusivo de deploy, vem de Secret |
| senha | vem de Secret, nunca aparece no log |
| pasta | o usuario cai direto na raiz publica. **Nao se acrescenta `/www`** |

O usuario e restrito a `/www` e nao alcanca `/home/efbitapira`, que fica acima da
area autorizada. Isso foi testado.

## O que ele publica, e o que nao publica

Publica os caminhos fixos de `lista-de-envio.txt`:

```
index.html
doacao/index.html
transparencia/index.html
```

mais **os PDFs que existirem em `transparencia/arquivos/`**. Os PDFs entram por
varredura porque quem publica pela web nao edita arquivo nenhum do repositorio:
manda o documento pelo painel e ele aparece ali. A varredura e restrita a essa
pasta e so aceita `.pdf`. Nada mais entra por descoberta automatica.

Envia um por um. **Nunca espelha, nunca sincroniza pasta, nunca usa `--delete`.**
Espelhar destruiria o `.htaccess`, que so existe no servidor, e publicaria o
`template.html`, os scripts em Python, o `.pages.yml` e o PNG original do QR do
PIX, que hoje respondem 404 e devem continuar assim.

**Nao gera a home nem a pagina de doacao.** Essas dependem da pasta `fotos/`, que
nao vive no repositorio publico, por decisao de nao expor fotografias de
criancas. Alterar texto ou desenho dessas paginas continua exigindo o computador
com as fotos. O que este processo faz e enviar o que ja foi gerado e versionado.

A pagina de Transparencia e a excecao: ela e gerada no proprio GitHub, sem fotos,
pelo workflow `Publicar Transparencia`, e chega aqui logo depois.

## As travas

| # | trava | onde |
|---|---|---|
| 1 | `deploy/TRAVA` precisa dizer `LIBERADO` | arquivo neste diretorio |
| 2 | no acionamento manual, e preciso digitar `PUBLICAR` | campo do formulario |
| 3 | o environment `producao` pode exigir aprovacao humana | GitHub, Settings |
| 4 | a validacao local reprova, nada e enviado | `validar.sh` |
| 5 | `permissions: contents: read` | o workflow nao escreve no repositorio |

O `.htaccess` nao esta na lista de envio e nunca e apagado. Alem disso, `validar.sh`
reprova a publicacao se alguem colocar `.htaccess`, `template*.html`, `*.py`,
`.pages.yml`, `CNAME`, os logos ou o PNG do QR na lista.

## A trava do PIX

`conferir-pix.py` decodifica o QR de dentro da pagina, compara o payload inteiro
com `pix-oficial.txt`, que veio do aplicativo do banco da Escolinha, e confere a
chave do botao de copiar.

Um QR redesenhado, estilizado, recomprimido ou com logotipo no meio nao passa.
Esse cuidado existe porque um QR quebrado nao aparece na tela: a pagina continua
bonita, e a doacao simplesmente nao chega.

Roda duas vezes: antes de enviar e depois, no arquivo que esta no ar.

## Tirar um documento do ar

Sao dois passos, e eles sao diferentes.

**1. Despublicar na pagina.** E o normal, e se faz pelo painel: desmarque
"Publicado no site". O documento some da lista de Transparencia. **O arquivo
continua no servidor**, e quem tiver guardado o endereco direto do PDF ainda
consegue abrir.

**2. Tirar o arquivo do servidor.** Escreva o caminho do PDF em `remover.txt`, um
por linha. A proxima publicacao apaga o arquivo do ar, e a conferencia confirma
que ele passou a responder 404. Depois, apague a linha.

Se o documento tinha informacao que nao podia ter sido publicada, o passo 1 nao
basta. Precisa dos dois.

Apagar em producao e a unica operacao destrutiva que esta automacao consegue
fazer. Ela fica presa a uma pasta e a uma extensao: `validar.sh` reprova qualquer
alvo que nao seja um `.pdf` direto em `transparencia/arquivos/`. E so apaga o que
estiver escrito a mao. Nunca deduz.

## Como restaurar uma versao anterior

Os tres HTML finais sao versionados. Rollback nao precisa gerar nada:

```
GitHub -> Actions -> Publicar na KingHost -> Run workflow
  commit:     o hash da versao boa
  confirmar:  PUBLICAR
```

Falha objetiva antes do envio aborta sozinha e a producao nem e tocada. Falha de
julgamento, como texto errado ou documento indevido, e decisao humana: nenhuma
maquina sabe se o conteudo esta certo.

## O que falta para ligar

**1. A Politica de IPs do FTP na KingHost.** E o unico bloqueio externo que
sobrou. Esta em *Liberar acesso nacional*, e os servidores do GitHub Actions ficam
fora do Brasil. Sem resolver isso, a conexao nem abre. E o proximo ajuste.

**2. Criar os Secrets** `KH_FTP_HOST`, `KH_FTP_USER` e `KH_FTP_PASS`. A senha vai
direto do painel da KingHost para o campo do Secret, por copiar e colar, sem
passar por Terminal, chat ou arquivo.

**3. Trocar `TRAVA` de `BLOQUEADO` para `LIBERADO`**, em commit proprio, para
ficar registrado quem ligou e quando.

Enquanto esses tres pontos nao estiverem resolvidos, o processo roda e para. Nada
chega na producao.

## Os arquivos

| arquivo | o que faz |
|---|---|
| `TRAVA` | liga e desliga a publicacao |
| `lista-de-envio.txt` | os caminhos fixos que vao para o ar |
| `montar-lista.sh` | junta os fixos com os PDFs da Transparencia |
| `remover.txt` | os PDFs a tirar do servidor |
| `pix-oficial.txt` | o payload do QR, vindo do banco |
| `validar.sh` | confere tudo antes de enviar |
| `conferir-pix.py` | a trava do PIX |
| `enviar.sh` | o envio por FTP |
| `conferir-producao.sh` | confere o site no ar depois |
