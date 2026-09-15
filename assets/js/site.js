(() => {
  const root = document.documentElement;
  const body = document.body;

  const normalizePath = (value) => value
    .replace(/index\.html$/, '')
    .replace(/\.html$/, '/')
    .replace(/\/+$/, '/');

  const currentPath = normalizePath(window.location.pathname);

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
  const closeMobileMenu = () => {
    if (!menuToggle || !mobileMenu) return;
    menuToggle.setAttribute('aria-expanded', 'false');
    mobileMenu.hidden = true;
  };
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
      const open = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!open));
      mobileMenu.hidden = open;
    });
    mobileMenu.addEventListener('click', (event) => {
      if (event.target.closest('a')) closeMobileMenu();
    });
  }

  const markCurrentNavigation = (container) => {
    if (!container) return;
    const links = [...container.querySelectorAll('a')];
    links.forEach((link) => link.removeAttribute('aria-current'));
    const candidates = links
      .map((link) => ({ link, target: normalizePath(new URL(link.href, window.location.href).pathname) }))
      .filter(({ target }) => currentPath === target || currentPath.startsWith(target));
    if (!candidates.length) return;
    const exact = candidates.find(({ target }) => target === currentPath);
    const selected = exact || candidates.sort((a, b) => b.target.length - a.target.length)[0];
    selected.link.setAttribute('aria-current', 'page');
  };

  markCurrentNavigation(document.querySelector('[data-primary-nav]'));
  markCurrentNavigation(document.querySelector('[data-mobile-primary-nav]'));

  const navLinks = [...document.querySelectorAll('[data-docs-nav] a')];
  navLinks.forEach((link) => {
    const target = normalizePath(new URL(link.href, window.location.href).pathname);
    if (target === currentPath) link.setAttribute('aria-current', 'page');
  });

  const filter = document.querySelector('[data-nav-filter]');
  if (filter) {
    filter.addEventListener('input', () => {
      const term = filter.value.trim().toLowerCase();
      navLinks.forEach((link) => {
        link.hidden = Boolean(term) && !link.textContent.toLowerCase().includes(term);
      });
      document.querySelectorAll('[data-docs-nav] .nav-label').forEach((label) => {
        label.hidden = Boolean(term);
      });
    });
  }

  const article = document.querySelector('.doc-article');
  const toc = document.querySelector('[data-toc]');
  const tocLinks = [];
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
      tocLinks.push({ heading, link });
    });
    if (!headings.length) {
      const tocPanel = toc.closest('.toc');
      if (tocPanel) tocPanel.hidden = true;
    } else if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (!visible) return;
        tocLinks.forEach(({ heading, link }) => {
          if (heading === visible.target) link.setAttribute('aria-current', 'true');
          else link.removeAttribute('aria-current');
        });
      }, { rootMargin: '-18% 0px -68% 0px', threshold: [0, 1] });
      tocLinks.forEach(({ heading }) => observer.observe(heading));
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

  const copyPageLink = document.querySelector('[data-copy-page-link]');
  if (copyPageLink) {
    copyPageLink.addEventListener('click', async () => {
      const pageUrl = window.location.href.split('#')[0];
      try {
        await navigator.clipboard.writeText(pageUrl);
        copyPageLink.textContent = 'Copied';
        setTimeout(() => { copyPageLink.textContent = 'Copy page link'; }, 1400);
      } catch (e) {
        copyPageLink.textContent = 'Copy unavailable';
      }
    });
  }

  const progress = document.querySelector('[data-reading-progress]');
  if (progress && article) {
    const updateProgress = () => {
      const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const pct = Math.max(0, Math.min(1, window.scrollY / max));
      progress.style.transform = `scaleX(${pct})`;
    };
    updateProgress();
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
  }

  const backToTop = document.querySelector('[data-back-to-top]');
  if (backToTop) {
    backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  const breadcrumbs = document.querySelector('[data-breadcrumbs]');
  if (breadcrumbs) {
    const baseurl = body.dataset.baseurl || '';
    const sectionMap = [
      ['/docs/guides/', 'Guides'],
      ['/docs/examples/', 'Examples'],
      ['/docs/workflows/', 'Workflows'],
      ['/docs/case-studies/', 'Case studies'],
      ['/docs/articles/', 'Articles'],
      ['/docs/reference/', 'Reference']
    ];
    const active = navLinks.find((link) => normalizePath(new URL(link.href, window.location.href).pathname) === currentPath);
    const crumbs = [
      { label: 'Home', href: `${baseurl}/` },
      { label: 'Docs', href: `${baseurl}/docs/` }
    ];
    const relativePath = currentPath.replace(normalizePath(baseurl || '/'), '/');
    const section = sectionMap.find(([prefix]) => relativePath.includes(prefix));
    if (section && !relativePath.endsWith(section[0])) crumbs.push({ label: section[1], href: `${baseurl}${section[0]}` });
    if (active && active.textContent.trim() !== 'Documentation hub') crumbs.push({ label: active.textContent.trim(), href: null });
    breadcrumbs.innerHTML = crumbs.map((crumb, index) => {
      const separator = index ? '<span aria-hidden="true">/</span>' : '';
      return crumb.href
        ? `${separator}<a href="${crumb.href}">${crumb.label}</a>`
        : `${separator}<span aria-current="page">${crumb.label}</span>`;
    }).join('');
  }

  const pagination = document.querySelector('[data-page-pagination]');
  if (pagination && navLinks.length) {
    const activeIndex = navLinks.findIndex((link) => normalizePath(new URL(link.href, window.location.href).pathname) === currentPath);
    if (activeIndex >= 0) {
      const previous = navLinks[activeIndex - 1];
      const next = navLinks[activeIndex + 1];
      const cards = [];
      if (previous) cards.push(`<a class="page-nav-card previous" href="${previous.href}"><span>Previous</span><strong>← ${previous.textContent.trim()}</strong></a>`);
      if (next) cards.push(`<a class="page-nav-card next" href="${next.href}"><span>Next</span><strong>${next.textContent.trim()} →</strong></a>`);
      pagination.innerHTML = cards.join('');
      if (!cards.length) pagination.hidden = true;
    } else {
      pagination.hidden = true;
    }
  }

  const dialog = document.querySelector('[data-search-dialog]');
  const searchInput = document.querySelector('[data-site-search]');
  const searchResults = document.querySelector('[data-search-results]');
  const closeSearch = document.querySelector('[data-search-close]');
  let searchIndex = null;
  let selectedResult = -1;

  const buildUrl = (url) => {
    const baseurl = body.dataset.baseurl || '';
    return `${baseurl}${url}`.replace(/\/+/g, '/');
  };

  const scoreItem = (item, terms) => {
    const title = item.title.toLowerCase();
    const category = item.category.toLowerCase();
    const description = item.description.toLowerCase();
    const keywords = item.keywords.toLowerCase();
    let score = 0;
    for (const term of terms) {
      if (title === term) score += 20;
      if (title.startsWith(term)) score += 12;
      if (title.includes(term)) score += 8;
      if (keywords.includes(term)) score += 5;
      if (category.includes(term)) score += 3;
      if (description.includes(term)) score += 2;
    }
    return score;
  };

  const renderSearch = (query = '') => {
    if (!searchResults || !searchIndex) return;
    const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let items = searchIndex;
    if (terms.length) {
      items = searchIndex
        .map((item) => ({ item, score: scoreItem(item, terms) }))
        .filter(({ score }) => score > 0)
        .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title))
        .map(({ item }) => item);
    }
    items = items.slice(0, 9);
    selectedResult = items.length ? 0 : -1;
    if (!items.length) {
      searchResults.innerHTML = '<p class="search-empty">No matching documentation. Try a method, dataset, or workflow term.</p>';
      return;
    }
    searchResults.innerHTML = items.map((item, index) => `
      <a class="search-result${index === selectedResult ? ' is-selected' : ''}" href="${buildUrl(item.url)}" data-search-result data-index="${index}">
        <span class="search-result-category">${item.category}</span>
        <strong>${item.title}</strong>
        <span>${item.description}</span>
      </a>`).join('');
  };

  const ensureSearchIndex = async () => {
    if (searchIndex) return searchIndex;
    const url = body.dataset.searchIndex;
    if (!url) return [];
    const response = await fetch(url, { credentials: 'same-origin' });
    if (!response.ok) throw new Error(`Search index request failed: ${response.status}`);
    searchIndex = await response.json();
    return searchIndex;
  };

  const openSearch = async () => {
    if (!dialog || !searchInput) return;
    try {
      await ensureSearchIndex();
      if (typeof dialog.showModal === 'function') dialog.showModal();
      else dialog.setAttribute('open', '');
      renderSearch(searchInput.value);
      requestAnimationFrame(() => searchInput.focus());
    } catch (error) {
      if (searchResults) searchResults.innerHTML = '<p class="search-empty">Search index could not be loaded. Use the documentation menu while this page is offline.</p>';
      if (typeof dialog.showModal === 'function' && !dialog.open) dialog.showModal();
    }
  };

  const closeSearchDialog = () => {
    if (!dialog) return;
    if (typeof dialog.close === 'function') dialog.close();
    else dialog.removeAttribute('open');
  };

  document.querySelectorAll('[data-search-open]').forEach((button) => button.addEventListener('click', openSearch));
  if (closeSearch) closeSearch.addEventListener('click', closeSearchDialog);
  if (dialog) {
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) closeSearchDialog();
    });
  }
  if (searchInput) {
    searchInput.addEventListener('input', () => renderSearch(searchInput.value));
    searchInput.addEventListener('keydown', (event) => {
      const results = [...document.querySelectorAll('[data-search-result]')];
      if (!results.length) return;
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        const delta = event.key === 'ArrowDown' ? 1 : -1;
        selectedResult = (selectedResult + delta + results.length) % results.length;
        results.forEach((result, index) => result.classList.toggle('is-selected', index === selectedResult));
        results[selectedResult].scrollIntoView({ block: 'nearest' });
      } else if (event.key === 'Enter' && selectedResult >= 0) {
        event.preventDefault();
        results[selectedResult].click();
      }
    });
  }

  document.addEventListener('keydown', (event) => {
    const target = event.target;
    const typing = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target?.isContentEditable;
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openSearch();
    } else if (event.key === '/' && !typing && dialog && !dialog.open) {
      event.preventDefault();
      openSearch();
    } else if (event.key === 'Escape' && mobileMenu && !mobileMenu.hidden) {
      closeMobileMenu();
      menuToggle?.focus();
    }
  });
})();

