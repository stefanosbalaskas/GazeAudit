(() => {
  const grid = document.querySelector('[data-diagnostic-grid]');
  const controls = document.querySelector('[data-diagnostic-controls]');
  if (!grid || !controls) return;

  const cards = Array.from(grid.querySelectorAll('[data-diagnostic-card]'));
  const search = controls.querySelector('[data-diagnostic-search]');
  const family = controls.querySelector('[data-diagnostic-family]');
  const clear = controls.querySelector('[data-diagnostic-clear]');
  const status = document.querySelector('[data-diagnostic-status]');
  const empty = document.querySelector('[data-diagnostic-empty]');

  if (!search || !family || !clear || !status || !empty) return;

  const normalize = (value) => (
    String(value || '').trim().toLocaleLowerCase()
  );

  const apply = () => {
    const query = normalize(search.value);
    const selectedFamily = family.value;
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = (
        !query || normalize(card.dataset.diagnosticSearch).includes(query)
      );
      const matchesFamily = (
        !selectedFamily || card.dataset.diagnosticFamily === selectedFamily
      );
      const show = matchesQuery && matchesFamily;
      card.hidden = !show;
      if (show) visible += 1;
    });

    const filtered = Boolean(query || selectedFamily);
    status.textContent = filtered
      ? `Showing ${visible} of ${cards.length} diagnostics.`
      : `Showing all ${cards.length} diagnostics.`;
    empty.hidden = visible !== 0;
  };

  [search, family].forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  clear.addEventListener('click', () => {
    search.value = '';
    family.value = '';
    apply();
    search.focus();
  });

  grid.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-diagnostic-copy]');
    if (!button) return;

    const card = button.closest('[data-diagnostic-card]');
    if (!card) return;

    const type = button.dataset.diagnosticCopy;
    const target = card.querySelector(`[data-diagnostic-template="${type}"]`);
    if (!target) return;

    try {
      await navigator.clipboard.writeText(target.textContent.trim());
      status.textContent = `${type} wording copied.`;
    } catch {
      status.textContent = (
        'Copy was unavailable. Select the diagnostic wording manually.'
      );
    }
  });

  apply();
})();
