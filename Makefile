PYTHON ?= python3
PLOT_PYTHON ?= .venv/bin/python
RTL := $(wildcard rtl/*.v)

.PHONY: all sim test lint traces experiments synthesis report figures demo clean
all: test lint report

sim: test lint experiments
	$(PLOT_PYTHON) scripts/build_report.py

test:
	$(PYTHON) scripts/test_project.py

lint:
	@mkdir -p build
	@for mode in 0 1 2; do \
		verilator --lint-only --top-module branch_predictor -GMODE=$$mode -Wall -Wno-UNUSEDSIGNAL $(RTL) || exit 1; \
	done
	verilator --lint-only --top-module branch_recovery -Wall rtl/branch_recovery.v
	verilator --lint-only --top-module timing_top -Wall -Wno-UNUSEDSIGNAL $(RTL) synth/timing_top.v

traces:
	$(PYTHON) scripts/generate_traces.py

experiments: traces
	$(PYTHON) scripts/run_experiments.py

synthesis:
	$(PYTHON) scripts/synthesize.py

report: experiments synthesis
	$(PLOT_PYTHON) scripts/build_report.py

figures:
	$(PLOT_PYTHON) scripts/build_report.py

demo:
	@$(PYTHON) scripts/demo.py

clean:
	rm -rf build
