(() => {
  const form = document.querySelector('[data-schema-mapper]');
  if (!form) return;

  const fields = {
    dataVar: form.querySelector('[data-schema-data-var]'),
    participant: form.querySelector('[data-schema-participant]'),
    trial: form.querySelector('[data-schema-trial]'),
    timestamp: form.querySelector('[data-schema-timestamp]'),
    x: form.querySelector('[data-schema-x]'),
    y: form.querySelector('[data-schema-y]'),
  };
  const clear = form.querySelector('[data-schema-clear]');
  const code = document.querySelector('[data-schema-code]');
  const copy = document.querySelector('[data-schema-copy]');
  const status = document.querySelector('[data-schema-status]');

  if (Object.values(fields).some((field) => !field) || !clear || !code || !copy || !status) {
    return;
  }

  const pythonString = (value) => JSON.stringify(String(value));
  const pythonIdentifier = /^[A-Za-z_][A-Za-z0-9_]*$/;

  const current = () => ({
    dataVar: fields.dataVar.value.trim(),
    participant: fields.participant.value.trim(),
    trial: fields.trial.value.trim(),
    timestamp: fields.timestamp.value.trim(),
    x: fields.x.value.trim(),
    y: fields.y.value.trim(),
  });

  const buildSnippet = (mapping) => [
    'from gazeaudit import GazeStudy',
    '',
    'study = GazeStudy(',
    `    ${mapping.dataVar},`,
    `    x=${pythonString(mapping.x)},`,
    `    y=${pythonString(mapping.y)},`,
    `    timestamp=${pythonString(mapping.timestamp)},`,
    `    participant=${pythonString(mapping.participant)},`,
    `    trial=${pythonString(mapping.trial)},`,
    ')',
  ].join('\n');

  const render = () => {
    const mapping = current();
    const semanticValues = [
      mapping.participant,
      mapping.trial,
      mapping.timestamp,
      mapping.x,
      mapping.y,
    ];

    if (!mapping.dataVar) {
      code.textContent = 'Enter a DataFrame variable name to generate code.';
      status.textContent = 'DataFrame variable is required.';
      copy.disabled = true;
      return;
    }

    if (!pythonIdentifier.test(mapping.dataVar)) {
      code.textContent = 'Use a valid Python identifier for the DataFrame variable.';
      status.textContent = 'The DataFrame variable must be a valid Python identifier.';
      copy.disabled = true;
      return;
    }

    if (semanticValues.some((value) => !value)) {
      code.textContent = 'Complete all five semantic column mappings to generate code.';
      status.textContent = 'Participant, trial, timestamp, x, and y column names are all required.';
      copy.disabled = true;
      return;
    }

    code.textContent = buildSnippet(mapping);
    status.textContent = 'Mapping snippet generated. Units and scientific meaning still need to be recorded separately.';
    copy.disabled = false;
  };

  const copyText = async (text) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    textarea.remove();
  };

  Object.values(fields).forEach((field) => {
    field.addEventListener('input', render);
  });

  clear.addEventListener('click', () => {
    fields.dataVar.value = 'frame';
    fields.participant.value = '';
    fields.trial.value = '';
    fields.timestamp.value = '';
    fields.x.value = '';
    fields.y.value = '';
    render();
    fields.participant.focus();
  });

  copy.addEventListener('click', async () => {
    if (copy.disabled) return;
    try {
      await copyText(code.textContent);
      const original = copy.textContent;
      copy.textContent = 'Copied';
      window.setTimeout(() => {
        copy.textContent = original;
      }, 1400);
    } catch {
      status.textContent = 'Copy failed. Select the generated code manually.';
    }
  });

  render();
})();
