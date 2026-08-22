<?php
if (!defined('PAINEL')) { http_response_code(404); exit; }
$novo   = ($_GET['novo'] ?? '') !== '';
$forma  = $novo || $editando !== null;
$titulo = $forma ? ($editando ? 'Editar documento' : 'Novo documento') : 'Documentos';
require __DIR__ . '/_topo.php';
?>
<main class="tela">

  <header class="topo">
    <p class="rotulo">Transparência</p>
    <h1><?= e($titulo) ?></h1>
    <p><?php if (!$forma): ?>Os documentos publicados aparecem na página de Transparência do site.
       <?php elseif ($editando): ?>Altere o que precisar e salve.
       <?php else: ?>Preencha e salve. Ele aparece na página de Transparência.<?php endif; ?></p>
  </header>

  <?php if ($recado): ?>
    <p class="recado recado--<?= $recado['tipo'] === 'erro' ? 'erro' : 'ok' ?>"><?= e($recado['texto']) ?></p>
  <?php endif; ?>

  <?php if ($erros): ?>
    <div class="recado recado--erro">
      <?= count($erros) === 1 ? e($erros[0]) : 'Confira:' ?>
      <?php if (count($erros) > 1): ?>
        <ul><?php foreach ($erros as $x): ?><li><?= e($x) ?></li><?php endforeach; ?></ul>
      <?php endif; ?>
    </div>
  <?php endif; ?>

<?php if (!$forma): ?>

  <?php if ($lista): ?>
    <ul class="lista">
      <?php foreach ($lista as $d): ?>
        <li>
          <a href="?doc=<?= (int)$d['_periodo'] ?>-<?= (int)$d['_id'] ?>">
            <span class="lista__txt">
              <span class="lista__n"><?= e($d['titulo'] ?? 'Documento') ?></span>
              <?php if (!empty($d['descricao'])): ?>
                <span class="lista__d"><?= e($d['descricao']) ?></span>
              <?php endif; ?>
            </span>
            <span class="selo <?= !empty($d['publicado']) ? 'selo--no-ar' : 'selo--rascunho' ?>">
              <?= !empty($d['publicado']) ? 'No ar' : 'Rascunho' ?>
            </span>
          </a>
        </li>
      <?php endforeach; ?>
    </ul>
  <?php else: ?>
    <p class="vazio">Nenhum documento ainda.</p>
  <?php endif; ?>

  <a class="btn" href="?novo=1">Novo documento</a>

