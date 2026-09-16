(() => {
  const root = document.querySelector('[data-plot-gallery]');
  const toolbar = document.querySelector('[data-plot-gallery-toolbar]');
  if (!root || !toolbar) return;

  const cards = Array.from(root.querySelectorAll('[data-gallery-card]'));
  const search = toolbar.querySelector('[data-gallery-search]');
  const buttons = Array.from(toolbar.querySelectorAll('[data-gallery-filter]'));
  const count = toolbar.querySelector('[data-gallery-count]');
  const shareStatus = toolbar.querySelector('[data-gallery-share-status]');
  const validCategories = new Set(buttons.map((button) => button.dataset.galleryFilter || 'all'));
  const params = new URLSearchParams(window.location.search);
  const requestedCategory = params.get('category') || 'all';
  let category = validCategories.has(requestedCategory) ? requestedCategory : 'all';

  if (search) search.value = params.get('q') || '';
  buttons.forEach((button) => {
    button.setAttribute('aria-pressed', String((button.dataset.galleryFilter || 'all') === category));
  });

  const syncURL = () => {
    const url = new URL(window.location.href);
    const query = (search?.value || '').trim();
    if (category === 'all') url.searchParams.delete('category');
    else url.searchParams.set('category', category);
    if (query) url.searchParams.set('q', query);
    else url.searchParams.delete('q');
    window.history.replaceState({}, '', url);
  };

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

    if (count) count.textContent = `${visible} of ${cards.length} plots`;
  };

  const fallbackCopy = (text) => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    const copied = document.execCommand('copy');
    textarea.remove();
    if (!copied) throw new Error('copy command failed');
  };

  const copyPlotLink = async (button) => {
    const plotId = button.dataset.plotId;
    if (!plotId) return;

    const url = new URL(window.location.href);
    url.hash = `plot-${plotId}`;
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(url.href);
      else fallbackCopy(url.href);
      const original = button.textContent;
      button.textContent = 'Copied';
      if (shareStatus) shareStatus.textContent = `Copied stable link for ${plotId}.`;
      window.setTimeout(() => {
        button.textContent = original;
      }, 1600);
    } catch (error) {
      if (shareStatus) shareStatus.textContent = 'Could not copy the plot link. Use the page URL and plot anchor instead.';
      console.error('GazeAudit plot link copy failed', error);
    }
  };

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      category = button.dataset.galleryFilter || 'all';
      buttons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      apply();
      syncURL();
    });
  });

  search?.addEventListener('input', () => {
    apply();
    syncURL();
  });

  root.querySelectorAll('[data-copy-plot-link]').forEach((button) => {
    button.addEventListener('click', () => copyPlotLink(button));
  });

  apply();
})();
