(() => {
  const languageLabels = new Map([
    ['bash', 'Shell'],
    ['console', 'Shell'],
    ['json', 'JSON'],
    ['python', 'Python'],
    ['r', 'R'],
    ['sh', 'Shell'],
    ['shell', 'Shell'],
    ['yaml', 'YAML'],
    ['yml', 'YAML'],
  ]);

  const languageFor = (code, pre) => {
    const candidates = [code, pre, pre.parentElement, pre.closest('[class*="language-"]')]
      .filter(Boolean);
    for (const node of candidates) {
      const languageClass = [...node.classList].find((name) => name.startsWith('language-'));
      if (!languageClass) continue;
      const language = languageClass.slice('language-'.length).toLowerCase();
      if (languageLabels.has(language)) return languageLabels.get(language);
    }
    return null;
  };

  const fallbackCopy = (text) => {
    const activeElement = document.activeElement;
    const selection = window.getSelection();
    const savedRanges = selection
      ? Array.from({ length: selection.rangeCount }, (_, index) => selection.getRangeAt(index).cloneRange())
      : [];
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.setAttribute('aria-hidden', 'true');
    textarea.style.position = 'fixed';
    textarea.style.inset = '0 auto auto -9999px';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    let copied = false;
    try {
      copied = document.execCommand('copy');
    } catch (error) {
      copied = false;
    }

    textarea.remove();
    if (selection) {
      selection.removeAllRanges();
      savedRanges.forEach((range) => selection.addRange(range));
    }
    if (activeElement instanceof HTMLElement) activeElement.focus({ preventScroll: true });
    return copied;
  };

  const copyText = async (text) => {
    if (navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        // Continue to the selection-preserving fallback below.
      }
    }
    return fallbackCopy(text);
  };

  document.querySelectorAll('pre > code').forEach((code, index) => {
    const pre = code.parentElement;
    if (!pre || pre.dataset.codeToolsReady === 'true') return;
    pre.dataset.codeToolsReady = 'true';
    pre.classList.add('has-code-tools');

    pre.querySelector('.copy-code')?.remove();

    const language = languageFor(code, pre);
    if (language) {
      const label = document.createElement('span');
      label.className = 'code-language';
      label.textContent = language;
      label.setAttribute('aria-hidden', 'true');
      pre.appendChild(label);
    }

    const status = document.createElement('span');
    status.className = 'sr-only code-copy-status';
    status.id = `code-copy-status-${index + 1}`;
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    pre.appendChild(status);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy';
    button.dataset.copyState = 'idle';
    button.setAttribute('aria-label', language ? `Copy ${language} code to clipboard` : 'Copy code to clipboard');
    button.setAttribute('aria-describedby', status.id);

    let resetTimer = null;
    button.addEventListener('click', async () => {
      if (resetTimer) window.clearTimeout(resetTimer);
      const copied = await copyText(code.textContent);
      button.dataset.copyState = copied ? 'success' : 'error';
      button.textContent = copied ? 'Copied' : 'Select';
      status.textContent = copied
        ? 'Code copied to clipboard.'
        : 'Automatic copy failed. Select the code and copy it manually.';

      resetTimer = window.setTimeout(() => {
        button.dataset.copyState = 'idle';
        button.textContent = 'Copy';
        status.textContent = '';
      }, 1800);
    });

    pre.appendChild(button);
  });
})();
