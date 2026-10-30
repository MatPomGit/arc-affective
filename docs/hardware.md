# Sensor inventory and access gates (2026-10-30)

| Device | Candidate signals | Real-data permission/status | Primary use | Fallback |
|---|---|---|---|---|
| Tobii Eye Tracker 5 (consumer; under-monitor installation photographed, model consistent with inventory) | Near-infrared 850 nm eye/head tracking, interactive gaze/head-directed UI | **Stock licence permits interaction, not research logging or processing of eye-tracking data.** No research gaze recording, deriving, aggregation or transmission without explicit separate licence. | Interactive gaming demo only; optical research stream **blocked** | Webcam-derived landmarks, licensed public gaze dataset |
| Muse S Athena | Four EEG channels at AF7, AF8, TP9, TP10 with FpZ reference; optical fNIRS/PPG and motion potentially available | **Blocked pending authorized research tool/license**. Consumer app does not expose raw research data. Do not assume fNIRS export is included. | EEG/optical signal research *only after gate* | Open licensed EEG datasets; non-EEG local sensor pilot |
| Ultraleap Leap Motion Controller 2 (Leap 2; identified from device and retail packaging photos, 2026-10-30) | Stereo-IR hand and finger pose, joint trajectories, tracking status/quality as exposed by the verified SDK | **Hardware model confirmed; runtime/research-data use not yet validated.** Verify Hyperion/LeapC release, OS, firmware, actual access and licence locally; benchmark the device before capture | P05/P07; optional P06/P08 | Webcam hand landmarks or scripted simulator |
| RGB webcam | Face/head landmarks, frame timestamps, blink/motion proxies with validated software | Local software processing feasible; facial images are sensitive/identifiable personal data | P03/P04/P06 | Licensed public benchmark and synthetic events |
| Slayo Mike S9 (2 wireless lavalier transmitters + 1 USB-C receiver; identified from packaging, 2026-10-30) | Two physical microphone locations; sound events, intensity/spectral/temporal features **only if receiver capture verified** | **Acquisition topology and left/right channel isolation unverified.** If receiver produces mono mix, do not claim stereo, sound-source direction or time-difference-of-arrival estimation; confirm consent for speech recording. | Optional P03/P06/P08 engineering pilot; optional P02 fusion methodology | Local mono environmental audio features or a verified independent-channel recorder |

## Tobii Eye Tracker 5: geometry, rate and licence gate

**Identification basis (2026-10-30):** the new photograph shows a Tobii-branded infrared tracking bar below the monitor, consistent with the Tobii Eye Tracker 5 already recorded in the inventory. The brand and placement are visible; the exact hardware revision is **not independently proved by this photo alone**. Confirm PID/model on the host before treating it as a physical-device test.

| Parameter | Tobii manufacturer information |
|---|---|
| Model | Tobii Eye Tracker 5 (consumer gaming/interaction device) |
| Optical principle | Tobii IS5 custom near-infrared camera and illuminator, 850 nm; simultaneous head and gaze interaction |
| Camera/image sampling | 133 Hz camera sampling; manufacturer comparison lists non-interlaced gaze updates at **33 Hz**, so do not report 133 Hz as the gaze-data output rate |
| Field of view | 40° × 40° |
| Recommended operating distance | 45–95 cm |
| Supported display region | 15–27-inch 16:9 or up to 30-inch 21:9 for gaze interaction; head-tracking use has different screen limits |
| Dimensions | 285 × 15 × 8.2 mm |
| Connection | USB 2.0 integrated cable (0.8 m), extension (1 m) provided with product |
| Operating system | Windows 10 64-bit RS3 or later; verify exact driver/OS release on host |
| Mount | Beneath monitor, using a compatible magnetic/flex mount; screen dimensions, angle and working distance must be checked |

**Rights gate: hard block.** Tobii's Eye Tracker 5 product page says that the product is not compatible with Tobii Pro SDK/Pro Lab and is **not licensed to collect Eye Tracking Data**. Its consumer licence explicitly excludes storing/transferring eye, head, face and similar derived tracking data for analytical use. Participant consent or self-participation does not override this licence. With the standard licence, only authorised interactive use is in scope; a research acquisition adapter for Tobii 5 remains **disabled**. Use a specially licensed Tobii setup or openly licensed research datasets for gaze analysis. The 133 Hz value is not a measured sample rate on this workstation.

