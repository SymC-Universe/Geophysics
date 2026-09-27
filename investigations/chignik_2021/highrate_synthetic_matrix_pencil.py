from __future__ import annotations
import csv, json, math, pathlib

import numpy as np
from scipy import linalg

ROOT = pathlib.Path("artifacts/chignik_highrate_probe/synthetic_fixtures")
MANIFEST = ROOT / "fixture_manifest.json"
OUT = ROOT / "matrix_pencil_known_truth.csv"
REPORT = ROOT / "MATRIX_PENCIL_KNOWN_TRUTH.md"

WINDOWS = [0.75, 1.0, 1.5, 2.0, 4.0]
ORDERS = [2, 4, 6]

def read_signal(path):
    t=[]; y=[]
    with open(path,newline="") as f:
        r=csv.DictReader(f)
        for row in r:
            t.append(float(row["time_s"]))
            y.append(float(row["value"]))
    return np.asarray(t), np.asarray(y)

def pencil_poles(path, fs, window_s, order):
    t,y = read_signal(path)
    n = min(len(y), int(round(window_s*fs))+1)
    y = y[:n].astype(float)
    if len(y) < max(20, 4*order):
        return []
    y = y - np.mean(y)
    # Fixed pencil geometry, independent of outcome.
    L = max(order+2, min(len(y)//3, len(y)-order-2))
    K = len(y)-L
    if K <= order+1:
        return []
    Y0 = np.column_stack([y[i:i+L] for i in range(K)])
    Y1 = np.column_stack([y[i+1:i+L+1] for i in range(K)])
    U,S,Vh = linalg.svd(Y0, full_matrices=False, check_finite=True)
    r = min(order, len(S))
    if r < 1:
        return []
    Ur = U[:,:r]
    Vr = Vh.conj().T[:,:r]
    Sr = S[:r]
    if np.any(Sr <= np.finfo(float).eps):
        return []
    A = Ur.conj().T @ Y1 @ Vr @ np.diag(1.0/Sr)
    z = linalg.eigvals(A)
    out=[]
    for zz in z:
        if not np.isfinite(zz.real) or not np.isfinite(zz.imag):
            continue
        if abs(zz) <= 0:
            continue
        ss = np.log(zz) * fs
        alpha = -ss.real
        wd = abs(ss.imag)
        wn = math.sqrt(alpha*alpha + wd*wd)
        if wn == 0:
            continue
        f0 = wn/(2*math.pi)
        zeta = alpha/wn
        out.append({
            "z_real": float(zz.real),
            "z_imag": float(zz.imag),
            "alpha_per_s": float(alpha),
            "wd_rad_s": float(wd),
            "f0_hz": float(f0),
            "zeta": float(zeta),
            "decaying": bool(alpha > 0),
            "oscillatory": bool(wd > 1e-9),
        })
    return out

def truth_modes_for_record(truth, station, component):
    """Return only oscillatory truth modes that actually exist in this record."""
    if "modes" in truth:
        return [m for m in truth["modes"] if m.get("zeta", 1.0) < 1.0]
    out = []
    if "shared" in truth and isinstance(truth["shared"], dict):
        sh = truth["shared"]
        if sh.get("zeta", 1.0) < 1.0 and "f0_hz" in sh:
            out.append(sh)
        loc = truth.get("local")
        if isinstance(loc, dict) and loc.get("station") == station and loc.get("component") == component:
            if loc.get("zeta", 1.0) < 1.0 and "f0_hz" in loc:
                out.append(loc)
        return out
    if "local_station" in truth:
        if station == truth.get("local_station") and truth.get("zeta", 1.0) < 1.0 and "f0_hz" in truth:
            return [{"zeta":truth["zeta"],"f0_hz":truth["f0_hz"]}]
        return []
    if "zeta" in truth and "f0_hz" in truth and truth["zeta"] < 1.0:
        return [{"zeta":truth["zeta"],"f0_hz":truth["f0_hz"]}]
    return []

manifest=json.loads(MANIFEST.read_text())
rows=[]
for case in manifest["cases"]:
    fs=float(case["sample_rate_hz"])
    truth=case.get("truth",{})
    for rec in case["records"]:
        truths=truth_modes_for_record(truth, rec["station"], rec["component"])
        for w in WINDOWS:
            for order in ORDERS:
                poles=pencil_poles(rec["path"],fs,w,order)
                # For known-truth qualification only, match each truth mode to nearest
                # decaying oscillatory pole by frequency. This matching is never used
                # for real-event discovery or model selection.
                candidates=[p for p in poles if p["decaying"] and p["oscillatory"] and p["f0_hz"] < fs/2]
                if truths:
                    for mi,tr in enumerate(truths):
                        if candidates:
                            p=min(candidates,key=lambda q:abs(q["f0_hz"]-tr["f0_hz"]))
                            rows.append({
                                "case_id":case["case_id"],
                                "expected_class":case["expected_class"],
                                "station":rec["station"],
                                "component":rec["component"],
                                "window_s":w,
                                "order":order,
                                "truth_mode_index":mi,
                                "truth_f0_hz":tr["f0_hz"],
                                "truth_zeta":tr["zeta"],
                                "matched_f0_hz":p["f0_hz"],
                                "matched_zeta":p["zeta"],
                                "rel_freq_error":abs(p["f0_hz"]-tr["f0_hz"])/tr["f0_hz"],
                                "abs_zeta_error":abs(p["zeta"]-tr["zeta"]),
                                "n_candidate_poles":len(candidates),
                            })
                        else:
                            rows.append({
                                "case_id":case["case_id"],
                                "expected_class":case["expected_class"],
                                "station":rec["station"],
                                "component":rec["component"],
                                "window_s":w,
                                "order":order,
                                "truth_mode_index":mi,
                                "truth_f0_hz":tr["f0_hz"],
                                "truth_zeta":tr["zeta"],
                                "matched_f0_hz":None,
                                "matched_zeta":None,
                                "rel_freq_error":None,
                                "abs_zeta_error":None,
                                "n_candidate_poles":0,
                            })
                else:
                    rows.append({
                        "case_id":case["case_id"],
                        "expected_class":case["expected_class"],
                        "station":rec["station"],
                        "component":rec["component"],
                        "window_s":w,
                        "order":order,
                        "truth_mode_index":None,
                        "truth_f0_hz":None,
                        "truth_zeta":None,
                        "matched_f0_hz":None,
                        "matched_zeta":None,
                        "rel_freq_error":None,
                        "abs_zeta_error":None,
                        "n_candidate_poles":len(candidates),
                    })

fields=sorted({k for r in rows for k in r})
with OUT.open("w",newline="") as f:
    wr=csv.DictWriter(f,fieldnames=fields)
    wr.writeheader()
    wr.writerows(rows)

def fmt(v):
    if v is None: return "n/a"
    return f"{v:.5g}"

lines=[
    "# Matrix-pencil known-truth qualification",
    "",
    "Purpose: test a stronger pole estimator on frozen synthetic cases before any real Chignik pole outcomes are inspected.",
    "",
    f"- Fixed windows: {WINDOWS} s",
    f"- Fixed model orders: {ORDERS}",
    "- Pencil geometry is fixed from sample count, not outcome.",
    "- Truth-based pole matching is used only to score synthetic qualification.",
    "- No admission threshold, preferred window, or preferred order is frozen by this run.",
    "",
    "## Single-mode summaries",
]
for cid in ["F01_clean_underdamped","F02_high_damping_underdamped"]:
    lines += ["", f"### {cid}"]
    subset=[r for r in rows if r["case_id"]==cid and r["station"]=="S1" and r["component"]=="E"]
    for r in subset:
        lines.append(
            f"- w={r['window_s']} s, order={r['order']}: "
            f"f0={fmt(r['matched_f0_hz'])} Hz, zeta={fmt(r['matched_zeta'])}, "
            f"rel_f_err={fmt(r['rel_freq_error'])}, abs_zeta_err={fmt(r['abs_zeta_error'])}, "
            f"candidate_poles={r['n_candidate_poles']}"
        )

lines += [
    "",
    "## All-fixture descriptive map",
    "",
    "This section reports the complete frozen fixture library without selecting a threshold, preferred window, preferred order, or real-data outcome.",
]
for case in manifest["cases"]:
    cid=case["case_id"]
    subset=[r for r in rows if r["case_id"]==cid]
    cell_map={}
    for r in subset:
        key=(r["station"],r["component"],r["window_s"],r["order"])
        cell_map[key]=r["n_candidate_poles"]
    counts=list(cell_map.values())
    zero_frac=(sum(1 for x in counts if x==0)/len(counts)) if counts else float("nan")
    matches=[r for r in subset if r["rel_freq_error"] is not None]
    lines += [
        "",
        f"### {cid}",
        f"- expected_class={case['expected_class']}",
        f"- unique station/component/window/order cells={len(counts)}",
        f"- decaying oscillatory candidate count range={min(counts) if counts else 'n/a'}..{max(counts) if counts else 'n/a'}",
        f"- zero-candidate cell fraction={zero_frac:.5g}" if counts else "- zero-candidate cell fraction=n/a",
    ]
    if matches:
        freq=np.asarray([r["rel_freq_error"] for r in matches],dtype=float)
        damp=np.asarray([r["abs_zeta_error"] for r in matches],dtype=float)
        lines += [
            f"- truth-match rows={len(matches)}",
            f"- median relative frequency error={np.median(freq):.5g}; max={np.max(freq):.5g}",
            f"- median absolute damping-ratio error={np.median(damp):.5g}; max={np.max(damp):.5g}",
        ]
    else:
        lines.append("- truth-match rows=0 (refusal/nonstationary/no-oscillatory-truth record)")
    for rec in case["records"]:
        vals=[v for k,v in cell_map.items() if k[0]==rec["station"] and k[1]==rec["component"]]
        lines.append(
            f"- record {rec['station']}:{rec['component']}: cells={len(vals)}, "
            f"candidate_count_range={min(vals) if vals else 'n/a'}..{max(vals) if vals else 'n/a'}"
        )

lines += [
    "",
    "## Interpretation",
    "",
    "This is a qualification map, not an optimization exercise. Stability across fixed windows/orders, known-truth error, and behavior on refusal fixtures will be used to design a separate prospective admission rule before any real-event pole interpretation.",
    "Critical, overdamped, monotonic, chirped, low-SNR, site-local, multimodal, and shared-plus-local fixtures remain refusal/qualification controls. Their outputs are evidence about estimator behavior, not permission to relax the refusal rules.",
]
REPORT.write_text("\n".join(lines)+"\n")
print(REPORT.read_text())
