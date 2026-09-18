(() => {
  const form = document.querySelector('[data-readiness-builder]');
  if (!form) return;

  const policyName = form.querySelector('[data-readiness-policy-name]');
  const rules = Array.from(form.querySelectorAll('[data-readiness-rule]'));
  const clearButton = form.querySelector('[data-readiness-clear]');
  const errors = document.querySelector('[data-readiness-errors]');
  const status = document.querySelector('[data-readiness-status]');
  const pythonOutput = document.querySelector('[data-readiness-python]');
  const jsonOutput = document.querySelector('[data-readiness-json]');
  const copyButtons = Array.from(document.querySelectorAll('[data-readiness-copy]'));

  if (
    !policyName
    || !clearButton
    || !errors
    || !status
    || !pythonOutput
    || !jsonOutput
  ) return;

  const allRuleNames = rules.map((card) => card.dataset.ruleName);

  const syncRule = (card) => {
    const active = card.querySelector('[data-readiness-active]');
    const value = card.querySelector('[data-readiness-value]');
    if (!active) return;

    card.dataset.active = active.checked ? 'true' : 'false';
    if (value) {
      value.disabled = !active.checked;
      value.required = active.checked;
      if (!active.checked) value.value = '';
    }
  };

  const pythonValue = (value, type) => {
    if (type === 'boolean') return 'True';
    if (type === 'integer') return String(Number.parseInt(value, 10));
    return String(Number(value));
  };

  const collect = () => {
    const name = policyName.value.trim();
    const thresholds = Object.fromEntries(allRuleNames.map((key) => [key, null]));
    const activeRules = [];
    const problems = [];

    if (!name) {
      problems.push({
        target: 'readiness-policy-name',
        message: 'Policy name is required.',
      });
    }

    rules.forEach((card) => {
      const active = card.querySelector('[data-readiness-active]');
      const value = card.querySelector('[data-readiness-value]');
      const ruleName = card.dataset.ruleName;
      const ruleType = card.dataset.ruleType;

      if (!active || !active.checked) return;
      activeRules.push(ruleName);

      if (ruleType === 'boolean') {
        thresholds[ruleName] = true;
        return;
      }

      if (!value || !value.value.trim()) {
        problems.push({
          target: value ? value.id : '',
          message: `${ruleName} is active but has no declared value.`,
        });
        return;
      }

      if (!value.checkValidity()) {
        problems.push({
          target: value.id,
          message: `${ruleName} is outside the allowed software input range.`,
        });
        return;
      }

      const number = Number(value.value);
      if (ruleType === 'integer' && !Number.isInteger(number)) {
        problems.push({
          target: value.id,
          message: `${ruleName} must be a positive integer.`,
        });
        return;
      }
      thresholds[ruleName] = number;
    });

    return { name, thresholds, activeRules, problems };
  };

  const showErrors = (problems) => {
    if (!problems.length) {
      errors.hidden = true;
      errors.replaceChildren();
      return;
    }

    const strong = document.createElement('strong');
    strong.textContent = `Fix ${problems.length} policy field${problems.length === 1 ? '' : 's'}:`;
    const list = document.createElement('ul');

    problems.forEach((problem) => {
      const item = document.createElement('li');
      if (problem.target) {
        const link = document.createElement('a');
        link.href = `#${problem.target}`;
        link.textContent = problem.message;
        item.appendChild(link);
      } else {
        item.textContent = problem.message;
      }
      list.appendChild(item);
    });

    errors.replaceChildren(strong, list);
    errors.hidden = false;
    errors.focus?.();
  };

  const buildPython = ({ name, thresholds, activeRules }) => {
    const lines = [
      'from gazeaudit import (',
      '    ReadinessThresholds,',
      '    cohort_impact_preview,',
      '    evaluate_analysis_readiness,',
      ')',
      '',
      'policy = ReadinessThresholds(',
    ];

    activeRules.forEach((ruleName) => {
      const card = rules.find((item) => item.dataset.ruleName === ruleName);
      const type = card ? card.dataset.ruleType : '';
      lines.push(`    ${ruleName}=${pythonValue(thresholds[ruleName], type)},`);
    });

    lines.push(
      ')',
      '',
      'readiness = evaluate_analysis_readiness(',
      '    study,',
      '    policy,',
      `    policy_name=${JSON.stringify(name)},`,
      ')',
      '',
      'print(readiness.status)',
      'print(cohort_impact_preview(readiness))',
    );

    return lines.join('\n');
  };

  const render = (payload) => {
    const draft = {
      schema: 'gazeaudit-readiness-policy-draft-v1',
      policy_name: payload.name,
      active_rules: payload.activeRules,
      thresholds: payload.thresholds,
    };

    pythonOutput.textContent = buildPython(payload);
    jsonOutput.textContent = JSON.stringify(draft, null, 2);
    copyButtons.forEach((button) => {
      button.disabled = false;
    });

    if (payload.activeRules.length === 0) {
      status.textContent = (
        'Policy draft generated with 0 active rules. '
        + 'The runtime readiness status will be unassessed until a criterion is active.'
      );
    } else {
      status.textContent = (
        `Policy draft generated with ${payload.activeRules.length} active `
        + `rule${payload.activeRules.length === 1 ? '' : 's'}. No filtering was applied.`
      );
    }
  };

  rules.forEach((card) => {
    const active = card.querySelector('[data-readiness-active]');
    if (!active) return;
    syncRule(card);
    active.addEventListener('change', () => syncRule(card));
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = collect();

    if (payload.problems.length) {
      showErrors(payload.problems);
      status.textContent = 'Policy draft not generated. Correct the listed fields.';
      return;
    }

    showErrors([]);
    render(payload);
  });

  clearButton.addEventListener('click', () => {
    form.reset();
    rules.forEach(syncRule);
    errors.hidden = true;
    errors.replaceChildren();
    pythonOutput.textContent = '# Choose a policy name and activate at least one justified criterion.';
    jsonOutput.textContent = JSON.stringify(
      {
        schema: 'gazeaudit-readiness-policy-draft-v1',
        policy_name: '',
        thresholds: {},
      },
      null,
      2,
    );
    copyButtons.forEach((button) => {
      button.disabled = true;
    });
    status.textContent = 'Policy cleared. No policy draft generated yet.';
    policyName.focus();
  });

  copyButtons.forEach((button) => {
    button.addEventListener('click', async () => {
      const target = button.dataset.readinessCopy === 'python' ? pythonOutput : jsonOutput;
      try {
        await navigator.clipboard.writeText(target.textContent || '');
        status.textContent = (
          button.dataset.readinessCopy === 'python'
            ? 'Python policy draft copied.'
            : 'JSON policy draft copied.'
        );
      } catch {
        status.textContent = 'Copy was unavailable. Select the generated text manually.';
      }
    });
  });
})();
