(() => {
  const root = document.querySelector('[data-api-pathways]');
  if (!root) return;

  const metadataUrl = root.dataset.apiSymbolReference;
  const sourceBase = root.dataset.apiSourceBase;
  if (!metadataUrl || !sourceBase || !window.fetch) return;

  const escapeHtml = (value) => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  const sourceUrl = (symbol) => {
    const base = sourceBase.replace(/\/$/, '');
    return `${base}/${symbol.source_path}#L${symbol.source_line}`;
  };

  const copyText = async (button, value) => {
    if (!navigator.clipboard) return;
    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(value);
      button.textContent = 'Copied';
    } catch (error) {
      button.textContent = 'Copy unavailable';
    }
    window.setTimeout(() => {
      button.textContent = original;
    }, 1400);
  };

  const renderSymbol = (symbol) => {
    const target = document.getElementById(symbol.anchor);
    if (!target || target.querySelector('[data-api-symbol-detail]')) return;

    const methodLinks = symbol.method_ids.map((methodId) => (
      `<a href="#path-${escapeHtml(methodId)}">${escapeHtml(methodId.replace(/-/g, ' '))}</a>`
    )).join('');

    const detail = document.createElement('div');
    detail.className = 'api-symbol-detail';
    detail.dataset.apiSymbolDetail = '';
    detail.innerHTML = `
      <div class="api-symbol-detail-head">
        <div>
          <span class="api-symbol-kind">${escapeHtml(symbol.kind)}</span>
          <code class="api-symbol-signature">${escapeHtml(symbol.name)}${escapeHtml(symbol.signature)}</code>
        </div>
        <a class="api-symbol-source" href="${escapeHtml(sourceUrl(symbol))}">View source</a>
      </div>
      <p class="api-symbol-summary">${escapeHtml(symbol.summary || 'No source summary is available.')}</p>
      <dl class="api-symbol-meta">
        <div><dt>Module</dt><dd><code>${escapeHtml(symbol.module)}</code></dd></div>
        <div><dt>Source</dt><dd><code>${escapeHtml(symbol.source_path)}:${escapeHtml(symbol.source_line)}</code></dd></div>
        <div><dt>Used by pathways</dt><dd class="api-symbol-pathway-links">${methodLinks}</dd></div>
      </dl>
      <div class="api-symbol-import">
        <code>${escapeHtml(symbol.import_statement)}</code>
        <button type="button" data-copy-api-import>Copy import</button>
      </div>`;

    target.appendChild(detail);
    detail.querySelector('[data-copy-api-import]')?.addEventListener('click', (event) => {
      copyText(event.currentTarget, symbol.import_statement);
    });
  };

  fetch(metadataUrl, { credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`API symbol metadata ${response.status}`);
      return response.json();
    })
    .then((metadata) => {
      if (!metadata || metadata.schema !== 'gazeaudit-api-symbol-reference-v1') {
        throw new Error('unexpected API symbol metadata schema');
      }
      if (!Array.isArray(metadata.symbols)) throw new Error('API symbol metadata is not an array');
      metadata.symbols.forEach(renderSymbol);
      root.dataset.apiReferenceState = 'ready';
      root.dataset.apiReferenceCount = String(metadata.symbols.length);
    })
    .catch(() => {
      root.dataset.apiReferenceState = 'unavailable';
    });
})();
