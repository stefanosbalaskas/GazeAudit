(() => {
  const form = document.querySelector('[data-spec-builder]');
  if (!form) return;

  const globalFields = Array.from(
    form.querySelectorAll('[data-spec-global-field]'),
  );
  const factorList = form.querySelector('[data-spec-factor-list]');
  const factorTemplate = form.querySelector('[data-spec-factor-template]');
  const addFactor = form.querySelector('[data-spec-add-factor]');
  const validityMode = form.querySelector('[data-spec-validity-mode]');
  const validityRule = document.getElementById('spec-validity_rule');
  const clearButton = form.querySelector('[data-spec-clear]');
  const errors = document.querySelector('[data-spec-errors]');
  const status = document.querySelector('[data-spec-status]');
  const jsonOutput = document.querySelector('[data-spec-json]');
  const pythonOutput = document.querySelector('[data-spec-python]');
  const copyButtons = Array.from(document.querySelectorAll('[data-spec-copy]'));

  if (
    !factorList
    || !factorTemplate
    || !addFactor
    || !validityMode
    || !clearButton
    || !errors
    || !status
    || !jsonOutput
    || !pythonOutput
  ) return;

  let nextFactorIndex = 2;

  const factorCards = () => Array.from(
    factorList.querySelectorAll('[data-spec-factor]'),
  );

  const updateRemoveButtons = () => {
    const cards = factorCards();
    cards.forEach((card) => {
      const button = card.querySelector('[data-spec-remove-factor]');
      if (button) button.disabled = cards.length === 1;
    });
  };

  const syncValidityMode = () => {
    const needsPredicate = validityMode.value === 'predicate_required';
    validityRule.disabled = !needsPredicate;
    validityRule.required = needsPredicate;

    if (!needsPredicate) {
      validityRule.value = '';
      validityRule.removeAttribute('aria-invalid');
    }
  };

  const parseLevels = (raw, type) => {
    const lines = String(raw)
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);

    if (!lines.length) {
      return { levels: [], error: 'at least one level is required' };
    }

    if (type === 'number') {
      const values = lines.map((value) => Number(value));
      if (values.some((value) => !Number.isFinite(value))) {
        return {
          levels: [],
          error: 'number levels must all be finite numeric values',
        };
      }
      return { levels: values, error: null };
    }

    if (type === 'boolean') {
      const normalized = lines.map((value) => value.toLocaleLowerCase());
      if (normalized.some((value) => !['true', 'false'].includes(value))) {
        return {
          levels: [],
          error: 'boolean levels must be true or false',
        };
      }
      return {
        levels: normalized.map((value) => value === 'true'),
        error: null,
      };
    }

    return { levels: lines, error: null };
  };

  const keyForLevel = (value) => (
    `${typeof value}:${JSON.stringify(value)}`
  );

  const pythonLiteral = (value) => {
    if (typeof value === 'boolean') return value ? 'True' : 'False';
    if (typeof value === 'number') return String(value);
    return JSON.stringify(value);
  };

  const collect = () => {
    const declaration = {};
    const problems = [];

    globalFields.forEach((card) => {
      const name = card.dataset.specName;
      const required = card.dataset.specRequired === 'true';
      const input = card.querySelector('[data-spec-global-value]');
      const value = input ? input.value.trim() : '';
      declaration[name] = value || null;

      if (required && !value) {
        problems.push({
          target: input ? input.id : '',
          message: `${name} is required.`,
        });
      }
    });

    const factors = [];
    const factorNames = new Set();

    factorCards().forEach((card, position) => {
      const nameInput = card.querySelector('[data-spec-factor-name]');
      const typeInput = card.querySelector('[data-spec-factor-type]');
      const levelsInput = card.querySelector('[data-spec-factor-levels]');
      const rationaleInput = card.querySelector('[data-spec-factor-rationale]');

      const name = nameInput ? nameInput.value.trim() : '';
      const type = typeInput ? typeInput.value : 'string';
      const rawLevels = levelsInput ? levelsInput.value : '';
      const rationale = rationaleInput ? rationaleInput.value.trim() : '';

      if (!name) {
        problems.push({
          target: nameInput ? nameInput.id : '',
          message: `Factor ${position + 1} needs a name.`,
        });
      } else if (factorNames.has(name)) {
        problems.push({
          target: nameInput ? nameInput.id : '',
          message: `Factor name ${name} is duplicated.`,
        });
      } else {
        factorNames.add(name);
      }

      const parsed = parseLevels(rawLevels, type);
      if (parsed.error) {
        problems.push({
          target: levelsInput ? levelsInput.id : '',
          message: `Factor ${name || position + 1}: ${parsed.error}.`,
        });
      } else {
        const unique = new Set(parsed.levels.map(keyForLevel));
        if (unique.size !== parsed.levels.length) {
          problems.push({
            target: levelsInput ? levelsInput.id : '',
            message: `Factor ${name || position + 1} contains duplicate levels.`,
          });
        }
      }

      if (!rationale) {
        problems.push({
          target: rationaleInput ? rationaleInput.id : '',
          message: `Factor ${name || position + 1} needs a rationale.`,
        });
      }

      factors.push({
        name,
        type,
        levels: parsed.levels,
        rationale,
      });
    });

    const validity = validityMode.value;
    declaration.validity_mode = validity;

    if (
      validity === 'predicate_required'
      && !declaration.validity_rule
    ) {
      const target = document.getElementById('spec-validity_rule');
      problems.push({
        target: target ? target.id : '',
        message: (
          'validity_rule is required when some combinations are invalid '
          + 'before execution.'
        ),
      });
    }

    const declaredCount = factors.reduce(
      (product, factor) => product * factor.levels.length,
      1,
    );

    return {
      declaration,
      factors,
      declaredCount,
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
    strong.textContent = (
      `Fix ${problems.length} specification declaration `
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

  const buildPython = (payload) => {
    const lines = [
      'from gazeaudit import PipelineSpace, run_specs',
      '',
      'space = PipelineSpace()',
    ];

    payload.factors.forEach((factor) => {
      const values = factor.levels.map(pythonLiteral).join(', ');
      lines.push(
        `space.add_choice(${JSON.stringify(factor.name)}, [${values}])`,
      );
    });

    lines.push(
      '',
      `assert space.size == ${payload.declaredCount}`,
      '',
    );

    if (payload.declaration.validity_mode === 'predicate_required') {
      const rule = payload.declaration.validity_rule || '';
      lines.push(
        'def valid_spec(spec):',
        `    # Declared pre-execution rule: ${rule.replace(/\n/g, ' ')}`,
        '    raise NotImplementedError(',
        '        "implement the declared pre-execution validity rule"',
        '    )',
        '',
        'valid_specs = space.enumerate_specs(valid_if=valid_spec)',
        '',
        'results = run_specs(',
        '    study,',
        '    space,',
        '    endpoint=endpoint,',
        '    processor=processor,',
        '    valid_if=valid_spec,',
        ')',
      );
    } else {
      lines.push(
        'valid_specs = space.enumerate_specs()',
        '',
        'results = run_specs(',
        '    study,',
        '    space,',
        '    endpoint=endpoint,',
        '    processor=processor,',
        ')',
      );
    }

    return lines.join('\n');
  };

  const render = (payload) => {
    const record = {
      schema: 'gazeaudit-specification-declaration-v1',
      ...payload.declaration,
      factors: payload.factors,
      declared_combination_count: payload.declaredCount,
      valid_combination_count: (
        payload.declaration.validity_mode === 'all_valid'
          ? payload.declaredCount
          : null
      ),
    };

    jsonOutput.textContent = JSON.stringify(record, null, 2);
    pythonOutput.textContent = buildPython(payload);
    copyButtons.forEach((button) => {
      button.disabled = false;
    });

    if (payload.declaration.validity_mode === 'all_valid') {
      status.textContent = (
        `Declaration generated: ${payload.declaredCount} declared and `
        + `${payload.declaredCount} valid combinations under the explicit `
        + 'all-valid declaration. No specifications were executed.'
      );
    } else {
      status.textContent = (
        `Declaration generated: ${payload.declaredCount} Cartesian `
        + 'combinations declared; valid count remains unknown until the '
        + 'declared validity predicate is implemented and enumerated.'
      );
    }
  };

  validityMode.addEventListener('change', syncValidityMode);

  addFactor.addEventListener('click', () => {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = factorTemplate.innerHTML.replaceAll(
      '__INDEX__',
      String(nextFactorIndex),
    );
    const card = wrapper.firstElementChild;
    if (!card) return;
    factorList.appendChild(card);
    nextFactorIndex += 1;
    updateRemoveButtons();
    card.querySelector('[data-spec-factor-name]')?.focus();
  });

  factorList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-spec-remove-factor]');
    if (!button || button.disabled) return;
    const card = button.closest('[data-spec-factor]');
    if (!card) return;
    card.remove();
    updateRemoveButtons();
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const payload = collect();

    if (payload.problems.length) {
      showErrors(payload.problems);
      status.textContent = (
        'Specification declaration not generated. Correct the listed fields.'
      );
      return;
    }

    showErrors([]);
    render(payload);
  });

  clearButton.addEventListener('click', () => {
    form.reset();

    factorCards().slice(1).forEach((card) => card.remove());
    const first = factorCards()[0];
    if (first) {
      first.querySelectorAll('input, textarea').forEach((control) => {
        control.value = '';
      });
      const type = first.querySelector('[data-spec-factor-type]');
      if (type) type.value = 'string';
    }

    validityMode.value = 'all_valid';
    syncValidityMode();
    nextFactorIndex = 2;
    updateRemoveButtons();

    errors.hidden = true;
    errors.replaceChildren();
    jsonOutput.textContent = JSON.stringify(
      { schema: 'gazeaudit-specification-declaration-v1' },
      null,
      2,
    );
    pythonOutput.textContent = '# Complete the specification declaration first.';
    copyButtons.forEach((button) => {
      button.disabled = true;
    });
    status.textContent = 'Specification declaration cleared.';
    document.getElementById('spec-space_name')?.focus();
  });

  copyButtons.forEach((button) => {
    button.addEventListener('click', async () => {
      const target = button.dataset.specCopy === 'json'
        ? jsonOutput
        : pythonOutput;
      try {
        await navigator.clipboard.writeText(target.textContent || '');
        status.textContent = (
          button.dataset.specCopy === 'json'
            ? 'Specification declaration JSON copied.'
            : 'PipelineSpace skeleton copied.'
        );
      } catch {
        status.textContent = 'Copy was unavailable. Select the generated text manually.';
      }
    });
  });

  syncValidityMode();
  updateRemoveButtons();
})();
