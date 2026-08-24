# OcuScreen model card

## Intended use

OcuScreen is an academic diabetic-retinopathy screening and triage prototype. It accepts a retinal fundus image and returns a five-class severity estimate, confidence values, an attention visualization, and general referral guidance.

It is not a diagnostic device, is not FDA cleared, and must not be used to make treatment decisions. A licensed clinician must review the original image and patient context.

## Data

Training experiments use the APTOS 2019 Blindness Detection dataset. Dataset images and trained weights are deliberately excluded from Git. Users must obtain the dataset under its original terms.

## Model

- EfficientNet-B0 backbone
- Five ordinal classes: no DR, mild, moderate, severe, proliferative DR
- Grad-CAM visualization for model-attention inspection
- Image-quality gate before inference

## Evaluation

The strongest leakage-free experiment recorded 80.9% accuracy and quadratic weighted kappa of 0.8771 on the project test split. These are academic experiment results, not external clinical validation.

An earlier experiment recorded 92.2% accuracy and 0.9534 QWK, but its split allowed same-patient left/right images to cross partitions. That result is retained in the experiment log for transparency and must not be presented as the model's validated performance.

The selected ensemble also used validation performance to choose components, so its test result may be mildly optimistic. See `training/experiment_log.md` for the complete experiment history and caveats.

## Known limitations

- No prospective or multi-site clinical validation
- Dataset shift across cameras, populations, and care settings
- Class imbalance, especially for severe disease
- Grad-CAM indicates model attention, not causal evidence or a lesion diagnosis
- Confidence scores are not guaranteed to be calibrated
- Quality checks cannot detect every unsuitable image
- No patient identity, laterality, medical-history, or clinician-workflow integration

## Privacy

The application requests no patient identifiers. Browser demo history remains in local storage. Operators are responsible for deployment security, retention controls, consent, and applicable health-data requirements.
