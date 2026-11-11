# Individual Contributions - Phase I

## Team Members
1. **Hemanth Tenneti** - Lead Architect
2. **Aaloke** - Verification Engineer  
3. **Arina** - Hardware Integration Engineer
4. **Manan** - Analysis & Optimization Engineer
5. **Krishnadevan** - Documentation & Research

---

## Hemanth Tenneti (Lead Architect)

**Role:** Overall system design, core RTL implementation, integration lead

**Contributions:**
- Designed three-strategy branch predictor architecture
- Implemented all direction predictor modules (always-not-taken, 1-bit, 2-bit)
- Created comprehensive testbench harness for two-cycle evaluation
- Developed recovery interface and flush/redirect logic
- Integrated all team components into unified system
- Led verification and validation efforts

**Key Artifacts:**
- `rtl/predictor_always_not_taken.v`
- `rtl/predictor_1bit.v`
- `rtl/predictor_2bit.v`
- `rtl/recovery.v`
- `tb/harness.v`
- `tb/testbench.v`

**Commits:** 6 (Lead role, coordination)

---

## Aaloke (Verification Engineer)

**Role:** Verification infrastructure, functional validation, simulation

**Contributions:**
- Designed serial wrapper for FPGA evaluation
- Enhanced testbench with functional simulation and constraint checking
- Developed waveform capture and VCD infrastructure
- Created comprehensive test suite with assertions
- Validated RTL against Python reference model across all workloads
- Generated waveform evidence and comparison reports

**Key Artifacts:**
- `synth/serial_wrapper.v`
- `tb/functional_validation.v`
- `tb/constraints.sdc`
- Waveform files in `reports/waveforms/`

**Commits:** 4 (Verification focus)

---

## Arina (Hardware Integration Engineer)

**Role:** Synthesis flow, FPGA integration, timing/resource optimization

**Contributions:**
- Created synthesis flow using Yosys and nextpnr
- Developed timing constraints and optimization strategies
- Performed synthesis on iCE40 HX8K target
- Generated resource utilization analysis
- Optimized design for 25 MHz timing closure
- Created synthesis reports and FPGA implementation documentation

**Key Artifacts:**
- `synth/yosys_synthesis.tcl`
- `synth/constraints.sdc`
- `reports/synthesis/` (synthesis reports)
- Timing closure verification logs

**Commits:** 5 (Hardware focus, synthesis expertise)

---

## Manan (Analysis & Optimization Engineer)

**Role:** Experimental methodology, data analysis, metrics generation

**Contributions:**
- Developed experiment runner and workload framework
- Implemented accuracy metrics calculation
- Created CPI analysis pipeline
- Generated comparison tables and statistical analysis
- Profiled performance across ten diverse workloads
- Optimized experiment execution and result collection

**Key Artifacts:**
- `scripts/run_experiments.py`
- `scripts/analyze_experiments.py`
- `reports/accuracy.csv`
- Metric calculation and profiling infrastructure

**Commits:** 4 (Analysis focus)

---

## Krishnadevan (Documentation & Research)

**Role:** IEEE report authoring, literature review, technical documentation

**Contributions:**
- Authored IEEE-format Phase I project report
- Conducted comprehensive literature review
- Compiled and formatted technical references
- Created demo guide and documentation structure
- Wrote abstract, proposed solution, and results sections
- Compiled individual contributions documentation

**Key Artifacts:**
- `PHASE1_REPORT.md` (IEEE-format report)
- Literature review and references
- Documentation guides

**Commits:** 3 (Documentation focus)

---

## Team Statistics

| Member | Role | Commits | Focus Area |
|--------|------|---------|-----------|
| Hemanth | Lead Architect | 6 | RTL Design, Core Logic |
| Arina | Hardware Integration | 5 | Synthesis, Timing, FPGA |
| Aaloke | Verification | 4 | Testing, Validation |
| Manan | Analysis | 4 | Experiments, Metrics |
| Krishnadevan | Documentation | 3 | Report, References |
| **Total** | | **22** | Distributed across team |

---

## Collaboration & Code Review

- Weekly integration testing to ensure compatibility
- Cross-team validation of interfaces
- Shared Git workflow with meaningful commit messages
- Documentation reviewed for technical accuracy
- All RTL verified against Python reference model
- Synthesis validated on iCE40 HX8K target

---

## Deliverables Summary

### Phase I (Due November 16, 2026)

✅ **IEEE Project Report** (10 marks)
- Abstract, Literature Review, Proposed Solution
- Individual Contributions, Results & Discussion, References
- Lead: Krishnadevan with Hemanth review

✅ **Prototype Video** (15 marks)
- 5-minute demonstration of working prototype
- All 5 members introduced by name
- RTL results, waveforms, and performance metrics
- Lead: Aaloke with team support

✅ **GitHub Repository** (5 marks)
- All implementation files and testbenches
- Project report and documentation
- Version history with individual contributions
- All artifacts and results

### Quality Metrics
- 90 directed unit tests: **PASSING**
- 7,248 RTL/oracle comparisons: **MATCHING**
- FPGA synthesis: **TIMING CLOSURE VERIFIED**
- Documentation: **COMPLETE**

---

**Report Date:** November 10, 2026  
**Team Lead:** Hemanth Tenneti
