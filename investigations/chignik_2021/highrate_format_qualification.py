#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import os
import pathlib
import re
import statistics
from collections import defaultdict

ROOT = pathlib.Path(os.environ.get("CHIGNIK_PROBE_ROOT", "artifacts/chignik_highrate_probe"))
EXTRACT = ROOT / "extracted"
OUTCSV = ROOT / "format_qualification.csv"
OUTJSON = ROOT / "format_qualification.json"
OUTMD = ROOT / "FORMAT_QUALIFICATION.md"

HEADER_RE = re.compile(r"^\s*(\d+)\s+(acceleration|velocity|displacement)\s+pts, approx\s+([0-9.]+)\s+secs, units=\s*([^,]+)", re.I)
ONSET_RE = re.compile(r"<EONSET>\s*event onset\(sec\)=\s*([0-9.+-]+)", re.I)
DECIMATE_RE = re.compile(r"<DECIMATE>\s*Data decimated to\s*([0-9.]+)\s*samples/sec", re.I)
RESAMPLE_RE = re.compile(r"<RESAMPLE>\s*Data resampled to\s*([0-9.]+)\s*samples/sec", re.I)
FILTER_RE = re.compile(r"Record filtered below\s+([0-9.]+)\s+Hz.*above\s+([0-9.]+)\s+Hz", re.I)
START_RE = re.compile(r"Rcrd start time:\s*([^\n]+?)\s+UTC", re.I)
STATION_RE = re.compile(r"Code:([A-Z0-9-]+)")
COORD_RE = re.compile(r"Coords:\s*([-0-9.]+)\s+([-0-9.]+)")
CHAN_RE = re.compile(r"\.([BHE][NZE12]{2}|[BH][NEZ])\.--\.(acc|vel|dis)\.V2c$", re.I)

def rms(xs):
    vals = [x for x in xs if math.isfinite(x)]
    return math.sqrt(sum(x*x for x in vals) / len(vals)) if vals else None

def read_v2c(path: pathlib.Path):
    lines = path.read_text(errors="replace").splitlines()
    onset = fs = fs_resampled = flo = fhi = lat = lon = None
    start = station = data_idx = quantity = units = None
    n_decl = dur_decl = None
    for i, line in enumerate(lines):
        m = ONSET_RE.search(line)
        if m: onset = float(m.group(1))
        m = DECIMATE_RE.search(line)
        if m: fs = float(m.group(1))
        m = RESAMPLE_RE.search(line)
        if m: fs_resampled = float(m.group(1))
        m = FILTER_RE.search(line)
        if m: flo, fhi = float(m.group(1)), float(m.group(2))
        m = START_RE.search(line)
        if m: start = m.group(1).strip()
        m = STATION_RE.search(line)
        if m: station = m.group(1).strip("-")
        m = COORD_RE.search(line)
        if m: lat, lon = float(m.group(1)), float(m.group(2))
        m = HEADER_RE.search(line)
        if m:
            n_decl = int(m.group(1))
            quantity = m.group(2).lower()
            dur_decl = float(m.group(3))
            units = m.group(4).strip()
            data_idx = i + 1
            break
    if data_idx is None:
        raise ValueError("data header not found")
    vals = []
    for line in lines[data_idx:]:
        s = line.strip()
        if not s:
            continue
        try:
            vals.append(float(s.split()[0]))
        except Exception:
            continue
    if fs is None and n_decl and dur_decl:
        fs = n_decl / dur_decl
    m = CHAN_RE.search(path.name)
    channel = m.group(1).upper() if m else None
    measure = m.group(2).lower() if m else None
    measure = {"acc": "acceleration", "vel": "velocity", "dis": "displacement"}.get(measure, measure)
    n = len(vals)
    duration = n / fs if fs and fs > 0 else None
    finite = [x for x in vals if math.isfinite(x)]
    vmin = min(finite) if finite else None
    vmax = max(finite) if finite else None
    peakabs = max(abs(vmin), abs(vmax)) if finite else None
    pre_rms = sig_rms = snr = None
    if onset is not None and fs and vals:
        oi = max(0, min(len(vals), int(round(onset * fs))))
        pre_rms = rms(vals[:oi])
        sig_rms = rms(vals[oi:])
        if pre_rms and pre_rms > 0 and sig_rms is not None:
            snr = sig_rms / pre_rms
    return {
        "archive": path.parts[-4] if len(path.parts) >= 4 else None,
        "station": station,
        "channel": channel,
        "measure": measure or quantity,
        "quantity_header": quantity,
        "units": units,
        "latitude": lat,
        "longitude": lon,
        "start_utc": start,
        "event_onset_s": onset,
        "sample_rate_hz": fs,
        "intermediate_resample_hz": fs_resampled,
        "filter_low_hz": flo,
        "filter_high_hz": fhi,
        "n_declared": n_decl,
        "n_parsed": n,
        "count_match": (n == n_decl) if n_decl is not None else None,
        "duration_declared_s": dur_decl,
        "duration_parsed_s": duration,
        "min": vmin,
        "max": vmax,
        "peak_abs": peakabs,
        "pre_event_rms": pre_rms,
        "post_onset_rms": sig_rms,
        "rms_snr": snr,
        "path": str(path),
    }

