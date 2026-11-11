# Phase I: Dynamic Branch Prediction Unit - Quick Start

**Project Status:** ✅ Phase I Complete  
**Submission Date:** November 10, 2026  
**Deadline:** November 16, 2026, 11:59 PM GMT+5:30  

## What's Inside

This repository contains a complete branch predictor implementation with:

✅ **RTL Implementation** - Verilog modules for 3 prediction strategies  
✅ **Test Suite** - 90 unit tests + 7,248 integration tests (100% passing)  
✅ **FPGA Synthesis** - Yosys + nextpnr flow targeting iCE40 HX8K  
✅ **Analysis Framework** - Experiment runner and metrics generation  
✅ **Documentation** - IEEE report, architecture specs, verification results  

## Quick Start (30 seconds)

```bash
# View the working prototype
make demo

# Run all tests
make test
make experiments

# View synthesis results
make synthesis

# Generate comprehensive report
make report
```

## Files for Submission

### 1. IEEE Project Report
**Location:** `PHASE1_REPORT.md`

**Contains:**
- Abstract
- Literature Review (branch prediction fundamentals)
- Proposed Solution (3-strategy design)
- Implementation Details
- Results & Discussion (89.69% accuracy, 23.5% CPI improvement)
- Individual Contributions
- References

### 2. Prototype Demonstration Video
**Status:** Script ready at `docs/video_script.md`

**Will Show:**
- All 5 team members introduced
- Project architecture and design
- Test results and accuracy metrics
- Performance improvements (CPI analysis)
- FPGA synthesis results
- Working prototype with waveforms

### 3. GitHub Repository
**Link:** https://github.com/HemanthTenneti/MCA_Project

**Includes:**
- 22 commits across 5 team members (Oct 28 - Nov 10)
- Complete RTL, testbenches, scripts
- Technical reports and documentation
- Waveforms and evidence
- Individual contributions tracked in commit history

## Key Results

| Metric | Result |
|--------|--------|
| **Unit Tests** | 90/90 passing |
| **Integration Tests** | 7,248/7,248 matching reference |
| **Accuracy (2-bit on loops)** | **89.69%** |
| **CPI Improvement** | **23.5%** (vs. baseline) |
| **FPGA Timing** | **27.5 MHz** (target: 25 MHz) |
| **Resource Usage** | 840 / 7,680 cells (10.9%) |

## Team Contributions

| Member | Role | Commits |
|--------|------|---------|
| Hemanth | Lead Architect | 6 |
| Arina | Hardware Integration | 5 |
| Aaloke | Verification | 4 |
| Manan | Analysis | 4 |
| Krishnadevan | Documentation | 3 |

**Total:** 22 commits distributed across team

## Documentation Map

```
Repository Structure:
├── PHASE1_REPORT.md          ← IEEE Format Report
├── CONTRIBUTIONS.md           ← Individual contributions
├── SUBMISSION.md              ← Submission checklist
├── README_PHASE1.md           ← This file
├── ARCHITECTURE.md            ← System design
├── VERIFICATION_RESULTS.md    ← Test results
├── TESTPLAN.md                ← Test strategy
├── docs/video_script.md       ← Video planning
├── rtl/                       ← Verilog implementation
├── tb/                        ← Testbenches
├── scripts/                   ← Analysis & experiments
├── synth/                     ← FPGA synthesis
└── reports/                   ← Results & evidence
```

## Running Tests

```bash
# Unit tests (directed checks)
make test

# Experiment framework (workload testing)
make experiments

# View results
python3 scripts/demo.py --details

# Waveforms
gtkwave reports/waveforms/two_bit.vcd docs/loop.gtkw
```

## Verification Checklist

✅ All RTL syntax validated  
✅ All unit tests passing  
✅ All workload predictions matching reference  
✅ Synthesis timing closure verified  
✅ FPGA resource estimates within budget  
✅ IEEE report complete with all sections  
✅ Video script ready for recording  
✅ GitHub repository ready for submission  
✅ Individual contributions documented  
✅ All deliverables present  

## Next Steps

1. **Record video** using script at `docs/video_script.md`
2. **Upload to YouTube** and get shareable link
3. **Update video link** in SUBMISSION.md
4. **Submit via form** with:
   - GitHub repository link
   - IEEE report (PHASE1_REPORT.md)
   - Video link
   - CONTRIBUTIONS.md

## Contact

**Project Lead:** Hemanth Tenneti  
**Repository:** https://github.com/HemanthTenneti/MCA_Project  
**Email:** eppalapalliaaloke@gmail.com

---

## Detailed Documentation

- **Architecture:** See `ARCHITECTURE.md` for system design details
- **Testing:** See `TESTPLAN.md` for comprehensive test strategy
- **Results:** See `VERIFICATION_RESULTS.md` for all metrics
- **IEEE Report:** See `PHASE1_REPORT.md` for full technical report
- **Contributions:** See `CONTRIBUTIONS.md` for team member details

**Ready for Phase I Submission! 🚀**
