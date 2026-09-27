# Seismology Stability Tool: Conglomeration Matrix and Question Ladder

**Status:** P0-N / A0 working record, NOT FROZEN  
**Date:** 2026-09-27  
**Purpose:** Convert prior-art conglomeration into sharper research questions and a defensible preregistration target. This document is not a novelty claim.

## 1. What is already occupied

| Candidate idea | Established prior art | Current disposition |
|---|---|---|
| chi = gamma/(2 omega0) as a new seismic quantity | ordinary second-order damping ratio zeta; Q/damping relations | REFUSE novelty |
| generic fault-stability parameter | rate-and-state friction, critical stiffness, Coulomb/stress metrics, fault-instability coefficients | REFUSE novelty |
| generic earthquake state variable | nowcasting, state-space/data-assimilation, latent fault-state estimation | REFUSE novelty |
| automatic mode/pole identification | OMA, SSI/FDD, Prony, matrix pencil, Bayesian model validity, stabilization diagrams, DMD | REFUSE novelty |
| automatic source characterization | SourceSpec, W-phase/source inversions, operational network pipelines | REFUSE novelty |
| automatic ground-motion processing | USGS gmprocess and related production workflows | REFUSE novelty |
| generic source/path/site separation | spectral decomposition, mixed-effects residual models, site-response methods | REFUSE novelty |
| generic seismic + GNSS fusion | seismogeodesy, joint inversion, high-rate GNSS/strong-motion fusion | REFUSE novelty |
| generic transferable waveform representation | SeisBench ecosystem, U-Trans, SeisMoLLM and other foundation models | REFUSE novelty |
| generic earthquake/fault digital twin | fault-volume twins, earthquake-cycle reduced-order/data-assimilation twins, operational DT programs | REFUSE novelty |
| generic forecast testing | CSEP/pyCSEP and prospective/retrospective forecast experiments | REFUSE novelty |

## 2. Residual candidate capabilities

These remain questions, not novelty claims.

| Candidate capability | What is potentially different | Strongest prior-art challenge | What must be shown |
|---|---|---|---|
| Cross-physics representation adjudication | choose/refuse among physically different model classes rather than optimize one class | OMA model selection; automated source-model selection; analyst workflows | lower model-selection error or better downstream decisions on untouched cases |
| Source-versus-site/path adjudication | decide whether extracted structure is event/source-consistent rather than local/path/instrumental | source/path/site decomposition; station residuals; spectral ratios | recover known source-consistent structure and refuse local artifacts |
| Cross-sensor validity map | state which physical quantities are substitutable across sensors, bandwidths and regimes | seismogeodesy and multimodal fusion | calibrated equivalence/non-equivalence with explicit limits |
| Local/modal-to-network architecture | preserve component/modal contradictions and network organization rather than collapse to one parameter | OMA, network coherence, graph/latent methods | incremental information beyond modes or coherence separately |
| Fast-event to slow-recovery linkage | test whether rupture organization carries independent information about postseismic recovery | joint coseismic/postseismic inversion, earthquake-cycle models, digital twins | out-of-event predictive/explanatory gain beyond standard source descriptors |
| Explicit refusal provenance | make NOT_APPLICABLE / NEED_MORE_INFORMATION a reproducible scientific output across model classes | Bayesian evidence/model selection, QC frameworks | refusal accuracy and utility across known-bad cases and holdouts |
| Analysis triage | identify when standard products are sufficient versus when expensive inversion is warranted | network analyst practice, automated source-solution selection | reduced computation/analyst burden with no unacceptable loss of scientific accuracy |

## 3. Candidate field problems

### F1. Representation triage after an earthquake

**Problem:** Analysts have many valid tools, but the appropriate physical representation varies by event, station, bandwidth and objective.

**Question:** Can a pre-specified engine identify whether the data are adequately described by standard source parameters, site/path response, a single damped factor, multiple/nonstationary factors, network-only organization, monotonic recovery, or an indeterminate state?

**Broad-use value if successful:** a common front-end that routes data to the right analysis rather than replacing native tools.

**Primary failure mode:** it merely reimplements ordinary model selection without better decisions.

### F2. Source-consistent versus local structure

**Problem:** A spectral peak, pole or damping estimate observed at a station can reflect the source, path, site or instrument.

**Question:** Can the engine identify event-wide structure that survives multi-station source/path/site controls and refuse features confined to local response?

**Broad-use value if successful:** prevents local resonance or processing artifacts from being promoted to source/fault interpretation.

**Primary failure mode:** source/path/site decomposition already solves the task equally well.

### F3. Cross-sensor equivalence

**Problem:** strong-motion, broadband seismic and high-rate GNSS overlap in some physical bandwidths but are not universally interchangeable.

