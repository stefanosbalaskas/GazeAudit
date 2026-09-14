---
title: GazeAudit
description: Measurement uncertainty and inferential robustness for eye-tracking research.
page_type: landing
---

<div class="hero-wrap">
  <section class="hero">
    <div class="hero-grid">
      <div>
        <p class="eyebrow">Scientific Python · eye-tracking methodology</p>
        <h1>Audit the <span class="gradient-text">conclusion</span>, not only the pipeline.</h1>
        <p class="hero-lede">GazeAudit propagates gaze-measurement uncertainty and evaluates scientifically defensible analytical alternatives so researchers can see whether an eye-tracking conclusion survives reasonable choices.</p>
        <div class="hero-actions">
          <a class="button primary" href="{{ '/docs/getting-started/' | relative_url }}">Start in 5 minutes →</a>
          <a class="button" href="{{ '/docs/case-studies/' | relative_url }}">See real case studies</a>
          <button class="button" type="button" data-search-open>Search documentation</button>
          <a class="button" href="https://github.com/stefanosbalaskas/GazeAudit">View source</a>
        </div>
      </div>
      <div class="hero-panel">
        <span class="terminal-label">INSTALL · PUBLIC RELEASE 0.1.0</span>
        <pre><code>pip install gazeaudit==0.1.0</code></pre>
        <span class="terminal-label">SCIENTIFIC QUESTION</span>
        <pre><code>Would the conclusion survive
other reasonable measurement
and analytical choices?</code></pre>
      </div>
    </div>
  </section>
</div>

<section class="section" aria-label="Release facts">
  <div class="metrics-grid">
    <div class="metric-card"><strong>0.1.0</strong><span>first public alpha release</span></div>
    <div class="metric-card"><strong>Python 3.10–3.13</strong><span>tested supported range</span></div>
    <div class="metric-card"><strong>3 frozen cases</strong><span>contrasting validation outcomes</span></div>
    <div class="metric-card"><strong>MIT</strong><span>open-source license</span></div>
  </div>
</section>

<section class="section">
  <div class="section-heading">
    <p class="eyebrow">Two uncertainties, one audit</p>
    <h2>Separate what the tracker may have measured from what the analyst chose.</h2>
    <p>GazeAudit sits above parsing and event-detection tools. Its job is to make uncertainty and analytical decision spaces explicit, auditable, and reproducible.</p>
  </div>
  <div class="card-grid">
    <article class="feature-card">
      <div class="card-icon">±</div>
      <h3>Measurement uncertainty</h3>
      <p>Fit transparent gaze-error models from validation information, propagate uncertainty into AOI membership, and quantify boundary risk instead of treating coordinates as exact.</p>
    </article>
    <article class="feature-card">
      <div class="card-icon">⤨</div>
      <h3>Analytical robustness</h3>
      <p>Declare defensible preprocessing, detector, AOI, sampling, missingness, and QC choices; evaluate a common endpoint across the resulting specification space.</p>
    </article>
    <article class="feature-card">
      <div class="card-icon">#</div>
      <h3>Reproducible evidence</h3>
      <p>Bind methods, specifications, summaries, provenance, and scientific outputs into deterministic audit bundles with fingerprints that detect later mutation.</p>
    </article>
  </div>
</section>

<section class="section">
  <div class="section-heading">
    <p class="eyebrow">Workflow</p>
    <h2>A scientific workflow built around declared choices.</h2>
  </div>
  <figure class="plot-card">
    <img src="{{ '/assets/images/workflow-overview.svg' | relative_url }}" alt="Six-stage GazeAudit workflow from gaze data to a reproducible audit bundle">
    <figcaption>The package does not search for a favourable pipeline. The specification space and scientific endpoint are defined before robustness is summarised.</figcaption>
  </figure>
</section>

<section class="section">
  <div class="section-heading">
    <p class="eyebrow">Visual diagnostics</p>
    <h2>Reason about uncertainty with plots, not only tables.</h2>
    <p>Runnable examples pair code with visual explanations of AOI-boundary uncertainty, specification curves, and perturbation sensitivity.</p>
  </div>
  <div class="plot-grid">
    <figure class="plot-card">
      <img src="{{ '/assets/images/aoi-boundary-uncertainty.svg' | relative_url }}" alt="Illustrative probabilistic AOI membership near a shared AOI boundary">
      <figcaption><strong>AOI uncertainty.</strong> A boundary fixation can contribute probabilistically rather than being forced immediately into one deterministic label.</figcaption>
    </figure>
    <figure class="plot-card">
      <img src="{{ '/assets/images/specification-curve.svg' | relative_url }}" alt="Illustrative specification curve with ordered negative estimates">
      <figcaption><strong>Specification curve.</strong> Ordered estimates expose the shape of the declared analytical decision space. Values shown are synthetic illustrations.</figcaption>
    </figure>
  </div>
