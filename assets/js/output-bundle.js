(() => {
  const explorer = document.querySelector('[data-bundle-explorer]');
  if (!explorer) return;

  const tabs = [...explorer.querySelectorAll('[data-bundle-item]')];
  const panel = explorer.querySelector('[data-bundle-panel]');
  if (!tabs.length || !panel) return;

  const name = panel.querySelector('[data-bundle-name]');
  const stage = panel.querySelector('[data-bundle-stage]');
  const purpose = panel.querySelector('[data-bundle-purpose]');
  const inspect = panel.querySelector('[data-bundle-inspect]');
  const boundary = panel.querySelector('[data-bundle-boundary]');
  const route = panel.querySelector('[data-bundle-route]');
  const copy = panel.querySelector('[data-bundle-copy]');
  const status = panel.querySelector('[data-bundle-status]');

  const setActive = (tab, { focus = false } = {}) => {
    tabs.forEach((candidate) => {
      const selected = candidate === tab;
      candidate.setAttribute('aria-selected', String(selected));
      candidate.tabIndex = selected ? 0 : -1;
    });

    name.textContent = tab.dataset.bundleName;
    stage.textContent = tab.dataset.bundleStage;
    purpose.textContent = tab.dataset.bundlePurpose;
    inspect.textContent = tab.dataset.bundleInspect;
    boundary.textContent = tab.dataset.bundleBoundary;
    route.textContent = tab.dataset.bundleRouteLabel;
    route.href = tab.dataset.bundleRoute;
    copy.dataset.copyValue = tab.dataset.bundleName;
    panel.setAttribute('aria-labelledby', tab.id);
    if (status) status.textContent = `${tab.dataset.bundleName} selected.`;
    if (focus) tab.focus({ preventScroll: true });
  };

  const move = (tab, offset) => {
    const index = tabs.indexOf(tab);
    const next = tabs[(index + offset + tabs.length) % tabs.length];
    setActive(next, { focus: true });
  };

  explorer.addEventListener('click', (event) => {
    const tab = event.target.closest('[data-bundle-item]');
    if (tab) {
      setActive(tab);
      return;
    }

    const copyButton = event.target.closest('[data-bundle-copy]');
    if (!copyButton) return;
    const value = copyButton.dataset.copyValue;
    const success = () => {
      copyButton.textContent = 'Copied';
      if (status) status.textContent = `${value} copied to clipboard.`;
      window.setTimeout(() => { copyButton.textContent = 'Copy artifact name'; }, 1600);
    };
    const failure = () => {
      copyButton.textContent = 'Copy manually';
      if (status) status.textContent = `Could not copy ${value} automatically.`;
    };

    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(value).then(success).catch(failure);
      return;
    }

    try {
      const helper = document.createElement('textarea');
      helper.value = value;
      helper.setAttribute('readonly', '');
      helper.className = 'bundle-copy-helper';
      document.body.appendChild(helper);
      helper.select();
      const copied = document.execCommand('copy');
      helper.remove();
      if (copied) success(); else failure();
    } catch (error) {
      failure();
    }
  });

  explorer.addEventListener('keydown', (event) => {
    const tab = event.target.closest('[data-bundle-item]');
    if (!tab) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(tab, 1);
    } else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
      event.preventDefault();
      move(tab, -1);
    } else if (event.key === 'Home') {
      event.preventDefault();
      setActive(tabs[0], { focus: true });
    } else if (event.key === 'End') {
      event.preventDefault();
      setActive(tabs[tabs.length - 1], { focus: true });
    }
  });

  setActive(tabs.find((tab) => tab.getAttribute('aria-selected') === 'true') || tabs[0]);
})();