References:
- [Tobii Eye Tracker 5: specifications and licensing FAQ](https://gaming.tobii.com/product/eye-tracker-5/)
- [Tobii Help Center: Eye Tracker 4C vs 5, sampling specification](https://help.tobii.com/hc/en-us/articles/360008539058-What-s-the-difference-between-Tobii-Eye-Tracker-4C-and-5)
- [Tobii Gaming End-User License](https://gaming.tobii.com/tobii-eye-tracking-end-user-license-use-agreement/)

## Slayo Mike S9: two microphone positions are not automatically stereo

**Identification basis (2026-10-30):** the supplied product box and rear sticker identify Slayo Mike S9, a kit of **two wireless clip-on transmitters and one receiver**. The checkboxes indicate the black Mike S9 and USB-C variant. These images do not demonstrate independent audio channels, microphone frequency response, sample rate, codec or actual host connectivity.

| Parameter | Slayo product information / status |
|---|---|
| Manufacturer and model | Slayo Mike S9, 2 × clip-on wireless microphone transmitters, 1 × shared receiver |
| RF link | Proprietary 2.4 GHz; **not Bluetooth** |
| Host audio interface | Receiver with USB-C connector; Lightning adapter described for the kit; compatibility requires a host capture test |
| Microphone pickup | Omnidirectional (360°), not a directional or binaural array |
| Radio range | Product box says **20 m**; current Slayo listing states **up to 30 m open-space, up to 15 m indoors**. Treat these conflicting advertising figures as unverified, not measured effective range |
| Endurance / charge | Up to 6 h per transmitter; approximately 1.5 h charge time |
| Battery | 65 mAh per transmitter |
| Size / mass | Microphone approximately 65 × 15 mm, manufacturer-listed 25 g; receiver approximately 44 × 15 mm |
| Processing | Vendor advertises electronic noise reduction; the actual DSP, AGC and compression behaviour must be characterised |
| Audio format / true channels | **Unknown**: no verified PCM sample rate, bit depth, latency or documented two-channel separation; USB-C port alone does not imply stereo |
| Status | **Model verified visually; two TX claimed by owner; real capture and independent left/right tracks NOT TESTED** |

**Two-microphone, left/right station pilot (strict gate):**

1. Label the physical units **A (left)** and **B (right)** in the *private* experiment log. Place them on fixed supports around the participant, not on two different people's clothing, if the goal is environmental left/right analysis. Record positions in metres, orientation, distance from user and the receiver/host configuration.
2. Verify whether the USB-C receiver is chosen as the *actual* recording source. Capture a 10-second ambient baseline; measure reported channel count, sample rate, sample format, gain controls and dropouts from the PCM stream. Never infer these from package graphics.
3. Record four bench conditions with **no human voices**: both microphones muted/off, A-only, B-only, and A+B. Generate a local brief test sound first near A and then B. Inspect per-channel RMS, cross-channel correlation and spectrograms. A two-channel WAV file may still contain a duplicated mono mix: **two tracks do not prove separability**.
4. If **two independently acquired, consistently mapped L/R signals** really exist, test fixed-position sound sources, calibrated gains, processing/AGC stability, channel alignment and drift under repeated sessions. Consider a *coarse* left/right classification only after held-out validation; inter-microphone time-difference-of-arrival or source localisation additionally requires proven sample-level interchannel timing unaffected by wireless/DSP delay. Mike S9 is not presented as binaural, ambisonic or calibrated 3D audio hardware.
5. If the receiver **sums both transmitters to mono**, use only mono environmental event, level and spectral features, or replace it with an explicitly independent dual-channel audio interface/microphone pair for spatial experiments. Never claim two source-localisable recordings from a mixed stream.
6. For multimodal sync, estimate audio-to-video/Leap marker offset and drift, trigger latency p50/p95/p99 and wireless dropouts. Store timestamps and device/driver/PCM settings in the private manifest. Document rights/consent for any speech or identifiable audio; avoid uploading raw recordings to Git.

Candidate metrics after actual capture: log-mel energy, RMS, spectral centroid, speech-activity fraction where ethically appropriate, transient events, dropout and latency. They are **acoustic proxies**, not validated affect/emotion or cognitive workload measurements. Pre-registration, within-session holdouts and multimodal ablations remain required.

Reference: [Slayo Mike S9 official product description and specification](https://slayo.pl/mikrofony-krawatowe/zestaw-2x-mikrofon-bezprzewodowy-krawatowy-do-telefonu-usb-c-lightning-slayo-mik).

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
- Slayo Mike S9 manufacturer specification: https://slayo.pl/mikrofony-krawatowe/zestaw-2x-mikrofon-bezprzewodowy-krawatowy-do-telefonu-usb-c-lightning-slayo-mik
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