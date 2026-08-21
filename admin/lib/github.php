<?php
/**
 * A conversa com o GitHub.
 *
 * Esta e a unica parte do painel que escreve no repositorio, e ela
 * so alcanca dois lugares:
 *
 *   transparencia/documentos.json
 *   transparencia/arquivos/<nome>.pdf
 *
 * Qualquer outro caminho e recusado aqui dentro, antes de sair
 * requisicao nenhuma. Home, doacao, PIX, .htaccess e workflows
 * estao fora do alcance do painel por construcao, e nao por
 * disciplina de quem escreveu a tela.
 */

const GH_LISTA   = 'transparencia/documentos.json';
const GH_PASTA   = 'transparencia/arquivos';
const GH_PDF_MAX = 12 * 1024 * 1024;   // 12 MB

/** Recusa qualquer caminho fora das duas areas autorizadas. */
function gh_caminho_permitido(string $caminho): bool {
    if ($caminho === GH_LISTA) return true;
    return (bool) preg_match('#^' . GH_PASTA . '/[a-z0-9][a-z0-9._-]{0,90}\.pdf$#', $caminho);
}

function gh_url(array $cfg, string $caminho): string {
    return 'https://api.github.com/repos/' . $cfg['repo'] . '/contents/' . $caminho;
}

/**
 * Uma chamada a API. Devolve [codigo, corpo].
 * O token vive so aqui, no servidor, e nunca chega ao navegador.
 */
function gh_chamar(array $cfg, string $metodo, string $caminho, ?array $corpo = null, array $query = []): array {
    if (!gh_caminho_permitido($caminho)) {
        return [403, ['message' => 'Caminho fora das areas autorizadas do painel.']];
    }
    $url = gh_url($cfg, $caminho);
    if ($query) $url .= '?' . http_build_query($query);

    $ch = curl_init($url);
    $cabecalhos = [
        'Accept: application/vnd.github+json',
        'X-GitHub-Api-Version: 2022-11-28',
        'User-Agent: painel-efbitapira',
        'Authorization: Bearer ' . $cfg['token'],
    ];
    if ($corpo !== null) $cabecalhos[] = 'Content-Type: application/json';

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CUSTOMREQUEST  => $metodo,
        CURLOPT_HTTPHEADER     => $cabecalhos,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_CONNECTTIMEOUT => 10,
    ]);
    if ($corpo !== null) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($corpo, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
    }
    $resposta = curl_exec($ch);
    if ($resposta === false) {
        $erro = curl_error($ch);
        curl_close($ch);
        return [0, ['message' => 'Nao consegui falar com o GitHub: ' . $erro]];
    }
    $codigo = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return [$codigo, json_decode($resposta, true) ?? []];
}

/** Le a lista de documentos. Devolve [dados, sha]. */
function gh_ler_lista(array $cfg): array {
    [$codigo, $corpo] = gh_chamar($cfg, 'GET', GH_LISTA, null, ['ref' => $cfg['ramo']]);
    if ($codigo !== 200 || empty($corpo['content'])) {
        return [null, null, $corpo['message'] ?? 'Nao consegui ler a lista de documentos.'];
    }
    $json = base64_decode(str_replace("\n", '', $corpo['content']));
    $dados = json_decode($json, true);
    if (!is_array($dados)) return [null, null, 'A lista de documentos esta ilegivel.'];
    return [$dados, $corpo['sha'], null];
}

/** Grava a lista de documentos por cima da anterior. */
function gh_gravar_lista(array $cfg, array $dados, string $sha, string $mensagem): ?string {
    $json = json_encode($dados, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";
    [$codigo, $corpo] = gh_chamar($cfg, 'PUT', GH_LISTA, [
        'message'   => $mensagem,
        'content'   => base64_encode($json),
        'sha'       => $sha,
        'branch'    => $cfg['ramo'],
        'committer' => ['name' => 'Painel da Escolinha', 'email' => 'painel@efbitapira.org'],
    ]);
    return in_array($codigo, [200, 201], true) ? null : ($corpo['message'] ?? 'Nao consegui salvar a lista.');
}

/** Envia um PDF. Devolve o caminho gravado ou uma mensagem de erro. */
function gh_enviar_pdf(array $cfg, string $nomeArquivo, string $conteudo, string $mensagem): array {
    $caminho = GH_PASTA . '/' . $nomeArquivo;
    if (!gh_caminho_permitido($caminho)) return [null, 'Nome de arquivo nao aceito.'];

    // se ja existir, precisa do sha para substituir
    [$c, $b] = gh_chamar($cfg, 'GET', $caminho, null, ['ref' => $cfg['ramo']]);
    $sha = ($c === 200 && !empty($b['sha'])) ? $b['sha'] : null;

    $envio = [
        'message'   => $mensagem,
        'content'   => base64_encode($conteudo),
        'branch'    => $cfg['ramo'],
        'committer' => ['name' => 'Painel da Escolinha', 'email' => 'painel@efbitapira.org'],
    ];
    if ($sha) $envio['sha'] = $sha;

    [$codigo, $corpo] = gh_chamar($cfg, 'PUT', $caminho, $envio);
    if (!in_array($codigo, [200, 201], true)) {
        return [null, $corpo['message'] ?? 'Nao consegui enviar o arquivo.'];
    }
    return ['/' . $caminho, null];
}

/** Apaga um PDF do repositorio. */
function gh_apagar_pdf(array $cfg, string $caminhoRelativo, string $mensagem): ?string {
    $caminho = ltrim($caminhoRelativo, '/');
    if (!gh_caminho_permitido($caminho)) return 'Arquivo fora das areas autorizadas.';

    [$c, $b] = gh_chamar($cfg, 'GET', $caminho, null, ['ref' => $cfg['ramo']]);
    if ($c !== 200 || empty($b['sha'])) return null;   // ja nao existe, nada a fazer

    [$codigo, $corpo] = gh_chamar($cfg, 'DELETE', $caminho, [
        'message'   => $mensagem,
        'sha'       => $b['sha'],
        'branch'    => $cfg['ramo'],
        'committer' => ['name' => 'Painel da Escolinha', 'email' => 'painel@efbitapira.org'],
    ]);
    return $codigo === 200 ? null : ($corpo['message'] ?? 'Nao consegui apagar o arquivo.');
}
