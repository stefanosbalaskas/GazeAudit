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
    sourceId: form.querySelector('[data-schema-source-id]'),
    coordinateUnit: form.querySelector('[data-schema-coordinate-unit]'),
    coordinateConvention: form.querySelector('[data-schema-coordinate-convention]'),
    timestampUnit: form.querySelector('[data-schema-timestamp-unit]'),
    transformations: form.querySelector('[data-schema-transformations]'),
  };
  const clear = form.querySelector('[data-schema-clear]');
  const code = document.querySelector('[data-schema-code]');
  const copy = document.querySelector('[data-schema-copy]');
  const status = document.querySelector('[data-schema-status]');
  const record = document.querySelector('[data-schema-record]');
  const recordCopy = document.querySelector('[data-schema-record-copy]');

  if (
    Object.values(fields).some((field) => !field)
    || !clear
    || !code
    || !copy
    || !status
    || !record
    || !recordCopy
  ) {
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
    sourceId: fields.sourceId.value.trim(),
    coordinateUnit: fields.coordinateUnit.value.trim(),
    coordinateConvention: fields.coordinateConvention.value.trim(),
    timestampUnit: fields.timestampUnit.value.trim(),
    transformations: fields.transformations.value.trim(),
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

  const buildRecord = (mapping) => JSON.stringify(
    {
      schema: 'gazeaudit-data-mapping-record-v1',
      source_id: mapping.sourceId,
      columns: {
        participant: mapping.participant,
        trial: mapping.trial,
        timestamp: mapping.timestamp,
        x: mapping.x,
        y: mapping.y,
      },
      units: {
        coordinates: mapping.coordinateUnit,
        timestamp: mapping.timestampUnit,
      },
      coordinate_convention: mapping.coordinateConvention,
      pre_mapping_transformations: mapping.transformations,
    },
    null,
    2,
  );

  const setIncomplete = (message, codeMessage) => {
    code.textContent = codeMessage;
    record.textContent = 'Complete all five semantic column mappings to generate the mapping record.';
    status.textContent = message;
    copy.disabled = true;
    recordCopy.disabled = true;
  };

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
      setIncomplete(
        'DataFrame variable is required.',
        'Enter a DataFrame variable name to generate code.',
      );
      return;
    }

    if (!pythonIdentifier.test(mapping.dataVar)) {
      setIncomplete(
        'The DataFrame variable must be a valid Python identifier.',
        'Use a valid Python identifier for the DataFrame variable.',
      );
      return;
    }

    if (semanticValues.some((value) => !value)) {
      setIncomplete(
        'Participant, trial, timestamp, x, and y column names are all required.',
        'Complete all five semantic column mappings to generate code.',
      );
      return;
    }

    code.textContent = buildSnippet(mapping);
    record.textContent = buildRecord(mapping);
    status.textContent = 'Mapping and provenance record generated. Optional provenance fields remain descriptive and are never inferred.';
    copy.disabled = false;
    recordCopy.disabled = false;
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
    fields.sourceId.value = '';
    fields.coordinateUnit.value = '';
    fields.coordinateConvention.value = '';
    fields.timestampUnit.value = '';
    fields.transformations.value = '';
    render();
    fields.participant.focus();
  });

  const wireCopy = (button, source, successLabel) => {
    button.addEventListener('click', async () => {
      if (button.disabled) return;
      try {
        await copyText(source.textContent);
        const original = button.textContent;
        button.textContent = successLabel;
        window.setTimeout(() => {
          button.textContent = original;
        }, 1400);
      } catch {
        status.textContent = 'Copy failed. Select the generated content manually.';
      }
    });
  };

  wireCopy(copy, code, 'Copied');
  wireCopy(recordCopy, record, 'Record copied');

  render();
})();
