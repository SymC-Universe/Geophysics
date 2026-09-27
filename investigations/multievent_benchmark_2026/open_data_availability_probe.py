#!/usr/bin/env python3
"""
Outcome-blind open-data availability probe for the multi-event benchmark.

This script inventories access and metadata only. It does not download full waveform
archives, estimate poles, calculate chi, or inspect event-specific scientific outcomes.
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import requests

OUT = pathlib.Path("artifacts/multievent_benchmark_2026")
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "SymC-Geophysics-open-data-probe/0.1"}

EVENTS = [
    {
        "event": "Anchorage 2018",
        "role": "fresh_candidate",
        "legacy_exposed": False,
        "usgs_id": "us1000hyfh",
        "lat": 61.340,
        "lon": -149.937,
        "time": "2018-11-30T17:29:28Z",
        "cesmd_page": "https://www.strongmotioncenter.org/cgi-bin/CESMD/iqr_dist_DM2.pl?ID=us1000hyfh",
    },
    {
        "event": "Ridgecrest 2019",
        "role": "development_only",
        "legacy_exposed": True,
        "usgs_id": "ci38457511",
        "lat": 35.770,
        "lon": -117.599,
        "time": "2019-07-06T03:19:53Z",
        "cesmd_page": "https://www.strongmotioncenter.org/cgi-bin/CESMD/iqr_dist_DM2.pl?ID=ci38457511",
    },
    {
        "event": "South Napa 2014",
        "role": "fresh_candidate",
        "legacy_exposed": False,
        "usgs_id": "nc72282711",
        "lat": 38.220,
        "lon": -122.313,
        "time": "2014-08-24T10:20:44Z",
        "cesmd_page": "https://www.strongmotioncenter.org/cgi-bin/CESMD/iqr_dist_DM2.pl?iqrID=AmericanCanyon_24Aug2014_72282711",
    },
    {
        "event": "Puerto Rico 2020",
        "role": "fresh_candidate",
        "legacy_exposed": False,
        "usgs_id": "us70006vll",
        "lat": 17.916,
        "lon": -66.813,
        "time": "2020-01-07T08:24:26Z",
        "cesmd_page": "https://www.strongmotioncenter.org/cgi-bin/CESMD/iqr_dist_DM2.pl?ID=us70006vll",
    },
    {
        "event": "Kaikoura 2016",
        "role": "fresh_candidate",
        "legacy_exposed": False,
        "usgs_id": "us1000778i",
        "geonet_id": "2016p858000",
        "lat": -42.69,
        "lon": 173.02,
        "time": "2016-11-13T11:02:56Z",
    },
    {
        "event": "Tohoku 2011",
        "role": "development_only",
        "legacy_exposed": True,
        "usgs_id": "usc0001xgp",
        "lat": 38.297,
        "lon": 142.373,
        "time": "2011-03-11T05:46:24Z",
    },
    {
        "event": "Maule 2010",
        "role": "development_only",
        "legacy_exposed": True,
        "usgs_id": "official20100227063411530_30",
        "lat": -35.909,
        "lon": -72.733,
        "time": "2010-02-27T06:34:14Z",
    },
]

def fetch(url: str, timeout: int = 30):
    try:
        r = requests.get(url, headers=UA, timeout=timeout, allow_redirects=True)
        return {
            "ok": 200 <= r.status_code < 300,
            "status": r.status_code,
            "bytes": len(r.content),
            "content_type": r.headers.get("content-type"),
            "url_final": r.url,
            "text": r.text[:2_000_000] if "text" in r.headers.get("content-type", "") or "json" in r.headers.get("content-type", "") else "",
        }
    except Exception as e:
        return {"ok": False, "error": repr(e), "status": None, "bytes": 0, "content_type": None, "url_final": url, "text": ""}

def station_count_earthscope(event):
    # Metadata-only query in a 1-degree radius and narrow event-time interval.
    t = event["time"].replace("Z", "")
    url = (
        "https://service.earthscope.org/fdsnws/station/1/query"
        f"?format=text&level=channel&latitude={event['lat']}&longitude={event['lon']}"
        f"&maxradius=1&starttime={t}&endtime={t}"
    )
    x = fetch(url)
    count = None
    if x.get("ok"):
        lines = [ln for ln in x.get("text", "").splitlines() if ln and not ln.startswith("#")]
        count = len(lines)
    x.pop("text", None)
    x["channel_rows"] = count
    x["service"] = "earthscope_fdsn_station"
    return x

rows = []
details = []

for ev in EVENTS:
    # USGS/ComCat availability and product classes
    usgs_url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{ev['usgs_id']}.geojson"
    usgs = fetch(usgs_url)
    product_keys = []
    if usgs.get("ok"):
        try:
            obj = requests.get(usgs_url, headers=UA, timeout=30).json()
            product_keys = sorted((obj.get("properties", {}).get("products") or {}).keys())
        except Exception:
            pass
    usgs.pop("text", None)
    usgs["service"] = "usgs_event_detail"
    usgs["product_keys"] = product_keys
    details.append({"event": ev["event"], **usgs})

    # EarthScope metadata availability around event
    es = station_count_earthscope(ev)
    details.append({"event": ev["event"], **es})

    cesmd = None
    if ev.get("cesmd_page"):
        cesmd = fetch(ev["cesmd_page"])
        text = cesmd.get("text", "")
        station_mentions = len(re.findall(r"Station", text, flags=re.I)) if text else None
        cesmd.pop("text", None)
        cesmd["service"] = "cesmd_event_page"
        cesmd["station_mentions"] = station_mentions
        details.append({"event": ev["event"], **cesmd})

    geonet_quake = geonet_strong = None
    if ev.get("geonet_id"):
        geonet_quake = fetch(f"https://api.geonet.org.nz/quake/{ev['geonet_id']}")
        geonet_quake.pop("text", None)
        geonet_quake["service"] = "geonet_quake_api"
        details.append({"event": ev["event"], **geonet_quake})

        geonet_strong = fetch(f"https://api.geonet.org.nz/intensity/strong/processed/{ev['geonet_id']}")
        strong_feature_count = None
        if geonet_strong.get("ok"):
            try:
                obj = requests.get(
                    f"https://api.geonet.org.nz/intensity/strong/processed/{ev['geonet_id']}",
                    headers=UA, timeout=30
                ).json()
                strong_feature_count = len(obj.get("features") or [])
            except Exception:
                pass
        geonet_strong.pop("text", None)
        geonet_strong["service"] = "geonet_strong_api"
        geonet_strong["feature_count"] = strong_feature_count
        details.append({"event": ev["event"], **geonet_strong})

    rows.append({
        "event": ev["event"],
        "role": ev["role"],
        "legacy_exposed": ev["legacy_exposed"],
        "usgs_event_ok": usgs.get("ok"),
        "usgs_product_count": len(product_keys),
        "usgs_products": ";".join(product_keys),
        "earthscope_station_ok": es.get("ok"),
        "earthscope_channel_rows_1deg": es.get("channel_rows"),
        "cesmd_event_ok": cesmd.get("ok") if cesmd else None,
        "geonet_quake_ok": geonet_quake.get("ok") if geonet_quake else None,
        "geonet_strong_ok": geonet_strong.get("ok") if geonet_strong else None,
        "geonet_strong_feature_count": geonet_strong.get("feature_count") if geonet_strong else None,
    })

csv_path = OUT / "event_data_availability.csv"
with csv_path.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

(OUT / "event_data_availability_details.json").write_text(json.dumps(details, indent=2))

lines = [
    "# Multi-event open-data availability probe",
    "",
    "**Outcome firewall:** metadata/access only. No waveform scientific outcomes, modal estimates, thresholds, or chi values inspected.",
    "",
]
for r in rows:
    lines.append(
        f"- **{r['event']}** ({r['role']}; legacy_exposed={r['legacy_exposed']}): "
        f"USGS={r['usgs_event_ok']} ({r['usgs_product_count']} product classes), "
        f"EarthScope station metadata={r['earthscope_station_ok']} "
        f"(channel rows within 1 deg={r['earthscope_channel_rows_1deg']}), "
        f"CESMD={r['cesmd_event_ok']}, GeoNet={r['geonet_quake_ok']}"
    )
(OUT / "AVAILABILITY_SUMMARY.md").write_text("\n".join(lines) + "\n")
print((OUT / "AVAILABILITY_SUMMARY.md").read_text())
