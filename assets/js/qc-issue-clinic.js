(() => {
  const root = document.querySelector('[data-qc-clinic]');
  const controls = document.querySelector('[data-qc-clinic-controls]');
  if (!root || !controls) return;

  const cards = Array.from(root.querySelectorAll('[data-qc-issue]'));
  const search = controls.querySelector('[data-qc-clinic-search]');
  const scope = controls.querySelector('[data-qc-clinic-scope]');
  const clear = controls.querySelector('[data-qc-clinic-clear]');
  const status = document.querySelector('[data-qc-clinic-status]');
  const empty = document.querySelector('[data-qc-clinic-empty]');

  if (!search || !scope || !clear || !status || !empty) return;

  const normalize = (value) => String(value || '').trim().toLocaleLowerCase();

  const apply = () => {
    const query = normalize(search.value);
    const scopeValue = scope.value;
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = !query || normalize(card.dataset.qcSearch).includes(query);
      const matchesScope = !scopeValue || card.dataset.qcScope === scopeValue;
      const show = matchesQuery && matchesScope;
      card.hidden = !show;
      if (show) visible += 1;
    });

    const total = cards.length;
    const filtered = Boolean(query || scopeValue);
    status.textContent = filtered
      ? `Showing ${visible} of ${total} issue families.`
      : `Showing all ${total} issue families.`;
    empty.hidden = visible !== 0;
  };

  [search, scope].forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  clear.addEventListener('click', () => {
    search.value = '';
    scope.value = '';
    apply();
    search.focus();
  });

  apply();
})();
