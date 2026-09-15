(() => {
  const root = document.querySelector('[data-audit-planner]');
  if (!root) return;

  const plannerUrl = root.dataset.plannerIndex;
  const methodUrl = root.dataset.methodIndex;
  const workflowUrl = root.dataset.workflowIndex;
  const choices = [...root.querySelectorAll('[data-planner-choice]')];
  const cards = [...root.querySelectorAll('[data-planner-choice-card]')];
  const results = root.querySelector('[data-planner-results]');
  const route = root.querySelector('[data-planner-route]');
  const workflowSection = root.querySelector('[data-planner-workflows]');
  const workflowList = root.querySelector('[data-planner-workflow-list]');
  const empty = root.querySelector('[data-planner-empty]');
  const actions = root.querySelector('[data-planner-actions]');
  const count = root.querySelector('[data-planner-count]');
  const clear = root.querySelector('[data-planner-clear]');
  const share = root.querySelector('[data-planner-share]');
  const copyBrief = root.querySelector('[data-planner-copy-brief]');
  const downloadJson = root.querySelector('[data-planner-download-json]');
  const exportStatus = root.querySelector('[data-planner-export-status]');

  const esc = (value) => String(value).replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));

  const relative = (url) => `${document.body.dataset.baseurl || ''}${url}`;
  const absolute = (url) => new URL(relative(url), window.location.origin).href;
  const selectedIds = () => choices.filter((input) => input.checked).map((input) => input.value);

  const docsRevision = () => {
    const link = document.querySelector('.footer-provenance a[href*="/commit/"]');
    if (!link) return 'local-build';
    return link.href.split('/commit/')[1]?.split(/[?#]/)[0] || 'local-build';
  };

  const releaseVersion = () => {
    const text = document.querySelector('.version-badge-link')?.textContent || '';
    return text.match(/v([0-9]+(?:\.[0-9]+)*)/)?.[1] || 'unknown';
  };

  const showExportStatus = (message) => {
    if (!exportStatus) return;
    exportStatus.textContent = message;
    exportStatus.hidden = false;
    window.clearTimeout(showExportStatus.timer);
    showExportStatus.timer = window.setTimeout(() => { exportStatus.hidden = true; }, 2600);
  };

  Promise.all([
    fetch(plannerUrl).then((r) => r.json()),
    fetch(methodUrl).then((r) => r.json()),
    fetch(workflowUrl).then((r) => r.json())
  ])
    .then(([rules, methods, workflows]) => {
      const ruleMap = new Map(rules.map((rule) => [rule.id, rule]));
      const methodMap = new Map(methods.map((method) => [method.id, method]));
      const invalid = rules.flatMap((rule) => rule.methods.filter((id) => !methodMap.has(id)));
      if (invalid.length) throw new Error(`Unknown planner method ids: ${invalid.join(', ')}`);

      const workflowMethods = workflows.flatMap((workflow) => workflow.methods);
      const invalidWorkflowMethods = workflowMethods.filter((id) => !methodMap.has(id));
      if (invalidWorkflowMethods.length) {
        throw new Error(`Unknown workflow handoff method ids: ${invalidWorkflowMethods.join(', ')}`);
      }
      const workflowCounts = new Map();
      workflowMethods.forEach((id) => workflowCounts.set(id, (workflowCounts.get(id) || 0) + 1));
      const duplicatedWorkflowMethods = [...workflowCounts.entries()]
        .filter(([, total]) => total !== 1)
        .map(([id]) => id);
      if (duplicatedWorkflowMethods.length) {
        throw new Error(`Workflow handoff methods must be unique: ${duplicatedWorkflowMethods.join(', ')}`);
      }

      root.dataset.catalogState = 'verified';

      const params = new URLSearchParams(window.location.search);
      const restored = (params.get('plan') || '').split(',').filter(Boolean);
      choices.forEach((input) => { input.checked = restored.includes(input.value); });

      let currentManifest = null;

      const buildManifest = (selected, ordered, handoffs, reasons) => ({
        schema_version: 1,
        artifact_type: 'gazeaudit-navigation-plan',
        boundary: 'Navigation artifact only. Thresholds, exclusions, scientific assumptions, and validity judgements remain researcher-owned.',
        selected_conditions: selected
          .map((id) => ruleMap.get(id))
          .filter(Boolean)
          .map((rule) => ({
            id: rule.id,
            group: rule.group,
            label: rule.label,
            prompt: rule.prompt,
            method_ids: [...rule.methods]
          })),
        method_route: ordered.map((method) => ({
          id: method.id,
          phase: method.phase,
          title: method.title,
          question: method.question,
          functions: [...method.functions],
          reasons: [...new Set(reasons.get(method.id) || [])],
          guide_url: absolute(method.guide_url),
          example_url: absolute(method.example_url),
          plot_url: absolute(method.plot_url),
          method_url: absolute(`/docs/methods/#method-${method.id}`)
        })),
        workflow_handoffs: handoffs.map((workflow) => ({
          id: workflow.id,
          title: workflow.title,
          matched_method_ids: [...workflow.matchedMethods],
          url: absolute(workflow.url)
        })),
        provenance: {
          gazeaudit_release: releaseVersion(),
          docs_revision: docsRevision(),
          plan_url: window.location.href
        }
      });

      const renderBrief = (manifest) => {
        const lines = [
          '# GazeAudit audit plan',
          '',
          `> ${manifest.boundary}`,
          '',
          '## Provenance',
          '',
          `- GazeAudit stable release: ${manifest.provenance.gazeaudit_release}`,
          `- Documentation revision: ${manifest.provenance.docs_revision}`,
          `- Shareable plan: ${manifest.provenance.plan_url}`,
          '',
          '## Selected study conditions',
          ''
        ];
        manifest.selected_conditions.forEach((condition) => {
          lines.push(`- **${condition.label}** — ${condition.prompt}`);
        });
        lines.push('', '## Governed method route', '');
        manifest.method_route.forEach((method, index) => {
          lines.push(
            `${index + 1}. **${method.title}** (${method.phase})`,
            `   - Question: ${method.question}`,
            `   - Why included: ${method.reasons.join(' ')}`,
            `   - Public API: ${method.functions.join(' → ')}`,
            `   - Guide: ${method.guide_url}`,
            `   - Example: ${method.example_url}`,
            `   - Plot: ${method.plot_url}`
          );
        });
        lines.push('', '## Workflow handoffs', '');
        manifest.workflow_handoffs.forEach((workflow) => {
          lines.push(`- **${workflow.title}** — ${workflow.url}`);
        });
        lines.push('', 'This export records navigation choices only; it does not constitute a QC verdict, exclusion rule, validation result, or preregistration.');
        return lines.join('\n');
      };

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
        const handoffs = workflows
          .map((workflow) => ({
            ...workflow,
            matchedMethods: workflow.methods.filter((methodId) => wanted.has(methodId))
          }))
          .filter((workflow) => workflow.matchedMethods.length);

        count.textContent = String(ordered.length);
        cards.forEach((card) => card.classList.toggle('is-selected', card.querySelector('input')?.checked));

        const next = new URL(window.location.href);
        if (selected.length) next.searchParams.set('plan', selected.join(','));
        else next.searchParams.delete('plan');
        window.history.replaceState({}, '', next);

        if (!ordered.length) {
          currentManifest = null;
          results.hidden = true;
          actions.hidden = true;
          workflowSection.hidden = true;
          empty.hidden = false;
          route.innerHTML = '';
          workflowList.innerHTML = '';
          if (exportStatus) exportStatus.hidden = true;
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

        workflowSection.hidden = !handoffs.length;
        workflowList.innerHTML = handoffs.map((workflow) => {
          const matched = workflow.matchedMethods
            .map((methodId) => methodMap.get(methodId))
            .filter(Boolean);
          const methodChips = matched
            .map((method) => `<span>${esc(method.title)}</span>`)
            .join('');
          return `<article class="planner-workflow-card">
            <div class="planner-workflow-copy">
              <span class="planner-kicker">${esc(workflow.title)}</span>
              <h3>${esc(workflow.label)}</h3>
              <p>${esc(workflow.description)}</p>
            </div>
            <div class="planner-workflow-match">
              <strong>Matched from this plan</strong>
              <div>${methodChips}</div>
            </div>
            <a class="button" href="${relative(workflow.url)}">Open workflow →</a>
          </article>`;
        }).join('');

        currentManifest = buildManifest(selected, ordered, handoffs, reasons);
      };

      choices.forEach((input) => input.addEventListener('change', render));
      clear?.addEventListener('click', () => {
        choices.forEach((input) => { input.checked = false; });
        render();
      });
      share?.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(window.location.href);
          showExportStatus('Shareable plan link copied.');
        } catch (_) {
          window.prompt('Copy this plan URL:', window.location.href);
        }
      });
      copyBrief?.addEventListener('click', async () => {
        if (!currentManifest) return;
        const brief = renderBrief(currentManifest);
        try {
          await navigator.clipboard.writeText(brief);
          showExportStatus('Audit brief copied as Markdown.');
        } catch (_) {
          window.prompt('Copy this audit brief:', brief);
        }
      });
      downloadJson?.addEventListener('click', () => {
        if (!currentManifest) return;
        const blob = new Blob([`${JSON.stringify(currentManifest, null, 2)}\n`], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'gazeaudit-audit-plan.json';
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
        showExportStatus('Audit plan JSON prepared from the governed route.');
      });
      render();
    })
    .catch((error) => {
      root.dataset.catalogState = 'error';
      console.error('GazeAudit audit planner failed to initialize', error);
    });
})();
