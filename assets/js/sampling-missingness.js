(() => {
  const contractGrid = document.querySelector('[data-sampling-contract-grid]');
  const contractControls = document.querySelector('[data-sampling-contract-controls]');

  if (contractGrid && contractControls) {
    const cards = Array.from(
      contractGrid.querySelectorAll('[data-sampling-contract-card]'),
    );
    const search = contractControls.querySelector('[data-sampling-contract-search]');
    const family = contractControls.querySelector('[data-sampling-contract-family]');
    const clear = contractControls.querySelector('[data-sampling-contract-clear]');
    const status = document.querySelector('[data-sampling-contract-status]');
    const empty = document.querySelector('[data-sampling-contract-empty]');

    if (search && family && clear && status && empty) {
      const normalize = (value) => (
        String(value || '').trim().toLocaleLowerCase()
      );

      const apply = () => {
        const query = normalize(search.value);
        const selectedFamily = family.value;
        let visible = 0;

        cards.forEach((card) => {
          const matchesQuery = (
            !query
            || normalize(card.dataset.samplingContractSearch).includes(query)
          );
          const matchesFamily = (
            !selectedFamily
            || card.dataset.samplingContractFamily === selectedFamily
          );
          const show = matchesQuery && matchesFamily;
          card.hidden = !show;
          if (show) visible += 1;
        });

        const filtered = Boolean(query || selectedFamily);
        status.textContent = filtered
          ? `Showing ${visible} of ${cards.length} contracts.`
          : `Showing all ${cards.length} contracts.`;
        empty.hidden = visible !== 0;
      };

      [search, family].forEach((control) => {
        control.addEventListener('input', apply);
        control.addEventListener('change', apply);
      });

      clear.addEventListener('click', () => {
        search.value = '';
        family.value = '';
        apply();
        search.focus();
      });

      apply();
    }
  }

  const form = document.querySelector('[data-sampling-plan-builder]');
  if (!form) return;

  const fields = {
    name: form.querySelector('[data-plan-name]'),
    endpoint: form.querySelector('[data-plan-endpoint]'),
    family: form.querySelector('[data-plan-family]'),
    baseline: form.querySelector('[data-plan-baseline]'),
    rationale: form.querySelector('[data-plan-rationale]'),
    boundary: form.querySelector('[data-plan-boundary]'),
    rates: form.querySelector('[data-plan-rates]'),
    timestampUnit: form.querySelector('[data-plan-timestamp-unit]'),
    fractions: form.querySelector('[data-plan-fractions]'),
    mechanism: form.querySelector('[data-plan-mechanism]'),
    seed: form.querySelector('[data-plan-seed]'),
    replication: form.querySelector('[data-plan-replication]'),
  };

  const samplingFieldset = form.querySelector('[data-plan-sampling-fields]');
  const missingnessFieldset = form.querySelector('[data-plan-missingness-fields]');
  const clearButton = form.querySelector('[data-plan-clear]');
  const errors = document.querySelector('[data-plan-errors]');
  const status = document.querySelector('[data-plan-status]');
  const jsonOutput = document.querySelector('[data-plan-json]');
  const pythonOutput = document.querySelector('[data-plan-python]');
  const copyButtons = Array.from(document.querySelectorAll('[data-plan-copy]'));

  if (
    Object.values(fields).some((field) => !field)
    || !samplingFieldset
    || !missingnessFieldset
    || !clearButton
    || !errors
    || !status
    || !jsonOutput
    || !pythonOutput
  ) return;

  const usesSampling = () => (
    fields.family.value === 'sampling'
    || fields.family.value === 'separate_both'
  );

  const usesMissingness = () => (
    fields.family.value === 'missingness'
    || fields.family.value === 'separate_both'
  );

  const syncFamily = () => {
    samplingFieldset.disabled = !usesSampling();
    missingnessFieldset.disabled = !usesMissingness();

    fields.rates.required = usesSampling();
    fields.timestampUnit.required = usesSampling();
    fields.fractions.required = usesMissingness();
    fields.mechanism.required = usesMissingness();
    fields.seed.required = usesMissingness();

    if (!usesSampling()) {
      fields.rates.value = '';
      fields.timestampUnit.value = '';
    }
    if (!usesMissingness()) {
      fields.fractions.value = '';
      fields.mechanism.value = '';
      fields.seed.value = '';
      fields.replication.value = '';
    }
  };

  const parseNumberList = (raw, { label, min, max = null, positive = false }) => {
    const rows = String(raw)
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);

    if (!rows.length) {
      return { values: [], error: `${label} requires at least one value.` };
    }

    const values = rows.map((value) => Number(value));
    if (values.some((value) => !Number.isFinite(value))) {
      return { values: [], error: `${label} values must be finite numbers.` };
    }
    if (positive && values.some((value) => value <= 0)) {
      return { values: [], error: `${label} values must be greater than zero.` };
    }
    if (values.some((value) => value < min)) {
      return { values: [], error: `${label} values must be at least ${min}.` };
    }
    if (max !== null && values.some((value) => value > max)) {
      return { values: [], error: `${label} values must be at most ${max}.` };
    }

    const keys = values.map((value) => String(value));
    if (new Set(keys).size !== keys.length) {
      return { values: [], error: `${label} contains duplicate values.` };
    }

    return { values, error: null };
  };

  const collect = () => {
    const problems = [];
    const required = [
      ['name', 'Plan name'],
      ['endpoint', 'Endpoint declaration reference'],
      ['family', 'Sensitivity family'],
      ['baseline', 'Baseline representation reference'],
      ['rationale', 'Scientific rationale'],
      ['boundary', 'Interpretation boundary'],
    ];

    required.forEach(([key, label]) => {
      if (!String(fields[key].value).trim()) {
        problems.push({
          target: fields[key].id,
          message: `${label} is required.`,
        });
      }
    });

    let rates = [];
    if (usesSampling()) {
      const parsed = parseNumberList(fields.rates.value, {
        label: 'Target rates',
        min: 0,
        positive: true,
      });
      if (parsed.error) {
        problems.push({ target: fields.rates.id, message: parsed.error });
      }
      rates = parsed.values;

      if (!['ms', 's'].includes(fields.timestampUnit.value)) {
        problems.push({
          target: fields.timestampUnit.id,
          message: 'Timestamp unit must be chosen explicitly.',
        });
      }
    }

    let fractions = [];
    let seed = null;
    if (usesMissingness()) {
      const parsed = parseNumberList(fields.fractions.value, {
        label: 'Missingness fractions',
        min: 0,
        max: 1,
      });
      if (parsed.error) {
        problems.push({ target: fields.fractions.id, message: parsed.error });
      }
      fractions = parsed.values;

      if (!['mcar', 'block'].includes(fields.mechanism.value)) {
        problems.push({
          target: fields.mechanism.id,
          message: 'Missingness mechanism must be chosen explicitly.',
        });
      }

      const seedText = String(fields.seed.value).trim();
      const parsedSeed = Number(seedText);
      if (
        !seedText
        || !Number.isSafeInteger(parsedSeed)
        || parsedSeed < 0
      ) {
        problems.push({
          target: fields.seed.id,
          message: 'Root seed must be a non-negative safe integer.',
        });
      } else {
        seed = parsedSeed;
      }
    }

    return {
      problems,
      record: {
        schema: 'gazeaudit-sampling-missingness-plan-v1',
        plan_name: fields.name.value.trim() || null,
        endpoint_reference: fields.endpoint.value.trim() || null,
        sensitivity_family: fields.family.value || null,
        baseline_reference: fields.baseline.value.trim() || null,
        scientific_rationale: fields.rationale.value.trim() || null,
        interpretation_boundary: fields.boundary.value.trim() || null,
        sampling: usesSampling()
          ? {
              target_rates_hz: rates,
              timestamp_unit: fields.timestampUnit.value,
            }
          : null,
        missingness: usesMissingness()
          ? {
              requested_fractions: fractions,
              mechanism: fields.mechanism.value,
              root_seed: seed,
              outer_replication_plan: fields.replication.value.trim() || null,
            }
          : null,
      },
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
    strong.textContent = (
      `Fix ${problems.length} sensitivity plan `
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

  const pythonList = (values) => (
    '[' + values.map((value) => String(value)).join(', ') + ']'
  );

  const buildPython = (record) => {
    const imports = ['summarize_missingness'];
    if (record.sampling) imports.push('sampling_sensitivity_curve');
    if (record.missingness) imports.push('missingness_sensitivity_curve');

    const lines = [
      'from gazeaudit import (',
      ...imports.map((name) => `    ${name},`),
      ')',
      '',
      'baseline_missingness = summarize_missingness(study)',
      'print(baseline_missingness)',
      '',
    ];

    if (record.sampling) {
      lines.push(
        'sampling_curve = sampling_sensitivity_curve(',
        '    study,',
        `    target_rates=${pythonList(record.sampling.target_rates_hz)},`,
        '    endpoint=endpoint,',
        `    timestamp_unit=${JSON.stringify(record.sampling.timestamp_unit)},`,
        ')',
        '',
      );
    }

    if (record.missingness) {
      lines.push(
        'missingness_curve = missingness_sensitivity_curve(',
        '    study,',
        `    fractions=${pythonList(record.missingness.requested_fractions)},`,
        '    endpoint=endpoint,',
        `    mechanism=${JSON.stringify(record.missingness.mechanism)},`,
        `    rng=${record.missingness.root_seed},`,
        ')',
        '',
      );

      if (record.missingness.outer_replication_plan) {
        lines.push(
          '# Outer replication is declared in project provenance but is not',
          '# generated automatically by missingness_sensitivity_curve():',
          `# ${record.missingness.outer_replication_plan.replace(/\n/g, ' ')}`,
          '',
        );
      }
    }

    return lines.join('\n').trimEnd();
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = collect();

    if (payload.problems.length) {
      showErrors(payload.problems);
      status.textContent = (
        'Sensitivity plan not generated. Correct the listed fields.'
      );
      return;
    }

    showErrors([]);
    jsonOutput.textContent = JSON.stringify(payload.record, null, 2);
    pythonOutput.textContent = buildPython(payload.record);
    copyButtons.forEach((button) => {
      button.disabled = false;
    });
    status.textContent = (
      'Sensitivity plan generated. No data were inspected or perturbed.'
    );
  });

  fields.family.addEventListener('change', syncFamily);

  clearButton.addEventListener('click', () => {
    form.reset();
    syncFamily();
    errors.hidden = true;
    errors.replaceChildren();
    jsonOutput.textContent = JSON.stringify(
      { schema: 'gazeaudit-sampling-missingness-plan-v1' },
      null,
      2,
    );
    pythonOutput.textContent = '# Complete the sensitivity plan first.';
    copyButtons.forEach((button) => {
      button.disabled = true;
    });
    status.textContent = 'Sensitivity plan cleared.';
    fields.name.focus();
  });

  copyButtons.forEach((button) => {
    button.addEventListener('click', async () => {
      const target = button.dataset.planCopy === 'json'
        ? jsonOutput
        : pythonOutput;
      try {
        await navigator.clipboard.writeText(target.textContent || '');
        status.textContent = (
          button.dataset.planCopy === 'json'
            ? 'Sensitivity plan JSON copied.'
            : 'Sensitivity Python skeleton copied.'
        );
      } catch {
        status.textContent = 'Copy was unavailable. Select the generated text manually.';
      }
    });
  });

  syncFamily();
})();
