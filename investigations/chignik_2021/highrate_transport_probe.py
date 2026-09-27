#!/usr/bin/env python3
"""
Chignik M8.2 high-rate data acquisition and transport qualification.

Purpose
-------
Recover machine-readable rupture records without inspecting or optimizing any
SymC/chi outcome. This script performs transport, integrity, provenance and
format inventory only. It does not estimate poles or chi.

Public routes attempted:
1. CESMD processed/raw ZIP products for USGS event us6000f02w.
2. Figshare article 19323386 (v7 lineage cited by Chignik literature).

Outputs are written under artifacts/chignik_highrate_probe/.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
import zipfile
from urllib.parse import urlparse

import requests

ROOT = pathlib.Path("artifacts/chignik_highrate_probe")
DL = ROOT / "downloads"
EXTRACT = ROOT / "extracted"
ROOT.mkdir(parents=True, exist_ok=True)
DL.mkdir(parents=True, exist_ok=True)
EXTRACT.mkdir(parents=True, exist_ok=True)

CESMD_BASE = "https://www.strongmotioncenter.org/NCESMD/data/us6000f02w/"
CESMD_FILES = [
    "aks15kp.zip",
    "akchnp.zip",
    "akcnpp.zip",
    "akhomp.zip",
    "ako19kp.zip",
    "aks19kp.zip",
    "akunvp.zip",
]
FIGSHARE_ARTICLE = "19323386"
FIGSHARE_API = f"https://api.figshare.com/v2/articles/{FIGSHARE_ARTICLE}"

UA = "SymC-Geophysics-Chignik-transport-probe/1.0"
TIMEOUT = 90
MAX_FIGSHARE_BYTES = 700 * 1024 * 1024

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def download(url: str, dest: pathlib.Path) -> dict:
    rec = {"url": url, "dest": str(dest), "ok": False}
    try:
        with requests.get(url, stream=True, timeout=TIMEOUT, headers={"User-Agent": UA}) as r:
            rec["status"] = r.status_code
            rec["content_type"] = r.headers.get("content-type")
            rec["content_length"] = r.headers.get("content-length")
            if r.status_code != 200:
                rec["error"] = f"HTTP {r.status_code}"
                return rec
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        rec["bytes"] = dest.stat().st_size
        rec["sha256"] = sha256(dest)
        rec["ok"] = True
    except Exception as e:
        rec["error"] = repr(e)
    return rec

def inspect_zip(path: pathlib.Path, label: str) -> dict:
    rec = {"archive": str(path), "label": label, "is_zip": False, "members": []}
    try:
        if not zipfile.is_zipfile(path):
            rec["error"] = "not a valid ZIP"
            return rec
        rec["is_zip"] = True
        outdir = EXTRACT / label.replace(".zip", "")
        outdir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                item = {
                    "name": info.filename,
                    "bytes": info.file_size,
                    "compressed_bytes": info.compress_size,
                }
                rec["members"].append(item)
            # Extract only reasonably sized, non-directory members. The archive
            # itself remains the provenance object.
            for info in z.infolist():
                if info.is_dir() or info.file_size > 250 * 1024 * 1024:
                    continue
                safe = pathlib.Path(info.filename)
                if ".." in safe.parts:
                    continue
                z.extract(info, outdir)
        rec["member_count"] = len(rec["members"])
    except Exception as e:
        rec["error"] = repr(e)
    return rec

def figshare_probe() -> dict:
    result = {"api": FIGSHARE_API, "ok": False, "files": [], "downloads": []}
    try:
        r = requests.get(FIGSHARE_API, timeout=TIMEOUT, headers={"User-Agent": UA})
        result["status"] = r.status_code
        if r.status_code != 200:
            result["error"] = r.text[:500]
            return result
        meta = r.json()
        result["ok"] = True
        result["title"] = meta.get("title")
        result["url_private_api"] = meta.get("url_private_api")
        result["doi"] = meta.get("doi")
        result["description_excerpt"] = re.sub("<[^>]+>", " ", meta.get("description", ""))[:1000]
        files = meta.get("files", [])
        result["files"] = [
            {
                "id": x.get("id"),
                "name": x.get("name"),
                "size": x.get("size"),
                "download_url": x.get("download_url"),
                "computed_md5": x.get("computed_md5"),
            } for x in files
        ]
        # Download likely machine-readable geodetic/seismic/model files when
        # size is bounded. No outcome-based filtering.
        rx = re.compile(r"(gnss|gps|seis|wave|strong|disp|vel|sac|mseed|rinex|data|model)", re.I)
        candidates = [x for x in files if x.get("download_url") and x.get("size", 0) <= MAX_FIGSHARE_BYTES and rx.search(x.get("name", ""))]
        if not candidates and len(files) <= 10:
            candidates = [x for x in files if x.get("download_url") and x.get("size", 0) <= MAX_FIGSHARE_BYTES]
        for x in candidates:
            name = x.get("name") or f"figshare_{x.get('id')}"
            dest = DL / ("figshare_" + pathlib.Path(name).name)
            d = download(x["download_url"], dest)
            d["figshare_file_id"] = x.get("id")
            result["downloads"].append(d)
            if d.get("ok") and zipfile.is_zipfile(dest):
                d["zip_inventory"] = inspect_zip(dest, "figshare_" + pathlib.Path(name).stem)
    except Exception as e:
        result["error"] = repr(e)
    return result

def inventory_extracted() -> list[dict]:
    rows = []
    for p in sorted(EXTRACT.rglob("*")):
        if not p.is_file():
            continue
        row = {
            "path": str(p),
            "bytes": p.stat().st_size,
            "suffix": p.suffix.lower(),
            "sha256": sha256(p),
        }
        # Peek at text-ish files for parser planning only.
        if p.suffix.lower() in {".txt", ".asc", ".dat", ".csv", ".v1", ".v2", ".v3", ".sac"} and p.stat().st_size < 50 * 1024 * 1024:
            try:
                raw = p.read_bytes()[:4096]
                row["head_ascii"] = raw.decode("utf-8", errors="replace")[:1200]
            except Exception as e:
                row["peek_error"] = repr(e)
        rows.append(row)
    return rows

def main() -> int:
    report = {
        "event": "2021-07-29 Chignik M8.2",
        "usgs_event_id": "us6000f02w",
        "purpose": "transport/provenance/format qualification only; no chi/pole estimation",
        "cesmd": [],
        "figshare": None,
        "extracted_inventory": [],
    }

    success = 0
    for name in CESMD_FILES:
        dest = DL / name
        d = download(CESMD_BASE + name, dest)
        if d.get("ok"):
            success += 1
            d["zip_inventory"] = inspect_zip(dest, name)
        report["cesmd"].append(d)

    report["figshare"] = figshare_probe()
    success += sum(1 for x in report["figshare"].get("downloads", []) if x.get("ok"))
    report["extracted_inventory"] = inventory_extracted()
    report["successful_downloads"] = success

    out = ROOT / "probe_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = ROOT / "SUMMARY.md"
    lines = [
        "# Chignik high-rate transport probe",
        "",
        f"- Successful downloads: **{success}**",
        f"- CESMD products attempted: **{len(CESMD_FILES)}**",
        f"- Extracted machine-readable files inventoried: **{len(report['extracted_inventory'])}**",
        "",
        "This run performs transport/provenance/format qualification only. It does **not** estimate poles or χ.",
        "",
        "## CESMD",
    ]
    for x in report["cesmd"]:
        lines.append(f"- {pathlib.Path(x['dest']).name}: {'OK' if x.get('ok') else 'FAIL'} ({x.get('status', 'n/a')})")
    lines += ["", "## Figshare", f"- API status: {report['figshare'].get('status', 'n/a')}"]
    for x in report["figshare"].get("downloads", []):
        lines.append(f"- {pathlib.Path(x['dest']).name}: {'OK' if x.get('ok') else 'FAIL'}")
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Measurement/format qualification is deliberately downstream of transport and
    # deliberately upstream of any modal, pole, or chi estimation.
    qualifier = pathlib.Path("investigations/chignik_2021/highrate_format_qualification.py")
    if qualifier.exists() and success > 0:
        subprocess.run([sys.executable, str(qualifier)], check=True)

    # Known-truth synthetic fixtures are generated before Chignik modal fitting.
    fixtures = pathlib.Path("investigations/chignik_2021/highrate_synthetic_fixtures.py")
    if fixtures.exists() and success > 0:
        subprocess.run([sys.executable, str(fixtures)], check=True)

    baseline = pathlib.Path("investigations/chignik_2021/highrate_synthetic_baseline.py")
    if baseline.exists() and success > 0:
        subprocess.run([sys.executable, str(baseline)], check=True)

    ar2 = pathlib.Path("investigations/chignik_2021/highrate_synthetic_ar2.py")
    if ar2.exists() and success > 0:
        subprocess.run([sys.executable, str(ar2)], check=True)

    dep_probe = pathlib.Path("investigations/chignik_2021/highrate_dependency_probe.py")
    if dep_probe.exists() and success > 0:
        subprocess.run([sys.executable, str(dep_probe)], check=True)

    # A zero-success run is a transport failure worth making visible to Actions.
    return 0 if success > 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
