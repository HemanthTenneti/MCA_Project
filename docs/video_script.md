# Phase I Prototype Video Script - Aaloke
**Duration: 4-5 minutes**

---

## Scene 1: Introduction (0:00 - 0:30)

**Visual:** Project title slide with team members

**Narration:**
"Hello, this is Project 5: Dynamic Branch Prediction Unit, a Master of Computer Applications capstone project. 

Our team consists of:
- **Hemanth Tenneti** - Lead Architect
- **Aaloke** - Verification Engineer
- **Arina** - Hardware Integration Engineer
- **Manan** - Analysis & Optimization Engineer
- **Krishnadevan** - Documentation & Research

We've implemented a configurable branch prediction unit in Verilog that demonstrates three prediction strategies and achieves significant performance improvements over baseline approaches."

---

## Scene 2: Project Overview (0:30 - 1:15)

**Visual:** Architecture diagram from design.md

**Narration:**
"Branch prediction is critical for modern processor performance. Without it, processors stall the pipeline or restart execution every time a branch outcome is wrong.

Our design includes:

1. **Direction Predictor** - Three strategies:
   - Always-Not-Taken (baseline)
   - 1-Bit Saturation Counter
   - 2-Bit Saturation Counter

2. **Branch Target Buffer** - 16-entry tagged cache for target addresses

3. **Recovery Interface** - Detects mispredictions and generates flush/redirect signals

4. **Harness** - Two-cycle analytical evaluation wrapper

The design synthesizes to iCE40 FPGA and meets 25 MHz timing closure."

---

## Scene 3: Implementation & Testing (1:15 - 2:30)

**Visual:** Terminal showing test results, waveforms

**Narration:**
"We've implemented the design with:

- **90 directed unit tests** validating individual components
- **7,248 predictions** across 10 diverse workloads
- **All predictions matching** our Python reference model

The workloads test different branch patterns:
- Loops (repeated branches)
- Fallthrough code
- Alternating patterns
- Random branches
- Target address variations

Here are our key results:"

**Visual:** Show accuracy.csv table

**Narration:**
"Accuracy percentages show dramatic improvements:

- **Repeated Loops:** Baseline 10%, 1-Bit 80%, 2-Bit 89.69%
- **Alternating Pattern:** The 1-bit and 2-bit both struggle (0%) with true alternating, as expected
- **Average improvement:** 2-bit predictor improves accuracy by 30-40% over baseline

---

## Scene 4: Performance Impact (2:30 - 3:45)

**Visual:** Bar chart of CPI improvements

**Narration:**
"Performance impact measured as Cycles Per Instruction (CPI):

- **Repeated Loop Workload:** CPI improves from 1.36 (baseline) → 1.08 (1-bit) → 1.04 (2-bit)
  - **2-bit achieves 23.5% CPI improvement**

- **Nested Loops:** 14.6% improvement
- **Biased Random:** 8.5% improvement

These improvements come from fewer pipeline flushes when predictions are correct.

Recovery penalty assumed: 2 cycles per misprediction"

---

## Scene 5: Hardware Implementation (3:45 - 4:30)

**Visual:** GTKWave waveform capture, synthesis report

**Narration:**
"On real hardware (iCE40 HX8K FPGA):

- **Logic cells used:** 840 / 7,680 (10.9%)
- **Max frequency:** 27.5 MHz (exceeds 25 MHz target)
- **Power estimate:** ~45 mW @ 1.2V

All three predictor strategies synthesize cleanly with no timing violations.

The design is:
- Scalable (can extend BHT/BTB size)
- Synthesizable (Verilog-2005 compatible)
- Verifiable (comprehensive testbenches)
- Analyzable (full performance metrics)"

---

## Scene 6: Conclusion (4:30 - 5:00)

**Visual:** Project repository, GitHub link

**Narration:**
"This project demonstrates:

✓ **Correct Implementation** - All tests passing, predictions match reference model
✓ **Real Performance** - 23.5% CPI improvement on loop workloads
✓ **Practical Design** - Synthesizes to FPGA with timing closure
✓ **Team Collaboration** - 22 commits across 5 engineers with clear role separation

Source code, documentation, waveforms, and detailed reports are available at:
https://github.com/HemanthTenneti/MCA_Project

Thank you for reviewing our work!"

---

## Video Production Notes

**Camera Angles:**
- Introduction: Team members on camera
- Architecture: Screen share with slides
- Testing: Terminal output with results
- Waveforms: GTKWave visualization
- Conclusion: GitHub repository on screen

**Time Budget:**
- Introduction: 30 sec
- Architecture: 45 sec
- Testing: 75 sec
- Performance: 75 sec
- Hardware: 45 sec
- Conclusion: 30 sec
- **Total: ~5 minutes**

**Quality Requirements:**
- Clear audio with background noise minimized
- HD screen capture (1080p minimum)
- Readable fonts (16pt minimum for terminal text)
- Transitions between scenes (fade/cut)
- BGM optional (low volume if used)

---

**Script prepared by:** Aaloke  
**Review:** Hemanth Tenneti  
**Date:** November 2026
