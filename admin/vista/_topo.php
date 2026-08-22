<?php if (!defined('PAINEL')) { http_response_code(404); exit; } ?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title><?= e($titulo ?? 'Painel') ?> · Escolinha de Futebol Batista</title>
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<header class="barra">
  <div class="barra__in">
    <span class="marca">
      <img class="marca__logo" src="ativos/logo-escolinha.png" alt="" width="320" height="320">
      <span class="marca__txt">
        <span class="marca__n">Escolinha de Futebol Batista</span>
        <span class="marca__s">Itapira · SP</span>
      </span>
    </span>
    <?php if (autenticado()): ?><a class="sair" href="?acao=sair">Sair</a><?php endif; ?>
  </div>
</header>
