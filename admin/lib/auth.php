<?php
/**
 * Entrada do painel.
 *
 * Uma pessoa, uma senha. Nao existe cadastro, nao existe
 * recuperacao automatica e nao existe usuario publico. A senha
 * vive no servidor, guardada como hash, e nunca sai dele.
 */

if (!defined('PAINEL')) { http_response_code(404); exit; }

const AUTH_TENTATIVAS = 5;
const AUTH_ESPERA     = 300;   // 5 minutos de castigo

function autenticado(): bool { return !empty($_SESSION['entrou']); }

function auth_bloqueado(): int {
    $ate = $_SESSION['bloqueado_ate'] ?? 0;
    return $ate > time() ? $ate - time() : 0;
}

function auth_entrar(array $cfg, string $senha): bool {
    if (auth_bloqueado() > 0) return false;

    if (password_verify($senha, $cfg['senha'])) {
        session_regenerate_id(true);
        $_SESSION['entrou'] = true;
        $_SESSION['erros']  = 0;
        return true;
    }
    $_SESSION['erros'] = ($_SESSION['erros'] ?? 0) + 1;
    if ($_SESSION['erros'] >= AUTH_TENTATIVAS) {
        $_SESSION['bloqueado_ate'] = time() + AUTH_ESPERA;
        $_SESSION['erros'] = 0;
    }
    return false;
}

function auth_sair(): void {
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();
}
