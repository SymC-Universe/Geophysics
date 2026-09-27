from __future__ import annotations
import csv, json, math, pathlib, statistics

ROOT=pathlib.Path('artifacts/chignik_highrate_probe/synthetic_fixtures')
MANIFEST=ROOT/'fixture_manifest.json'
OUT=ROOT/'baseline_logdecrement_results.csv'
REPORT=ROOT/'BASELINE_LOGDECREMENT.md'

def read_signal(path):
    t=[]; y=[]
    with open(path,newline='') as f:
        r=csv.DictReader(f)
        for row in r:
            t.append(float(row['time_s'])); y.append(float(row['value']))
    return t,y

def estimate(path, window_s=10.0):
    t,y=read_signal(path)
    idx=[i for i,tt in enumerate(t) if tt <= window_s]
    if len(idx)<5: return None
    n=idx[-1]+1
    peaks=[]
    for i in range(1,n-1):
        if y[i]>0 and y[i]>=y[i-1] and y[i]>y[i+1]:
            peaks.append((t[i],y[i]))
    peaks=peaks[:12]
    if len(peaks)<3:
        return {'n_peaks':len(peaks),'f_est_hz':None,'zeta_est':None,'period_cv':None,'logdec_cv':None}
    periods=[peaks[i+1][0]-peaks[i][0] for i in range(len(peaks)-1) if peaks[i+1][0]>peaks[i][0]]
    f_est=1/statistics.median(periods) if periods else None
    deltas=[]
    for i in range(len(peaks)-1):
        a,b=peaks[i][1],peaks[i+1][1]
        if a>0 and b>0:
            deltas.append(math.log(a/b))
    pos=[d for d in deltas if d>0]
    delta=statistics.median(pos) if pos else None
    zeta=delta/math.sqrt((2*math.pi)**2+delta**2) if delta is not None else None
    def cv(xs):
        if not xs or len(xs)<2: return None
        m=statistics.mean(xs)
        return statistics.stdev(xs)/abs(m) if m else None
    return {'n_peaks':len(peaks),'f_est_hz':f_est,'zeta_est':zeta,'period_cv':cv(periods),'logdec_cv':cv(pos)}

m=json.loads(MANIFEST.read_text())
rows=[]
for c in m['cases']:
    truth=c.get('truth',{})
    for rec in c['records']:
        e=estimate(rec['path'])
        if e is None: continue
        row={'case_id':c['case_id'],'expected_class':c['expected_class'],'station':rec['station'],'component':rec['component'],**e}
        if 'zeta' in truth: row['truth_zeta']=truth['zeta']
        if 'f0_hz' in truth: row['truth_f0_hz']=truth['f0_hz']
        if 'zeta' in truth and e.get('zeta_est') is not None: row['abs_zeta_error']=abs(e['zeta_est']-truth['zeta'])
        if 'f0_hz' in truth and e.get('f_est_hz') is not None: row['rel_freq_error']=abs(e['f_est_hz']-truth['f0_hz'])/truth['f0_hz']
        rows.append(row)

fields=sorted({k for r in rows for k in r})
with OUT.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

single=[r for r in rows if r['case_id'] in {'F01_clean_underdamped','F02_high_damping_underdamped'}]
lines=['# Synthetic baseline: simple logarithmic decrement','',
       'Purpose: establish a deliberately simple native damping baseline on known-truth fixtures before any Chignik modal estimation.','',
       '- Fixed estimation window: first 10 s',
       '- Frequency: median spacing of earliest positive local maxima',
       '- Damping: median positive logarithmic decrement converted to damping ratio',
       '- No admission thresholds are defined by this run.','']
for r in single:
    lines.append(f"- {r['case_id']} {r['station']}:{r['component']}: f_est={r.get('f_est_hz')}, zeta_est={r.get('zeta_est')}, rel_freq_error={r.get('rel_freq_error')}, abs_zeta_error={r.get('abs_zeta_error')}")
lines += ['', 'The full CSV includes multimode, chirp, low-SNR, site-local, and shared-mode cases so instability/failure of this simplistic estimator remains visible rather than being hidden.']
REPORT.write_text('\n'.join(lines)+'\n')
print(REPORT.read_text())
