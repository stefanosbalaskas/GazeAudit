(() => {
  const form = document.querySelector('[data-conclusion-builder]');
  if (!form) return;

  const fields = Array.from(form.querySelectorAll('[data-conclusion-field]'));
  const clearButton = form.querySelector('[data-conclusion-clear]');
  const errors = document.querySelector('[data-conclusion-errors]');
  const status = document.querySelector('[data-conclusion-status]');
  const jsonOutput = document.querySelector('[data-conclusion-json]');
  const pythonOutput = document.querySelector('[data-conclusion-python]');
  const copyButtons = Array.from(document.querySelectorAll('[data-conclusion-copy]'));

  if (!clearButton || !errors || !status || !jsonOutput || !pythonOutput) return;

  const readValues = () => {
    const values = {};
    const problems = [];

    fields.forEach((card) => {
      const name = card.dataset.conclusionName;
      const required = card.dataset.conclusionRequired === 'true';
      const input = card.querySelector('[data-conclusion-value]');
      const raw = input ? input.value.trim() : '';

      values[name] = raw || null;

      if (required && !raw) {
        problems.push({
          target: input ? input.id : '',
          message: `${name} is required.`,
        });
      }
    });

    const numberFields = [
      'reference_effect',
      'relative_tolerance',
      'absolute_tolerance',
      'minimum_recovery_fraction',
    ];

    numberFields.forEach((name) => {
      const raw = values[name];
      if (raw === null) return;
      const number = Number(raw);
      if (!Number.isFinite(number)) {
        problems.push({
          target: `conclusion-${name}`,
          message: `${name} must be finite.`,
        });
      } else {
        values[name] = number;
      }
    });

    const relative = values.relative_tolerance;
    const absolute = values.absolute_tolerance;
    if (relative === null && absolute === null) {
      problems.push({
        target: 'conclusion-relative_tolerance',
        message: (
          'At least one of relative_tolerance or absolute_tolerance is required.'
        ),
      });
    }

    for (const [name, value] of [
      ['relative_tolerance', relative],
      ['absolute_tolerance', absolute],
    ]) {
      if (typeof value === 'number' && value < 0) {
        problems.push({
          target: `conclusion-${name}`,
          message: `${name} must be non-negative.`,
        });
      }
    }

    const reference = values.reference_effect;
    if (
      typeof reference === 'number'
      && reference === 0
      && relative !== null
    ) {
      problems.push({
        target: 'conclusion-relative_tolerance',
        message: (
          'relative_tolerance cannot be used when reference_effect is zero; '
          + 'declare an absolute_tolerance instead.'
        ),
      });
    }

    const fraction = values.minimum_recovery_fraction;
    if (
      typeof fraction === 'number'
      && (fraction < 0 || fraction > 1)
    ) {
      problems.push({
        target: 'conclusion-minimum_recovery_fraction',
        message: 'minimum_recovery_fraction must be between 0 and 1.',
      });
    }

    if (values.require_sign === 'true') values.require_sign = true;
    if (values.require_sign === 'false') values.require_sign = false;

    return { values, problems };
  };

  const showErrors = (problems) => {
    form.querySelectorAll('[aria-invalid="true"]').forEach((control) => {
      control.removeAttribute('aria-invalid');
    });

    if (!problems.length) {
      errors.hidden = true;
      errors.replaceChildren();
      return;
    }

    const strong = document.createElement('strong');
    strong.textContent = (
      `Fix ${problems.length} conclusion-rule `
      + `field${problems.length === 1 ? '' : 's'}:`
    );
    const list = document.createElement('ul');

    problems.forEach((problem) => {
      const item = document.createElement('li');
      const target = problem.target
        ? document.getElementById(problem.target)
        : null;
      if (target) target.setAttribute('aria-invalid', 'true');

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
    errors.focus();
  };

  const pythonValue = (value) => {
    if (value === null) return 'None';
    if (value === true) return 'True';
    if (value === false) return 'False';
    if (typeof value === 'number') return String(value);
    return JSON.stringify(value);
  };

  const buildPython = (values) => [
    'from gazeaudit import ConclusionRule',
    '',
    `reference_effect = ${pythonValue(values.reference_effect)}`,
    '',
    'rule = ConclusionRule(',
    `    relative_tolerance=${pythonValue(values.relative_tolerance)},`,
    `    absolute_tolerance=${pythonValue(values.absolute_tolerance)},`,
    `    require_sign=${pythonValue(values.require_sign)},`,
    (
      '    minimum_recovery_fraction='
      + `${pythonValue(values.minimum_recovery_fraction)},`
    ),
    ')',
  ].join('\n');

  const render = (values) => {
    const record = {
      schema: 'gazeaudit-conclusion-rule-declaration-v1',
      ...values,
    };

    jsonOutput.textContent = JSON.stringify(record, null, 2);
    pythonOutput.textContent = buildPython(values);
    copyButtons.forEach((button) => {
      button.disabled = false;
    });
    status.textContent = (
      'Conclusion rule generated. Scientific justification remains external '
      + 'to the builder and must be preserved with the declaration.'
    );
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = readValues();

    if (payload.problems.length) {
      showErrors(payload.problems);
      status.textContent = (
        'Conclusion rule not generated. Correct the listed fields.'
      );
      return;
    }

    showErrors([]);
    render(payload.values);
  });

  clearButton.addEventListener('click', () => {
    form.reset();
    errors.hidden = true;
    errors.replaceChildren();
    jsonOutput.textContent = JSON.stringify(
      { schema: 'gazeaudit-conclusion-rule-declaration-v1' },
      null,
      2,
    );
    pythonOutput.textContent = '# Complete the conclusion rule declaration first.';
    copyButtons.forEach((button) => {
      button.disabled = true;
    });
    status.textContent = 'Conclusion rule declaration cleared.';
    document.getElementById('conclusion-rule_name')?.focus();
  });

  copyButtons.forEach((button) => {
    button.addEventListener('click', async () => {
      const target = button.dataset.conclusionCopy === 'json'
        ? jsonOutput
        : pythonOutput;
      try {
        await navigator.clipboard.writeText(target.textContent || '');
        status.textContent = (
          button.dataset.conclusionCopy === 'json'
            ? 'Conclusion rule JSON copied.'
            : 'Conclusion rule Python copied.'
        );
      } catch {
        status.textContent = 'Copy was unavailable. Select the generated text manually.';
      }
    });
  });
})();