def main():
    files = sorted(EXTRACT.rglob("*.V2c"))
    rows, failures = [], []
    for p in files:
        try:
            rows.append(read_v2c(p))
        except Exception as e:
            failures.append({"path": str(p), "error": repr(e)})
    if not rows:
        raise SystemExit("No V2c files parsed")
    fields = list(rows[0].keys())
    with OUTCSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    stations = sorted({r["station"] for r in rows if r["station"]})
    measures = sorted({r["measure"] for r in rows if r["measure"]})
    channels = sorted({r["channel"] for r in rows if r["channel"]})
    rates = sorted({r["sample_rate_hz"] for r in rows if r["sample_rate_hz"]})
    by_station = defaultdict(list)
    for r in rows:
        by_station[r["station"]].append(r)
    snrs = [r["rms_snr"] for r in rows if r["rms_snr"] is not None]
    summary = {
        "purpose": "format/measurement qualification only; no poles or chi",
        "parsed_files": len(rows),
        "failures": failures,
        "stations": stations,
        "measures": measures,
        "channels": channels,
        "sample_rates_hz": rates,
        "filter_bands_hz": sorted({(r["filter_low_hz"], r["filter_high_hz"]) for r in rows}),
        "all_counts_match": all(r["count_match"] for r in rows),
        "station_file_counts": {k: len(v) for k, v in sorted(by_station.items())},
        "snr_summary": {"median": statistics.median(snrs), "min": min(snrs), "max": max(snrs)},
    }
    OUTJSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))
    lines = [
        "# Chignik high-rate format and measurement qualification",
        "",
        "- Purpose: **format/measurement qualification only; no pole or χ estimation**",
        f"- Parsed V2c files: **{len(rows)}**",
        f"- Stations: **{', '.join(stations)}**",
        f"- Measures: **{', '.join(measures)}**",
        f"- Channels: **{', '.join(channels)}**",
        f"- Sample rates: **{', '.join(str(x) for x in rates)} Hz**",
        f"- Declared/parsed sample counts all match: **{summary['all_counts_match']}**",
        f"- RMS signal/pre-event-noise SNR median: **{summary['snr_summary']['median']:.2f}** (range {summary['snr_summary']['min']:.2f}-{summary['snr_summary']['max']:.2f})",
        "",
        "## Station coverage",
    ]
    for k, v in sorted(by_station.items()):
        combos = sorted({f"{r['channel']}:{r['measure']}" for r in v})
        lines.append(f"- {k}: {len(v)} files; {', '.join(combos)}")
    if failures:
        lines += ["", "## Parse failures"] + [f"- {x['path']}: {x['error']}" for x in failures]
    OUTMD.write_text("\n".join(lines) + "\n")
    print(OUTMD.read_text())

if __name__ == "__main__":
    main()
