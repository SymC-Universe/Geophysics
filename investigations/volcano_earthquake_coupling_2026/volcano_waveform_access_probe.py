#!/usr/bin/env python3
"""
Outcome-blind waveform-access probe for volcano benchmark cases.

For each case, find an active nearby seismic channel from station metadata and request
a short waveform slice. No signal metrics, spectral features, poles, eruption labels,
or stability quantities are computed.
"""
from __future__ import annotations
import csv, datetime as dt, pathlib, requests

OUT = pathlib.Path("artifacts/volcano_earthquake_coupling_2026")
OUT.mkdir(parents=True, exist_ok=True)
UA={"User-Agent":"SymC-Geophysics-volcano-waveform-access/0.1"}

CASES=[
    {"name":"Mauna Loa 2022","role":"fresh_candidate","lat":19.475,"lon":-155.608,"time":"2022-11-28T09:30:00","base":"https://service.earthscope.org"},
    {"name":"Redoubt 2009","role":"fresh_candidate","lat":60.485,"lon":-152.742,"time":"2009-03-23T06:00:00","base":"https://service.earthscope.org"},
    {"name":"Whakaari 2019","role":"fresh_candidate","lat":-37.520,"lon":177.180,"time":"2019-12-09T01:11:00","base":"https://service.geonet.org.nz"},
    {"name":"Taupo 2022-2023","role":"fresh_negative_control","lat":-38.820,"lon":176.000,"time":"2022-11-30T10:47:00","base":"https://service.geonet.org.nz"},
    {"name":"Ruapehu 2007","role":"fresh_candidate","lat":-39.281,"lon":175.570,"time":"2007-09-25T08:26:00","base":"https://service.geonet.org.nz"},
    {"name":"Tongariro 2012","role":"fresh_candidate","lat":-39.129,"lon":175.642,"time":"2012-08-06T11:50:00","base":"https://service.geonet.org.nz"},
]

PREF=("HHZ","BHZ","EHZ","SHZ","HNZ","HHN","BHN","EHN","HHE","BHE","EHE","HNN","HNE")

def get(url,timeout=45):
    try:
        r=requests.get(url,headers=UA,timeout=timeout,allow_redirects=True)
        return r
    except Exception:
        return None

def iso_add_seconds(s,sec):
    x=dt.datetime.fromisoformat(s)
    return (x+dt.timedelta(seconds=sec)).isoformat()

rows=[]
for c in CASES:
    sturl=(f"{c['base']}/fdsnws/station/1/query?format=text&level=channel"
           f"&latitude={c['lat']}&longitude={c['lon']}&maxradius=0.7"
           f"&starttime={c['time']}&endtime={c['time']}")
    r=get(sturl)
    choices=[]
    if r is not None and 200<=r.status_code<300:
        for ln in r.text.splitlines():
            if not ln or ln.startswith("#"): continue
            parts=ln.split("|")
            if len(parts)<4: continue
            net,sta,loc,cha=parts[:4]
            if cha in PREF:
                choices.append((PREF.index(cha),net,sta,loc,cha))
        choices.sort()
    selected=None
    status=None
    nbytes=0
    ctype=None
    for _,net,sta,loc,cha in choices[:20]:
        locq=loc if loc else "--"
        q=(f"{c['base']}/fdsnws/dataselect/1/query?net={net}&sta={sta}&loc={locq}&cha={cha}"
           f"&start={c['time']}&end={iso_add_seconds(c['time'],20)}")
        w=get(q)
        if w is not None:
            status=w.status_code
            nbytes=len(w.content)
            ctype=w.headers.get("content-type")
            if 200<=w.status_code<300 and nbytes>0:
                selected=(net,sta,loc,cha)
                break
    rows.append({
        "case":c["name"],
        "role":c["role"],
        "metadata_candidate_channels":len(choices),
        "waveform_fetch_ok":selected is not None,
        "selected_network":selected[0] if selected else None,
        "selected_station":selected[1] if selected else None,
        "selected_location":selected[2] if selected else None,
        "selected_channel":selected[3] if selected else None,
        "http_status":status,
        "bytes_20s":nbytes,
        "content_type":ctype,
    })

with (OUT/"volcano_waveform_access.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

lines=["# Volcano waveform access probe","",
       "**Firewall:** short-byte retrieval only. No waveform-derived scientific quantity is computed.",""]
for x in rows:
    lines.append(
        f"- **{x['case']}** ({x['role']}): fetch_ok={x['waveform_fetch_ok']}; "
        f"channel={x['selected_network']}.{x['selected_station']}.{x['selected_channel']}; "
        f"bytes_20s={x['bytes_20s']}; candidates={x['metadata_candidate_channels']}"
    )
(OUT/"VOLCANO_WAVEFORM_ACCESS.md").write_text("\n".join(lines)+"\n")
print((OUT/"VOLCANO_WAVEFORM_ACCESS.md").read_text())
if not any(x["waveform_fetch_ok"] for x in rows):
    raise SystemExit("No fresh volcano waveform slice could be retrieved")
