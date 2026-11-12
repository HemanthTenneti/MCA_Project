# Individual Contributions - Phase I

Each member's contributions below follow the repository commit history (21 commits).

## Team Members
1. **Hemanth Tenneti** - Lead Architect
2. **Aaloke** - Verification Engineer
3. **Arina Ali** - Hardware Integration Engineer
4. **Manan** - Analysis and Optimization Engineer
5. **Krishnadevan** - Documentation and Research

---

## Hemanth Tenneti (Lead Architect)

**Role:** Overall system design, core RTL, architecture documentation

**Contributions:**
- Created the initial project structure and the Python reference model
- Implemented the top-level branch predictor and the direction predictors (always-not-taken, 1-bit, 2-bit)
- Implemented branch recovery with flush/redirect logic
- Wrote the architecture and design documentation
- Added the project guide builder and finalized `.gitignore`

**Key Artifacts:**
- `rtl/branch_predictor.v`
- `rtl/direction_predictor.v`
- `rtl/branch_recovery.v`
- `scripts/reference_model.py`
- `ARCHITECTURE.md`, `docs/design.md`
- `scripts/build_project_guide.py`, `docs/project_guide.docx`, `output/pdf/project_guide.pdf`

**Commits:** 4

---

## Aaloke (Verification Engineer)

**Role:** Testbenches, functional validation, waveforms, video script

**Contributions:**
- Wrote the unit and trace testbenches and the project test runner
- Wrote the functional validation testbench and the test plan
- Produced verification results, VCD waveforms and test metrics
- Wrote the prototype video script

**Key Artifacts:**
- `tb/tb_unit.v`, `tb/tb_trace.v`, `scripts/test_project.py`
- `tb/functional_validation.v`, `TESTPLAN.md`
- `VERIFICATION_RESULTS.md`, `reports/verification.json`, `reports/validation.log`, `reports/unit_checks.json`
- `reports/waveforms/`, `docs/loop.gtkw`
- `docs/video_script.md`

**Commits:** 4

---

## Arina Ali (Hardware Integration Engineer)

**Role:** Branch target buffer, build flow, synthesis and timing, Phase I report

**Contributions:**
- Implemented the branch target buffer and the build Makefile
- Built the Yosys/nextpnr synthesis flow
- Added timing constraints, the timing harness and synthesis reports
- Wrote the Phase I report, build targets and delivery checklist

**Key Artifacts:**
- `rtl/branch_target_buffer.v`, `Makefile`
- `scripts/synthesize.py`, `synth/yosys_synthesis.tcl`
- `synth/constraints.sdc`, `synth/timing_top.v`, `tb/tb_timing_top.v`
- `reports/synthesis/`
- `PHASE1_REPORT.md`, `Makefile.phase1`, `DELIVERY_CHECKLIST.md`

**Commits:** 4

---

## Manan (Analysis and Optimization Engineer)

**Role:** Demo, readable results, README and submission package

**Contributions:**
- Wrote the demo walkthrough script and guide
- Built the readable results report, presentation and result screenshots
- Rewrote the README for submission
- Prepared the Phase I submission package and quick start guide

**Key Artifacts:**
- `docs/demo.md`, `scripts/demo.py`
- `scripts/build_readable_report.py`, `scripts/presentation.py`, `reports/results.html`
- `output/playwright/results-desktop.png`, `output/playwright/results-mobile.png`
- `README.md`, `README_PHASE1.md`, `SUBMISSION.md`

**Commits:** 4

---

## Krishnadevan (Documentation and Research)

**Role:** Workloads, experiments, analysis, diagrams and technical report

**Contributions:**
- Wrote the branch trace generator and the workload traces
- Wrote the experiment runner and collected the raw results
- Built the experiment analysis pipeline and result figures (accuracy, CPI)
- Wrote the technical report builder and this contributions document
- Added the architecture and behaviour diagrams to the report figures

**Key Artifacts:**
- `scripts/generate_traces.py`, `traces/`
- `scripts/run_experiments.py`, `reports/raw/`
- `scripts/analyze_experiments.py`, `reports/accuracy.csv`, `reports/figures/`
- `reports/figures/datapath_microarchitecture.png`, `reports/figures/pipeline_recovery_integration.png`
- `reports/figures/bht_1bit_state_transitions.png`, `reports/figures/loop_exit_comparison.png`
- `scripts/build_report.py`, `reports/technical_report.md`
- `CONTRIBUTIONS.md`

**Commits:** 5

---

## Team Statistics

| Member | Role | Commits | Focus Area |
|--------|------|---------|-----------|
| Hemanth | Lead Architect | 4 | Core RTL, architecture, reference model |
| Aaloke | Verification | 4 | Testbenches, validation, waveforms |
| Arina | Hardware Integration | 4 | BTB, synthesis, timing, Phase I report |
| Manan | Analysis and Optimization | 4 | Demo, results report, README, submission |
| Krishnadevan | Documentation and Research | 5 | Traces, experiments, analysis, diagrams, technical report |
| **Total** | | **21** | |

---

**Team Lead:** Hemanth Tenneti
