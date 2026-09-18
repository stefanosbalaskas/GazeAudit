(() => {
  const form = document.querySelector('[data-endpoint-builder]');
  if (!form) return;

  const fields = Array.from(form.querySelectorAll('[data-endpoint-field]'));
  const finiteGuard = form.querySelector('[data-endpoint-finite-guard]');
  const clearButton = form.querySelector('[data-endpoint-clear]');
  const errors = document.querySelector('[data-endpoint-errors]');
  const status = document.querySelector('[data-endpoint-status]');
  const jsonOutput = document.querySelector('[data-endpoint-json]');
  const pythonOutput = document.querySelector('[data-endpoint-python]');
  const copyButtons = Array.from(document.querySelectorAll('[data-endpoint-copy]'));

  if (
    !finiteGuard
    || !clearButton
    || !errors
    || !status
    || !jsonOutput
    || !pythonOutput
  ) return;

  const collect = () => {
    const declaration = {};
    const problems = [];

    fields.forEach((card) => {
      const name = card.dataset.endpointName;
      const required = card.dataset.endpointRequired === 'true';
      const input = card.querySelector('[data-endpoint-value]');
      const value = input ? input.value.trim() : '';

      declaration[name] = value || null;

      if (required && !value) {
        problems.push({
          target: input ? input.id : '',
          message: `${name} is required.`,
        });
      }
    });

    return {
      declaration,
      finiteGuard: finiteGuard.checked,
      problems,
    };
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
    strong.textContent = `Complete ${problems.length} required endpoint field${problems.length === 1 ? '' : 's'}:`;
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

  const commentLines = (label, value) => {
    const text = value || 'not declared';
    return String(text)
      .split(/\r?\n/)
      .map((line, index) => (
        index === 0
          ? `    # ${label}: ${line}`
          : `    # ${' '.repeat(label.length + 2)}${line}`
      ));
  };

  const buildPython = ({ declaration, finiteGuard: guard }) => {
    const lines = [
      'from gazeaudit import run_specs',
    ];

    if (guard) lines.unshift('import numpy as np');

    lines.push(
      '',
      'def endpoint(processed, spec):',
      `    """Return one scalar: ${declaration.endpoint_name}."""`,
      ...commentLines('Scientific quantity', declaration.scientific_quantity),
      ...commentLines('Unit / scale', declaration.unit),
      ...commentLines('Contrast / direction', declaration.contrast_direction),
      ...commentLines('Analysis unit', declaration.analysis_unit),
      ...commentLines('Population / denominator', declaration.population_denominator),
      ...commentLines('Missing-input policy', declaration.missingness_policy),
      ...commentLines('Non-finite policy', declaration.nonfinite_policy),
      ...commentLines('Transformation', declaration.transformation),
      ...commentLines('Scientific null', declaration.scientific_null),
      ...commentLines('Required inputs', declaration.required_inputs),
      ...commentLines('Interpretation boundary', declaration.interpretation_boundary),
      '',
      '    # Implement the prespecified calculation; do not change the estimand by branch.',
      '    raise NotImplementedError("implement the declared endpoint calculation")',
    );

    if (guard) {
      lines.push(
        '',
        '# After replacing NotImplementedError with the calculation, apply the declared guard:',
        '# estimate = float(estimate)',
        '# if not np.isfinite(estimate):',
        '#     raise ValueError("endpoint estimate must be finite under the declared contract")',
        '# return estimate',
      );
    }

    lines.push(
      '',
      'results = run_specs(',
      '    study,',
      '    space,',
      '    endpoint=endpoint,',
      '    processor=processor,',
      ')',
    );
    return lines.join('\n');
  };

  const render = (payload) => {
    const record = {
      schema: 'gazeaudit-endpoint-declaration-v1',
      ...payload.declaration,
      generate_finite_guard: payload.finiteGuard,
    };

    jsonOutput.textContent = JSON.stringify(record, null, 2);
    pythonOutput.textContent = buildPython(payload);
    copyButtons.forEach((button) => {
      button.disabled = false;
    });
    status.textContent = (
      'Endpoint declaration generated. The Python calculation remains intentionally unimplemented.'
    );
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = collect();

    if (payload.problems.length) {
      showErrors(payload.problems);
      status.textContent = 'Endpoint declaration not generated. Complete the required fields.';
      return;
    }

    showErrors([]);
    render(payload);
  });

  clearButton.addEventListener('click', () => {
    form.reset();
    errors.hidden = true;
    errors.replaceChildren();
    jsonOutput.textContent = JSON.stringify(
      { schema: 'gazeaudit-endpoint-declaration-v1' },
      null,
      2,
    );
    pythonOutput.textContent = '# Complete the endpoint declaration first.';
    copyButtons.forEach((button) => {
      button.disabled = true;
    });
    status.textContent = 'Endpoint declaration cleared.';
    const first = fields[0]?.querySelector('[data-endpoint-value]');
    first?.focus();
  });

  copyButtons.forEach((button) => {
    button.addEventListener('click', async () => {
      const target = button.dataset.endpointCopy === 'json'
        ? jsonOutput
        : pythonOutput;
      try {
        await navigator.clipboard.writeText(target.textContent || '');
        status.textContent = (
          button.dataset.endpointCopy === 'json'
            ? 'Endpoint declaration JSON copied.'
            : 'Endpoint Python skeleton copied.'
        );
      } catch {
        status.textContent = 'Copy was unavailable. Select the generated text manually.';
      }
    });
  });
})();
