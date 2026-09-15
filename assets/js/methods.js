(function () {
  const root = document.querySelector('[data-method-explorer]');
  if (!root) return;

  const controls = root.querySelector('[data-method-controls]');
  const input = root.querySelector('[data-method-search]');
  const buttons = [...root.querySelectorAll('[data-method-filter]')];
  const cards = [...root.querySelectorAll('[data-method-card]')];
  const count = root.querySelector('[data-method-result-count]');
  const empty = root.querySelector('[data-method-empty]');
  const copyButtons = [...root.querySelectorAll('[data-copy-sequence]')];
  const validPhases = new Set(buttons.map(button => button.dataset.methodFilter).filter(Boolean));
  const params = new URLSearchParams(window.location.search);
  let phase = params.get('phase') || 'all';

  if (!validPhases.has(phase)) phase = 'all';
  if (input) input.value = params.get('q') || '';
  if (controls) controls.hidden = false;

  function normalized(value) {
    return String(value || '').trim().toLowerCase();
  }

  function syncUrl() {
    if (!window.history || !window.history.replaceState) return;
    const next = new URL(window.location.href);
    const query = normalized(input && input.value);
    if (phase === 'all') next.searchParams.delete('phase');
    else next.searchParams.set('phase', phase);
    if (query) next.searchParams.set('q', input.value.trim());
    else next.searchParams.delete('q');
    window.history.replaceState(null, '', next);
  }

  function applyFilters(updateUrl) {
    const query = normalized(input && input.value);
    let visible = 0;

    cards.forEach(card => {
      const phaseMatch = phase === 'all' || card.dataset.phase === phase;
      const searchText = normalized(card.dataset.search || card.textContent);
      const queryMatch = !query || searchText.includes(query);
      card.hidden = !(phaseMatch && queryMatch);
      if (!card.hidden) visible += 1;
    });

    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.methodFilter === phase));
    });

    if (count) count.textContent = `${visible} of ${cards.length} method families shown`;
    if (empty) empty.hidden = visible !== 0;
    if (updateUrl) syncUrl();
  }

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      phase = button.dataset.methodFilter || 'all';
      applyFilters(true);
    });
  });

  if (input) {
    input.addEventListener('input', () => applyFilters(true));
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape' && input.value) {
        input.value = '';
        applyFilters(true);
      }
    });
  }

  copyButtons.forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const sequence = button.dataset.copySequence || '';
      if (!sequence || !navigator.clipboard) return;
      try {
        await navigator.clipboard.writeText(sequence);
        const previous = button.textContent;
        button.textContent = 'Copied';
        window.setTimeout(() => { button.textContent = previous; }, 1200);
      } catch (error) {
        button.textContent = 'Copy unavailable';
      }
    });
  });

  const indexUrl = root.dataset.methodIndex;
  if (indexUrl && window.fetch) {
    fetch(indexUrl)
      .then(response => {
        if (!response.ok) throw new Error(`method index ${response.status}`);
        return response.json();
      })
      .then(index => {
        if (!Array.isArray(index)) throw new Error('method index is not an array');
        const rendered = new Set(cards.map(card => card.dataset.methodId));
        const catalog = new Set(index.map(item => item && item.id));
        const sameIds = rendered.size === catalog.size && [...rendered].every(id => catalog.has(id));
        root.dataset.catalogState = sameIds ? 'verified' : 'mismatch';
      })
      .catch(() => {
        root.dataset.catalogState = 'unavailable';
      });
  }

  applyFilters(false);
}());
