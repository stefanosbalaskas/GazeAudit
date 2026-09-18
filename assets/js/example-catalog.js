(() => {
  const root = document.querySelector('[data-example-catalog]');
  const controls = document.querySelector('[data-example-catalog-controls]');
  if (!root || !controls) return;

  const cards = Array.from(root.querySelectorAll('[data-example-card]'));
  const search = controls.querySelector('[data-example-catalog-search]');
  const dataFilter = controls.querySelector('[data-example-data-filter]');
  const focusFilter = controls.querySelector('[data-example-focus-filter]');
  const clear = controls.querySelector('[data-example-catalog-clear]');
  const status = document.querySelector('[data-example-catalog-status]');
  const empty = document.querySelector('[data-example-catalog-empty]');

  if (!search || !dataFilter || !focusFilter || !clear || !status || !empty) return;

  const normalize = (value) => String(value || '').trim().toLocaleLowerCase();

  const apply = () => {
    const query = normalize(search.value);
    const dataValue = dataFilter.value;
    const focusValue = focusFilter.value;
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = !query || normalize(card.dataset.exampleSearch).includes(query);
      const matchesData = !dataValue || card.dataset.exampleData === dataValue;
      const matchesFocus = !focusValue || card.dataset.exampleFocus === focusValue;
      const show = matchesQuery && matchesData && matchesFocus;
      card.hidden = !show;
      if (show) visible += 1;
    });

    const total = cards.length;
    const filtered = Boolean(query || dataValue || focusValue);
    status.textContent = filtered
      ? `Showing ${visible} of ${total} examples.`
      : `Showing all ${total} examples.`;
    empty.hidden = visible !== 0;
  };

  [search, dataFilter, focusFilter].forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  clear.addEventListener('click', () => {
    search.value = '';
    dataFilter.value = '';
    focusFilter.value = '';
    apply();
    search.focus();
  });

  apply();
})();
