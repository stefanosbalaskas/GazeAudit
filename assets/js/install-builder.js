(() => {
  const form = document.querySelector('[data-install-builder]');
  if (!form) return;

  const extra = form.querySelector('[data-install-extra]');
  const command = form.querySelector('[data-install-command]');
  const status = form.querySelector('[data-install-status]');
  const copy = form.querySelector('[data-copy-install]');
  if (!extra || !command || !status || !copy) return;

  const packageName = form.dataset.package || 'gazeaudit';
  const version = form.dataset.version || '';

  const selectedSource = () => (
    form.querySelector('input[name="install-source"]:checked')?.value || 'release'
  );

  const buildCommand = () => {
    const source = selectedSource();
    const selectedExtra = extra.value;
    if (source === 'source') {
      return selectedExtra
        ? `python -m pip install -e ".[${selectedExtra}]"`
        : 'python -m pip install -e .';
    }

    const target = selectedExtra
      ? `${packageName}[${selectedExtra}]`
      : packageName;
    return version
      ? `python -m pip install "${target}==${version}"`
      : `python -m pip install "${target}"`;
  };

  const render = () => {
    const value = buildCommand();
    command.textContent = value;
    const sourceLabel = selectedSource() === 'source'
      ? 'current source checkout'
      : `public release ${version}`;
    const extraLabel = extra.value ? ` with the ${extra.value} extra` : '';
    status.textContent = `Install command updated for ${sourceLabel}${extraLabel}.`;
  };

  form.addEventListener('change', render);

  copy.addEventListener('click', async () => {
    const value = buildCommand();
    if (!navigator.clipboard) {
      status.textContent = 'Clipboard access is unavailable. Select and copy the command manually.';
      return;
    }
    try {
      await navigator.clipboard.writeText(value);
      status.textContent = 'Install command copied to the clipboard.';
      copy.textContent = 'Copied';
      window.setTimeout(() => {
        copy.textContent = 'Copy command';
      }, 1400);
    } catch (error) {
      status.textContent = 'Clipboard access failed. Select and copy the command manually.';
    }
  });

  render();
})();
