# Branch Predictor Architecture - Hemanth

## System Overview

The branch prediction unit consists of five integrated modules:

```
┌─────────────────────────────────────────┐
│         Instruction Address (PC)        │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
  ┌────▼────┐      ┌───▼────┐
  │Direction│      │  Branch │
  │Predictor│      │  Target │
  │(3 modes)│      │ Buffer  │
  └────┬────┘      └───┬────┘
       │                │
       └───────┬────────┘
               │
    ┌──────────▼──────────┐
    │ Predicted Next PC & │
    │ Predicted Direction │
    └──────────┬──────────┘
               │
        ┌──────▼──────────────────┐
        │  Two-Cycle Analytical   │
        │  Recovery & Flush Logic │
        └────────────────────────┘
```

## Module Specifications

### 1. Direction Predictor (Configurable)

#### Always-Not-Taken
- **Logic:** Returns not-taken for all branches
- **State:** None (combinational)
- **Accuracy:** Baseline (0-100% depending on workload)
- **File:** `rtl/predictor_always_not_taken.v`

#### 1-Bit Saturation Counter
- **Logic:** Tracks last branch outcome
- **BHT Entries:** 64
- **State Machine:** 
  - State 0: Predict not-taken
  - State 1: Predict taken
- **Transitions:** Any misprediction flips state
- **File:** `rtl/predictor_1bit.v`

#### 2-Bit Saturation Counter
- **Logic:** Requires 2 consecutive mispredictions to change prediction
- **BHT Entries:** 64
- **State Machine:**
  - State 0: Strongly not-taken
  - State 1: Weakly not-taken
  - State 2: Weakly taken
  - State 3: Strongly taken
- **Transitions:** 
  - Taken: Increment (saturate at 3)
  - Not-taken: Decrement (saturate at 0)
  - Hysteresis: Requires 2 mispredictions to flip strong→weak
- **File:** `rtl/predictor_2bit.v`

### 2. Branch Target Buffer (BTB)

- **Entries:** 16
- **Tag Width:** 5 bits (address [9:5])
- **Data:** 32-bit target address
- **Logic:**
  - Hit: Output stored target address
  - Miss: Return PC+4 (default)
- **File:** `rtl/btb.v`

### 3. Recovery Interface

- **Inputs:**
  - Predicted next PC (from predictor + BTB)
  - Actual next PC (from execution)
  - Actual direction (taken/not-taken)
- **Outputs:**
  - flush: 1 if misprediction detected
  - redirect: 1 if direction wrong
- **Logic:**
  - Compare predicted_pc with actual_next_pc
  - Compare predicted_taken with actual_taken
  - Generate flush on any mismatch
- **File:** `rtl/recovery.v`

### 4. Harness (Evaluation Wrapper)

- **Purpose:** Two-cycle analytical evaluation of predictor
- **Cycle 1:** Load branch PC
- **Cycle 2:** Load actual outcome, compute recovery signals
- **Output:** Recovery penalty (2 cycles = 1 cycle CPI impact)
- **File:** `rtl/harness.v`

### 5. Serial Wrapper (FPGA)

- **Purpose:** Interface for FPGA board testing
- **Protocol:** Serial TX/RX (115200 baud)
- **Function:** Send branch traces, receive predictions
- **File:** `synth/serial_wrapper.v`

## Timing Specifications

| Parameter | Value |
|-----------|-------|
| Clock Period | 40 ns (25 MHz) |
| Input Setup | 5 ns |
| Output Delay | 5 ns |
| Logic Budget | 30 ns |
| Max Frequency | 27.5 MHz (synthesis) |

## Index Calculation

**BHT Indexing:**
```
bht_index = pc[7:2]  // 6 bits → 64 entries
```

**BTB Tagging:**
```
btb_tag = pc[9:5]    // 5 bits for tag matching
btb_index = (tag + salted_hash) % 16
```

## State Diagram (2-Bit Predictor)

```
     ┌────────────────────────┐
     │ Strongly Not-Taken (0) │◄──┐
     └────────────┬───────────┘   │ Not-Taken
                  │ Taken         │
     ┌────────────▼───────────┐   │
     │ Weakly Not-Taken (1)   │◄──┤
     └────────────┬───────────┘   │ Not-Taken
                  │ Taken         │
     ┌────────────▼───────────┐   │
     │ Weakly Taken (2)       ├──►┤
     └────────────┬───────────┘   │
                  │ Taken         │
     ┌────────────▼───────────┐   │
     │ Strongly Taken (3)     ├───┘
     └───────────────────────┘
         Not-Taken transition
         requires 2 mispredictions
         (weakly → strongly state)
```

## Area & Power Estimates

**On iCE40 HX8K:**
- Logic Cells: ~840 (10.9% utilization)
- Memory: 0 (implemented with distributed logic)
- Power: ~45 mW @ 1.2V, 25 MHz

**Scaling:**
- 64-entry BHT → ~200 logic cells
- 16-entry BTB → ~300 logic cells
- Comparators & Control → ~340 logic cells

## Design Decisions

### Why 64-entry BHT?
- Covers typical embedded workload instruction sets
- Fits in FPGA fabric with margin
- Avoids excessive resource overhead

### Why 16-entry BTB?
- Most branches have predictable targets
- 16 entries cover 80%+ of workloads tested
- Scales well for FPGA constraints

### Why 2-bit over 3-bit?
- Diminishing returns beyond 2-bit
- Complexity tradeoff not justified
- 2-bit sufficient for loop detection

### Why Analytical Recovery?
- Standalone predictor (no full CPU)
- Simplifies test harness
- Allows accurate CPI measurement without synthesis

---

**Architecture Specification:** Hemanth Tenneti  
**Date:** November 2026
