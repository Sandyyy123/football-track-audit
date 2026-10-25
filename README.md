> **Proprietary - All Rights Reserved.** Licensed to Sandeep Grover. No reuse, copying, modification, or distribution without prior written permission. See LICENSE.

# Football track audit

A small measurement-validity component using constructed pitch coordinates. It is not a football detector, calibration algorithm, trained model or real-match accuracy benchmark.

Run `python3 -m unittest -v` (12 tests), then `python3 track_audit.py --output example.json`. `--dry-run` prints without writing. Standard library only.

The fixture contains 12 observations. Five accepted adjacent intervals total2.5metres over0.5seconds; coverage is one third of the1.5second span. Identity switches, camera cuts, missing play and unverified calibration are not bridged. No whole-match distance is estimated.

Positions must already be in a common calibrated pitch frame in metres. Confidence,12m/s speed and0.2s gap thresholds here are illustrative review rules. They do not establish measurement accuracy or universal physiology. The example retains all rejected observations and explains each excluded interval.

Real implementation needs permitted footage, reviewed player identities/footpoints, calibration appropriate to camera motion, match-level holdouts, uncertainty assessment, reference measurements where available and deployment benchmarks. Metrics such as sprints also need a validated duration/event definition.

All data are synthetic. Copyright Sandeep Grover2026; proprietary license in LICENSE.
