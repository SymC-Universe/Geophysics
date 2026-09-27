# Seismology Stability Tool: Novelty and Preregistration Foundation

**Status:** P0-N / A0 working draft, NOT FROZEN  
**Date:** 2026-09-27  
**GOM:** v0.8.8 active baseline  
**Program goal:** Develop a scientifically defensible, broadly usable seismology/geodesy tool whose value is demonstrated by incremental utility against native field methods, not by recovery of any legacy SymC result.

## 1. Problem statement

The target is not “prove chi in earthquakes.” The target is to determine whether a reusable stability-state diagnostic can solve an unmet field problem.

Current seismology/geodesy has strong specialized tools for:
- earthquake early warning and rapid source characterization;
- operational earthquake forecasting and prospective forecast testing;
- seismic/GNSS transient detection;
- high-rate GNSS and seismogeodetic waveform reconstruction;
- spectral attenuation, quality factor Q, damping and resonance analysis;
- rupture inversion and joint seismic-geodetic inversion;
- postseismic afterslip/viscoelastic modeling;
- rate-and-state friction stability modeling;
- stress inversion and fault-instability coefficients;
- machine-learning monitoring, phase picking, detection and catalog building;
- earthquake-cycle data assimilation and latent-state estimation.

A new tool must therefore add something beyond these capabilities.

## 2. Novelty boundaries already established

### 2.1 Scalar chi is not a novel mathematical quantity by itself

For an admitted second-order factor,

\[
x'' + \gamma x' + \omega_0^2 x = 0,
\qquad
\chi = \frac{\gamma}{2\omega_0}.
\]

This is mathematically the ordinary dimensionless damping ratio \(\zeta\). Seismology, earthquake engineering and geotechnical dynamics already use damping ratio and its relationship to quality factor \(Q\), commonly \(\zeta \approx 1/(2Q)\) under the relevant assumptions.

**Consequence:** no novelty claim may rest on the scalar formula alone.

Relevant prior art:
- Mitrofanov & Priimenko, *Prony Filtering of Seismic Data*, Acta Geophysica, DOI 10.1515/acgeo-2015-0012.
- Lai et al. lineage on material damping / Q and causal attenuation-dispersion relations.
- Standard seismometer and SDOF response theory uses dimensionless damping directly.

### 2.2 “Fault stability” is already an established concept with multiple native parameters

Rate-and-state friction uses parameters such as \(a-b\), state variable \(\theta\), critical slip distance \(D_c\), and critical stiffness relationships to distinguish stable/unstable slip.

Stress-inversion literature also uses dimensionless fault-instability coefficients that measure proximity/orientation to failure under a stress field.

**Consequence:** the proposed tool must never present chi as a replacement name for RSF stability, critical stiffness, Coulomb proximity, or an existing instability coefficient.

Relevant prior art:
- Marone, 1998, *Laboratory-Derived Friction Laws and Their Application to Seismic Faulting*, DOI 10.1146/annurev.earth.26.1.643.
- Vavrycuk / Martinez-Garzon stress-inversion lineage using fault instability coefficient I.

### 2.3 Generic “earthquake state variables” are not novel

Earthquake nowcasting literature already constructs proxy state-variable time series from seismicity and evaluates threshold skill. Data-assimilation literature estimates latent fault stress/strength states. GNSS transient-detection literature uses PCA/ICA, optimization and ML.

**Consequence:** novelty cannot rest on merely calling an output a state variable.

Examples:
- Rundle et al., earthquake nowcasting / state-variable methods, DOI 10.1029/2021EA001757 and 10.1029/2022EA002343.
- Ensemble and particle-filter earthquake-cycle state estimation.
- PICCA slow-slip detection, DOI 10.3389/feart.2021.788054.

### 2.4 Cross-sensor and cross-timescale integration already exists

Seismogeodesy fuses strong-motion and GNSS information. Joint inversions combine seismic and geodetic observations. Physics-based work has explicitly bridged coseismic rupture and postseismic slip.

**Consequence:** simply combining seismic + GNSS is not novel.

Examples:
- Dittmann et al., high-rate GNSS strong-motion detection, DOI 10.1029/2022JB024854.
- Chignik work showing near-interchangeability of GNSS and strong-motion velocity below about 0.25 Hz.
- *Bridging time scales of faulting: From coseismic to postseismic slip of the 2014 South Napa earthquake*.
- Postseismic GNSS data assimilation, DOI 10.1186/s40623-020-01293-0.

## 3. Provisional residual novelty space

The literature search has not yet established that the following combination exists as a standard reusable field tool. These are candidate novelty classes, NOT claims of novelty.

### N1. Representation-admission and refusal architecture

A tool that does not assume every dataset supports a scalar state.

It would:
1. start from native observables;
2. test component, modal and system representations;
3. admit scalar damping coordinates only where a licensed second-order factor exists;
4. return explicit NOT_APPLICABLE / refusal states where scalar reduction fails;
5. propagate the reason for refusal as scientific information.

