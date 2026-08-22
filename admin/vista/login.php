<?php $titulo = 'Entrar'; require __DIR__ . '/_topo.php'; ?>
if (!defined('PAINEL')) { http_response_code(404); exit; }
<main class="porta">
  <header class="topo">
    <p class="rotulo">Painel</p>
    <h1>Entrar</h1>
    <p>Digite a senha para administrar os documentos da Transparência.</p>
  </header>

  <?php if ($recado): ?>
    <p class="recado recado--<?= $recado['tipo'] === 'erro' ? 'erro' : 'ok' ?>"><?= e($recado['texto']) ?></p>
  <?php endif; ?>

  <form method="post" action="?">
    <input type="hidden" name="acao" value="entrar">
    <input type="hidden" name="csrf" value="<?= e(csrf()) ?>">
    <div class="campo">
      <div class="rot"><label for="senha">Senha</label></div>
      <input type="password" id="senha" name="senha" autocomplete="current-password" autofocus>
    </div>
    <div class="acoes"><button type="submit" class="btn">Entrar</button></div>
  </form>

  <div class="assina">
    <img src="ativos/logo-iaieu.png" alt="IAieu" width="1774" height="887">
    <p class="assina__frase">A inteligência será sempre sua.</p>
  </div>
</main>
</body>
</html>
