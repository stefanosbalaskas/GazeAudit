(() => {
  const root = document.documentElement;

  const themeToggle = document.querySelector('[data-theme-toggle]');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = root.dataset.theme;
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const effective = current === 'dark' || (current === 'auto' && prefersDark) ? 'dark' : 'light';
      const next = effective === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('gazeaudit-theme', next); } catch (e) {}
    });
  }

  const menuToggle = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('[data-mobile-menu]');
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
      const open = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!open));
      mobileMenu.hidden = open;
    });
  }

  const normalizePath = (value) => value.replace(/index\.html$/, '').replace(/\.html$/, '/').replace(/\/+$/, '/');
  const currentPath = normalizePath(window.location.pathname);
  document.querySelectorAll('[data-docs-nav] a').forEach((link) => {
    const target = normalizePath(new URL(link.href, window.location.href).pathname);
    if (target === currentPath) link.setAttribute('aria-current', 'page');
  });

  const filter = document.querySelector('[data-nav-filter]');
  if (filter) {
    filter.addEventListener('input', () => {
      const term = filter.value.trim().toLowerCase();
      document.querySelectorAll('[data-docs-nav] a').forEach((link) => {
        link.hidden = term && !link.textContent.toLowerCase().includes(term);
      });
      document.querySelectorAll('[data-docs-nav] .nav-label').forEach((label) => {
        label.hidden = Boolean(term);
      });
    });
  }

  const article = document.querySelector('.doc-article');
  const toc = document.querySelector('[data-toc]');
  if (article && toc) {
    const headings = [...article.querySelectorAll('h2, h3')];
    headings.forEach((heading, index) => {
      if (!heading.id) {
        heading.id = heading.textContent
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9\s-]/g, '')
          .replace(/\s+/g, '-') || `section-${index + 1}`;
      }
      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      link.dataset.level = heading.tagName === 'H3' ? '3' : '2';
      toc.appendChild(link);
    });
    if (!headings.length) {
      const tocPanel = toc.closest('.toc');
      if (tocPanel) tocPanel.hidden = true;
    }
  }

  document.querySelectorAll('pre > code').forEach((code) => {
    const pre = code.parentElement;
    if (!pre || pre.querySelector('.copy-code')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.textContent = 'Copied';
        setTimeout(() => { button.textContent = 'Copy'; }, 1400);
      } catch (e) {
        button.textContent = 'Select';
      }
    });
    pre.appendChild(button);
  });
})();