Potential value: prevents attractive but invalid reduction of heterogeneous geophysical data.

### N2. Local/modal-to-system stability architecture

Rather than one number, reconstruct:
- native component behavior;
- reproducible modal factors where they exist;
- local/modal damping coordinates where licensed;
- coupling and spatial organization;
- system-level architecture \(\Chi\);
- uncertainty, heterogeneity and refusal states.

Potential value: an interpretable intermediate layer between raw signals and full physics-based inversions.

### N3. Cross-timescale state linkage

Test whether fast rupture dynamics and slower recovery organization carry reproducible joint information across events.

This is distinct from merely fitting both phases. The question is whether a compact, transferable relation exists between:
- rupture modal/pole organization;
- cross-station coherence/heterogeneity;
- postseismic recovery direction, rate, mechanism mixture or organization.

Potential value: bridge event-scale dynamic behavior and recovery characterization without pretending that one timescale is the other.

### N4. Cross-sensor comparable diagnostic

A useful field tool should determine whether equivalent physical information can be recovered from:
- strong-motion velocity/displacement;
- high-rate GNSS;
- broadband seismic records;
- lower-rate GNSS recovery data where applicable.

The tool must expose when sensor substitution is valid and when it is not.

Potential value: broaden usable station coverage and permit common diagnostic outputs from heterogeneous networks.

### N5. Incremental-value / triage layer

The tool may be most useful as a diagnostic or triage layer rather than a forecast engine.

Candidate role:
- characterize whether an event/system response is single-mode, multimode, coherent, heterogeneous, site-local, recovery-dominated, or unclassifiable;
- prioritize which events/stations merit detailed rupture, attenuation, afterslip or viscoelastic inversion;
- provide standardized comparison across events without replacing detailed native models.

## 4. Problems the tool should attempt to solve

### P1. Representation problem
Given a multichannel earthquake dataset, what is the simplest scientifically adequate representation, and when must scalar reduction be refused?

### P2. Site-versus-system problem
Can a reproducible workflow distinguish a site-local resonance/damping feature from a rupture-wide or network-wide dynamical factor?

### P3. Cross-sensor problem
Can the same admitted physical factor be recovered within uncertainty from collocated/near-collocated strong-motion and high-rate GNSS records?

### P4. Cross-event comparability problem
Can outputs be compared across events without requiring identical sensors, amplitudes, distances or processing pipelines?

### P5. Recovery-architecture problem
Can postseismic recovery be summarized in a way that preserves coherent horizontal behavior, heterogeneous vertical behavior and multiple physical mechanisms rather than averaging them away?

### P6. Joint fast/slow problem
Does fast rupture organization contain information about subsequent recovery architecture beyond standard source/event descriptors?

### P7. Operational uncertainty problem
Can the tool produce calibrated uncertainty and explicit refusal rather than always returning a plausible-looking score?

### P8. Broad-use problem
Can an analyst run the tool on standard public waveform/geodetic products with modest configuration, obtain reproducible outputs, and understand why a representation was admitted or refused?

## 5. Candidate primary research questions for preregistration

These questions are deliberately stronger than “is chi near a particular value?”

### RQ1: Admission validity
Can a pre-specified engine correctly identify when a second-order/modal reduction is supported versus when the data are site-local, multimodal, monotonic, low-SNR or otherwise non-admissible?

### RQ2: Cross-sensor reproducibility
For collocated or near-collocated GNSS and strong-motion observations of the same event, do admitted modal frequency/damping estimates agree within pre-specified uncertainty?

### RQ3: Cross-station reproducibility
Do candidate event-scale modes recur across independent stations after accounting for travel time, orientation, site effects and instrument response?

### RQ4: Incremental information
Does the proposed architecture explain or predict an independently defined downstream quantity better than simpler native descriptors?

Candidate downstream targets include:
- postseismic recovery direction/coherence;
- recovery timescale class;
- afterslip-versus-viscoelastic mixture class where independently modeled;
- waveform duration or source-process class;
- cross-event clustering defined independently of the proposed metric.

### RQ5: Transferability
Do admission/refusal rules and any incremental relationship survive event and tectonic holdouts without retuning?

### RQ6: Parsimony
Does the full architecture outperform simpler representations sufficiently to justify its complexity? If ordinary Q/damping, PCA/coherence, PGV/PGD, source duration, or native postseismic models perform equivalently, report EQUIVALENT or SUBTRACTS.

## 6. Native comparators that must be included

The preregistration should not permit a weak comparator.

Minimum comparator families:
- standard waveform amplitude metrics: PGA, PGV, PGD;
- significant duration / energy metrics where appropriate;
- spectral peak/corner/bandwidth descriptors;
- Q or ordinary damping estimates where scientifically defined;
- waveform cross-correlation/coherence;
- PCA/ICA or similarly simple multichannel decomposition;
- Prony/matrix-pencil or another direct pole estimator if pole claims are made;
- site-response/resonance controls;
- standard GNSS transient/change-point methods for slow signals;
- standard postseismic logarithmic/exponential relaxation models;
- source magnitude, mechanism, distance and source duration as event-level controls;
- native physics-based afterslip/viscoelastic classifications when used as downstream truth;
- CSEP/ETAS-style comparator only if a forecasting claim is eventually made.

