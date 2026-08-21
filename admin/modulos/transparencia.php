<?php
/**
 * MODULO TRANSPARENCIA
 *
 * O unico modulo que existe hoje. Cuida da lista de documentos e
 * dos PDFs, e mais nada.
 *
 * Um modulo novo, no futuro, entra em modulos/ com esta mesma
 * forma: um titulo, uma rota e as funcoes que a tela chama. Nada
 * do que ainda nao existe aparece na interface.
 */

/** Devolve todos os documentos, achatados, com o indice do periodo. */
function tr_documentos(array $dados): array {
    $saida = [];
    foreach ($dados['periodos'] ?? [] as $ip => $per) {
        foreach ($per['documentos'] ?? [] as $id => $doc) {
            $doc['_periodo'] = $ip;
            $doc['_id']      = $id;
            $doc['_ano']     = $per['ano'] ?? '';
            $saida[] = $doc;
        }
    }
    usort($saida, function ($a, $b) {
        return [$b['_ano'], $a['ordem'] ?? 1] <=> [$a['_ano'], $b['ordem'] ?? 1];
    });
    return $saida;
}

function tr_documento(array $dados, int $periodo, int $id): ?array {
    $doc = $dados['periodos'][$periodo]['documentos'][$id] ?? null;
    if ($doc === null) return null;
    $doc['_periodo'] = $periodo;
    $doc['_id']      = $id;
    return $doc;
}

/** O periodo onde documentos novos entram: o primeiro da lista. */
function tr_periodo_padrao(array $dados): int {
    return empty($dados['periodos']) ? -1 : 0;
}

/**
 * Valida o que veio da tela. Devolve [campos, erros].
 * Os limites sao os mesmos da interface, conferidos de novo aqui:
 * o navegador impede, mas quem manda e o servidor.
 */
function tr_validar(array $post, bool $temArquivo, bool $arquivoJaExiste): array {
    $erros = [];

    $nome = limitar((string)($post['nome'] ?? ''), 80);
    if ($nome === '') $erros[] = 'Escreva o nome do documento.';

    $descricao = limitar((string)($post['descricao'] ?? ''), 160);

    $ordem = (int)($post['ordem'] ?? 1);
    if ($ordem < 1)    $ordem = 1;
    if ($ordem > 999)  $ordem = 999;

    $publicado = (($post['publicado'] ?? 'nao') === 'sim');

    if (!$temArquivo && !$arquivoJaExiste) $erros[] = 'Escolha o arquivo PDF.';

    return [compact('nome', 'descricao', 'ordem', 'publicado'), $erros];
}

/**
 * Confere o arquivo enviado. So PDF, so ate o limite.
 * Nao confia na extensao nem no que o navegador disse: le os
 * primeiros bytes do arquivo.
 */
function tr_validar_pdf(array $arquivo): array {
    if (($arquivo['error'] ?? UPLOAD_ERR_NO_FILE) === UPLOAD_ERR_NO_FILE) return [null, null];

    if ($arquivo['error'] !== UPLOAD_ERR_OK) {
        return [null, 'O envio do arquivo falhou. Tente de novo.'];
    }
    if ($arquivo['size'] > GH_PDF_MAX) {
        return [null, 'O arquivo passa de ' . tamanho_legivel(GH_PDF_MAX) . '.'];
    }
    if (!is_uploaded_file($arquivo['tmp_name'])) {
        return [null, 'Arquivo invalido.'];
    }
    $conteudo = file_get_contents($arquivo['tmp_name']);
    if ($conteudo === false || strncmp($conteudo, '%PDF-', 5) !== 0) {
        return [null, 'O arquivo precisa ser um PDF.'];
    }
    return [$conteudo, null];
}

/** Grava, criando ou editando. Devolve mensagem de erro ou null. */
function tr_salvar(array $cfg, ?int $periodo, ?int $id, array $campos, ?string $conteudoPdf, string $nomeBaseArquivo): ?string {
    [$dados, $sha, $erro] = gh_ler_lista($cfg);
    if ($erro) return $erro;

    $novo = ($id === null);
    if ($novo) {
        $periodo = tr_periodo_padrao($dados);
        if ($periodo < 0) return 'Nao ha periodo cadastrado para receber o documento.';
    }
    if (!isset($dados['periodos'][$periodo])) return 'Periodo nao encontrado.';

    $doc = $novo ? [] : ($dados['periodos'][$periodo]['documentos'][$id] ?? null);
    if (!$novo && $doc === null) return 'Documento nao encontrado.';

    // o PDF vai primeiro: a pagina so pode citar um arquivo que ja existe
    if ($conteudoPdf !== null) {
        $nomeArquivo = apelido($nomeBaseArquivo) . '.pdf';
        [$caminho, $erroPdf] = gh_enviar_pdf($cfg, $nomeArquivo, $conteudoPdf,
            'Painel: envia ' . $nomeArquivo);
        if ($erroPdf) return $erroPdf;

        $anterior = $doc['arquivo'] ?? null;
        $doc['arquivo'] = $caminho;

        if ($anterior && $anterior !== $caminho) {
            gh_apagar_pdf($cfg, $anterior, 'Painel: remove arquivo substituido');
        }
        // a lista mudou de sha depois do commit do PDF
        [$dados, $sha, $erro] = gh_ler_lista($cfg);
        if ($erro) return $erro;
        if ($novo) $periodo = tr_periodo_padrao($dados);
        $guardado = $doc['arquivo'];
        $doc = $novo ? [] : ($dados['periodos'][$periodo]['documentos'][$id] ?? []);
        $doc['arquivo'] = $guardado;
    }

    $doc['titulo']    = $campos['nome'];
    $doc['descricao'] = $campos['descricao'];
    $doc['publicado'] = $campos['publicado'];
    $doc['ordem']     = $campos['ordem'];

    if (!isset($dados['periodos'][$periodo]['documentos'])) {
        $dados['periodos'][$periodo]['documentos'] = [];
    }
    if ($novo) {
        $dados['periodos'][$periodo]['documentos'][] = $doc;
    } else {
        $dados['periodos'][$periodo]['documentos'][$id] = $doc;
    }

    return gh_gravar_lista($cfg, $dados, $sha,
        'Painel: ' . ($novo ? 'novo documento' : 'documento atualizado') . ' na Transparencia');
}

/** Apaga o documento e o PDF. */
function tr_excluir(array $cfg, int $periodo, int $id): ?string {
    [$dados, $sha, $erro] = gh_ler_lista($cfg);
    if ($erro) return $erro;

    $doc = $dados['periodos'][$periodo]['documentos'][$id] ?? null;
    if ($doc === null) return 'Documento nao encontrado.';

    $arquivo = $doc['arquivo'] ?? null;

    array_splice($dados['periodos'][$periodo]['documentos'], $id, 1);
    if (empty($dados['periodos'][$periodo]['documentos'])) {
        unset($dados['periodos'][$periodo]['documentos']);
    }

    $erro = gh_gravar_lista($cfg, $dados, $sha, 'Painel: documento removido da Transparencia');
    if ($erro) return $erro;

    if ($arquivo) gh_apagar_pdf($cfg, $arquivo, 'Painel: remove o arquivo do documento');
    return null;
}
