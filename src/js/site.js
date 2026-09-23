/* PalmaLuv — site script. No dependencies; sql.js is loaded on demand. */
(function () {
  'use strict';
  const root = document.documentElement;
  const ROOT = document.body.dataset.root || '';
  const LANG = document.body.dataset.lang || 'en';
  const T = (() => { try { return JSON.parse(document.getElementById('i18n').textContent); } catch { return {}; } })();
  const t = (k, vars) => { let s = T[k] || k; if (vars) for (const [a, b] of Object.entries(vars)) s = s.replaceAll('{' + a + '}', b); return s; };
  root.classList.add('js');

  /* ---------- theme: saved choice wins, otherwise dark (set in the markup) ---------- */
  const themeBtn = document.getElementById('theme');
  function toggleTheme() {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch {}
  }
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  /* ---------- reveal blocks once, when they come into view ---------- */
  const reveals = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) reveals.forEach(el => el.classList.add('in'));
  else {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
    reveals.forEach(el => io.observe(el));
  }

  /* ---------- header pills and the section list follow the section on screen ---------- */
  (function () {
    const links = [...document.querySelectorAll('.nav-pill[href^="#"], .res-item[href^="#"]')];
    const ids = [...new Set(links.map(a => a.getAttribute('href').slice(1)))].filter(id => document.getElementById(id));
    if (!ids.length) return;
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id));
    }), { rootMargin: '-40% 0px -50% 0px' });
    ids.forEach(id => io.observe(document.getElementById(id)));
  })();

  /* ---------- projects: star counts refresh from GitHub when reachable ---------- */
  (async function () {
    for (const card of document.querySelectorAll('[data-repo]')) {
      try {
        const res = await fetch('https://api.github.com/repos/' + card.dataset.repo);
        if (!res.ok) continue;
        const r = await res.json();
        const el = card.querySelector('[data-field="stars"]');
        if (el) el.textContent = r.stargazers_count;
      } catch {}
    }
  })();

  /* ---------- activity calendars, GitHub style, from data/<source>.json ---------- */
  const MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const iso = d => d.toISOString().slice(0, 10);
  const level = n => n === 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : n <= 5 ? 3 : 4;
  document.querySelectorAll('.heat[data-source]').forEach(async box => {
    const what = box.dataset.what;                     // submissions | contributions
    const grid = box.querySelector('.heat-grid'), months = box.querySelector('.heat-months');
    const years = box.querySelector('.years'), summary = box.querySelector('.heat-summary'), note = box.querySelector('.heat-note');
    let data;
    try {
      const res = await fetch(ROOT + 'data/' + box.dataset.source + '.json');
      if (!res.ok) throw new Error(res.status);
      data = await res.json();
    } catch { summary.textContent = t('heat_failed'); return; }
    // en: one / many. uk: one (1, 21…), few (2–4, 22–24…), many (the rest)
    const plural = (n, one, many) => {
      if (LANG !== 'uk') return n === 1 ? t(one) : t(many);
      const m10 = n % 10, m100 = n % 100;
      if (m10 === 1 && m100 !== 11) return t(one);
      if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return T[many + '_few'] || t(many);
      return t(many);
    };
    const whatOf = n => plural(n, what.slice(0, -1), what);

    function render(year) {
      const days = data.calendar[year] || {};
      const first = new Date(Date.UTC(year, 0, 1)), last = new Date(Date.UTC(year, 11, 31));
      const cells = [], labels = [];
      let col = 0;
      for (let i = 0; i < first.getUTCDay(); i++) cells.push('<i class="c pad"></i>');
      for (let d = new Date(first); d <= last; d.setUTCDate(d.getUTCDate() + 1)) {
        const key = iso(d), n = days[key] || 0;
        if (d.getUTCDate() === 1) labels.push({ m: d.getUTCMonth(), col });
        cells.push('<i class="c l' + level(n) + '" title="' + n + ' ' + whatOf(n) + ', ' + key + '"></i>');
        if (d.getUTCDay() === 6) col++;
      }
      grid.innerHTML = cells.join('');
      months.innerHTML = labels.map(l => '<span style="left:' + (l.col * 15) + 'px">' + MONTH[l.m] + '</span>').join('');
      const total = Object.values(days).reduce((a, b) => a + b, 0), active = Object.keys(days).length;
      summary.textContent = t('heat_summary', { n: total, what: whatOf(total), year, days: active, daysword: plural(active, 'day', 'days') });
      years.querySelectorAll('button').forEach(b => b.setAttribute('aria-selected', b.dataset.year == year));
    }
    const allN = Object.values(data.calendar).reduce((a, y) => a + Object.values(y).reduce((s, n) => s + n, 0), 0);
    const allD = Object.values(data.calendar).reduce((a, y) => a + Object.keys(y).length, 0);
    note.textContent = t('heat_note', { n: allN, what: whatOf(allN), days: allD, from: data.years[0], date: data.fetched });
    years.innerHTML = data.years.map(y => {
      const n = Object.values(data.calendar[y] || {}).reduce((a, b) => a + b, 0);
      return '<button type="button" role="tab" data-year="' + y + '">' + y + '<small>' + n + '</small></button>';
    }).join('');
    years.addEventListener('click', e => { const b = e.target.closest('button'); if (b) render(+b.dataset.year); });
    render(data.years[data.years.length - 1]);
  });

  /* ---------- command palette, Ctrl+K ---------- */
  (function () {
    const pal = document.getElementById('palette');
    if (!pal) return;
    const input = document.getElementById('palette-q'), list = document.getElementById('palette-list'), opener = document.getElementById('palette-open');
    let items = [], filtered = [], index = 0;

    function collect() {
      items = [];
      document.querySelectorAll('.res-item[href^="#"]').forEach(a => items.push({ g: t('palette_sections'), label: a.querySelector('span').firstChild.textContent.trim(), run: () => location.hash = a.getAttribute('href') }));
      document.querySelectorAll('.social a, .clinks a').forEach(a => items.push({ g: t('palette_links'), label: a.getAttribute('aria-label') || a.textContent.trim(), run: () => window.open(a.href, '_blank') }));
      document.querySelectorAll('.proj').forEach(a => items.push({ g: t('palette_projects'), label: a.querySelector('h3').textContent, run: () => window.open(a.href, '_blank') }));
      const lang = document.querySelector('.lang-pill'), cv = document.querySelector('.cv-link');
      items.push({ g: t('palette_actions'), label: t('act_theme'), run: toggleTheme });
      if (lang) items.push({ g: t('palette_actions'), label: t('act_lang'), run: () => location.href = lang.href });
      if (cv) items.push({ g: t('palette_actions'), label: t('act_cv'), run: () => location.href = cv.href });
      items.push({ g: t('palette_actions'), label: t('act_copy'), run: async () => { try { await navigator.clipboard.writeText(location.href.split('#')[0]); toast(t('act_copied')); } catch {} } });
      items.push({ g: t('palette_actions'), label: t('act_top'), run: () => window.scrollTo({ top: 0, behavior: 'smooth' }) });
      // de-duplicate labels within a group
      const seen = new Set();
      items = items.filter(i => { const k = i.g + '|' + i.label; if (seen.has(k)) return false; seen.add(k); return true; });
    }
    function draw() {
      const s = input.value.trim().toLowerCase();
      filtered = s ? items.filter(i => i.label.toLowerCase().includes(s) || i.g.toLowerCase().includes(s)) : items;
      index = Math.min(index, Math.max(0, filtered.length - 1));
      if (!filtered.length) { list.innerHTML = '<li class="empty">' + t('palette_empty') + '</li>'; return; }
      let g = '', h = '';
      filtered.forEach((i, n) => {
        if (i.g !== g) { g = i.g; h += '<li class="group">' + g + '</li>'; }
        h += '<li role="option" data-n="' + n + '"' + (n === index ? ' class="active" aria-selected="true"' : '') + '>' + i.label + '</li>';
      });
      list.innerHTML = h;
      const a = list.querySelector('.active'); if (a) a.scrollIntoView({ block: 'nearest' });
    }
    function open() { collect(); pal.hidden = false; input.value = ''; index = 0; draw(); input.focus(); document.body.style.overflow = 'hidden'; }
    function close() { pal.hidden = true; document.body.style.overflow = ''; }
    function go() { const i = filtered[index]; if (!i) return; close(); i.run(); }
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); pal.hidden ? open() : close(); return; }
      if (pal.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowDown') { e.preventDefault(); index = (index + 1) % filtered.length; draw(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); index = (index - 1 + filtered.length) % filtered.length; draw(); }
      else if (e.key === 'Enter') { e.preventDefault(); go(); }
    });
    input.addEventListener('input', () => { index = 0; draw(); });
    list.addEventListener('click', e => { const li = e.target.closest('[data-n]'); if (li) { index = +li.dataset.n; go(); } });
    pal.addEventListener('click', e => { if (e.target === pal) close(); });
    if (opener) opener.addEventListener('click', open);
  })();

  function toast(msg) {
    const el = document.createElement('div'); el.className = 'toast'; el.textContent = msg; document.body.appendChild(el);
    requestAnimationFrame(() => el.classList.add('in'));
    setTimeout(() => { el.classList.remove('in'); setTimeout(() => el.remove(), 300); }, 1800);
  }
})();
