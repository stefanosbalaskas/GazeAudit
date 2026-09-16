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
})();
