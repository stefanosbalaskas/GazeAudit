(() => {
  const root = document.querySelector('[data-reporting-contracts]');
  const controls = document.querySelector('[data-reporting-controls]');
  if (!root || !controls) return;

  const cards = Array.from(root.querySelectorAll('[data-reporting-contract]'));
  const search = controls.querySelector('[data-reporting-search]');
  const layer = controls.querySelector('[data-reporting-layer]');
  const kind = controls.querySelector('[data-reporting-kind]');
  const clear = controls.querySelector('[data-reporting-clear]');
  const status = document.querySelector('[data-reporting-status]');
  const empty = document.querySelector('[data-reporting-empty]');

  if (!search || !layer || !kind || !clear || !status || !empty) return;

  const normalize = (value) => String(value || '').trim().toLocaleLowerCase();

  const apply = () => {
    const query = normalize(search.value);
    const layerValue = layer.value;
    const kindValue = kind.value;
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = (
        !query || normalize(card.dataset.reportingSearch).includes(query)
      );
      const matchesLayer = (
        !layerValue || card.dataset.reportingLayer === layerValue
      );
      const matchesKind = (
        !kindValue || card.dataset.reportingKind === kindValue
      );
      const show = matchesQuery && matchesLayer && matchesKind;
      card.hidden = !show;
      if (show) visible += 1;
    });

    const total = cards.length;
    const filtered = Boolean(query || layerValue || kindValue);
    status.textContent = filtered
      ? `Showing ${visible} of ${total} reporting contracts.`
      : `Showing all ${total} reporting contracts.`;
    empty.hidden = visible !== 0;
  };

  [search, layer, kind].forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  clear.addEventListener('click', () => {
    search.value = '';
    layer.value = '';
    kind.value = '';
    apply();
    search.focus();
  });

  root.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-reporting-copy]');
    if (!button) return;

    const card = button.closest('[data-reporting-contract]');
    if (!card) return;

    const type = button.dataset.reportingCopy;
    const target = card.querySelector(`[data-reporting-template="${type}"]`);
    if (!target) return;

    try {
      await navigator.clipboard.writeText(target.textContent.trim());
      status.textContent = `${type} wording copied.`;
    } catch {
      status.textContent = (
        'Copy was unavailable. Select the reporting template manually.'
      );
    }
  });

  apply();
})();
