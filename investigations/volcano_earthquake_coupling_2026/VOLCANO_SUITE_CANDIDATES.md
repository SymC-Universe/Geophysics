# Volcano Benchmark Candidate Suite

**Status:** exploratory inventory, NOT FROZEN  
**Date:** 2026-09-27  
**Purpose:** Build volcano cases alongside the multi-earthquake benchmark before selecting any confirmatory holdouts.

## Event-role firewall

### Legacy-exposed / development-only

- **Kilauea**: prior SymC work used Kilauea as a volcanic case. All Kilauea events are conservatively treated as legacy-exposed for confirmation purposes.
- **Mount St. Helens**: prior exploratory SymC volcano work exists. Development-only.

### Fresh candidate cases

#### Mauna Loa 2022, Hawaii
- decade-scale precursory seismic unrest;
- inflation/deformation;
- clear transition to eruption;
- rich HVO/EarthScope public monitoring record;
- useful for pre-eruptive state progression without relying on Kilauea.

#### Redoubt 2009, Alaska
- ~6 months of precursory seismic activity;
- swarms, tremor, explosions, dome growth, lahars;
- open USGS/AVO earthquake catalog and public seismic-network lineage;
- geodetic response was complex and station-limited, which is useful for NEED_MORE_INFORMATION behavior.

#### Whakaari / White Island 2019, New Zealand
- sudden explosive eruption;
- GeoNet seismic/infrasound monitoring;
- deformation and volcano-monitoring context;
- strong counterpoint to slowly escalating unrest systems.

#### Taupo 2022-2023 unrest, New Zealand
- >1700 detected earthquakes;
- deformation and seismic network;
- M_L 5.7 event;
- no eruption during the unrest episode;
- critical negative/control case against eruption-selected analysis.

#### Ruapehu unrest/eruption episodes, New Zealand
- repeated unrest/eruption cycles;
- strong GeoNet seismic, acoustic and deformation coverage;
- candidate repeated-measures system.

#### Tongariro 2012, New Zealand
- eruption following long quiescence;
- GeoNet seismic and deformation context;
- candidate abrupt-regime test.

#### Bardarbunga-Holuhraun 2014-2015, Iceland
- extraordinary seismic swarm/dike propagation;
- major effusive eruption and caldera deformation;
- strong test of coupled deformation-seismic-volcanic representation;
- open-data route to be verified.

#### Reykjanes/Fagradalsfjall 2021-2024, Iceland
- repeated intrusions, swarms, deformation, eruptions;
- natural repeated perturbation/recovery laboratory;
- open-data route to be verified.

#### Campi Flegrei 2010s-2020s unrest, Italy
- long-term bradyseism, seismicity and degassing;
- no simple eruption endpoint;
- valuable long-unrest control;
- open-data route to be verified.

## Required volcano contrasts

The benchmark should eventually include:
- effusive basaltic eruption;
- explosive arc eruption;
- caldera unrest without eruption;
- hydrothermal-dominated unrest;
- long precursor versus short precursor;
- open versus closed degassing where independently classified;
- earthquake-trigger candidate versus no-trigger case;
- deformation-rich versus deformation-poor case;
- repeated episodes from the same volcano.

## Data layers per volcano

1. eruption chronology and GVP labels;
2. local VT/LF seismicity;
3. continuous seismic/tremor;
4. RSAM/SSAM where available;
5. infrasound;
6. GNSS deformation;
7. tilt;
8. InSAR;
9. gas flux/composition;
10. thermal/hydrothermal observations;
11. eruption/extrusion rate;
12. regional tectonic earthquakes;
13. published magma-storage/plumbing models;
14. alert-level or observatory state labels as external operational comparators.

## Initial development allocation

- Kilauea: legacy development.
- Mount St. Helens: legacy development.
- Mauna Loa 2022: fresh exploratory candidate, do not expose confirmatory endpoints until role is frozen.
- Redoubt 2009: fresh exploratory candidate.
- Taupo 2022-2023: fresh negative/unrest control candidate.
- Whakaari 2019: fresh abrupt-eruption candidate.

No fresh event is a confirmatory holdout until the preregistration is frozen.