</section>

<section class="section">
  <div class="section-heading">
    <p class="eyebrow">Frozen validation programme</p>
    <h2>Robustness is allowed to produce different answers.</h2>
    <p>The real-data programme intentionally preserves contrasting outcomes. These are protocol-bound scientific records, not interchangeable quality badges.</p>
  </div>
  <div class="status-grid">
    <article class="status-card">
      <span class="status incomplete">Incomplete</span>
      <h3>GazeBase multi-detector audit</h3>
      <p>The frozen detector specification space did not satisfy the predeclared completeness gate.</p>
    </article>
    <article class="status-card">
      <span class="status robust">Robust negative</span>
      <h3>Korthals target-tracking AOI</h3>
      <p>The negative paired AOI effect survived the frozen measurement-error propagation model.</p>
    </article>
    <article class="status-card">
      <span class="status fragile">Materially fragile</span>
      <h3>Pedrotti/de Chambrier</h3>
      <p>The gaze-path-rate contrast did not remain stable across the frozen sampling and missingness perturbations.</p>
    </article>
  </div>
  <div class="hero-actions">
    <a class="button" href="{{ '/docs/case-studies/' | relative_url }}">Explore case studies</a>
    <a class="button" href="{{ '/docs/VALIDATION_MATRIX.html' | relative_url }}">Open validation matrix</a>
    <a class="button" href="{{ '/docs/SCIENTIFIC_METHODS.html' | relative_url }}">Read scientific methods</a>
  </div>
</section>

<section class="section">
  <div class="section-heading">
    <p class="eyebrow">Observed evidence</p>
    <h2>See what the frozen validation cases actually did.</h2>
    <p>These plots use the archived case-study numbers. They are explanatory views of the authoritative records, not new analyses.</p>
  </div>
  <div class="evidence-plot-grid">
    <figure class="plot-card">
      <img src="{{ '/assets/images/gazebase-completeness.svg' | relative_url }}" alt="GazeBase detector completeness plot">
      <figcaption><strong>GazeBase completeness.</strong> Five detectors reached 322/322 finite estimates; two reached 0/322, so the frozen 95% completeness gate failed. <a href="{{ '/docs/case-studies/gazebase-incomplete/' | relative_url }}">Read case →</a></figcaption>
    </figure>
    <figure class="plot-card">
      <img src="{{ '/assets/images/korthals-effect.svg' | relative_url }}" alt="Korthals hard and uncertainty-propagated AOI effects">
      <figcaption><strong>Korthals uncertainty.</strong> The expected effect moved toward zero but all 2,000 prespecified draws remained below zero. <a href="{{ '/docs/case-studies/korthals-target-tracking/' | relative_url }}">Read case →</a></figcaption>
    </figure>
    <figure class="plot-card">
      <img src="{{ '/assets/images/pedrotti-sampling-sensitivity.svg' | relative_url }}" alt="Pedrotti sampling-rate sensitivity plot">
      <figcaption><strong>Pedrotti sensitivity.</strong> Direction stayed negative while magnitude recovery failed at 125, 100, and 50 Hz. <a href="{{ '/docs/case-studies/pedrotti-sensitivity/' | relative_url }}">Read case →</a></figcaption>
    </figure>
  </div>
</section>

<section class="section">
  <div class="section-heading">
    <p class="eyebrow">Choose a path</p>
    <h2>Documentation organised by the job you are trying to do.</h2>
  </div>
  <div class="card-grid">
    <article class="card">
      <h3>Learn the package</h3>
      <p>Install GazeAudit, fit an error model, define AOIs, and run the smallest uncertainty-aware example.</p>
      <p><a href="{{ '/docs/getting-started/' | relative_url }}">Getting started →</a></p>
    </article>
    <article class="card">
      <h3>Design an analysis</h3>
      <p>Build a specification space, define a common endpoint, and decide which sensitivity analyses belong in the study.</p>
      <p><a href="{{ '/docs/guides/specification-space/' | relative_url }}">Specification-space guide →</a></p>
    </article>
    <article class="card">
      <h3>Publish reproducibly</h3>
      <p>Generate deterministic audit bundles, capture provenance, and report what was declared before inspecting robustness outputs.</p>
      <p><a href="{{ '/docs/workflows/reproducible-publication/' | relative_url }}">Publication workflow →</a></p>
    </article>
  </div>
</section>

<section class="section narrow">
  <div class="section-heading">
    <p class="eyebrow">Citation</p>
    <h2>Archive a specific release when reproducibility matters.</h2>
    <p>Version 0.1.0 is archived at Zenodo DOI <a href="https://doi.org/10.5281/zenodo.22757340">10.5281/zenodo.22757340</a>. Record the exact software version or commit used in the analysis.</p>
  </div>
</section>
