(() => {
  const baseurl = document.body.dataset.baseurl || '';
  const revisionToolkitUrl = `${baseurl}/docs/workspace/revision-toolkit/`;
  const revisionRouteUrl = `${baseurl}/docs/guides/revision-route-map/`;
  const revisionChecklistUrl = `${baseurl}/docs/guides/peer-review-revision-checklist/`;
  const revisionScenariosUrl = `${baseurl}/docs/examples/revision-round-scenarios/`;
  const revisionQuickstartUrl = `${baseurl}/docs/examples/revision-package-quickstart/`;
  const reviewerAmendmentUrl = `${baseurl}/docs/guides/reviewer-requested-amendments/`;
  const reviewerResponseUrl = `${baseurl}/docs/guides/reviewer-response-letter/`;
  const resubmissionUrl = `${baseurl}/docs/guides/resubmission-readiness/`;
  const firstAuditUrl = `${baseurl}/docs/guides/first-real-audit/`;
  const plannerUrl = `${baseurl}/docs/planner/`;
  const interpretationUrl = `${baseurl}/docs/guides/interpret-audit-result/`;
  const resultPatternsUrl = `${baseurl}/docs/examples/result-patterns/`;
  const publicationUrl = `${baseurl}/docs/workflows/reproducible-publication/`;

  const ensureRevisionStyles = () => {
    if (document.querySelector('link[data-revision-discovery-styles]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `${baseurl}/assets/css/revision-discovery.css`;
    link.dataset.revisionDiscoveryStyles = '';
    document.head.appendChild(link);
  };

  const makeLink = (href, label, className = '') => {
    const link = document.createElement('a');
    link.href = href;
    link.textContent = label;
    link.dataset.revisionNav = '';
    if (className) link.className = className;
    if (window.location.pathname === new URL(href, window.location.origin).pathname) {
      link.setAttribute('aria-current', 'page');
    }
    return link;
  };

  const injectRevisionNavigation = () => {
    const topNav = document.querySelector('[data-primary-nav]');
    if (topNav && !topNav.querySelector('[data-revision-nav]')) {
      const evidence = topNav.querySelector('a[href$="/docs/case-studies/"]');
      const revise = makeLink(revisionToolkitUrl, 'Revise', 'revision-nav-link');
      topNav.insertBefore(revise, evidence || topNav.firstChild);
    }

    const exploreGroups = Array.from(document.querySelectorAll('.nav-explore-group'));
    const applyGroup = exploreGroups.find((group) => group.querySelector('span')?.textContent.trim() === 'Apply');
    if (applyGroup && !applyGroup.querySelector('[data-revision-nav]')) {
      applyGroup.appendChild(makeLink(revisionToolkitUrl, 'Peer-review revision toolkit'));
      applyGroup.appendChild(makeLink(revisionRouteUrl, 'Revision route map'));
    }

    const mobilePriority = document.querySelector('.mobile-nav-priority');
    if (mobilePriority && !mobilePriority.querySelector('[data-revision-nav]')) {
      mobilePriority.appendChild(makeLink(revisionToolkitUrl, 'Peer-review revision'));
    }

    const mobileGroups = Array.from(document.querySelectorAll('.mobile-nav-group'));
    const mobileApply = mobileGroups.find((group) => group.querySelector('span')?.textContent.trim() === 'Apply');
    if (mobileApply && !mobileApply.querySelector('[data-revision-nav]')) {
      mobileApply.appendChild(makeLink(revisionRouteUrl, 'Revision route map'));
      mobileApply.appendChild(makeLink(revisionChecklistUrl, 'Revision checklist'));
    }

    const docsNav = document.querySelector('[data-docs-nav]');
    if (docsNav && !docsNav.querySelector('[data-revision-nav-group]')) {
      const workflowLabel = Array.from(docsNav.querySelectorAll('.nav-label')).find(
        (label) => label.textContent.trim() === 'Research workflows',
      );
      const fragment = document.createDocumentFragment();
      const label = document.createElement('p');
      label.className = 'nav-label';
      label.dataset.revisionNavGroup = '';
      label.textContent = 'Peer review';
      fragment.appendChild(label);
      fragment.appendChild(makeLink(revisionToolkitUrl, 'Revision toolkit'));
      fragment.appendChild(makeLink(revisionRouteUrl, 'Revision route map'));
      fragment.appendChild(makeLink(revisionChecklistUrl, 'Revision checklist'));
      fragment.appendChild(makeLink(reviewerAmendmentUrl, 'Reviewer amendments'));
      fragment.appendChild(makeLink(reviewerResponseUrl, 'Reviewer response'));
      fragment.appendChild(makeLink(revisionQuickstartUrl, 'Revision-package quickstart'));
      fragment.appendChild(makeLink(resubmissionUrl, 'Resubmission readiness'));
      docsNav.insertBefore(fragment, workflowLabel || null);
    }
  };

  const addProjectStageRouter = () => {
    const researchRouter = document.querySelector('[data-research-router]');
    if (!researchRouter || document.querySelector('[data-project-stage-router]')) return;

    const stages = [
      {
        id: 'plan',
        number: '01',
        label: 'Plan the study',
        short: 'Before analysis',
        kicker: 'Study design and governance',
        title: 'Declare the route before the result can influence it.',
        body: 'Start from study conditions, document researcher-owned decisions, and choose the smallest governed method route that answers the actual methodological question.',
        flow: ['scope risks', 'declare decisions', 'choose methods', 'preserve route'],
        actions: [
          [plannerUrl, 'Open the Audit planner →'],
          [`${baseurl}/docs/guides/researcher-audit-checklist/`, 'Researcher checklist'],
        ],
      },
      {
        id: 'audit',
        number: '02',
        label: 'Audit the data',
        short: 'Execution',
        kicker: 'Data to evidence',
        title: 'Move from a gaze table to an inspectable audit bundle.',
        body: 'Map the study explicitly, run structural preflight, execute declared alternatives, and save the outputs and provenance together instead of keeping only a preferred estimate.',
        flow: ['map data', 'inspect structure', 'execute alternatives', 'save evidence'],
        actions: [
          [firstAuditUrl, 'Run a first real audit →'],
          [`${baseurl}/docs/guides/audit-output-bundle/`, 'Read the output bundle'],
        ],
      },
      {
        id: 'interpret',
        number: '03',
        label: 'Interpret results',
        short: 'Before writing',
        kicker: 'Evidence to claim',
        title: 'Check completeness before reducing the audit to a sentence.',
        body: 'Separate execution completeness, endpoint consistency, direction, magnitude, descriptive sensitivity, and unresolved uncertainty before choosing reporting language.',
        flow: ['check denominator', 'hold endpoint fixed', 'read pattern', 'bound the claim'],
        actions: [
          [interpretationUrl, 'Interpret an audit result →'],
          [resultPatternsUrl, 'Compare result patterns'],
        ],
      },
      {
        id: 'peer-review',
        number: '04',
        label: 'Revise after review',
        short: 'Peer review',
        kicker: 'Submitted evidence to revision record',
        title: 'Extend the evidence history without rewriting the submitted record.',
        body: 'Classify each reviewer request, preserve the submitted denominator, execute post-review work under its own denominator, keep different endpoints separate, and bind responses to manuscript and archive locations.',
        flow: ['classify request', 'preserve submission', 'execute amendment', 'reconcile response', 'validate package'],
        actions: [
          [revisionToolkitUrl, 'Open the Revision Toolkit →'],
          [revisionRouteUrl, 'Choose the revision route'],
          [revisionScenariosUrl, 'Work through scenarios'],
          [revisionQuickstartUrl, 'Run the CLI quickstart'],
        ],
      },
      {
        id: 'handoff',
        number: '05',
        label: 'Finalize handoff',
        short: 'Resubmission',
        kicker: 'Revision to durable record',
        title: 'Make the final manuscript traceable across every evidence layer.',
        body: 'Check reviewer-item closure, version changes, software identity, final evidence mapping, and archive reproducibility without treating editorial status as scientific validation.',
        flow: ['close reviewer items', 'reconcile changes', 'verify archive', 'map final claims'],
        actions: [
          [resubmissionUrl, 'Run resubmission readiness →'],
          [publicationUrl, 'Reproducible publication workflow'],
        ],
      },
    ];

    const section = document.createElement('section');
    section.id = 'project-stage';
    section.className = 'section project-stage-section';
    section.dataset.projectStageRouter = '';
    section.innerHTML = `
      <div class="section-heading wide-heading">
        <p class="eyebrow">Start from your project stage</p>
        <h2>Go directly to the record you need to build now.</h2>
        <p>Study planning, execution, interpretation, peer review, and final handoff require different evidence records. Choose the current stage rather than browsing the whole documentation tree.</p>
      </div>
      <div class="project-stage-shell">
        <div class="project-stage-tabs" role="tablist" aria-label="Research project stages">
          ${stages.map((stage, index) => `
            <button class="project-stage-tab" type="button" role="tab"
              id="project-stage-tab-${stage.id}" aria-controls="project-stage-panel-${stage.id}"
              aria-selected="${index === 0 ? 'true' : 'false'}" tabindex="${index === 0 ? '0' : '-1'}"
              data-project-stage-tab="${stage.id}">
              <span class="project-stage-number">${stage.number}</span>
              <strong>${stage.label}</strong>
              <small>${stage.short}</small>
            </button>`).join('')}
        </div>
        <div class="project-stage-panels">
          ${stages.map((stage, index) => `
            <article class="project-stage-panel" role="tabpanel"
              id="project-stage-panel-${stage.id}" aria-labelledby="project-stage-tab-${stage.id}"
              data-project-stage-panel="${stage.id}" ${index === 0 ? '' : 'hidden'}>
              <p class="project-stage-kicker">${stage.kicker}</p>
              <h3>${stage.title}</h3>
              <p>${stage.body}</p>
              <ol class="project-stage-flow" aria-label="${stage.label} workflow">
                ${stage.flow.map((step) => `<li>${step}</li>`).join('')}
              </ol>
              <div class="project-stage-actions">
                ${stage.actions.map(([href, label]) => `<a href="${href}">${label}</a>`).join('')}
              </div>
              ${stage.id === 'peer-review' ? `<p class="project-stage-boundary"><strong>Boundary:</strong> this route organises temporal provenance. It does not decide whether a reviewer request, threshold, endpoint, analysis, or interpretation is scientifically justified.</p>` : ''}
            </article>`).join('')}
        </div>
      </div>`;

    researchRouter.parentNode.insertBefore(section, researchRouter);

    const jumpNav = document.querySelector('.landing-jump-nav');
    if (jumpNav && !jumpNav.querySelector('a[href="#project-stage"]')) {
      const jump = document.createElement('a');
      jump.href = '#project-stage';
      jump.textContent = 'Project stage';
      const firstLink = jumpNav.querySelector('a');
      jumpNav.insertBefore(jump, firstLink || null);
    }

    const tabs = Array.from(section.querySelectorAll('[data-project-stage-tab]'));
    const panels = Array.from(section.querySelectorAll('[data-project-stage-panel]'));
    const stageIds = new Set(stages.map((stage) => stage.id));

    const activate = (name, { focus = false, syncUrl = false } = {}) => {
      if (!stageIds.has(name)) return;
      tabs.forEach((tab) => {
        const selected = tab.dataset.projectStageTab === name;
        tab.setAttribute('aria-selected', String(selected));
        tab.tabIndex = selected ? 0 : -1;
        if (selected && focus) tab.focus();
      });
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.projectStagePanel !== name;
      });
      if (syncUrl) {
        const url = new URL(window.location.href);
        url.searchParams.set('stage', name);
        window.history.replaceState({}, '', url);
      }
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        activate(tab.dataset.projectStageTab, { syncUrl: true });
      });
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
        activate(tabs[nextIndex].dataset.projectStageTab, { focus: true, syncUrl: true });
      });
    });

    const requested = new URLSearchParams(window.location.search).get('stage');
    if (requested && stageIds.has(requested)) activate(requested);
  };

  ensureRevisionStyles();
  injectRevisionNavigation();
  addProjectStageRouter();

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
