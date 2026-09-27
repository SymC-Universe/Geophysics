from __future__ import annotations
import csv, json, math, pathlib, statistics

ROOT = pathlib.Path("artifacts/chignik_highrate_probe/synthetic_fixtures")
MANIFEST = ROOT / "fixture_manifest.json"
OUT = ROOT / "ar2_window_sensitivity.csv"
REPORT = ROOT / "AR2_WINDOW_SENSITIVITY.md"
WINDOWS = [0.75, 1.0, 1.5, 2.0, 4.0, 8.0, 10.0]

def read_signal(path):
    t=[]; y=[]
    with open(path,newline="") as f:
        r=csv.DictReader(f)
        for row in r:
            t.append(float(row["time_s"])); y.append(float(row["value"]))
    return t,y

def ar2_estimate(path, fs, window_s):
    t,y=read_signal(path)
    n=min(len(y), int(round(window_s*fs))+1)
    if n < 6:
        return {"status":"INSUFFICIENT"}
    x=y[:n]
    # Remove a constant offset only. No event-dependent filtering or tuning.
    m=sum(x)/len(x)
    x=[v-m for v in x]
    s11=s22=s12=b1=b2=0.0
    for i in range(2,len(x)):
        p1=x[i-1]; p2=x[i-2]; yy=x[i]
        s11 += p1*p1
        s22 += p2*p2
        s12 += p1*p2
        b1 += p1*yy
        b2 += p2*yy
    det=s11*s22-s12*s12
    if not math.isfinite(det) or abs(det) < 1e-18:
        return {"status":"SINGULAR"}
    a1=(b1*s22-b2*s12)/det
    a2=(s11*b2-s12*b1)/det
    disc=a1*a1+4.0*a2
    out={"status":"OK","a1":a1,"a2":a2,"discriminant":disc}
    if disc >= 0:
        sd=math.sqrt(disc)
        out.update({"pole_type":"REAL","root1":(a1+sd)/2.0,"root2":(a1-sd)/2.0})
        return out
    if a2 >= 0:
        out.update({"pole_type":"INVALID_COMPLEX"})
        return out
    r=math.sqrt(-a2)
    if not (0.0 < r < 1.0):
        out.update({"pole_type":"UNSTABLE_OR_NONDECAYING","radius":r})
        return out
    arg=max(-1.0,min(1.0,a1/(2.0*r)))
    theta=math.acos(arg)
    alpha=-math.log(r)*fs
    wd=theta*fs
    wn=math.sqrt(alpha*alpha+wd*wd)
    zeta=alpha/wn if wn>0 else None
    f0=wn/(2.0*math.pi) if wn>0 else None
    out.update({
        "pole_type":"COMPLEX_DECAYING",
        "radius":r,
        "theta_rad":theta,
        "alpha_per_s":alpha,
        "wd_rad_s":wd,
        "wn_rad_s":wn,
        "f0_est_hz":f0,
        "zeta_est":zeta,
    })
    return out

m=json.loads(MANIFEST.read_text())
rows=[]
for case in m["cases"]:
    truth=case.get("truth",{})
    fs=float(case["sample_rate_hz"])
    for rec in case["records"]:
        for w in WINDOWS:
            e=ar2_estimate(rec["path"],fs,w)
            row={
                "case_id":case["case_id"],
                "expected_class":case["expected_class"],
                "station":rec["station"],
                "component":rec["component"],
                "window_s":w,
                **e,
            }
            if "zeta" in truth:
                row["truth_zeta"]=truth["zeta"]
                if e.get("zeta_est") is not None:
                    row["abs_zeta_error"]=abs(e["zeta_est"]-truth["zeta"])
            if "f0_hz" in truth:
                row["truth_f0_hz"]=truth["f0_hz"]
                if e.get("f0_est_hz") is not None:
                    row["rel_freq_error"]=abs(e["f0_est_hz"]-truth["f0_hz"])/truth["f0_hz"]
            rows.append(row)

fields=sorted({k for r in rows for k in r})
with OUT.open("w",newline="") as f:
    wr=csv.DictWriter(f,fieldnames=fields); wr.writeheader(); wr.writerows(rows)

def fmt(v):
    return "n/a" if v is None else f"{v:.5g}"

lines=[
    "# Synthetic AR(2) pole baseline: fixed-window sensitivity",
    "",
    "Purpose: map the behavior and failure modes of a minimal pole estimator on frozen known-truth fixtures before any Chignik pole inspection.",
    "",
    f"- Fixed windows: {WINDOWS} s",
    "- Model: zero-offset AR(2) least-squares recurrence",
    "- Complex roots are converted to decay rate, damped frequency, natural frequency, and damping ratio.",
    "- No window is selected by outcome and no admission threshold is defined here.",
    "",
    "## Single-mode known-truth cases",
]
for cid in ["F01_clean_underdamped","F02_high_damping_underdamped"]:
    lines += ["", f"### {cid}"]
    for r in rows:
        if r["case_id"]==cid and r["station"]=="S1" and r["component"]=="E":
            lines.append(
                f"- {r['window_s']} s: pole={r.get('pole_type','n/a')}, "
                f"f0={fmt(r.get('f0_est_hz'))} Hz, zeta={fmt(r.get('zeta_est'))}, "
                f"rel_f_err={fmt(r.get('rel_freq_error'))}, abs_zeta_err={fmt(r.get('abs_zeta_error'))}"
            )

lines += [
    "",
    "## Interpretation rule for this qualification stage",
    "",
    "This output is descriptive. Window sensitivity, complex-versus-real pole behavior, and known-truth error will be used to design an admission/refusal test, but thresholds must be frozen separately before real-event pole outcomes are inspected.",
]
REPORT.write_text("\n".join(lines)+"\n")
print(REPORT.read_text())
