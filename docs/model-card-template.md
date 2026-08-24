# OcuScreen model card template

This template defines the minimum evidence required before publishing performance claims for an OcuScreen checkpoint. Blank fields are intentional; they must be populated from a reproducible evaluation run rather than estimates.

## Model identity

- Model version:
- Checkpoint checksum:
- Architecture:
- Training configuration commit:
- Evaluation date:

## Intended use

- Intended users:
- Supported input conditions:
- Explicitly unsupported uses:
- Human-review requirements:

## Dataset provenance

- Dataset and license:
- Split methodology:
- Number of images by class:
- Leakage and duplicate checks:
- Preprocessing and augmentation:

## Held-out results

- Quadratic-weighted kappa:
- Macro F1:
- Per-class precision and recall:
- Calibration metric:
- Image-quality rejection rate:
- Confidence interval or repeated-run variance:

Attach the confusion matrix and the exact evaluation command/output. Do not report a target value as an achieved result.

## Limitations and risk

- Known failure modes:
- Performance across demographic or acquisition subgroups:
- Out-of-distribution behavior:
- Escalation behavior for low-confidence results:
- Clinical validation status:

OcuScreen remains a decision-support demonstration and not a diagnostic device, regardless of benchmark performance.
