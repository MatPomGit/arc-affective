# Ethics, privacy and scientific integrity

- Data minimisation: store engineered features and non-identifying experiment events when sufficient; raw video, audio, EEG and other biometric signals default to **off**. No covert participant monitoring.
- Local data stay in ignored `data/`, encrypted/controlled as required by institutional policy. No identifiable information, sample face video, participant names, ID numbers or vendor SDK binaries in the public repository, issues or CI logs.
- Separate study information/consent from records, use pseudonymous study IDs, record retention/deletion schedule and access log. Obtain institutional ethics/DPO assessment before any prospective human study, including N=1 or colleague experiments.
- Explain the limited inferential validity of physiological correlates and facial expressions; avoid clinical/diagnostic labels, employee surveillance and categorical emotion attribution from a webcam.
- Honour third-party data-use agreements and model/software terms; do not redistribute datasets without permission.
- Robotics: estimator output never overrides collision protection or emergency stop; use simulated safety supervisor, bounded speed/acceleration, watchdog, operator override and defined loss-of-tracking behavior. Never test safety by commanding hazardous physical motion.
- Maintain no-cost stack: local Python, offline tests, existing equipment and free-permitted software; verify actual device permissions before accessing a stream.
- A manuscript's results must be supported by archived protocol, deterministic scripts and a documented negative-result policy; do not use the same dataset partition as a hidden test across iterations.