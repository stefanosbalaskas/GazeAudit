(() => {
  const explore = document.querySelector('[data-explore-menu]');
  if (!explore) return;

  const summary = explore.querySelector('summary');

  const closeExplore = ({ focus = false } = {}) => {
    if (!explore.open) return;
    explore.open = false;
    if (focus) summary?.focus();
  };

  const syncCurrentState = () => {
    const hasCurrent = Boolean(explore.querySelector('a[aria-current="page"]'));
    summary?.classList.toggle('is-current', hasCurrent);
    if (summary) {
      if (hasCurrent) summary.setAttribute('aria-current', 'page');
      else summary.removeAttribute('aria-current');
    }
  };

  explore.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeExplore();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !explore.open) return;
    event.preventDefault();
    closeExplore({ focus: true });
  });

  document.addEventListener('click', (event) => {
    if (explore.open && !explore.contains(event.target)) closeExplore();
  });

  syncCurrentState();
})();
