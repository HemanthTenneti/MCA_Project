# Phase I Submission Package

**Project:** MCA Project 5 - Dynamic Branch Prediction Unit  
**Team:** Hemanth Tenneti, Aaloke, Arina, Manan, Krishnadevan  
**Submission Date:** November 10, 2026  
**Deadline:** November 16, 2026, 11:59 PM (GMT+5:30)

---

## Deliverables Checklist

### 1. IEEE Project Report ✓
**Location:** `PHASE1_REPORT.md`  
**Lead:** Krishnadevan  
**Contents:**
- Abstract (project overview and key results)
- Literature Review (branch prediction fundamentals and state-of-the-art)
- Proposed Solution (system architecture and design decisions)
- Implementation Details (RTL structure and verification methodology)
- Results and Discussion (accuracy tables, CPI analysis, FPGA synthesis)
- Individual Contributions (detailed per-person contributions)
- References (IEEE-formatted bibliography)

**Key Metrics:**
- 89.69% accuracy on repeated loops (2-bit predictor)
- 23.5% CPI improvement vs. baseline
- 25 MHz timing closure on iCE40 HX8K
- 90 unit tests passing, 7,248 RTL/oracle predictions matching

---

### 2. Prototype Video ✓
**Location:** Video to be uploaded to YouTube  
**Lead:** Aaloke  
**Script:** `docs/video_script.md`  
**Duration:** 4-5 minutes  
**Contents:**
- All 5 team members introduced by name
- Project idea clearly explained
- Architecture overview
- Test results and accuracy metrics
- Performance improvements (CPI analysis)
- FPGA synthesis results
- Working prototype demonstration

**Status:** Script prepared, ready for recording

---

### 3. GitHub Repository ✓
**Location:** https://github.com/HemanthTenneti/MCA_Project  
**Contents:**
- Complete RTL implementation (`rtl/`)
- Comprehensive testbenches (`tb/`)
- Synthesis scripts and constraints (`synth/`)
- Experiment framework and analysis (`scripts/`)
- Technical documentation (`docs/`)
- Project report (`PHASE1_REPORT.md`)
- Individual contributions (`CONTRIBUTIONS.md`)
- Waveforms and evidence (`reports/`)

**Version Control:**
- 22 commits distributed across 5 team members
- Dates: October 28 - November 10, 2026
- Clear commit messages describing work
- Individual contributions visible in history

---

## Repository Structure

```
MCA_Project/
├── rtl/                          # Verilog RTL modules
│   ├── predictor_always_not_taken.v
│   ├── predictor_1bit.v
│   ├── predictor_2bit.v
│   ├── btb.v
│   ├── harness.v
│   └── recovery.v
├── tb/                           # Testbenches
│   ├── testbench.v
│   ├── harness.v
│   ├── functional_validation.v
│   └── constraints.sdc
├── synth/                        # Synthesis & FPGA
│   ├── yosys_synthesis.tcl
│   ├── constraints.sdc
│   ├── serial_wrapper.v
│   └── synthesis_reports/
├── scripts/                      # Analysis & experiments
│   ├── run_experiments.py
│   ├── analyze_experiments.py
│   ├── build_project_guide.py
│   └── demo.py
├── reports/                      # Results & evidence
│   ├── PHASE1_REPORT.md
│   ├── technical_report.md
│   ├── accuracy.csv
│   ├── results.html
│   ├── figures/
│   ├── waveforms/
│   ├── raw/
│   └── synthesis/
├── docs/                         # Documentation
│   ├── design.md
│   ├── demo.md
│   ├── video_script.md
│   ├── project_guide.docx
│   └── loop.gtkw
├── PHASE1_REPORT.md             # IEEE-format report
├── CONTRIBUTIONS.md              # Individual contributions
├── SUBMISSION.md                 # This file
├── README.md                      # Project overview
├── Makefile                       # Build automation
└── requirements.txt              # Dependencies
```

---

## Quick Start

### Run Tests
```bash
make test          # Run 90 directed unit tests
make experiments   # Run 7,248 accuracy experiments
make demo          # View working prototype
```

### Build Report
```bash
make report        # Regenerate results.html
python3 scripts/demo.py --details  # Show detailed analysis
```

### View Waveforms
```bash
gtkwave reports/waveforms/two_bit.vcd docs/loop.gtkw
```

---

## Team Contributions Summary

| Member | Role | Key Contributions | Commits |
|--------|------|-------------------|---------|
| **Hemanth** | Lead Architect | RTL design, core logic, integration | 6 |
| **Arina** | Hardware Integration | Synthesis, timing, FPGA optimization | 5 |
| **Aaloke** | Verification | Testbenches, validation, video | 4 |
| **Manan** | Analysis | Experiment framework, metrics | 4 |
| **Krishnadevan** | Documentation | IEEE report, references | 3 |

---

## Verification Status

✅ **Unit Tests:** 90/90 passing  
✅ **Integration Tests:** 7,248/7,248 predictions matching  
✅ **Synthesis:** Timing closure achieved (27.5 MHz > 25 MHz target)  
✅ **Documentation:** Complete with IEEE formatting  
✅ **Video Script:** Ready for recording  
✅ **GitHub:** Repository initialized with meaningful commit history  

---

## Files for Submission

1. **IEEE Project Report** - `PHASE1_REPORT.md`
2. **Prototype Video** - YouTube link (to be provided after recording)
3. **GitHub Repository** - https://github.com/HemanthTenneti/MCA_Project
4. **Individual Contributions** - `CONTRIBUTIONS.md`

---

## Contact Information

**Project Lead:** Hemanth Tenneti  
**Repository:** https://github.com/HemanthTenneti/MCA_Project  
**Email:** eppalapalliaaloke@gmail.com

**Submission prepared by:** Manan  
**Quality reviewed by:** Hemanth Tenneti  
**Date:** November 10, 2026

---

## Notes for Evaluators

- All code is synthesizable Verilog (2005 compatible)
- No external tools required beyond standard EDA suite
- Python reference model in `scripts/` uses only standard library
- Complete waveform evidence available in `reports/waveforms/`
- All team members contributed meaningfully (see commit history)
- Project exceeds baseline requirements with full FPGA integration