(() => {
  const body = document.body;
  const docsShell = document.querySelector('.docs-shell');
  const docsNav = document.querySelector('[data-docs-nav]');
  const toc = document.querySelector('[data-toc]');
  if (!docsShell || !docsNav) return;

  body.classList.add('site-js');

  const dock = document.createElement('nav');
  dock.className = 'mobile-doc-dock';
  dock.dataset.mobileDocDock = '';
  dock.setAttribute('aria-label', 'Documentation shortcuts');
  dock.innerHTML = `
    <button type="button" data-mobile-doc-open="browse">Browse docs</button>
    <button type="button" data-mobile-doc-open="toc">On this page</button>
    <button type="button" data-search-open>Search</button>`;

  const mobileDocDialog = document.createElement('dialog');
  mobileDocDialog.className = 'mobile-doc-dialog';
  mobileDocDialog.dataset.mobileDocDialog = '';
  mobileDocDialog.setAttribute('aria-labelledby', 'mobile-doc-dialog-title');
  mobileDocDialog.innerHTML = `
    <div class="mobile-doc-dialog-inner">
      <div class="mobile-doc-dialog-head">
        <div>
          <p class="eyebrow">Documentation</p>
          <h2 id="mobile-doc-dialog-title">Browse documentation</h2>
        </div>
        <button type="button" class="mobile-doc-close" data-mobile-doc-close aria-label="Close documentation navigator">×</button>
      </div>
      <div class="mobile-doc-dialog-content" data-mobile-doc-content></div>
    </div>`;

  docsShell.insertBefore(dock, docsShell.firstChild);
  document.body.appendChild(mobileDocDialog);

  const mobileDocTitle = mobileDocDialog.querySelector('#mobile-doc-dialog-title');
  const mobileDocContent = mobileDocDialog.querySelector('[data-mobile-doc-content]');
  const tocButton = dock.querySelector('[data-mobile-doc-open="toc"]');

  const openMobileDocs = (mode) => {
    if (!mobileDocContent || !mobileDocTitle) return;
    mobileDocContent.innerHTML = '';
    if (mode === 'toc') {
      mobileDocTitle.textContent = 'On this page';
      if (toc && toc.querySelector('a')) {
        const clone = toc.cloneNode(true);
        clone.removeAttribute('data-toc');
        clone.classList.add('mobile-doc-toc');
        mobileDocContent.appendChild(clone);
      } else {
        mobileDocContent.innerHTML = '<p class="mobile-doc-empty">This page has no section headings.</p>';
      }
    } else {
      mobileDocTitle.textContent = 'Browse documentation';
      const clone = docsNav.cloneNode(true);
      clone.removeAttribute('data-docs-nav');
      clone.classList.add('mobile-doc-browser');
      mobileDocContent.appendChild(clone);
    }
    if (typeof mobileDocDialog.showModal === 'function') mobileDocDialog.showModal();
    else mobileDocDialog.setAttribute('open', '');
  };

  if (tocButton && (!toc || !toc.querySelector('a'))) tocButton.disabled = true;

  dock.querySelectorAll('[data-mobile-doc-open]').forEach((button) => {
    button.addEventListener('click', () => openMobileDocs(button.dataset.mobileDocOpen));
  });

  const closeMobileDocs = () => {
    if (typeof mobileDocDialog.close === 'function') mobileDocDialog.close();
    else mobileDocDialog.removeAttribute('open');
  };
  mobileDocDialog.querySelector('[data-mobile-doc-close]')?.addEventListener('click', closeMobileDocs);
  mobileDocDialog.addEventListener('click', (event) => {
    if (event.target === mobileDocDialog) closeMobileDocs();
  });
  mobileDocContent?.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMobileDocs();
  });

  dock.querySelector('[data-search-open]')?.addEventListener('click', () => {
    document.querySelector('.mobile-menu [data-search-open], .header-actions [data-search-open]')?.click();
  });
})();
