#!/usr/bin/env python3
"""
Known-truth synthetic fixtures for Chignik/high-rate stability-engine qualification.

This script does NOT fit Chignik data and does NOT define acceptance thresholds.
It creates a frozen library of deliberately diverse cases that a future engine
must classify, estimate, or refuse without outcome-dependent tuning.
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import random

ROOT = pathlib.Path("artifacts/chignik_highrate_probe/synthetic_fixtures")
ROOT.mkdir(parents=True, exist_ok=True)

FS = 100.0
DURATION = 120.0
N = int(FS * DURATION)
T = [i / FS for i in range(N)]
RNG = random.Random(20260927)

def gaussian_noise(scale: float):
    return [RNG.gauss(0.0, scale) for _ in range(N)]

def add(*signals):
    return [sum(xs) for xs in zip(*signals)]

def scale_signal(x, a):
    return [a*v for v in x]

def shift_signal(x, seconds):
    k = int(round(seconds * FS))
    if k <= 0:
        return x[-k:] + [0.0]*(-k) if k < 0 else list(x)
    return [0.0]*k + x[:-k]

def damped(zeta, f0, amp=1.0, phase=0.0):
    wn = 2*math.pi*f0
    if zeta < 1.0:
        wd = wn*math.sqrt(1-zeta*zeta)
        return [amp*math.exp(-zeta*wn*t)*math.sin(wd*t+phase) for t in T]
    if abs(zeta-1.0) < 1e-12:
        return [amp*(1+wn*t)*math.exp(-wn*t) for t in T]
    s = math.sqrt(zeta*zeta-1.0)
    r1 = -wn*(zeta-s)
    r2 = -wn*(zeta+s)
    return [amp*(math.exp(r1*t)-math.exp(r2*t)) for t in T]

def exp_relax(tau, amp=1.0):
    return [amp*math.exp(-t/tau) for t in T]

def chirp(f_start=0.5, f_end=5.0, amp=1.0, decay=0.01):
    k = (f_end-f_start)/DURATION
    out=[]
    for t in T:
        phase = 2*math.pi*(f_start*t + 0.5*k*t*t)
        out.append(amp*math.exp(-decay*t)*math.sin(phase))
    return out

def noise(scale):
    return gaussian_noise(scale)

cases = []

def add_case(case_id, expected_class, notes, station_signals, truth=None):
    case_dir = ROOT / case_id
    case_dir.mkdir(exist_ok=True)
    truth = truth or {}
    records = []
    for station, components in station_signals.items():
        for component, values in components.items():
            path = case_dir / f"{station}_{component}.csv"
            with path.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["time_s","value"])
                w.writerows(zip(T, values))
            records.append({"station":station,"component":component,"path":str(path)})
    cases.append({
        "case_id":case_id,
        "expected_class":expected_class,
        "notes":notes,
        "sample_rate_hz":FS,
        "duration_s":DURATION,
        "truth":truth,
        "records":records,
    })

# 1. Clean single underdamped mode.
base = damped(0.12, 1.8)
add_case(
    "F01_clean_underdamped",
    "ADMIT_SINGLE_UNDERDAMPED_FACTOR",
    "Clean second-order underdamped factor; estimator should recover a stable complex pair.",
    {"S1":{"E":add(base,noise(0.01))}},
    {"zeta":0.12,"f0_hz":1.8},
)

# 2. Higher but still underdamped damping.
base = damped(0.55, 1.1)
add_case(
    "F02_high_damping_underdamped",
    "ADMIT_SINGLE_UNDERDAMPED_FACTOR",
    "Underdamped but rapidly decaying factor.",
    {"S1":{"E":add(base,noise(0.01))}},
    {"zeta":0.55,"f0_hz":1.1},
)

# 3. Critical damping.
add_case(
    "F03_critical",
    "REFUSE_OSCILLATORY_SCALAR",
    "Critically damped response has no oscillatory complex-pair interpretation.",
    {"S1":{"E":add(damped(1.0,1.5),noise(0.01))}},
    {"zeta":1.0,"f0_hz":1.5},
)

# 4. Overdamped.
add_case(
    "F04_overdamped",
    "REFUSE_OSCILLATORY_SCALAR",
    "Overdamped response is nonoscillatory and must not be forced into an oscillatory chi.",
    {"S1":{"E":add(damped(1.4,1.5),noise(0.01))}},
    {"zeta":1.4,"f0_hz":1.5},
)

# 5. Pure monotonic relaxation.
add_case(
    "F05_monotonic_relaxation",
    "REFUSE_OSCILLATORY_SCALAR",
    "Single exponential relaxation with no native oscillation.",
    {"S1":{"E":add(exp_relax(12.0),noise(0.01))}},
    {"tau_s":12.0},
)

# 6. Two resolvable modes.
m1 = damped(0.08,0.8,1.0)
m2 = damped(0.18,2.7,0.65,0.4)
add_case(
    "F06_two_mode",
    "MULTIMODAL",
    "Two distinct damped factors; one-scalar reduction should be refused.",
    {"S1":{"E":add(m1,m2,noise(0.015))}},
    {"modes":[{"zeta":0.08,"f0_hz":0.8},{"zeta":0.18,"f0_hz":2.7}]},
)

# 7. Closely spaced modes.
m1 = damped(0.10,1.8,1.0)
m2 = damped(0.13,2.05,0.8,0.3)
add_case(
    "F07_close_modes",
    "MULTIMODAL_OR_UNRESOLVED",
    "Closely spaced factors challenge modal identifiability.",
    {"S1":{"E":add(m1,m2,noise(0.02))}},
    {"modes":[{"zeta":0.10,"f0_hz":1.8},{"zeta":0.13,"f0_hz":2.05}]},
)

# 8. Chirp/nonstationary oscillation.
add_case(
    "F08_chirp",
    "REFUSE_STATIONARY_POLE_MODEL",
    "Frequency evolves continuously, so a stationary damped-pole model is misspecified.",
    {"S1":{"E":add(chirp(),noise(0.02))}},
    {"f_start_hz":0.5,"f_end_hz":5.0},
)

# 9. Low-SNR underdamped factor.
base = damped(0.20,1.6,0.25)
add_case(
    "F09_low_snr",
    "LOW_SNR_OR_INDETERMINATE",
    "A true factor exists but observation noise should make admission conditional on uncertainty.",
    {"S1":{"E":add(base,noise(0.20))}},
    {"zeta":0.20,"f0_hz":1.6},
)

# 10. Site-local mode: only S1 has it.
local = damped(0.10,3.2)
station_signals = {
    "S1":{"E":add(local,noise(0.03))},
    "S2":{"E":noise(0.03)},
    "S3":{"E":noise(0.03)},
}
add_case(
    "F10_site_local",
    "SITE_LOCAL_ONLY",
    "A strong factor confined to one station must not be labeled system-wide.",
    station_signals,
    {"local_station":"S1","zeta":0.10,"f0_hz":3.2},
)

# 11. Shared mode with realistic gain and arrival shifts.
shared = damped(0.16,1.35)
station_signals = {
    "S1":{"E":add(scale_signal(shift_signal(shared,0.0),1.0),noise(0.03))},
    "S2":{"E":add(scale_signal(shift_signal(shared,0.7),0.65),noise(0.03))},
    "S3":{"E":add(scale_signal(shift_signal(shared,1.4),1.35),noise(0.03))},
}
add_case(
    "F11_cross_station_shared",
    "ADMIT_SHARED_FACTOR",
    "Same factor appears with station-dependent delay and amplitude.",
    station_signals,
    {"zeta":0.16,"f0_hz":1.35,"relative_delays_s":[0.0,0.7,1.4]},
)

# 12. Three-component mixed case: one physical shared factor + local component contamination.
shared = damped(0.14,1.05)
local = damped(0.06,4.5,0.4)
station_signals = {}
for i, station in enumerate(["S1","S2","S3"]):
    delay = 0.4*i
    station_signals[station] = {
        "E": add(scale_signal(shift_signal(shared,delay),1.0-0.15*i),noise(0.03)),
        "N": add(scale_signal(shift_signal(shared,delay),0.8+0.1*i),noise(0.03)),
        "U": add(scale_signal(shift_signal(shared,delay),0.35), local if station=="S1" else [0.0]*N, noise(0.05)),
    }
add_case(
    "F12_multicomponent_mixed",
    "SHARED_PLUS_LOCAL_CONTAMINATION",
    "Shared horizontal factor plus station/component-local higher-frequency contamination.",
    station_signals,
    {"shared":{"zeta":0.14,"f0_hz":1.05},"local":{"station":"S1","component":"U","zeta":0.06,"f0_hz":4.5}},
)

manifest = {
    "purpose":"known-truth qualification fixtures only; no Chignik outcome inspection",
    "random_seed":20260927,
    "sample_rate_hz":FS,
    "duration_s":DURATION,
    "cases":cases,
}
(ROOT/"fixture_manifest.json").write_text(json.dumps(manifest,indent=2))

lines = [
    "# High-rate stability-engine synthetic fixtures",
    "",
    f"- Cases: **{len(cases)}**",
    f"- Fixed random seed: **{manifest['random_seed']}**",
    f"- Sample rate: **{FS} Hz**",
    f"- Duration: **{DURATION} s**",
    "",
    "These fixtures are generated before Chignik pole estimation and do not define pass/fail thresholds.",
    "They provide known-truth admission, refusal, multimode, identifiability, SNR, site-local, and cross-station cases.",
    "",
]
for c in cases:
    lines.append(f"- **{c['case_id']}**: {c['expected_class']} — {c['notes']}")
(ROOT/"README.md").write_text("\n".join(lines)+"\n")
print((ROOT/"README.md").read_text())
