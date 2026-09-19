(() => {
  const controls = document.querySelector('[data-robustness-controls]');
  const grid = document.querySelector('[data-robustness-grid]');
  if (!controls || !grid) return;

  const search = controls.querySelector('[data-robustness-search]');
  const kind = controls.querySelector('[data-robustness-kind]');
  const clear = controls.querySelector('[data-robustness-clear]');
  const status = document.querySelector('[data-robustness-status]');
  const empty = document.querySelector('[data-robustness-empty]');
  const cards = Array.from(grid.querySelectorAll('[data-robustness-card]'));

  if (!search || !kind || !clear || !status || !empty) return;

  const normalize = (value) => String(value || '').trim().toLocaleLowerCase();

  const apply = () => {
    const query = normalize(search.value);
    const kindValue = kind.value;
    let visible = 0;

    cards.forEach((card) => {
      const matchesSearch = (
        !query || normalize(card.dataset.robustnessSearch).includes(query)
      );
      const matchesKind = (
        !kindValue || card.dataset.robustnessKind === kindValue
      );
      const show = matchesSearch && matchesKind;
      card.hidden = !show;
      if (show) visible += 1;
    });

    const total = cards.length;
    const filtered = Boolean(query || kindValue);
    status.textContent = filtered
      ? `Showing ${visible} of ${total} diagnostic families.`
      : `Showing all ${total} diagnostic families.`;
    empty.hidden = visible !== 0;
  };

  [search, kind].forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  clear.addEventListener('click', () => {
    search.value = '';
    kind.value = '';
    apply();
    search.focus();
  });

  apply();
})();
