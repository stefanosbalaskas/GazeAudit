(() => {
  const router = document.querySelector('[data-research-router]');
  if (!router) return;

  const tabs = Array.from(router.querySelectorAll('[data-router-tab]'));
  const panels = Array.from(router.querySelectorAll('[data-router-panel]'));
  if (!tabs.length || tabs.length !== panels.length) return;

  const activate = (name, { focus = false } = {}) => {
    tabs.forEach((tab) => {
      const selected = tab.dataset.routerTab === name;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && focus) tab.focus();
    });

    panels.forEach((panel) => {
      panel.hidden = panel.dataset.routerPanel !== name;
    });
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab.dataset.routerTab));

    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) {
        return;
      }

      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'Home') nextIndex = 0;
      else if (event.key === 'End') nextIndex = tabs.length - 1;
      else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
        nextIndex = (index - 1 + tabs.length) % tabs.length;
      } else {
        nextIndex = (index + 1) % tabs.length;
      }
      activate(tabs[nextIndex].dataset.routerTab, { focus: true });
    });
  });
})();
