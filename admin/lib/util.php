<?php
/** Funcoes pequenas que a tela usa o tempo todo. */


if (!defined('PAINEL')) { http_response_code(404); exit; }
function e(?string $s): string { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

function limitar(string $texto, int $limite): string {
    $texto = trim(preg_replace('/\s+/u', ' ', $texto));
    return mb_substr($texto, 0, $limite, 'UTF-8');
}

/**
 * Transforma o nome do documento num nome de arquivo seguro.
 * A troca de acentos e feita a mao: o iconv depende da instalacao
 * do servidor e chegou a comer o "a" de "nao", virando "n-o".
 */
function apelido(string $texto): string {
    $de = ['á','à','â','ã','ä','é','è','ê','ë','í','ì','î','ï','ó','ò','ô','õ','ö',
           'ú','ù','û','ü','ç','ñ','Á','À','Â','Ã','Ä','É','È','Ê','Ë','Í','Ì','Î',
           'Ï','Ó','Ò','Ô','Õ','Ö','Ú','Ù','Û','Ü','Ç','Ñ'];
    $para = ['a','a','a','a','a','e','e','e','e','i','i','i','i','o','o','o','o','o',
             'u','u','u','u','c','n','a','a','a','a','a','e','e','e','e','i','i','i',
             'i','o','o','o','o','o','u','u','u','u','c','n'];
    $t = str_replace($de, $para, $texto);
    $t = strtolower(preg_replace('/[^a-zA-Z0-9]+/', '-', $t));
    $t = trim($t, '-');
    if ($t === '') $t = 'documento';
    return substr($t, 0, 60);
}

function tamanho_legivel(int $bytes): string {
    return $bytes >= 1048576
        ? number_format($bytes / 1048576, 1, ',', '.') . ' MB'
        : max(1, (int) round($bytes / 1024)) . ' KB';
}

function csrf(): string {
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
    return $_SESSION['csrf'];
}

function csrf_valido(): bool {
    return !empty($_POST['csrf']) && !empty($_SESSION['csrf'])
        && hash_equals($_SESSION['csrf'], $_POST['csrf']);
}

function ir_para(string $url): void { header('Location: ' . $url); exit; }

function recado(?string $tipo = null, ?string $texto = null): ?array {
    if ($tipo !== null) { $_SESSION['recado'] = ['tipo' => $tipo, 'texto' => $texto]; return null; }
    $r = $_SESSION['recado'] ?? null;
    unset($_SESSION['recado']);
    return $r;
}
