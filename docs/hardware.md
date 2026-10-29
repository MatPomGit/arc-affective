# Sensor inventory and access gates (2026-10-29)

| Device | Candidate signals | Real-data permission/status | Primary use | Fallback |
|---|---|---|---|---|
| Tobii Eye Tracker 5 (consumer) | Interactive gaze/head-directed UI | **Do not record/derive gaze data for research under stock licence.** Tobii states it is incompatible with Tobii Pro SDK/Pro Lab and not licensed for Eye Tracking Data collection. | Gaming interaction demonstration only after EULA verification | Webcam-derived landmarks, public licensed gaze dataset |
| Muse S Athena | Four EEG channels at AF7, AF8, TP9, TP10 with FpZ reference; optical fNIRS/PPG and motion potentially available | **Blocked pending authorized research tool/license**. Consumer app does not expose raw research data. Do not assume fNIRS export is included. | EEG/optical signal research *only after gate* | Open licensed EEG datasets; non-EEG local sensor pilot |
| Leap Motion (revision unknown) | Hand pose/joints/kinematic trajectories, confidence and tracking status depending on SDK | Confirm exact hardware generation, compatible driver/Gemini/Orion release, SDK and rights in Windows; test local throughput | P05/P07 | Webcam hand landmarks or scripted simulator |
| RGB webcam | Face/head landmarks, frame timestamps, blink/motion proxies with validated software | Local software processing feasible; facial images are sensitive/identifiable personal data | P03/P04/P06 | Licensed public benchmark and synthetic events |

**Official references**
- Tobii consumer 5 limitations: https://gaming.tobii.com/product/eye-tracker-5/
- Tobii research SDK license caveat: https://developer.tobii.com/tobii-pro-sdk/
- Muse platform and access: https://musehealth.ai/pages/platform-data
- Muse Athena FAQ: https://musehealth.ai/pages/faq
- Ultraleap hand tracking docs: https://docs.ultraleap.com/hand-tracking/index.html
- Ultraleap Python bindings (device/version dependent): https://github.com/ultraleap/leapc-python-bindings

## Mandatory capability test per device

1. Record make/model/serial privately, firmware, OS, driver, API version and *license evidence*.
2. Verify legal research use and allowed storage/redistribution; reject adapters lacking that basis.
3. Measure timestamps, output units, usable channels/landmarks, sampling jitter, packet loss and calibration stability.
4. Perform synthetic/bench tests before human acquisition.
5. Mark as `confirmed`, `unsupported` or `blocked`; update paper's fallback without inventing measurements.

**Do not presume equivalence** of a four-electrode Muse montage and arbitrary four channels selected from 14-/32-channel EEG datasets. Channel coordinates, reference, acquisition characteristics and preprocessing must be reviewed.