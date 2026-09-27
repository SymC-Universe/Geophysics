# Multi-Event Seismology Benchmark Expansion

**Status:** A0 / P0-N exploratory infrastructure, NOT FROZEN  
**Date:** 2026-09-27  
**GOM:** v0.8.8  
**Program objective:** Build a broad-use, scientifically defensible representation/adjudication tool using heterogeneous public earthquake datasets. Chignik is one development event, not the investigation.

## 1. Event-role firewall

No event becomes a confirmatory holdout merely by appearing in this inventory. Holdout status will be frozen only after the preregistration question, representation rules, comparators, and admission/refusal criteria are finalized.

### Legacy-exposed / development-only

These events have prior SymC or derived-data exposure and are therefore unsuitable as pristine confirmatory holdouts.

- 2021 Chignik, Alaska, Mw 8.2
- 2019 Ridgecrest, California, Mw 7.1
- 2011 Tohoku, Japan, Mw 9.0
- 2010 Maule, Chile, Mw 8.8

They remain useful for:
- parser and transport qualification;
- estimator development;
- known failure reconstruction;
- comparator implementation;
- source/site/path challenge design;
- cross-event stress testing after all legacy targets are quarantined.

## 2. Fresh expansion candidates

### 2018 Anchorage, Alaska, Mw 7.0
**Why useful:** deep/intraslab geometry, dense strong-motion coverage, very different source/path structure from Chignik and Ridgecrest.  
**Open-data route:** CESMD + EarthScope/USGS products.  
**Known current inventory:** CESMD lists 98 strong-motion records for the mainshock.  
**Role:** fresh stress-test candidate; eligibility screening only until prereg freeze.

### 2016 Kaikoura, New Zealand, Mw 7.8
**Why useful:** exceptionally complex multi-fault rupture, long rupture duration, rich strong-motion and geodetic network, excellent test of whether a simplistic one-mode/scalar representation is correctly refused.  
**Open-data route:** GeoNet FDSN, AWS Open Data, strong-motion database, daily GNSS/Tilde, rupture-model database.  
**Role:** high-value representation-adjudication stress test.

### 2014 South Napa, California, Mw 6.0
**Why useful:** smaller shallow crustal event with dense near-field records and strong site-response contrasts.  
**Open-data route:** CESMD/COSMOS + EarthScope waveforms + USGS products.  
**Role:** source-versus-site/path qualification case.

### 2020 Puerto Rico, Mw 6.4
**Why useful:** shallow crustal sequence with dense local strong-motion coverage and a different tectonic/network setting.  
**Open-data route:** CESMD + PR seismic networks/EarthScope + USGS products.  
**Known current inventory:** CESMD lists 71 records for the 7 Jan 2020 mainshock.  
**Role:** transfer/stress-test candidate.

## 3. Auxiliary global candidates

These are scientifically valuable but may carry access friction that should be recorded rather than hidden.

### 2016 Kumamoto, Japan
- Dense K-NET/KiK-net strong motion.
- Waveform download requires free NIED user registration.
- Excellent site/source discrimination case.

### 2024 Noto Peninsula, Japan
- Dense Japanese strong-motion and GEONET coverage.
- GSI GEONET 30 s RINEX is available with access procedures for foreign researchers.
- High-sampling GNSS access is not treated as automatically free/open.
- Candidate for later external validation if access conditions remain compatible.

## 4. Open infrastructure already available

### EarthScope / NSF National Geophysical Facility
- Global FDSN station and dataselect services.
- miniSEED, SAC zip, and GeoCSV waveform return formats.
- Global Seismographic Network data are free and open.
- EarthScope 1 Hz real-time GNSS streams are available at no cost for scientific/noncommercial use; historical products must be inventoried separately.

### CESMD / COSMOS
- Strong-motion event archive and station products.
- Large-event record counts and processed products available across many U.S. and global earthquakes.
- Particularly useful for identical processing conventions across multiple events.

### GeoNet New Zealand
- FDSN waveform access.
- AWS Open Data for miniSEED, GNSS, and strong-motion products.
- Strong-motion database includes Kaikoura.
- Daily GNSS displacement series available via Tilde.
- Rupture models available for significant events.

### USGS
- FDSN event catalog.
- ShakeMap products and Atlas.
- Event metadata, source products, finite-fault products, and station summaries where available.

## 5. Expansion principle

The benchmark must maximize **scientific contrast**, not event count.

Required contrasts should eventually include:
- subduction megathrust;
- intraslab;
- shallow strike-slip;
- complex multi-fault rupture;
- moderate near-field crustal event;
- different network densities;
- different sensor mixes;
- source-rich versus site-dominated cases;
- clean single-factor synthetic cases and deliberately unclassifiable real/synthetic cases.

## 6. Data layers per event

For every candidate event, inventory independently:

1. event/source metadata;
2. strong-motion acceleration/velocity/displacement;
3. broadband seismic waveforms;
4. high-rate GNSS where genuinely available;
5. daily GNSS recovery;
6. InSAR where useful;
7. published rupture/source models;
8. published site/path characterization;
9. postseismic afterslip/viscoelastic models;
10. native field products and comparator outputs.

Absence of a layer is not exclusion by itself. It determines which scientific questions the event can test.

## 7. Provisional event-use matrix

| Event | Legacy exposed? | Strong motion | Seismic | High-rate GNSS | Daily GNSS | Recovery | Primary candidate role |
|---|---|---|---|---|---|---|---|
| Chignik 2021 | YES | strong | strong | available in published work | yes | yes | development |
| Ridgecrest 2019 | YES | exceptional | exceptional | yes | yes | yes | development / source-site challenge |
| Tohoku 2011 | YES | exceptional | exceptional | rich | rich | rich | legacy stress test only |
| Maule 2010 | YES | available | rich | published | rich | rich | legacy stress test only |
| Anchorage 2018 | NO known program exposure | 98 CESMD records | rich | inventory pending | likely | likely | fresh stress test |
| Kaikoura 2016 | NO known program exposure | rich/open | rich/open | inventory pending | open | rich | complex-rupture refusal test |
| South Napa 2014 | NO known program exposure | dense | rich | inventory pending | available regionally | published | source/site/path test |
| Puerto Rico 2020 | NO known program exposure | 71 CESMD records | rich | inventory pending | regional | sequence available | transfer test |
| Kumamoto 2016 | NO known program exposure | exceptional | rich | GEONET context | GEONET | available | auxiliary global test |
| Noto 2024 | NO known program exposure | exceptional | rich | access-dependent | GEONET | ongoing literature | future external test |

## 8. Immediate machine work

Before inspecting any new-event modal or chi outcome:

1. probe open endpoints and data volume for Anchorage, Kaikoura, South Napa, and Puerto Rico;
2. produce a machine-readable event/data-layer inventory;
3. classify ACCESSIBLE / REGISTRATION_REQUIRED / BLOCKED / MISSING for every layer;
4. preserve legacy-exposure flags;
5. identify events capable of testing each candidate prereg question;
6. do not estimate chi or choose thresholds from these fresh events;
7. select the development/stress/holdout allocation only after novelty and preregistration structure closes.

## 9. Why this matters for the tool

A broadly useful field tool should fail if it works only on Chignik.

The eventual claim must be something closer to:

> A frozen representation-adjudication architecture produces calibrated, interpretable decisions across heterogeneous earthquakes, networks, and sensor combinations, and knows when the requested representation is not scientifically supported.

That claim requires a multi-event suite by construction.