## 7. Preregistration foundation

No confirmatory freeze should be created until the novelty map closes and a specific use case is selected.

The eventual preregistration must freeze at minimum:

1. **Tool purpose**: diagnostic, classification, downstream prediction, forecasting, or another explicitly named task.
2. **Target population**: event class, magnitude range, tectonic environments, station/sensor requirements.
3. **Input hierarchy**: permitted sensors, preprocessing, instrument-response handling, units and frequency bands.
4. **Representation ladder**: native -> component -> modal -> scalar-if-licensed -> system architecture.
5. **Admission rules**: exact criteria for accepting a modal/second-order factor.
6. **Refusal rules**: exact NO_MODE / SITE_LOCAL / MULTIMODAL / LOW_SNR / MONOTONIC / FILTER_SENSITIVE / WINDOW_SENSITIVE / NOT_APPLICABLE states.
7. **Primary endpoint**: one independently defined outcome.
8. **Native comparators**: pre-specified and implemented before holdout exposure.
9. **Holdout design**: event, region and/or prospective holdouts with no retuning.
10. **Uncertainty rule**: bootstrap/posterior/ensemble method and indeterminate zone.
11. **Multiplicity control**: frequency bands, windows, modes, components and endpoints.
12. **Leakage controls**: no target-dependent window/band/model selection.
13. **Incremental-value criterion**: pre-specified margin over comparator or decision-analytic improvement.
14. **Failure consequence**: EQUIVALENT, SUBTRACTS, DOMAIN_LIMITED, scalar NOT_APPLICABLE, architecture unsupported, or claim retired.

## 8. Candidate broad-use success criteria

A broadly useful tool should eventually demonstrate all of the following, not merely a statistically interesting event:

- reproducible on public data;
- works on more than one event;
- transfers to at least one independent tectonic/event holdout;
- ingests standard formats or simple exports;
- returns interpretable results and explicit failure/refusal reasons;
- uncertainty is propagated;
- does not require hidden hand tuning;
- does not manufacture a scalar when the native system is not scalar;
- adds measurable value beyond a simple native comparator;
- remains computationally practical for routine event analysis;
- separates diagnostic/state claims from forecasting claims;
- can be independently reproduced from a repository workflow.

## 9. Chignik's role

Chignik is a discovery and engine-development event, not the final validation event.

Chignik has already contributed:
- a negative pre-event result after fair pseudo-hindcast controls;
- a coherent but heterogeneous postseismic recovery field;
- evidence that daily GNSS recovery does not license scalar chi;
- seven CESMD strong-motion station packages and 63 processed V2c waveform channels suitable for high-rate engine qualification.

Chignik must not be used both to invent and to confirm the final rules.

## 10. Current provisional hypothesis space

Do NOT freeze these yet.

### H-A: Representation utility
A pre-specified admission/refusal engine can distinguish when local/modal damping coordinates are physically meaningful and when they are not.

### H-B: Cross-sensor adequacy
Where an event-scale mode is genuine and lies in shared sensor bandwidth, its frequency/damping structure is recoverable across strong-motion and high-rate GNSS within uncertainty.

### H-C: System architecture utility
A system-level architecture built from admitted modes plus cross-station organization contains incremental information beyond scalar damping or simple coherence alone.

### H-D: Fast/slow linkage
Event-scale rupture organization contains reproducible information about independently reconstructed postseismic recovery architecture beyond standard event descriptors.

Each hypothesis can fail independently. H-D is not required for H-A through H-C to be useful.

## 11. Current decision posture

- Scalar formula novelty: **REFUSED**.
- Generic “fault stability metric” novelty: **REFUSED**.
- Generic “earthquake state variable” novelty: **REFUSED**.
- Generic seismic+GNSS fusion novelty: **REFUSED**.
- Representation/refusal architecture: **OPEN / PRIOR ART SEARCH IN PROGRESS**.
- Local/modal-to-system architecture: **OPEN / PRIOR ART SEARCH IN PROGRESS**.
- Cross-timescale joint architecture: **OPEN / PRIOR ART SEARCH IN PROGRESS**.
- Broad-use diagnostic/triage utility: **OPEN / REQUIRES BENCHMARK DEFINITION**.
- Forecasting/precursor claim: **NOT A CURRENT TARGET**.

## 12. Immediate next work

1. Complete prior-art search specifically for equivalent multi-layer state/stability architectures under alternate terminology.
2. Identify the strongest existing open-source tools that would be fair comparators.
3. Choose one primary field problem for the first preregistration rather than attempting every use case at once.
4. Build the qualification and refusal engine before outcome testing.
5. Select discovery events and untouched event/region holdouts.
6. Draft MFR-14 around incremental utility and explicit failure consequences.
7. Only after those steps freeze the preregistration.
