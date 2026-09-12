# Korthals tutorial source-scope boundary

This note records an endpoint-blind intake correction for the frozen Korthals et al. case study.

The published study describes one tutorial trial before the 144-trial task battery. The experiment code instantiates that tutorial as `trial_number = 0`, with `trial_name = "Tutorial"`, `target_type = "moving_circle"`, `target_speed = 2`, and eastward trajectory. The 144 scientific task trials are then numbered 1 through 144.

GazeAudit's frozen endpoint already defines repetition 1 as trials 1–72 and repetition 2 as trials 73–144. Source intake therefore excludes trial 0 only when all out-of-range rows match the authoritative tutorial signature above. Any other out-of-range trial remains a hard failure.

This correction does not change the frozen protocol fingerprint, task cohort, AOI definition, task-trial preprocessing, pairing rule, validation model, Monte Carlo seed, classification rule, or any scientific outcome. It only prevents the explicitly non-task tutorial from entering the 1–144 task-trial guard.

No Korthals scientific endpoint had been executed or inspected when this boundary was implemented.
