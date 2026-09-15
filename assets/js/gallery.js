(() => {
  const root = document.querySelector('[data-plot-gallery]');
  const toolbar = document.querySelector('[data-plot-gallery-toolbar]');
  if (!root || !toolbar) return;

  const cards = Array.from(root.querySelectorAll('[data-gallery-card]'));
  const search = toolbar.querySelector('[data-gallery-search]');
  const buttons = Array.from(toolbar.querySelectorAll('[data-gallery-filter]'));
  const count = toolbar.querySelector('[data-gallery-count]');
  const empty = root.querySelector('[data-gallery-empty]');
  let category = 'all';

  const apply = () => {
    const query = (search?.value || '').trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const categoryOK = category === 'all' || card.dataset.category === category;
      const haystack = (card.dataset.search || card.textContent || '').toLowerCase();
      const queryOK = !query || haystack.includes(query);
      card.hidden = !(categoryOK && queryOK);
      if (!card.hidden) visible += 1;
    });

    if (empty) empty.hidden = visible !== 0;
    if (count) count.textContent = `${visible} of ${cards.length} plots`;
  };

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      category = button.dataset.galleryFilter || 'all';
      buttons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      apply();
    });
  });

  search?.addEventListener('input', apply);
  apply();
})();
