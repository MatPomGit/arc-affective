# Sensor inventory and access gates (2026-10-30)

| Device | Candidate signals | Real-data permission/status | Primary use | Fallback |
|---|---|---|---|---|
| Tobii Eye Tracker 5 (consumer) | Interactive gaze/head-directed UI | **Do not record/derive gaze data for research under stock licence.** Tobii states it is incompatible with Tobii Pro SDK/Pro Lab and not licensed for Eye Tracking Data collection. | Gaming interaction demonstration only after EULA verification | Webcam-derived landmarks, public licensed gaze dataset |
| Muse S Athena | Four EEG channels at AF7, AF8, TP9, TP10 with FpZ reference; optical fNIRS/PPG and motion potentially available | **Blocked pending authorized research tool/license**. Consumer app does not expose raw research data. Do not assume fNIRS export is included. | EEG/optical signal research *only after gate* | Open licensed EEG datasets; non-EEG local sensor pilot |
| Ultraleap Leap Motion Controller 2 (Leap 2; identified from device and retail packaging photos, 2026-10-30) | Stereo-IR hand and finger pose, joint trajectories, tracking status/quality as exposed by the verified SDK | **Hardware model confirmed; runtime/research-data use not yet validated.** Verify Hyperion/LeapC release, OS, firmware, actual access and licence locally; benchmark the device before capture | P05/P07; optional P06/P08 | Webcam hand landmarks or scripted simulator |
| RGB webcam | Face/head landmarks, frame timestamps, blink/motion proxies with validated software | Local software processing feasible; facial images are sensitive/identifiable personal data | P03/P04/P06 | Licensed public benchmark and synthetic events |

## Ultraleap Leap Motion Controller 2: verified hardware specification

**Identification evidence (2026-10-30):** the supplied photographs show the original `Leap 2 Motion Controller` product packaging and the matching USB-C stereo-IR camera. This identifies the product generation, **not** the device's serial number, firmware revision, operational state or data-access permissions. The university inventory number is deliberately not stored in this public repository.

| Parameter | Manufacturer specification |
|---|---|
| Manufacturer / model | Ultraleap / Leap Motion Controller 2 (LMC2; second generation, not the original Leap Motion Controller or Stereo IR 170) |
| Sensing principle | Stereo infrared cameras with active IR illumination; optical markerless hand/finger tracking |
| Sensor | OmniVision OG01A1B; UVC 1.1 compliant, subject to actual host/firmware configuration |
| Tracking depth | 10–110 cm, measured under controlled conditions |
| Maximum field of view | 160° × 160°, measured under controlled conditions |
| Camera imaging modes | 1024 × 1024 at 88 fps or 512 × 512 at 120 fps (2 × 2 pixel binning), USB 3 |
| Camera frame rate | Up to 120 fps; **not a guaranteed hand-pose output frequency** |
| IR wavelength | 850 nm |
| Connection | USB 3.0 via USB-C connector; use a USB 3-rated cable and host port |
| Power | 5 V DC, 500 mA over USB |
| Size / weight | 84 × 20 × 12 mm / 29 g |
| Materials | Aluminium and scratch-resistant glass |
| Operating / storage temperature | 0–40 °C / −30 to 60 °C |
| Vendor-listed host platforms | Windows 10+ (64-bit), macOS 11+ and supported Android XR2 headsets; check current release requirements. **Linux is not assumed supported.** |
| Tracking software | Ultraleap Hyperion Tracking Service and LeapC C-style Tracking SDK; official Unity/Unreal integrations |
| Model output | With Hyperion, the vendor describes 27 hand elements/joints; assess the actual schema, confidence/status fields and missing-data semantics at runtime |
| Licence | Hyperion commercial-use terms are described by the vendor, but institutional **research acquisition, permitted storage, redistribution and any raw-camera access must still be verified against the applicable licence** |

Camera fps, maximum FOV and detection depth are *datasheet limits*, not measured performance of the university-owned unit. Track losses due to self-occlusion, ambient IR, reflections, hand orientation and distance in the experimental protocol. Do not equate kinematic gestures or hand tremor directly with affect, cognitive state or clinical status.

### Acquisition/readiness gate for P05, P07 and optional P06/P08

1. On an authorised host, confirm USB 3 link and read actual model/PID (`eLeapDevicePID_LMC2`), firmware, Tracking Service and LeapC versions. Keep serial, computer identifiers and inventory records **private**.
2. Review the exact Hyperion licence and privacy/ethics basis for recording kinematic trajectories; do not start human-data acquisition before approval.
3. Run an offline smoke test: detect one/two hands, enumerate joints, document the coordinate frame, units, handedness, vendor timestamps, quality/visibility flags, reconnect behaviour and dropped frames.
4. Benchmark *measured* hand-pose event rate, latency p50/p95/p99, jitter and missingness at multiple distances/poses/light levels; compare camera mode and pose-stream fps separately.
5. Record SDK versions and results in a private session manifest. Until these checks pass, keep the device status **model-confirmed / integration-unverified** and use the mock/webcam fallback.

**Manufacturer documentation and datasheet**

- [Leap Motion Controller 2, issue 15 technical datasheet (Ultraleap; distributor-hosted PDF)](https://www.mouser.lt/datasheet/2/1031/Ultraleap_UL_006511_SP_17_Leap_Motion_Controller_2-3453135.pdf)
- [Ultraleap Hyperion: tracking service, LeapC and plugin overview](https://docs.ultraleap.com/hand-tracking/Hyperion/index.html)
- [Leap Motion Controller 2 desktop setup](https://docs.ultraleap.com/hand-tracking/desktop-setup.html)
- [LeapC device PID enumeration](https://docs.ultraleap.com/api-reference/tracking-api/group/group___enum.html)

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