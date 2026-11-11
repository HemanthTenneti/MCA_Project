# Dynamic Branch Prediction Unit

A standalone Verilog implementation of MCA Project 5: always-not-taken, 1-bit,
and 2-bit branch prediction, a tagged branch target buffer, and a flush/redirect
interface. No complete CPU or physical FPGA is required to run the experiments.

**Start here:** [visual results](reports/results.html),
[project guide PDF](output/pdf/project_guide.pdf), [editable project guide](docs/project_guide.docx).
The guide explains the requirements, design, implementation, verification, and presentation.
For detailed evidence, use the [technical report](reports/technical_report.md),
[design notes](docs/design.md), and [demo guide](docs/demo.md).

## Quick start

From this directory:

```sh
# macOS tools (use equivalent packages on Linux)
brew install icarus-verilog verilator gtkwave yosys nextpnr-ice40
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

make all      # tests, lint, traces, RTL/oracle comparisons, synthesis, figures, report
make demo     # a plain-English comparison and visit-by-visit loop walkthrough
```

Open `reports/results.html` directly in your browser: it works offline, includes its
images and data, and lets you explore each workload. The terminal demo uses clear
labels and a compact comparison; `python3 scripts/demo.py --details` adds readable
counter states and saved addresses. Raw CSV and JSON evidence is preserved.

The Python reference model and test runner use only the standard library.
Matplotlib is required only to regenerate charts, diagrams, and the waveform preview.
Use `make sim` for verification and reports without rerunning FPGA synthesis.
An existing synthesis report is retained; if absent, the generated report explicitly
states synthesis has not been run. `make test` and `make experiments` do not require
Matplotlib or FPGA tools.

## Results delivered

The included reports contain actual local runs, not example values:

- 90 directed RTL checks, five hand-calculated Python tests, and three serial-wrapper transactions.
- 7,248 RTL/oracle branch comparisons across ten workloads and three strategies.
- Repeated-loop next-address accuracy: **10.00%, 80.00%, 89.69%**, respectively.
- Repeated-loop analytical CPI: **1.36000, 1.08000, 1.04125**, respectively.
- Routed timing estimates and resource usage for iCE40 HX8K CT256, plus fixture-only reference results.
- Post-synthesis functional simulations for all three wrapped strategies.

See `reports/accuracy.csv` for every workload and `reports/raw/` for each branch.
Both dynamic predictors lose to the baseline on the deliberately alternating trace.
Results use cold tables at the start of each independent workload; no warm-up is excluded.

## Layout

| Directory | Contents |
|---|---|
| `rtl/` | Synthesizable direction predictor, target buffer, prediction and recovery modules |
| `tb/` | Directed tests, two-cycle branch-resolution harness, serial-wrapper checks |
| `traces/` | Deterministic operand-derived BEQ/BNE traces and instruction counts |
| `scripts/` | Trace generation, independent oracle, experiments, synthesis, reporting, demo |
| `synth/` | Registered serial evaluation wrapper |
| `reports/` | Visual report, measurements, raw predictions, VCDs, figures, technical report, tool logs |
| `docs/` | Editable project guide, design notes, and demo instructions |
| `output/pdf/` | Shareable project guide PDF |

RTL is Verilog-2005 compatible; testbenches are compiled with Icarus `-g2012`.
The default configuration is 32-bit addresses, 64 BHT entries, 16 BTB entries,
and a two-cycle analytical recovery penalty. The harness allows one outstanding
branch and is not a CPU performance simulator.

## Individual commands

```sh
make test
make lint
make experiments
make synthesis
make figures
make demo
python3 scripts/demo.py --details
# Explore different analytical assumptions without changing predictor behavior:
python3 scripts/run_experiments.py --base-cpi 1 --penalty 3
# Return the report to its default assumptions:
make report
# Inspect recorded RTL waveforms:
gtkwave reports/waveforms/two_bit.vcd docs/loop.gtkw
```

Only `UNUSEDSIGNAL` warnings are disabled for lint: BHT indexing intentionally
ignores address tags/alignment bits, and parameter specialization removes signals.
Other enabled Verilator warnings remain fatal. `make clean` removes disposable
build products, preserving submitted reports and waveforms.

## Source brief

The supplied *Project_list_MCA.pdf*, Project 5 and Common Project Requirements,
is the requirements source. Suggested module names and tool choices in that brief
are treated as suggestions. This repository chooses a standalone predictor, not
a complete processor; FPGA results are static tool estimates, not board measurements.

The project guide is an explanatory document, separate from the generated technical
report. Its source is `scripts/build_project_guide.py` (requires python-docx).
The delivered PDF and editable Word copy contain the same seven-page guide.
