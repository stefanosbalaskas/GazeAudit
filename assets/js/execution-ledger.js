(() => {
  const stateGrid = document.querySelector('[data-execution-state-grid]');
  const stateControls = document.querySelector('[data-execution-state-controls]');

  if (stateGrid && stateControls) {
    const cards = Array.from(
      stateGrid.querySelectorAll('[data-execution-state-card]'),
    );
    const search = stateControls.querySelector('[data-execution-state-search]');
    const phase = stateControls.querySelector('[data-execution-state-phase]');
    const clear = stateControls.querySelector('[data-execution-state-clear]');
    const status = document.querySelector('[data-execution-state-status]');
    const empty = document.querySelector('[data-execution-state-empty]');

    if (search && phase && clear && status && empty) {
      const normalize = (value) => (
        String(value || '').trim().toLocaleLowerCase()
      );

      const apply = () => {
        const query = normalize(search.value);
        const selectedPhase = phase.value;
        let visible = 0;

        cards.forEach((card) => {
          const matchesQuery = (
            !query || normalize(card.dataset.executionStateSearch).includes(query)
          );
          const matchesPhase = (
            !selectedPhase
            || card.dataset.executionStatePhase === selectedPhase
          );
          const show = matchesQuery && matchesPhase;
          card.hidden = !show;
          if (show) visible += 1;
        });

        const filtered = Boolean(query || selectedPhase);
        status.textContent = filtered
          ? `Showing ${visible} of ${cards.length} execution states/events.`
          : `Showing all ${cards.length} execution states/events.`;
        empty.hidden = visible !== 0;
      };

      [search, phase].forEach((control) => {
        control.addEventListener('input', apply);
        control.addEventListener('change', apply);
      });

      clear.addEventListener('click', () => {
        search.value = '';
        phase.value = '';
        apply();
        search.focus();
      });

      stateGrid.addEventListener('click', async (event) => {
        const button = event.target.closest('[data-execution-copy-report]');
        if (!button) return;
        const card = button.closest('[data-execution-state-card]');
        const target = card?.querySelector('[data-execution-report-template]');
        if (!target) return;

        try {
          await navigator.clipboard.writeText(target.textContent.trim());
          status.textContent = 'Reporting wording copied.';
        } catch {
          status.textContent = (
            'Copy was unavailable. Select the reporting wording manually.'
          );
        }
      });

      apply();
    }
  }

  const form = document.querySelector('[data-execution-attempt-builder]');
  if (!form) return;

  const fields = {
    branch: form.querySelector('[data-attempt-branch]'),
    attempt: form.querySelector('[data-attempt-id]'),
    validity: form.querySelector('[data-attempt-validity]'),
    state: form.querySelector('[data-attempt-state]'),
    endpoint: form.querySelector('[data-attempt-endpoint]'),
    layer: form.querySelector('[data-attempt-layer]'),
    factors: form.querySelector('[data-attempt-factors]'),
    source: form.querySelector('[data-attempt-source]'),
    estimate: form.querySelector('[data-attempt-estimate]'),
    errorType: form.querySelector('[data-attempt-error-type]'),
    errorMessage: form.querySelector('[data-attempt-error-message]'),
    prior: form.querySelector('[data-attempt-prior]'),
    repair: form.querySelector('[data-attempt-repair]'),
    outcomeSeen: form.querySelector('[data-attempt-outcome-seen]'),
  };

  const clearButton = form.querySelector('[data-attempt-clear]');
  const errors = document.querySelector('[data-attempt-errors]');
  const status = document.querySelector('[data-attempt-status]');
  const output = document.querySelector('[data-attempt-json]');
  const copy = document.querySelector('[data-attempt-copy]');

  if (
    Object.values(fields).some((field) => !field)
    || !clearButton
    || !errors
    || !status
    || !output
    || !copy
  ) return;

  const parseFactors = (raw) => {
    const rows = String(raw)
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);
    const values = {};
    const problems = [];

    rows.forEach((row) => {
      const separator = row.indexOf('=');
      if (separator <= 0 || separator === row.length - 1) {
        problems.push(
          'Factor values must use one factor=value pair per line.',
        );
        return;
      }
      const name = row.slice(0, separator).trim();
      const value = row.slice(separator + 1).trim();
      if (Object.prototype.hasOwnProperty.call(values, name)) {
        problems.push(`Factor ${name} is duplicated.`);
        return;
      }
      values[name] = value;
    });

    return { values, problems };
  };

  const isFiniteNumberText = (raw) => {
    const value = String(raw).trim();
    if (!value) return false;
    const parsed = Number(value);
    return Number.isFinite(parsed);
  };

  const isNonFiniteText = (raw) => (
    ['nan', 'infinity', '+infinity', '-infinity'].includes(
      String(raw).trim().toLocaleLowerCase(),
    )
  );

  const collect = () => {
    const problems = [];
    const required = [
      ['branch', 'Branch ID'],
      ['attempt', 'Attempt ID'],
      ['validity', 'Scientific validity'],
      ['state', 'Execution state'],
      ['endpoint', 'Endpoint reference'],
      ['layer', 'Temporal evidence layer'],
      ['factors', 'Factor values'],
      ['source', 'Source/software reference'],
      ['outcomeSeen', 'Outcome-inspection state'],
    ];

    required.forEach(([key, label]) => {
      if (!String(fields[key].value).trim()) {
        problems.push({
          target: fields[key].id,
          message: `${label} is required.`,
        });
      }
    });

    const factors = parseFactors(fields.factors.value);
    factors.problems.forEach((message) => {
      problems.push({
        target: fields.factors.id,
        message,
      });
    });

    const validity = fields.validity.value;
    const state = fields.state.value;
    const estimate = fields.estimate.value.trim();
    const errorType = fields.errorType.value.trim();
    const errorMessage = fields.errorMessage.value.trim();
    const prior = fields.prior.value.trim();
    const repair = fields.repair.value.trim();

    if (state === 'invalid_before_execution') {
      if (validity !== 'invalid_before_execution') {
        problems.push({
          target: fields.validity.id,
          message: (
            'Invalid-before-execution state requires matching scientific '
            + 'validity.'
          ),
        });
      }
      if (estimate || errorType || errorMessage) {
        problems.push({
          target: fields.estimate.id,
          message: (
            'Invalid-before-execution records must not contain an estimate '
            + 'or execution error.'
          ),
        });
      }
    } else if (state) {
      if (validity !== 'valid') {
        problems.push({
          target: fields.validity.id,
          message: `${state} requires a scientifically valid branch.`,
        });
      }
    }

    if (state === 'successful' && !isFiniteNumberText(estimate)) {
      problems.push({
        target: fields.estimate.id,
        message: 'Successful execution requires a finite numeric estimate.',
      });
    }

    if (
      state === 'successful'
      && (errorType || errorMessage || prior || repair)
    ) {
      problems.push({
        target: fields.errorMessage.id,
        message: (
          'Successful execution must not contain an execution error, '
          + 'prior attempt, or repair reference.'
        ),
      });
    }

    if (
      state === 'technical_failure'
      && !errorType
      && !errorMessage
    ) {
      problems.push({
        target: fields.errorMessage.id,
        message: (
          'Technical failure requires an error type or error message.'
        ),
      });
    }

    if (state === 'technical_failure' && estimate) {
      problems.push({
        target: fields.estimate.id,
        message: (
          'Technical failure must not contain a scientific estimate.'
        ),
      });
    }

    if (state === 'non_finite_endpoint' && !isNonFiniteText(estimate)) {
      problems.push({
        target: fields.estimate.id,
        message: (
          'Non-finite endpoint requires NaN, Infinity, +Infinity, '
          + 'or -Infinity.'
        ),
      });
    }

    if (state === 'non_finite_endpoint' && errorType) {
      problems.push({
        target: fields.errorType.id,
        message: (
          'Non-finite endpoint is an endpoint value state, not an '
          + 'exception type.'
        ),
      });
    }

    if (state === 'not_run') {
      if (!errorMessage) {
        problems.push({
          target: fields.errorMessage.id,
          message: 'Not-run state requires an explicit reason.',
        });
      }
      if (estimate) {
        problems.push({
          target: fields.estimate.id,
          message: 'Not-run state must not contain an estimate.',
        });
      }
    }

    if (state === 'repair_rerun_success') {
      if (!isFiniteNumberText(estimate)) {
        problems.push({
          target: fields.estimate.id,
          message: 'Successful repair rerun requires a finite estimate.',
        });
      }
      if (!prior) {
        problems.push({
          target: fields.prior.id,
          message: 'Successful repair rerun requires the prior attempt ID.',
        });
      }
      if (!repair) {
        problems.push({
          target: fields.repair.id,
          message: 'Successful repair rerun requires a repair record reference.',
        });
      }
      if (prior && prior === fields.attempt.value.trim()) {
        problems.push({
          target: fields.prior.id,
          message: (
            'Prior attempt ID must differ from the new repair-rerun attempt ID.'
          ),
        });
      }
      if (errorType || errorMessage) {
        problems.push({
          target: fields.errorMessage.id,
          message: (
            'Successful repair rerun must not retain an active execution error.'
          ),
        });
      }
    }

    const parsedEstimate = (
      state === 'successful' || state === 'repair_rerun_success'
        ? Number(estimate)
        : estimate || null
    );

    const record = {
      schema: 'gazeaudit-execution-attempt-v1',
      branch_id: fields.branch.value.trim() || null,
      attempt_id: fields.attempt.value.trim() || null,
      scientific_validity: validity || null,
      execution_state: state || null,
      endpoint_reference: fields.endpoint.value.trim() || null,
      temporal_evidence_layer: fields.layer.value.trim() || null,
      factor_values: factors.values,
      source_software_reference: fields.source.value.trim() || null,
      estimate: parsedEstimate,
      error_type: errorType || null,
      error_or_not_run_reason: errorMessage || null,
      prior_attempt_id: prior || null,
      repair_record_reference: repair || null,
      relevant_outcomes_already_inspected: (
        fields.outcomeSeen.value === ''
          ? null
          : fields.outcomeSeen.value === 'true'
      ),
    };

    return { problems, record };
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
      `Fix ${problems.length} attempt record `
      + `field${problems.length === 1 ? '' : 's'}:`
    );
    const list = document.createElement('ul');

    problems.forEach((problem) => {
      const item = document.createElement('li');
      const target = document.getElementById(problem.target);
      if (target) target.setAttribute('aria-invalid', 'true');

      if (target) {
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

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = collect();

    if (payload.problems.length) {
      showErrors(payload.problems);
      status.textContent = (
        'Attempt record not generated. Correct the listed fields.'
      );
      return;
    }

    showErrors([]);
    output.textContent = JSON.stringify(payload.record, null, 2);
    copy.disabled = false;
    status.textContent = (
      'Attempt record generated. Scientific validity and repair '
      + 'appropriateness remain researcher-owned.'
    );
  });

  clearButton.addEventListener('click', () => {
    form.reset();
    errors.hidden = true;
    errors.replaceChildren();
    output.textContent = JSON.stringify(
      { schema: 'gazeaudit-execution-attempt-v1' },
      null,
      2,
    );
    copy.disabled = true;
    status.textContent = 'Attempt record cleared.';
    fields.branch.focus();
  });

  copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(output.textContent || '');
      status.textContent = 'Attempt JSON copied.';
    } catch {
      status.textContent = (
        'Copy was unavailable. Select the generated JSON manually.'
      );
    }
  });
})();