**Question:** Can the engine learn or derive a validity map that states which physical quantities agree across sensors and when substitution fails?

**Broad-use value if successful:** expands usable network coverage while retaining explicit limits.

**Primary failure mode:** ordinary seismogeodetic fusion already captures all useful information.

### F4. Event-to-recovery architecture

**Problem:** rupture characterization and postseismic recovery are usually treated with different tools and timescales.

**Question:** Does independently measured fast-event organization contain reproducible information about subsequent recovery direction, coherence, timescale class, or afterslip/viscoelastic mixture beyond magnitude, mechanism, source duration, stress drop, slip model and geometry?

**Broad-use value if successful:** rapid post-event triage or initialization of recovery analysis.

**Primary failure mode:** no incremental relationship survives event holdouts.

### F5. Forecasting / precursor detection

**Status:** DEFERRED.

This would require CSEP-style evaluation, extreme leakage control, rare-event calibration, false-alarm accounting and prospective holdouts. It is not needed for the tool to be valuable and should not be used as the first preregistration target.

## 4. Better preregistration questions

### Q1. Representation class
For an input meeting fixed quality criteria, which representation class is supported by pre-specified evidence and which alternatives are refused?

### Q2. Attribution
Is the admitted structure source-consistent, site/path-local, instrument-specific, or unresolved?

### Q3. Sensor validity
Does the same physical quantity agree across independent sensor classes within pre-specified uncertainty and bandwidth limits?

### Q4. Incremental value
Does the architecture improve a pre-specified downstream scientific decision relative to the strongest native comparator?

### Q5. Transfer
Does that improvement survive event, station, region and tectonic holdouts without threshold/model retuning?

### Q6. Parsimony
If a standard source parameter, Q/damping ratio, coherence metric, PCA/ICA factor, or native recovery model performs equivalently, is the extra architecture retired for that task?

### Q7. Failure information
When the engine refuses a representation, is the refusal itself calibrated and informative rather than merely missing output?

### Q8. Operational practicality
Can the same frozen workflow run on standard public formats with bounded analyst configuration and produce reproducible machine-readable provenance?

## 5. Candidate preregistration hierarchy

The first preregistration should not attempt all questions at once.

**Foundation gate:** parser/QC/known-truth model-class/refusal performance.

**Prereg 1 candidate:** source-versus-site/path representation adjudication across multiple real earthquakes, with Chignik used only for development.

**Prereg 2 candidate:** cross-sensor validity on collocated/near-collocated strong-motion and high-rate GNSS.

**Prereg 3 candidate:** incremental event-to-recovery linkage, only after independent fast and slow representations are qualified.

**Forecasting gate:** only if the diagnostic architecture later produces a clearly defined prospective forecast quantity.

The numbering above is a dependency order, not a claim ranking.

## 6. Comparator stack

The tool should consume or benchmark against native methods rather than hiding them.

- **Processing/QC:** USGS gmprocess or equivalent transparent processing.
- **Source parameters:** SourceSpec or equivalent Brune/source-spectrum workflow.
- **Modal/system identification:** SSI/FDD, Prony/matrix pencil and a modern robust pole method.
- **Source/path/site attribution:** station residual/spectral decomposition and mixed-effects approaches.
- **Simple network structure:** correlation/coherence and PCA/ICA/SVD.
- **Representation learning:** a current seismic foundation-model baseline where the downstream task permits a fair comparison.
- **Recovery:** standard logarithmic/exponential postseismic models and, where available, published afterslip/viscoelastic inversion.
- **Forecast evaluation:** pyCSEP only if a forecasting claim is eventually introduced.

## 7. Tool-design constraints implied by broad use

A field-worthy implementation should eventually:
- accept standard seismic/geodetic formats or documented conversions;
- expose every preprocessing/model-selection step;
- preserve native units and native parameter names;
- return machine-readable uncertainty and refusal provenance;
- separate observation, representation and interpretation layers;
- allow native comparator outputs to be inspected beside the proposed architecture;
- support batch multi-event analysis;
- run without hidden hand tuning;
- make the simplest sufficient representation a valid successful outcome;
- make NOT_APPLICABLE a first-class result;
- be reproducible through the public repository workflow;
- avoid requiring a proprietary model or unavailable dataset for core operation.

## 8. Current novelty posture

The broad mathematical pieces are largely prior art. The open possibility is a **specific integration and decision architecture** whose scientific value is demonstrated experimentally.

Therefore the novelty question is no longer:

> Is chi novel in seismology?

It is:

> Can a transparent, representation-aware decision layer improve how seismologists decide what physical description is justified, what is local versus system-wide, what can be compared across sensors/timescales, and what deeper analysis is warranted, while refusing unsupported reductions and outperforming existing native decision workflows on untouched cases?

That is the question the next prior-art pass must try to kill.
