(() => {
  const root = document.querySelector('[data-audit-planner]');
  if (!root) return;

  const plannerUrl = root.dataset.plannerIndex;
  const methodUrl = root.dataset.methodIndex;
  const choices = [...root.querySelectorAll('[data-planner-choice]')];
  const cards = [...root.querySelectorAll('[data-planner-choice-card]')];
  const results = root.querySelector('[data-planner-results]');
  const route = root.querySelector('[data-planner-route]');
  const empty = root.querySelector('[data-planner-empty]');
  const actions = root.querySelector('[data-planner-actions]');
  const count = root.querySelector('[data-planner-count]');
  const clear = root.querySelector('[data-planner-clear]');
  const share = root.querySelector('[data-planner-share]');

  const esc = (value) => String(value).replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));

  const relative = (url) => `${document.body.dataset.baseurl || ''}${url}`;
  const selectedIds = () => choices.filter((input) => input.checked).map((input) => input.value);

  Promise.all([fetch(plannerUrl).then((r) => r.json()), fetch(methodUrl).then((r) => r.json())])
    .then(([rules, methods]) => {
      const ruleMap = new Map(rules.map((rule) => [rule.id, rule]));
      const methodMap = new Map(methods.map((method) => [method.id, method]));
      const invalid = rules.flatMap((rule) => rule.methods.filter((id) => !methodMap.has(id)));
      if (invalid.length) throw new Error(`Unknown planner method ids: ${invalid.join(', ')}`);
      root.dataset.catalogState = 'verified';

      const params = new URLSearchParams(window.location.search);
      const restored = (params.get('plan') || '').split(',').filter(Boolean);
      choices.forEach((input) => { input.checked = restored.includes(input.value); });

      const render = () => {
        const selected = selectedIds();
        const reasons = new Map();
        const wanted = new Set();

        selected.forEach((id) => {
          const rule = ruleMap.get(id);
          if (!rule) return;
          rule.methods.forEach((methodId) => {
            wanted.add(methodId);
            const list = reasons.get(methodId) || [];
            list.push(rule.reason);
            reasons.set(methodId, list);
          });
        });

        const ordered = methods.filter((method) => wanted.has(method.id));
        count.textContent = String(ordered.length);
        cards.forEach((card) => card.classList.toggle('is-selected', card.querySelector('input')?.checked));

        const next = new URL(window.location.href);
        if (selected.length) next.searchParams.set('plan', selected.join(','));
        else next.searchParams.delete('plan');
        window.history.replaceState({}, '', next);

        if (!ordered.length) {
          results.hidden = true;
          actions.hidden = true;
          empty.hidden = false;
          route.innerHTML = '';
          return;
        }

        empty.hidden = true;
        actions.hidden = false;
        results.hidden = false;
        route.innerHTML = ordered.map((method, index) => {
          const why = [...new Set(reasons.get(method.id) || [])]
            .map((reason) => `<li>${esc(reason)}</li>`).join('');
          const evidence = method.evidence_url
            ? `<a href="${relative(method.evidence_url)}">${esc(method.evidence_label)} →</a>`
            : `<span>${esc(method.evidence_note)}</span>`;
          const functions = method.functions.map((name) => `<code>${esc(name)}</code>`).join('');
          return `<article class="planner-method-card">
            <div class="planner-method-number">${String(index + 1).padStart(2, '0')}</div>
            <div class="planner-method-body">
              <div class="planner-method-head"><span>${esc(method.phase)}</span><h3>${esc(method.title)}</h3></div>
              <p class="planner-method-question">${esc(method.question)}</p>
              <div class="planner-why"><strong>Why it is in this route</strong><ul>${why}</ul></div>
              <div class="planner-function-list">${functions}</div>
              <div class="planner-method-links">
                <a href="${relative(method.guide_url)}">Guide</a>
                <a href="${relative(method.example_url)}">Run</a>
                <a href="${relative(method.plot_url)}">Plot</a>
                <a href="${relative(`/docs/methods/#method-${method.id}`)}">Method card</a>
              </div>
              <div class="planner-evidence-boundary"><strong>Evidence boundary</strong>${evidence}</div>
            </div>
          </article>`;
        }).join('');
      };

      choices.forEach((input) => input.addEventListener('change', render));
      clear?.addEventListener('click', () => {
        choices.forEach((input) => { input.checked = false; });
        render();
      });
      share?.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(window.location.href);
          const original = share.textContent;
          share.textContent = 'Plan link copied';
          window.setTimeout(() => { share.textContent = original; }, 1600);
        } catch (_) {
          window.prompt('Copy this plan URL:', window.location.href);
        }
      });
      render();
    })
    .catch((error) => {
      root.dataset.catalogState = 'error';
      console.error('GazeAudit audit planner failed to initialize', error);
    });
})();