<?php else: ?>

  <form method="post" action="?" enctype="multipart/form-data" id="forma" novalidate>
    <input type="hidden" name="acao" value="salvar">
    <input type="hidden" name="csrf" value="<?= e(csrf()) ?>">
    <?php if ($editando): ?>
      <input type="hidden" name="periodo" value="<?= (int)$editando['_periodo'] ?>">
      <input type="hidden" name="id" value="<?= (int)$editando['_id'] ?>">
    <?php endif; ?>

    <div class="campo">
      <div class="rot">
        <label for="nome">Nome do documento</label>
        <span class="conta" id="conta-nome">0/80</span>
      </div>
      <input type="text" id="nome" name="nome" maxlength="80" autocomplete="off"
             placeholder="Demonstrativo financeiro de 2026"
             value="<?= e($editando['titulo'] ?? '') ?>">
    </div>

    <div class="campo">
      <div class="rot">
        <label for="descricao">Descrição curta</label>
        <span class="conta" id="conta-descricao">0/160</span>
      </div>
      <p class="ajuda">Explique em uma frase o que contém este documento.</p>
      <textarea id="descricao" name="descricao" maxlength="160" rows="2"
                placeholder="Receitas, despesas e saldo do exercício."><?= e($editando['descricao'] ?? '') ?></textarea>
    </div>

    <div class="campo arquivo">
      <div class="rot"><label for="pdf">Arquivo PDF</label></div>
      <input type="file" id="pdf" name="pdf" accept="application/pdf,.pdf">
      <label class="solta" for="pdf">
        <span class="solta__ico" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>
          </svg>
        </span>
        <span class="solta__txt">
          <span class="solta__t" id="arq-titulo"><?= $editando && !empty($editando['arquivo'])
              ? e(basename($editando['arquivo'])) : 'Escolher arquivo' ?></span>
          <span class="solta__s" id="arq-sub"><?= $editando && !empty($editando['arquivo'])
              ? 'Já enviado' : 'Somente PDF' ?></span>
        </span>
        <button type="button" class="trocar" id="trocar"
                <?= $editando && !empty($editando['arquivo']) ? '' : 'hidden' ?>>Trocar</button>
      </label>
    </div>

    <div class="dupla">
      <div class="campo">
        <div class="rot"><label>Publicado no site</label></div>
        <div class="opcoes">
          <input type="radio" name="publicado" id="pub-sim" value="sim"
                 <?= !empty($editando['publicado']) ? 'checked' : '' ?>>
          <label for="pub-sim">Sim</label>
          <input type="radio" name="publicado" id="pub-nao" value="nao"
                 <?= empty($editando['publicado']) ? 'checked' : '' ?>>
          <label for="pub-nao">Não</label>
        </div>
      </div>

      <div class="campo">
        <div class="rot"><label for="ordem">Ordem</label></div>
        <input type="number" id="ordem" name="ordem" min="1" max="999" step="1"
               inputmode="numeric" value="<?= (int)($editando['ordem'] ?? 1) ?>">
        <p class="ajuda ajuda--pe">Menor aparece primeiro.</p>
      </div>
    </div>

    <div class="acoes">
      <button type="submit" class="btn" id="salvar">Salvar</button>
      <a class="discreto" href="?">Voltar sem salvar</a>
    </div>
  </form>

  <?php if ($editando): ?>
    <button type="button" class="discreto" id="excluir">Excluir documento</button>

    <div class="veu" id="veu" hidden role="dialog" aria-modal="true" aria-labelledby="veu-t">
      <div class="caixa">
        <h2 id="veu-t">Excluir este documento?</h2>
        <p>Ele sai da página de Transparência e o arquivo deixa de ficar disponível. Não dá para desfazer.</p>
        <form method="post" action="?" class="caixa__acoes">
          <input type="hidden" name="acao" value="excluir">
          <input type="hidden" name="csrf" value="<?= e(csrf()) ?>">
          <input type="hidden" name="periodo" value="<?= (int)$editando['_periodo'] ?>">
          <input type="hidden" name="id" value="<?= (int)$editando['_id'] ?>">
          <button type="button" class="btn btn--e" id="cancelar">Cancelar</button>
          <button type="submit" class="btn btn--grave">Excluir</button>
        </form>
      </div>
    </div>
  <?php endif; ?>

<?php endif; ?>

  <div class="assina">
    <img src="ativos/logo-iaieu.png" alt="IAieu" width="1774" height="887">
    <p class="assina__frase">A inteligência será sempre sua.</p>
  </div>
</main>

<?php if ($forma): ?>
<script>
(function () {
  var $ = function (id) { return document.getElementById(id); };

  function contador(campo, saida, limite) {
    function pintar() {
      var n = campo.value.length;
      saida.textContent = n + '/' + limite;
      saida.classList.toggle('perto', n >= limite * 0.9 && n < limite);
      saida.classList.toggle('cheio', n >= limite);
    }
    campo.addEventListener('input', pintar);
    pintar();
  }
  contador($('nome'), $('conta-nome'), 80);
  contador($('descricao'), $('conta-descricao'), 160);

  var pdf = $('pdf');
  pdf.addEventListener('change', function () {
    var f = pdf.files && pdf.files[0];
    $('arq-titulo').textContent = f ? f.name : 'Escolher arquivo';
    $('arq-sub').textContent = f
      ? (f.size >= 1048576 ? (f.size / 1048576).toFixed(1) + ' MB'
                           : Math.max(1, Math.round(f.size / 1024)) + ' KB')
      : 'Somente PDF';
    $('trocar').hidden = !f;
  });
  $('trocar').addEventListener('click', function (e) { e.preventDefault(); pdf.click(); });

  function rotular() {
    $('salvar').textContent = $('pub-sim').checked ? 'Salvar e publicar' : 'Salvar';
  }
  $('pub-sim').addEventListener('change', rotular);
  $('pub-nao').addEventListener('change', rotular);
  rotular();

  $('forma').addEventListener('submit', function () {
    $('salvar').disabled = true;
    $('salvar').textContent = 'Salvando…';
  });

  var veu = $('veu');
  if (veu) {
    $('excluir').addEventListener('click', function () { veu.hidden = false; $('cancelar').focus(); });
    $('cancelar').addEventListener('click', function () { veu.hidden = true; $('excluir').focus(); });
    veu.addEventListener('click', function (e) { if (e.target === veu) veu.hidden = true; });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !veu.hidden) veu.hidden = true;
    });
  }
})();
</script>
<?php endif; ?>
</body>
</html>
