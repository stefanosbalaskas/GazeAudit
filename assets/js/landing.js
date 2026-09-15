(() => {
  const baseurl = document.body.dataset.baseurl || '';
  const plannerIndexUrl = `${baseurl}/assets/planner-index.json`;
  const plannerUrl = `${baseurl}/docs/planner/`;
  const firstAuditUrl = `${baseurl}/docs/guides/first-real-audit/`;
  const gettingStartedUrl = `${baseurl}/docs/getting-started/`;
  const workspaceUrl = `${baseurl}/docs/workspace/`;

  const addPracticalStart = () => {
    const router = document.querySelector('[data-research-router]');
    if (!router || document.querySelector('[data-practical-start]')) return;

    const heroActions = document.querySelector('.product-hero-actions');
    const primary = heroActions?.querySelector('.button.primary');
    if (primary) {
      primary.href = firstAuditUrl;
      primary.textContent = 'Audit your own data →';
      primary.dataset.heroOwnData = '';
    }

    const section = document.createElement('section');
    section.className = 'section practical-start-section';
    section.dataset.practicalStart = '';
    section.innerHTML = `
      <div class="section-heading wide-heading">
        <p class="eyebrow">Start from where you are</p>
        <h2>Use the shortest route into GazeAudit.</h2>
        <p>You do not need to learn the whole package before using it. Choose the starting point that matches what you already have.</p>
      </div>
      <div class="practical-start-grid" aria-label="Practical GazeAudit starting routes">
        <a class="practical-start-card is-primary" href="${firstAuditUrl}">
          <span class="start-kicker">I have gaze data</span>
          <strong>Run a first real audit</strong>
          <p>Map a canonical CSV, run structural preflight, declare a finite robustness space, and save the complete evidence trail.</p>
          <small>CSV → preflight → robustness → outputs →</small>
        </a>
        <a class="practical-start-card" href="${gettingStartedUrl}">
          <span class="start-kicker">I am learning the package</span>
          <strong>Install and learn the core API</strong>
          <p>Start with the stable release, fit a transparent gaze-error model, propagate AOI uncertainty, and continue into specification spaces.</p>
          <small>Open getting started →</small>
        </a>
        <a class="practical-start-card" href="${plannerUrl}">
          <span class="start-kicker">I am designing an audit</span>
          <strong>Build a governed method route</strong>
          <p>Select only the study conditions that apply and hand the route into measurement, robustness, or publication workflows.</p>
          <small>Open Audit planner →</small>
        </a>
      </div>
      <p class="practical-start-boundary">These routes organise documentation and provenance. Thresholds, exclusions, AOIs, perturbations, endpoints, and validity judgements remain researcher-owned. <a href="${workspaceUrl}">See the full researcher workspace →</a></p>`;

    router.parentNode.insertBefore(section, router);
  };

  const ensurePlannerStyles = () => {
    if (document.querySelector('link[data-landing-planner-styles]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `${baseurl}/assets/css/landing-planner.css`;
    link.dataset.landingPlannerStyles = '';
    document.head.appendChild(link);
  };

  const addPlannerJourney = async () => {
    const router = document.querySelector('[data-research-router]');
    if (!router) return;

    const presets = [
      {
        id: 'new-study',
        eyebrow: 'Start clean',
        title: 'New gaze dataset',
        summary: 'Inspect structure and make analysis-readiness policy explicit before downstream decisions.',
        choices: ['incoming-data'],
      },
      {
        id: 'aoi-study',
        eyebrow: 'Measurement',
        title: 'AOI-based study',
        summary: 'Combine structural preflight with explicit AOI boundary uncertainty.',
        choices: ['incoming-data', 'aoi-boundary'],
      },
      {
        id: 'robustness-study',
        eyebrow: 'Stress test',
        title: 'Robustness audit',
        summary: 'Inspect defensible analytical choices together with sampling and missingness sensitivity.',
        choices: ['analysis-choices', 'sampling-risk', 'missingness-risk'],
      },
      {
        id: 'publication-study',
        eyebrow: 'Evidence',
        title: 'Publication record',
        summary: 'Build a deterministic provenance route for results, rules, methods text, and software identity.',
        choices: ['publication-record'],
      },
    ];

    try {
      const response = await fetch(plannerIndexUrl);
      if (!response.ok) throw new Error(`Planner index returned ${response.status}`);
      const rules = await response.json();
      const validIds = new Set(rules.map((rule) => rule.id));
      const invalid = presets.flatMap((preset) => preset.choices.filter((id) => !validIds.has(id)));
      if (invalid.length) throw new Error(`Homepage preset references unknown planner ids: ${invalid.join(', ')}`);

      ensurePlannerStyles();
      const section = document.createElement('section');
      section.className = 'section landing-planner-section';
      section.dataset.landingPlanner = '';
      section.innerHTML = `
        <div class="section-heading wide-heading section-heading-row">
          <div>
            <p class="eyebrow">Plan the audit</p>
            <h2>Know the study situation? Build the route in one click.</h2>
            <p>These presets only preselect transparent planner choices. They do not diagnose your data, choose thresholds, or transfer validation outcomes to your study.</p>
          </div>
          <a class="text-cta" href="${plannerUrl}">Open the full Audit planner →</a>
        </div>
        <div class="landing-planner-grid" aria-label="Common audit-planning starting points">
          ${presets.map((preset) => {
            const href = `${plannerUrl}?plan=${encodeURIComponent(preset.choices.join(','))}`;
            return `<a class="landing-planner-card" href="${href}" data-planner-preset="${preset.id}">
              <span>${preset.eyebrow}</span>
              <strong>${preset.title}</strong>
              <p>${preset.summary}</p>
              <small>${preset.choices.length === 1 ? '1 planner choice' : `${preset.choices.length} planner choices`} · inspect route →</small>
            </a>`;
          }).join('')}
        </div>
        <p class="landing-planner-boundary"><strong>Researcher-controlled:</strong> open any preset and change the selections before using the route. A planner URL records navigation choices, not a scientific conclusion.</p>`;
      router.parentNode.insertBefore(section, router);

      const heroActions = document.querySelector('.product-hero-actions');
      if (heroActions && !heroActions.querySelector('[data-hero-planner]')) {
        const plannerLink = document.createElement('a');
        plannerLink.className = 'button';
        plannerLink.href = plannerUrl;
        plannerLink.dataset.heroPlanner = '';
        plannerLink.textContent = 'Plan an audit';
        heroActions.insertBefore(plannerLink, heroActions.children[1] || null);
      }
      document.documentElement.dataset.landingPlanner = 'ready';
    } catch (error) {
      document.documentElement.dataset.landingPlanner = 'unavailable';
      console.error('GazeAudit homepage planner presets unavailable', error);
    }
  };

  const router = document.querySelector('[data-research-router]');
  if (router) {
    const tabs = Array.from(router.querySelectorAll('[data-router-tab]'));
    const panels = Array.from(router.querySelectorAll('[data-router-panel]'));

    if (tabs.length && tabs.length === panels.length) {
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
    }
  }

  addPracticalStart();
  addPlannerJourney();
})();
