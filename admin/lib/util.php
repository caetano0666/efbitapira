<?php
/** Funcoes pequenas que a tela usa o tempo todo. */


if (!defined('PAINEL')) { http_response_code(404); exit; }
function e(?string $s): string { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

function limitar(string $texto, int $limite): string {
    $texto = trim(preg_replace('/\s+/u', ' ', $texto));
    return mb_substr($texto, 0, $limite, 'UTF-8');
}

/** Transforma o nome do documento num nome de arquivo seguro. */
function apelido(string $texto): string {
    $t = iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $texto);
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
