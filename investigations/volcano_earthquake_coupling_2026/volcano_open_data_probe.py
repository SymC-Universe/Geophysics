#!/usr/bin/env python3
"""
Outcome-blind volcano data availability probe.

Inventories monitoring/data access only. Does not inspect eruption outcomes beyond
predeclared case labels, estimate state metrics, poles, chi, or tune thresholds.
"""
from __future__ import annotations
import csv, json, pathlib, requests

OUT = pathlib.Path("artifacts/volcano_earthquake_coupling_2026")
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent":"SymC-Geophysics-volcano-open-data-probe/0.1"}

CASES = [
    {"name":"Mauna Loa 2022","role":"fresh_candidate","legacy":False,"lat":19.475,"lon":-155.608,"time":"2022-11-28T09:30:00","dc":"earthscope"},
    {"name":"Redoubt 2009","role":"fresh_candidate","legacy":False,"lat":60.485,"lon":-152.742,"time":"2009-03-23T06:00:00","dc":"earthscope"},
    {"name":"Whakaari 2019","role":"fresh_candidate","legacy":False,"lat":-37.520,"lon":177.180,"time":"2019-12-09T01:11:00","dc":"geonet"},
    {"name":"Taupo 2022-2023","role":"fresh_negative_control","legacy":False,"lat":-38.820,"lon":176.000,"time":"2022-11-30T10:47:00","dc":"geonet"},
    {"name":"Ruapehu 2007","role":"fresh_candidate","legacy":False,"lat":-39.281,"lon":175.570,"time":"2007-09-25T08:26:00","dc":"geonet"},
    {"name":"Tongariro 2012","role":"fresh_candidate","legacy":False,"lat":-39.129,"lon":175.642,"time":"2012-08-06T11:50:00","dc":"geonet"},
    {"name":"Kilauea 2018","role":"development_only","legacy":True,"lat":19.421,"lon":-155.287,"time":"2018-05-03T22:30:00","dc":"earthscope"},
    {"name":"Mount St Helens 2004","role":"development_only","legacy":True,"lat":46.200,"lon":-122.180,"time":"2004-09-23T00:00:00","dc":"earthscope"},
]

def get(url, timeout=30):
    try:
        r=requests.get(url,headers=UA,timeout=timeout,allow_redirects=True)
        return {"ok":200<=r.status_code<300,"status":r.status_code,"bytes":len(r.content),"ctype":r.headers.get("content-type"),"text":r.text[:500000]}
    except Exception as e:
        return {"ok":False,"status":None,"bytes":0,"ctype":None,"text":"","error":repr(e)}

def station_query(base, c):
    url=(f"{base}/fdsnws/station/1/query?format=text&level=channel"
         f"&latitude={c['lat']}&longitude={c['lon']}&maxradius=0.7"
         f"&starttime={c['time']}&endtime={c['time']}")
    x=get(url)
    lines=[ln for ln in x.get("text","").splitlines() if ln and not ln.startswith("#")] if x["ok"] else []
    nets=sorted({ln.split("|")[0] for ln in lines if "|" in ln})
    stations=sorted({(ln.split("|")[0],ln.split("|")[1]) for ln in lines if ln.count("|")>=1})
    return {"ok":x["ok"],"status":x["status"],"channel_rows":len(lines),"network_count":len(nets),"station_count":len(stations)}

# Smithsonian VOTW webservice capability probe
gvp = get("https://webservices.volcano.si.edu/geoserver/GVP-VOTW/wfs?request=GetCapabilities")
gvp_summary={"ok":gvp["ok"],"status":gvp["status"],"bytes":gvp["bytes"]}

rows=[]
for c in CASES:
    base="https://service.geonet.org.nz" if c["dc"]=="geonet" else "https://service.earthscope.org"
    sta=station_query(base,c)
    rows.append({
        "case":c["name"],
        "role":c["role"],
        "legacy_exposed":c["legacy"],
        "data_center":c["dc"],
        "station_service_ok":sta["ok"],
        "channel_rows_within_0p7deg":sta["channel_rows"],
        "station_count_within_0p7deg":sta["station_count"],
        "network_count_within_0p7deg":sta["network_count"],
        "gvp_wfs_ok":gvp_summary["ok"],
    })

# GeoNet monitoring-page/API access probes useful to the NZ volcano cases.
support = [
    ("geonet_fdsn_station","https://service.geonet.org.nz/fdsnws/station/1/version"),
    ("geonet_fdsn_event","https://service.geonet.org.nz/fdsnws/event/1/version"),
    ("earthscope_fdsn_station","https://service.earthscope.org/fdsnws/station/1/version"),
    ("gvp_wfs_capabilities","https://webservices.volcano.si.edu/geoserver/GVP-VOTW/wfs?request=GetCapabilities"),
    ("geonet_volcano_monitoring","https://www.geonet.org.nz/volcano/how"),
]
support_rows=[]
for name,url in support:
    x=get(url)
    support_rows.append({"service":name,"url":url,"ok":x["ok"],"status":x["status"],"bytes":x["bytes"],"content_type":x["ctype"]})

with (OUT/"volcano_data_availability.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
(OUT/"volcano_support_services.json").write_text(json.dumps(support_rows,indent=2))

lines=[
    "# Volcano open-data availability probe","",
    "**Firewall:** metadata/access only. No event-specific stability metric, pole, chi, or outcome-based threshold inspected.","",
    f"- Smithsonian GVP WFS accessible: **{gvp_summary['ok']}**","",
]
for r in rows:
    lines.append(
        f"- **{r['case']}** ({r['role']}; legacy={r['legacy_exposed']}): "
        f"{r['data_center']} station metadata ok={r['station_service_ok']}; "
        f"stations within 0.7 deg={r['station_count_within_0p7deg']}; "
        f"channel rows={r['channel_rows_within_0p7deg']}"
    )
(OUT/"VOLCANO_AVAILABILITY_SUMMARY.md").write_text("\n".join(lines)+"\n")
print((OUT/"VOLCANO_AVAILABILITY_SUMMARY.md").read_text())
