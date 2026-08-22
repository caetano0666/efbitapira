<?php
/**
 * PAINEL DA ESCOLINHA
 *
 * Uma tela, um trabalho. Quem entra aqui quer publicar um
 * documento e ir embora.
 *
 * O que acontece depois de salvar, e que o cliente nunca precisa
 * saber: o painel grava no repositorio do projeto, um processo
 * automatico refaz a pagina de Transparencia e envia para o
 * servidor do site. Em torno de um minuto.
 */

declare(strict_types=1);

// as pecas internas so rodam a partir daqui
define('PAINEL', true);

$raiz = __DIR__;
if (!is_file($raiz . '/config.php')) {
    http_response_code(500);
    exit('Painel ainda nao configurado.');
}
$cfg = require $raiz . '/config.php';

require $raiz . '/lib/util.php';
require $raiz . '/lib/auth.php';
require $raiz . '/lib/github.php';
require $raiz . '/modulos/transparencia.php';

/* ------------------------------------------------------------
   MODULOS
   Hoje existe um so. Um modulo novo entra aqui, com sua rota e
   sua tela, sem mexer no que ja funciona.
   ------------------------------------------------------------ */
$MODULOS = [
    'transparencia' => ['titulo' => 'Transparência', 'vista' => 'transparencia'],
];
$MODULO = 'transparencia';

session_set_cookie_params([
    'httponly' => true,
    'samesite' => 'Lax',
    'secure'   => (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
                  || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https'),
]);
session_name('efbpainel');
session_start();

header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
header('Cache-Control: no-store');

$acao = $_POST['acao'] ?? $_GET['acao'] ?? '';

/* ------------------------------------------------------------
   ENTRAR E SAIR
   ------------------------------------------------------------ */
if ($acao === 'sair') { auth_sair(); ir_para('?'); }

if ($acao === 'entrar' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!csrf_valido()) {
        recado('erro', 'A sessão expirou. Tente entrar de novo.');
    } elseif (auth_entrar($cfg, (string)($_POST['senha'] ?? ''))) {
        ir_para('?');
    } else {
        $espera = auth_bloqueado();
        recado('erro', $espera > 0
            ? 'Muitas tentativas. Espere ' . ceil($espera / 60) . ' minutos.'
            : 'Senha incorreta.');
    }
    ir_para('?');
}

if (!autenticado()) {
    $recado = recado();
    require $raiz . '/vista/login.php';
    exit;
}

/* ------------------------------------------------------------
   AS ACOES DO MODULO
   ------------------------------------------------------------ */
$erros = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && in_array($acao, ['salvar', 'excluir'], true)) {
    if (!csrf_valido()) {
        $erros[] = 'A sessão expirou. Recarregue a página e tente de novo.';
    } else {
        $periodo = isset($_POST['periodo']) && $_POST['periodo'] !== '' ? (int)$_POST['periodo'] : null;
        $id      = isset($_POST['id'])      && $_POST['id']      !== '' ? (int)$_POST['id']      : null;

        if ($acao === 'excluir') {
            if ($periodo === null || $id === null) {
                $erros[] = 'Documento não identificado.';
            } else {
                $erro = tr_excluir($cfg, $periodo, $id);
                if ($erro) { $erros[] = $erro; }
                else { recado('ok', 'Documento excluído. A página de Transparência é atualizada em cerca de um minuto.'); ir_para('?'); }
            }
        } else {
            [$conteudoPdf, $erroPdf] = tr_validar_pdf($_FILES['pdf'] ?? []);
            if ($erroPdf) $erros[] = $erroPdf;

            $jaTem = false;
            if ($id !== null && $periodo !== null) {
                [$d, , $e] = gh_ler_lista($cfg);
                if (!$e) $jaTem = !empty($d['periodos'][$periodo]['documentos'][$id]['arquivo']);
            }
            [$campos, $errosCampos] = tr_validar($_POST, $conteudoPdf !== null, $jaTem);
            $erros = array_merge($erros, $errosCampos);

            if (!$erros) {
                $erro = tr_salvar($cfg, $periodo, $id, $campos, $conteudoPdf, $campos['nome']);
                if ($erro) { $erros[] = $erro; }
                else {
                    recado('ok', $campos['publicado']
                        ? 'Salvo e publicado. Confira na página de Transparência em cerca de um minuto.'
                        : 'Salvo. O documento ainda não aparece no site.');
                    ir_para('?');
                }
            }
        }
    }
}

/* ------------------------------------------------------------
   O QUE A TELA VAI MOSTRAR
   ------------------------------------------------------------ */
[$dados, , $erroLeitura] = gh_ler_lista($cfg);
if ($erroLeitura) $erros[] = $erroLeitura;

$lista = $dados ? tr_documentos($dados) : [];

$editando = null;
if (($_GET['doc'] ?? '') !== '' && $dados) {
    [$p, $i] = array_pad(explode('-', (string)$_GET['doc'], 2), 2, null);
    if ($p !== null && $i !== null) $editando = tr_documento($dados, (int)$p, (int)$i);
}

$recado = recado();
require $raiz . '/vista/' . $MODULOS[$MODULO]['vista'] . '.php';
