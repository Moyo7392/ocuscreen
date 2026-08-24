# OcuScreen Experiment Lab Notebook

## Experiment 1
- Script: experiment_1.py
- Changes: Evaluated EfficientNet-B0 and EfficientNet-B3 checkpoints independently and as probability ensembles over a 0.00–1.00 B0-weight grid, using the required stratified `random_state=42` validation split.
- Hypothesis: The checkpoints' different architectures and preprocessing pipelines make complementary errors, so probability averaging may improve accuracy.
- Result: accuracy=92.2%, QWK=0.9534 (best blend B0=0.95, B3=0.05; B0 alone tied at 92.2% after rounding)
- Analysis: The numerical target was reached. Per-class accuracy was grade0=98.3%, grade1=87.8%, grade2=87.0%, grade3=79.5%, grade4=86.4%. Critical validity caveat: B0 was originally trained with a seed-4316 split, so some seed-42 validation images were likely in its training partition. Therefore 92.2% is the requested fixed-split result but not a leakage-free estimate. The B3 checkpoint, which was trained on the seed-42 partition, scored 79.8% / QWK 0.8906. A future publication-grade benchmark should retrain B0 on the seed-42 training partition or use an untouched external test set.

## Web App Update 1
- Feature: Retinal Health Intelligence dashboard with an explicit scan-to-referral decision pathway, confidence interpretation, risk-based follow-up window, hotspot counts by retinal quadrant, and APTOS class-distribution context.
- Why: Converts existing model output into structured clinical context while carefully distinguishing model attention from confirmed lesions and dataset composition from population prevalence.
- Files changed: `app/src/components/RetinalIntelligence.tsx`, `app/src/components/ResultView.tsx`

## Experiment 2
- Script: experiment_2.py
- Changes: Leakage-free ImageNet initialization on the seed-42 training partition; EfficientNet-B3 at 384px; circle crop and Ben Graham enhancement; ordinal-aware CE plus expected-grade loss; square-root minority sampling and mild class weighting.
- Hypothesis: Higher resolution and fundus-specific contrast would preserve subtle lesions, while ordinal supervision and moderate balancing would improve adjacent-grade discrimination.
- Result: accuracy=79.8%, QWK=0.8756
- Analysis: The experiment did not improve exact accuracy and reduced QWK versus v2 (0.8906). Grade 0 remained strong (95.8%), but grade 2 reached only 68.0%, grade 3 35.9%, and grade 4 54.2%. Sampling, class-weighted loss, and the ordinal auxiliary term likely over-corrected imbalance while Ben Graham processing may have suppressed useful color cues. Next: measure whether its distinct preprocessing contributes complementary ensemble signal before committing to another full training run.

## Experiment 3
- Script: experiment_3.py
- Changes: Leakage-free probability ensemble of model_v2_best and experiment_2_best, with a fixed grid over blend weights and softmax temperatures. Both members were trained only on the seed-42 training partition.
- Hypothesis: Different resolution and preprocessing pipelines would produce complementary errors and improve exact-grade accuracy without another training run.
- Result: accuracy=80.9%, QWK=0.8771
- Analysis: The ensemble added 1.1 percentage points over either individual model, confirming some complementary signal, but remains 9.1 points below target. Best settings were v2=0.40, experiment_2=0.60 with temperatures 0.75/1.25. Grade 3 (38.5%) and grade 4 (55.9%) remain the main bottlenecks. Because blend settings were selected on the validation set itself, 80.9% should be confirmed on an untouched test set before publication.
