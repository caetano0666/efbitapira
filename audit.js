const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = []; p.on('console', m => { if (m.type()==='error') errs.push(m.text()); });
  p.on('pageerror', e => errs.push('PAGEERROR '+e.message));
  await p.goto('file:///home/claude/escolinha/escolinha-batista-home.html', { waitUntil:'networkidle' });
  const r = await p.evaluate(() => {
    const out = { quebrados: [], externos: [], semAlt: 0, botoesPequenos: [], travessao: [] };
    document.querySelectorAll('a[href]').forEach(a => {
      const h = a.getAttribute('href');
      if (h.startsWith('#')) { if (h !== '#' && !document.querySelector(h)) out.quebrados.push(h + ' :: ' + a.textContent.trim().slice(0,30)); }
      else out.externos.push(h);
    });
    document.querySelectorAll('img').forEach(i => { if (!i.alt) out.semAlt++; });
    document.querySelectorAll('a.btn,button,a.link-seta').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.height > 0 && r.height < 40) out.botoesPequenos.push(el.textContent.trim().slice(0,26) + ' h' + Math.round(r.height));
    });
    const txt = document.body.innerText;
    ['—','–'].forEach(d => { let i = txt.indexOf(d); while (i > -1) { out.travessao.push(txt.slice(Math.max(0,i-25), i+25)); i = txt.indexOf(d, i+1); } });
    return out;
  });
  r.externos = [...new Set(r.externos)];
  console.log(JSON.stringify(r, null, 1));
  console.log('CONSOLE ERROS:', errs.length ? errs : 'nenhum');
  await b.close();
})();
