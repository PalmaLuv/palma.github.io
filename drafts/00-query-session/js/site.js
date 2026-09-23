/* Theme: saved choice wins, otherwise follow the system. */
(function () {
  const root = document.documentElement;
  root.classList.add('js');

  const btn = document.getElementById('theme');
  const saved = (() => { try { return localStorage.getItem('theme'); } catch { return null; } })();
  const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  apply(saved || system);

  btn.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    apply(next);
    try { localStorage.setItem('theme', next); } catch {}
  });

  function apply(theme) {
    root.dataset.theme = theme;
    btn.textContent = theme === 'dark' ? 'Light theme' : 'Dark theme';
    btn.setAttribute('aria-pressed', theme === 'dark');
  }
})();

/* Projects: the rows are baked in; GitHub refreshes the star counts when reachable. */
(async function () {
  const rows = document.querySelectorAll('[data-repo]');
  for (const row of rows) {
    try {
      const res = await fetch('https://api.github.com/repos/' + row.dataset.repo);
      if (!res.ok) continue;
      const r = await res.json();
      const stars = row.querySelector('[data-field="stars"]');
      if (stars) stars.textContent = r.stargazers_count;
    } catch {}
  }
})();
