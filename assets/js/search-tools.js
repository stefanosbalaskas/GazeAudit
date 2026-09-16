(() => {
  const body = document.body;
  const dialog = document.querySelector('[data-search-dialog]');
  const input = document.querySelector('[data-site-search]');
  const results = document.querySelector('[data-search-results]');
  if (!dialog || !input || !results) return;

  const kindOrder = [
    'Guide',
    'Example',
    'Workflow',
    'Method',
    'Plot',
    'Case study',
    'Article',
    'Reference',
    'Evidence',
    'Start',
    'Documentation',
  ];
  const quickQueries = [
    ['Own data', 'first real audit'],
    ['Robustness', 'robustness'],
    ['AOI', 'AOI'],
    ['Publication', 'publication'],
  ];
  const relatedKindOrder = {
    Guide: ['Example', 'Workflow', 'Plot', 'Method', 'Article', 'Reference'],
    Example: ['Guide', 'Workflow', 'Plot', 'Method', 'Reference'],
    Workflow: ['Guide', 'Example', 'Plot', 'Method', 'Reference'],
    Method: ['Guide', 'Example', 'Workflow', 'Plot', 'Reference'],
    Plot: ['Guide', 'Example', 'Workflow', 'Method', 'Reference'],
    'Case study': ['Evidence', 'Guide', 'Workflow', 'Article', 'Reference'],
    Evidence: ['Case study', 'Reference', 'Article', 'Guide'],
    Article: ['Guide', 'Workflow', 'Case study', 'Reference'],
    Start: ['Guide', 'Example', 'Workflow', 'Reference'],
    Reference: ['Guide', 'Workflow', 'Evidence', 'Method'],
    Documentation: ['Guide', 'Workflow', 'Reference', 'Example'],
  };
  const relatedStopWords = new Set([
    'a', 'an', 'and', 'audit', 'audits', 'documentation', 'for', 'from', 'gaze',
    'gazeaudit', 'guide', 'guides', 'in', 'index', 'of', 'on', 'or', 'the', 'to',
    'with', 'workflow', 'workflows', 'example', 'examples', 'method', 'methods',
  ]);
  const relatedHubPaths = new Set([
    '/docs/',
    '/docs/workspace/',
    '/docs/planner/',
    '/docs/methods/',
    '/docs/guides/',
    '/docs/examples/',
    '/docs/plots/',
    '/docs/workflows/',
    '/docs/case-studies/',
    '/docs/articles/',
  ]);

  let index = null;
  let activeKind = 'All';

  const escapeHtml = (value) => String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  const buildUrl = (url) => {
    const baseurl = body.dataset.baseurl || '';
    return `${baseurl}${url}`.replace(/\/+/g, '/');
  };

  const normalisePath = (value) => {
    const baseurl = (body.dataset.baseurl || '').replace(/\/$/, '');
    let path = value || '/';
    try {
      path = new URL(path, window.location.origin).pathname;
    } catch (error) {
      path = String(path).split(/[?#]/, 1)[0];
    }
    if (baseurl && path.startsWith(`${baseurl}/`)) path = path.slice(baseurl.length);
    if (!path.startsWith('/')) path = `/${path}`;
    if (!/\.[a-z0-9]+$/i.test(path) && !path.endsWith('/')) path += '/';
    return path.replace(/\/+/g, '/');
  };

  const scoreItem = (item, terms) => {
    const title = item.title.toLowerCase();
    const category = item.category.toLowerCase();
    const description = item.description.toLowerCase();
    const keywords = item.keywords.toLowerCase();
    const kind = (item.kind || 'Documentation').toLowerCase();
    let score = 0;
    for (const term of terms) {
      if (title === term) score += 20;
      if (title.startsWith(term)) score += 12;
      if (title.includes(term)) score += 8;
      if (keywords.includes(term)) score += 5;
      if (kind.includes(term)) score += 4;
      if (category.includes(term)) score += 3;
      if (description.includes(term)) score += 2;
    }
    return score;
  };

  const controls = document.createElement('div');
  controls.className = 'search-discovery';
  controls.innerHTML = `
    <div class="search-facets" data-search-facets role="group" aria-label="Filter search results by documentation type"></div>
    <div class="search-quick-queries" data-search-quick-queries aria-label="Suggested searches"></div>
    <p class="search-result-summary" data-search-result-summary aria-hidden="true"></p>`;
  input.insertAdjacentElement('afterend', controls);

  const facetContainer = controls.querySelector('[data-search-facets]');
  const quickContainer = controls.querySelector('[data-search-quick-queries]');
  const summary = controls.querySelector('[data-search-result-summary]');

  quickContainer.innerHTML = quickQueries.map(([label, query]) => `
    <button type="button" class="search-query-chip" data-search-query="${escapeHtml(query)}">${escapeHtml(label)}</button>`).join('');

  const loadIndex = async () => {
    if (index) return index;
    const url = body.dataset.searchIndex;
    if (!url) return [];
    const response = await fetch(url, { credentials: 'same-origin' });
    if (!response.ok) throw new Error(`Search index request failed: ${response.status}`);
    index = await response.json();
    return index;
  };

  const renderFacets = () => {
    if (!index || !facetContainer) return;
    const counts = new Map();
    index.forEach((item) => {
      const kind = item.kind || 'Documentation';
      counts.set(kind, (counts.get(kind) || 0) + 1);
    });
    const orderedKinds = [...counts.keys()].sort((a, b) => {
      const ai = kindOrder.indexOf(a);
      const bi = kindOrder.indexOf(b);
      const ar = ai === -1 ? kindOrder.length : ai;
      const br = bi === -1 ? kindOrder.length : bi;
      return ar - br || a.localeCompare(b);
    });
    const kinds = ['All', ...orderedKinds];
    if (!kinds.includes(activeKind)) activeKind = 'All';
    facetContainer.innerHTML = kinds.map((kind) => {
      const count = kind === 'All' ? index.length : counts.get(kind);
      return `<button type="button" class="search-facet" data-search-kind="${escapeHtml(kind)}" aria-pressed="${kind === activeKind}">${escapeHtml(kind)} <span>${count}</span></button>`;
    }).join('');
  };

  const rankedItems = (query) => {
    const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let items = index || [];
    if (activeKind !== 'All') {
      items = items.filter((item) => (item.kind || 'Documentation') === activeKind);
    }
    if (terms.length) {
      return items
        .map((item) => ({ item, score: scoreItem(item, terms) }))
        .filter(({ score }) => score > 0)
        .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title))
        .map(({ item }) => item);
    }
    return [...items].sort((a, b) => {
      const ai = kindOrder.indexOf(a.kind || 'Documentation');
      const bi = kindOrder.indexOf(b.kind || 'Documentation');
      const ar = ai === -1 ? kindOrder.length : ai;
      const br = bi === -1 ? kindOrder.length : bi;
      return ar - br || a.title.localeCompare(b.title);
    });
  };

  const render = () => {
    if (!index) return;
    const matched = rankedItems(input.value);
    const visible = matched.slice(0, 12);
    if (summary) {
      const label = activeKind === 'All' ? 'all documentation types' : activeKind;
      summary.textContent = `${matched.length} ${matched.length === 1 ? 'result' : 'results'} · ${label}`;
    }
    if (!visible.length) {
      const suffix = activeKind === 'All' ? '' : ` in ${escapeHtml(activeKind)}`;
      results.innerHTML = `<p class="search-empty">No matching documentation${suffix}. Try another term or choose All.</p>`;
      return;
    }
    results.innerHTML = visible.map((item, indexPosition) => `
      <a class="search-result${indexPosition === 0 ? ' is-selected' : ''}" href="${buildUrl(item.url)}" data-search-result data-index="${indexPosition}">
        <span class="search-result-meta">
          <span class="search-result-kind">${escapeHtml(item.kind || 'Documentation')}</span>
          <span class="search-result-category">${escapeHtml(item.category)}</span>
        </span>
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.description)}</span>
      </a>`).join('');
  };

  const topicTokens = (item) => {
    const text = [item.title, item.category, item.description, item.keywords, item.url]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return new Set(text
      .split(/[^a-z0-9]+/)
      .filter((token) => token.length > 2 && !relatedStopWords.has(token)));
  };

  const relatedScore = (current, candidate) => {
    const currentKind = current.kind || 'Documentation';
    const candidateKind = candidate.kind || 'Documentation';
    const preferredKinds = relatedKindOrder[currentKind] || relatedKindOrder.Documentation;
    const kindPosition = preferredKinds.indexOf(candidateKind);
    const currentTokens = topicTokens(current);
    const candidateTokens = topicTokens(candidate);
    let sharedTokens = 0;
    currentTokens.forEach((token) => {
      if (candidateTokens.has(token)) sharedTokens += 1;
    });
    const sameCategory = Boolean(
      current.category && candidate.category && current.category === candidate.category,
    );
    if (sharedTokens === 0 && !sameCategory) return 0;

    let score = Math.min(sharedTokens, 5) * 3;
    if (sameCategory) score += 6;
    if (kindPosition !== -1) score += Math.max(1, 7 - kindPosition);
    if (candidateKind !== currentKind) score += 1;
    return score;
  };

  const renderRelated = () => {
    const article = document.querySelector('.doc-article');
    const pagination = article?.querySelector('[data-page-pagination]');
    if (!article || !pagination || !index?.length) return;

    const currentPath = normalisePath(window.location.pathname);
    if (relatedHubPaths.has(currentPath)) return;
    const current = index.find((item) => normalisePath(item.url) === currentPath);
    if (!current) return;

    const related = index
      .filter((item) => normalisePath(item.url) !== currentPath)
      .map((item) => ({ item, score: relatedScore(current, item) }))
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title))
      .map(({ item }) => item)
      .slice(0, 4);

    if (!related.length) return;

    const section = document.createElement('section');
    section.className = 'related-content';
    section.dataset.relatedContent = '';
    section.setAttribute('aria-labelledby', 'related-content-title');
    section.setAttribute('aria-describedby', 'related-content-note');
    section.innerHTML = `
      <div class="related-content-head">
        <div>
          <p class="related-content-kicker">Continue exploring</p>
          <h2 id="related-content-title">Related documentation for this topic</h2>
        </div>
        <p id="related-content-note">Generated from documentation metadata and content type. This is navigation support, not a scientific recommendation.</p>
      </div>
      <div class="related-content-grid">
        ${related.map((item) => `
          <a class="related-content-card" href="${buildUrl(item.url)}">
            <span class="related-content-meta">
              <span class="related-content-kind">${escapeHtml(item.kind || 'Documentation')}</span>
              <span>${escapeHtml(item.category)}</span>
            </span>
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.description)}</span>
            <span class="related-content-cta" aria-hidden="true">Open →</span>
          </a>`).join('')}
      </div>`;
    pagination.insertAdjacentElement('beforebegin', section);
  };

  const refresh = async () => {
    try {
      await loadIndex();
      renderFacets();
      render();
    } catch (error) {
      // The core site search retains its own offline fallback.
    }
  };

  input.addEventListener('focus', refresh);
  input.addEventListener('input', refresh);

  facetContainer?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-search-kind]');
    if (!button) return;
    activeKind = button.dataset.searchKind;
    renderFacets();
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.focus({ preventScroll: true });
  });

  quickContainer?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-search-query]');
    if (!button) return;
    activeKind = 'All';
    input.value = button.dataset.searchQuery;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.focus({ preventScroll: true });
  });

  document.querySelectorAll('[data-search-open]').forEach((button) => {
    button.addEventListener('click', () => {
      window.requestAnimationFrame(() => refresh());
    });
  });

  if (document.querySelector('.doc-article')) {
    window.requestAnimationFrame(() => {
      loadIndex().then(renderRelated).catch(() => {
        // Related navigation is progressive enhancement; core docs remain intact.
      });
    });
  }
})();
