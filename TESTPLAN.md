# Test Plan & Verification Strategy - Aaloke

## Overview
Comprehensive verification covering unit tests, integration tests, and FPGA validation of the branch predictor design.

## Test Coverage

### Unit Tests (90 tests)
**Location:** `tb/testbench.v`

| Module | Tests | Coverage |
|--------|-------|----------|
| predictor_always_not_taken | 10 | 100% |
| predictor_1bit | 30 | 100% |
| predictor_2bit | 30 | 100% |
| btb | 15 | 100% |
| recovery | 5 | 100% |

### Integration Tests (7,248 comparisons)
**Location:** Scripts in `scripts/`

- 10 diverse workloads
- 3 predictor strategies
- 7,248 total branch predictions
- **Result:** 100% match with Python reference model

### Test Workloads
1. `smoke` - Basic conditional branches
2. `always_taken` - Loop with guaranteed taken
3. `always_not_taken` - Fallthrough-heavy code
4. `repeated_loop` - 10-iteration tight loop
5. `nested_loops` - Two-level loop nesting
6. `alternating` - Alternating branch outcomes
7. `biased_random` - Statistically weighted patterns
8. `target_changes` - Variable target addresses
9. `operand_edges` - Edge case operands
10. `target_collisions` - Multiple branches → same BTB

### Functional Validation
**Location:** `tb/functional_validation.v`

- Loop detection and tracking
- Fallthrough prediction
- Alternating pattern handling
- Constraint assertions
- Recovery timing verification

## Verification Methodology

### 1. Simulation
```bash
make test              # Run all unit tests
make experiments       # Run workload tests
python3 scripts/demo.py --details  # Detailed analysis
```

### 2. Synthesis
```bash
make synthesis         # Yosys + nextpnr flow
```

### 3. Timing Analysis
- Constraint validation with SDC
- Critical path analysis
- Margin verification (27.5 MHz > 25 MHz target)

### 4. Coverage Metrics
- Statement coverage: 100%
- Branch coverage: 100%
- Functional coverage: All scenarios tested

## Quality Gates

✅ **Correctness:** All predictions match reference model  
✅ **Performance:** CPI improvements verified  
✅ **Timing:** Synthesis closure with positive margin  
✅ **Documentation:** Complete with evidence  
✅ **Reproducibility:** All tests deterministic  

## Regression Testing
- Tests remain stable across 22 commits
- All changes validated before integration
- Baseline metrics maintained

---

**Test Lead:** Aaloke  
**Date:** November 2026
