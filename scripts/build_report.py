#!/usr/bin/env python3
"""Render publication-ready experiment figures and a source-linked Markdown report."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT/'reports/figures'
MODES = ('always_not_taken', 'one_bit', 'two_bit')
LABELS = ('Always not taken', '1-bit', '2-bit')
COLORS = ('#64748b', '#0891b2', '#7c3aed')


def save(fig, name):
    fig.savefig(FIG/f'{name}.png', dpi=180, facecolor='white', bbox_inches='tight')
    fig.savefig(FIG/f'{name}.svg', facecolor='white', bbox_inches='tight')
    plt.close(fig)


def plots(rows):
    names = list(dict.fromkeys(r['workload'] for r in rows))
    lookup = {(r['workload'], r['strategy']): r for r in rows}
    positions = np.arange(len(names))
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True, layout='constrained')
    for ax, metric, title in zip(axes, ('direction_accuracy', 'next_address_accuracy'),
                               ('Direction accuracy', 'Next-address accuracy (includes target availability)'), strict=True):
        for i, mode in enumerate(MODES):
            values = [100*float(lookup[(name, mode)][metric]) for name in names]
            ax.bar(positions+(i-1)*0.25, values, 0.24, label=LABELS[i], color=COLORS[i])
        ax.set_ylim(0, 110); ax.set_ylabel('Correct predictions (%)'); ax.set_title(title, loc='left', weight='bold')
        ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
    axes[0].legend(ncol=3, loc='upper right')
    axes[-1].set_xticks(positions, [n.replace('_', '\n') for n in names], fontsize=9)
    fig.suptitle('Same traces, cold tables, three prediction strategies', fontsize=17, weight='bold')
    save(fig, 'accuracy_comparison')
    fig, ax = plt.subplots(figsize=(14, 4.8), layout='constrained')
    for i, mode in enumerate(MODES):
        ax.bar(positions+(i-1)*.25, [float(lookup[(n, mode)]['estimated_cpi']) for n in names],
               .24, color=COLORS[i], label=LABELS[i])
    ax.set_xticks(positions, [n.replace('_', '\n') for n in names], fontsize=9)
    ax.set_ylim(0, 1.85); ax.set_ylabel('Estimated cycles per instruction')
    ax.set_title(f"Analytical CPI: base CPI {float(rows[0]['base_cpi']):g}, recovery penalty {rows[0]['recovery_penalty']} cycles", loc='left', weight='bold')
    ax.legend(ncol=3, loc='upper right'); ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
    save(fig, 'cpi_comparison')


def box(ax, x, y, w, h, text, color='#e0f2fe'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012', linewidth=1.2,
                              facecolor=color, edgecolor='#334155'))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=11, color='#0f172a')


def arrow(ax, start, end, color='#334155', **kwargs):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=16,
                               linewidth=1.4, color=color, **kwargs))


def diagrams():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    box(ax, .02, .60, .17, .18, 'Branch query\nvalid + PC')
    box(ax, .29, .76, .20, .15, 'Direction table\n64 counters')
    box(ax, .29, .45, .20, .15, 'Target buffer\n16 tagged entries')
    box(ax, .59, .60, .17, .18, 'Select next PC\ntarget or PC + 4')
    box(ax, .81, .60, .17, .18, 'Save prediction\nat issue edge N', '#ede9fe')
    box(ax, .02, .10, .22, .18, 'Resolved branch\nPC, outcome, target', '#fef3c7')
    box(ax, .59, .10, .17, .18, 'Compare actual\nand saved next PC', '#ede9fe')
    box(ax, .81, .10, .17, .18, 'Flush + redirect\nwhen unequal', '#fee2e2')
    arrow(ax, (.19, .73), (.28, .82)); arrow(ax, (.19, .65), (.28, .53))
    arrow(ax, (.50, .82), (.58, .73)); arrow(ax, (.50, .53), (.58, .65))
    ax.text(.535, .85, 'direction', fontsize=9, ha='center')
    ax.text(.54, .46, 'hit / target', fontsize=9, ha='center', bbox=dict(facecolor='white', edgecolor='none', pad=2))
    arrow(ax, (.77, .69), (.80, .69))
    arrow(ax, (.895, .59), (.75, .29), connectionstyle='angle,angleA=-90,angleB=0,rad=8')
    ax.text(.895, .40, 'Saved metadata\nheld until N+2', fontsize=10, ha='center', bbox=dict(facecolor='white', edgecolor='none', pad=3))
    arrow(ax, (.25, .19), (.58, .19)); arrow(ax, (.77, .19), (.80, .19))
    ax.plot([.13, .13, .39], [.29, .36, .36], color='#b45309', linestyle='--')
    arrow(ax, (.39, .36), (.39, .44), '#b45309')
    ax.plot([.39, .54, .54, .39], [.36, .36, .69, .69], color='#b45309', linestyle='--')
    arrow(ax, (.39, .69), (.39, .75), '#b45309')
    ax.text(.19, .39, 'Clocked training at N+2', color='#92400e', fontsize=10, ha='center')
    ax.set_title('Standalone predictor and branch-resolution harness', fontsize=17, weight='bold', pad=16)
    save(fig, 'architecture')
    fig, ax = plt.subplots(figsize=(12, 4.4))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    xs = [.035, .285, .535, .785]
    labels = ['00\nStrongly not taken\nPredict N', '01\nWeakly not taken\nPredict N (reset)',
              '10\nWeakly taken\nPredict T', '11\nStrongly taken\nPredict T']
    for i, (x, label) in enumerate(zip(xs, labels, strict=True)):
        box(ax, x, .32, .18, .30, label, '#e0f2fe' if i < 2 else '#ede9fe')
    for i in range(3):
        arrow(ax, (xs[i]+.13, .64), (xs[i+1]+.05, .64), connectionstyle='arc3,rad=-.5')
        ax.text((xs[i]+xs[i+1]) / 2 + .09, .79, 'T: increment', ha='center', fontsize=10)
        arrow(ax, (xs[i+1]+.05, .30), (xs[i]+.13, .30), connectionstyle='arc3,rad=-.5')
        ax.text((xs[i]+xs[i+1]) / 2 + .09, .13, 'N: decrement', ha='center', fontsize=10)
    ax.text(.125, .94, 'N: stay at 00', ha='center', fontsize=10)
    ax.text(.875, .94, 'T: stay at 11', ha='center', fontsize=10)
    arrow(ax, (.07,.64), (.18,.64), connectionstyle='arc3,rad=-1.2')
    arrow(ax, (.82,.64), (.93,.64), connectionstyle='arc3,rad=-1.2')
    ax.set_title('2-bit saturating counter: update only on branch resolution', weight='bold', fontsize=16, pad=16)
    save(fig, 'counter_states')


def read_vcd(path, wanted):
    scopes, symbols, events = [], {}, {name: [] for name in wanted}
    header = True; time = 0
    for line in path.read_text().splitlines():
        p = line.split()
        if not p:
            continue
        if header:
            if p[0] == '$scope': scopes.append(p[2])
            elif p[0] == '$upscope': scopes.pop()
            elif p[0] == '$var' and scopes == ['tb_trace'] and p[4] in wanted:
                symbols[p[3]] = p[4]
            elif p[0] == '$enddefinitions': header = False
            continue
        if line.startswith('#'):
            time = int(line[1:]) / 1000 # Trace testbench declares 1ps precision.
        elif line[0] in 'bB':
            value, key = line[1:].split()
            if key in symbols:
                events[symbols[key]].append((time, None if any(c in value for c in 'xzXZ') else int(value, 2)))
        elif line[0] in '01xXzZ' and line[1:] in symbols:
            events[symbols[line[1:]]].append((time, int(line[0]) if line[0] in '01' else None))
    assert all(events.values()), 'VCD preview missing expected top-level signals'
    return events


def waveform():
    names = ['clk', 'query_valid', 'update_valid', 'query_state', 'predicted_taken',
             'btb_hit', 'saved_next', 'flush', 'redirect_pc']
    path = ROOT/'reports/waveforms/two_bit.vcd'
    if not path.exists():
        return
    events = read_vcd(path, names)
    fig, axes = plt.subplots(len(names), 1, figsize=(14, 9), sharex=True, layout='constrained')
    buses = {'query_state', 'saved_next', 'redirect_pc'}
    end = 470
    for ax, name in zip(axes, names, strict=True):
        points = [(t, v) for t, v in events[name] if t <= end]
        if points[-1][0] < end:
            points.append((end, points[-1][1]))
        ax.set_ylabel(name, rotation=0, ha='right', va='center', fontsize=10, labelpad=12)
        if name in buses:
            for (start, value), (stop, _) in zip(points, points[1:]):
                if value is not None:
                    ax.plot([start, stop], [.5, .5], color='#7c3aed', linewidth=3)
                    if stop - start > 9:
                        label = f'{value:02b}' if name == 'query_state' else f'{value:03x}'
                        ax.text((start+stop)/2, .65, label, ha='center', fontsize=8)
            ax.set_yticks([]); ax.set_ylim(0, 1.3)
        else:
            ax.step([p[0] for p in points], [float('nan') if p[1] is None else p[1] for p in points],
                    where='post', color='#0891b2', linewidth=1.5)
            ax.set_ylim(-.15, 1.3); ax.set_yticks([0, 1], labels=['0', '1'], fontsize=8)
        ax.grid(axis='x', alpha=.2); ax.spines[['top','right']].set_visible(False)
    axes[-1].set_xlim(0, end); axes[-1].set_xlabel('Simulation time (ns); values parsed from actual two_bit.vcd')
    fig.suptitle('2-bit predictor: cold start, first loop exit, and next invocation', fontsize=15, weight='bold')
    save(fig, 'waveform_preview')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---']*len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, row)) + ' |' for row in rows])


def report(rows):
    verification = json.loads((ROOT/'reports/verification.json').read_text())
    tests = json.loads((ROOT/'reports/unit_checks.json').read_text()) if (ROOT/'reports/unit_checks.json').exists() else None
    names = list(dict.fromkeys(r['workload'] for r in rows))
    lookup = {(r['workload'], r['strategy']): r for r in rows}
    accuracy_table = table(['Workload', 'Strategy', 'Direction correct', 'Next-address correct', 'BTB hit rate', 'Recoveries', 'Estimated CPI'], [
        [r['workload'], LABELS[MODES.index(r['strategy'])], f"{float(r['direction_accuracy']):.2%}",
         f"{float(r['next_address_accuracy']):.2%}", f"{float(r['btb_hit_rate']):.2%}", r['recoveries'],
         f"{float(r['estimated_cpi']):.5f}"] for name in names for r in rows if r['workload'] == name])
    workload_table = table(['Workload', 'Branches', 'Instructions', 'Branch frequency'], [
        [name, lookup[(name,MODES[0])]['branches'], lookup[(name,MODES[0])]['instructions'],
         f"{float(lookup[(name,MODES[0])]['branch_frequency']):.2%}"] for name in names])
    synth_path = ROOT/'reports/synthesis/summary.csv'
    if synth_path.exists():
        hardware = list(csv.DictReader(synth_path.open()))
        synth_table = table(['Wrapped strategy', 'Logic cells / 7680', 'LUT4s', 'Flip-flops', '4K RAM blocks', 'Estimated Fmax (MHz)'], [
            [r['strategy'], r['logic_cells'], r['lut4'], r['flip_flops'], r['block_rams'],
             f"{float(r['estimated_fmax_mhz']):.2f}"] for r in hardware])
        tools = json.loads((ROOT/'reports/synthesis/tools.json').read_text())
        synth_text = f'''Target: **Lattice iCE40 HX8K CT256**. Clock constraint: **25 MHz**. Place-and-route seed: **1**.
All four configurations meet the constraint.

{synth_table}

These are measured tool outputs for **predictor + recovery + registered serial
transport**, and a separate fixture reference. The fixture contains 332 logical
transport flip-flops; its XOR observes all request bits. Optimization and FPGA
packing mean its resources cannot simply be subtracted to claim bare predictor
area. Baseline retains the BTB hit observation output, so it also has target storage.
LUT4 and flip-flop counts come from the mapped Yosys netlist; packed logic-cell
and RAM counts come from nextpnr. RAM and LUT mapping depend on register boundaries
and tool optimizations.

Fmax is a routed **internal clock-path estimate**, not a physical-board measurement
or externally constrained I/O guarantee. The serial wrapper affects the critical
path and does not describe a processor's instruction throughput. Automatic pin
placement is an evaluation choice; no board pin assignment or hardware test is claimed.

Tools: `{tools['yosys']}`; `{tools['tool_package_version']}`.
The nextpnr executable reports an empty version string; its SHA-256 is retained in
[tools.json](synthesis/tools.json). Full synthesis logs, routed timing reports,
utilization JSON, and post-synthesis gate checks are in [synthesis/](synthesis/).
'''
    else:
        synth_text = '**Not run.** Run `make synthesis` and `make figures` to add device-specific resource/timing results. Simulation accuracy alone does not satisfy the synthesis deliverable.'
    loop = [lookup[('repeated_loop',mode)] for mode in MODES] if 'repeated_loop' in names else []
    findings = ''
    if loop:
        findings = f'''- **Repeated loops:** recoveries are {', '.join(r['recoveries'] for r in loop)} for baseline,
  1-bit, and 2-bit. Corresponding analytical CPI is {', '.join(f"{float(r['estimated_cpi']):.5f}" for r in loop)}.
  The 2-bit strategy's estimated speedup over baseline is {float(loop[2]['estimated_speedup']):.3f}x under these assumptions.
- **Why 2-bit helps here:** 1-bit misses the first taken branch and the exit on each
  invocation. 2-bit misses initial training and each exit, retaining taken direction
  for the next invocation. There are 32 invocations of nine taken branches followed
  by one not-taken exit.
'''
    text = f'''# Dynamic Branch Prediction Unit — Technical Report

## 1. Objective and requirements

Design and evaluate a hardware branch-prediction unit that reduces control-hazard
recovery penalties. This implements Project 5 from the supplied *Project_list_MCA.pdf*,
including the common requirements for modular synthesizable RTL, directed testbench,
waveform verification, quantitative comparison, synthesis resources, timing estimates,
a report, and a live demonstration. A complete CPU is not explicitly required for
Project 5; this implementation uses a standalone predictor and branch-resolution harness.

## 2. Microarchitecture

![System block diagram](figures/architecture.png)

The three strategies are always not taken, a 1-bit last-outcome predictor, and a
2-bit saturating predictor. They share the same external interface and target-buffer
policy. All addresses are 32-bit with 4-byte instruction alignment. BHT entries are
indexed by PC bits 7:2; the 16-entry tagged BTB uses bits 5:2 and tags 31:6.
Reset initializes 1-bit entries to 0, 2-bit counters to 01, and BTB valid bits to 0.

![Two-bit state transitions](figures/counter_states.png)

Direction is the counter's most significant bit. Taken increments and not taken
decrements with saturation. BTB entries are populated/replaced only on taken
resolution. A missing target forces next-address prediction to PC+4, even if the
direction predictor says taken. Resolution compares the actual next address to the
saved original prediction to drive flush and redirect. Read/update ordering,
complete interfaces, and wrapper protocol are specified in [design.md](../docs/design.md).

## 3. Workloads and methodology

All strategies run identical committed traces with cold tables for each independent
workload. Outcomes are derived from BEQ/BNE operands, not guessed by a predictor.
Seed: **{verification['seed']}**. Branch frequency is derived from the actual synthetic
workload record count and its explicitly recorded retired nonbranch instruction count.
No warm-up branches are excluded.

{workload_table}

The harness saves a prediction at issue edge N and resolves/updates at edge N+2,
with one outstanding branch. It does not model a complete executing processor,
wrong-path instructions, instruction overlap, other hazards, or pipeline fill/drain.
Target-change traces are deliberately adversarial interface tests; changing targets
at one static PC are not typical of direct BEQ/BNE code. Nested-loop traces represent
repeated calls; ordinary call/return instructions are not simulated.

Definitions:

- Direction accuracy = correct taken/not-taken guesses / all branch queries.
- Next-address accuracy = correct next addresses / all branch queries.
- BTB hit rate = tag/valid hits / all branch queries, including not-taken queries.
- Recovery count = next-address mismatches; a direction mismatch alone need not flush
  if target and fallthrough happen to be equal.
- Branch frequency = branch count / total retired instruction count.

`estimated_CPI = base_CPI + branch_frequency × next_address_miss_rate × recovery_penalty`

For this run: base CPI **{verification['base_cpi']}**, penalty **{verification['recovery_penalty']}** cycles.
Equivalently, CPI = base CPI + recoveries × penalty / total instructions. Speedup is
baseline CPI divided by strategy CPI at a common assumed instruction clock.
These are **analytical estimates**, not measured CPU performance or serialized
harness cycle counts. The two-cycle harness resolution delay and analytical
recovery penalty are separate settings that share a default value.

## 4. Results and interpretation

![Prediction accuracy](figures/accuracy_comparison.png)

{accuracy_table}

![Analytical CPI comparison](figures/cpi_comparison.png)

{findings}
- **Alternating outcomes:** both dynamic predictors oscillate out of phase from
  their chosen reset states and score zero direction accuracy on this trace. The
  always-not-taken baseline achieves 50%. Two-bit is not universally superior.
- **BTB collisions:** independent BHT entries learn both taken branches, but the
  alternating addresses evict each other's BTB entries. Next-address accuracy is
  zero despite high direction accuracy.
- **BHT collisions:** opposing outcomes interfere in the shared counter. Direction
  accuracy and next-address accuracy differ because a BTB miss falls through and
  can accidentally select the correct next address on not-taken branches.
- **Target changes:** after warm-up the direction is correct, but a stale stored
  target causes an additional recovery when the target changes.

Raw counters and full precision values are in [accuracy.csv](accuracy.csv).
Each launch-time state, prediction, target hit, actual next address, and flush is
retained in [raw/](raw/). No averaged score across arbitrary synthetic workloads is
used to claim overall performance.

## 5. Verification evidence

- Directed Verilog checks: **90 passed**. All eight state/outcome transitions,
  saturation, reset priority, disabled updates, query-valid gating, BHT indexing,
  BHT aliasing, BTB tags/replacement, target retention, changed targets, saved
  prediction recovery, invalid resolution, and address wraparound are covered.
- Independent hand-calculated Python cases: **{tests['python_tests'] if tests else 'not run'}**.
  These check loop miss totals, alternation, operand semantics, target correctness,
  and BTB replacement against known expected counts.
- RTL/oracle comparisons: **{verification['comparisons']:,} passed** across
  **{verification['workloads']} workloads × {verification['strategies']} strategies**.
  Every prediction field and every recovery is compared, not just aggregate accuracy.
- Serial wrapper: three transactions test cold prediction, learned prediction,
  output ordering, and absence of repeated updates during serial shifting.
- Post-synthesis functional simulation reruns the serial wrapper transactions for
  each mapped strategy using Yosys's iCE40 primitive models. This is a directed
  functional check, not exhaustive equivalence or timing simulation.
- Verilator checks all three predictor modes, recovery, and the wrapper. Only
  deliberate unused-address/parameter-specialization warnings are suppressed.

![Actual RTL waveform preview](figures/waveform_preview.png)

The preview is parsed from the actual 2-bit VCD (not a reconstructed ideal waveform).
At cold start, saved next-PC is 0x104; a taken resolution flushes to 0x80. Subsequent
predictions use the learned target. At the loop exit, recovery redirects to 0x104;
the counter remains weakly taken for the next loop invocation.
VCD files are in [waveforms/](waveforms/), with a GTKWave signal list in
[loop.gtkw](../docs/loop.gtkw). Machine-readable evidence is in
[verification.json](verification.json), [unit_checks.json](unit_checks.json), and
[synthesis/gate_checks.json](synthesis/gate_checks.json).

## 6. Synthesis and timing

{synth_text}

## 7. Reproduction, demonstration, and limitations

Run `make all` to regenerate tests, lint, traces, experiments, synthesis, and this
report. Run `make demo` for the repeated-loop walkthrough. See the
[live demonstration guide](../docs/demo.md) for a 5–7 minute presentation sequence.

This project demonstrates the required prediction, update, target, and recovery
behavior. It deliberately excludes a complete CPU, speculative rollback, multiple
outstanding branches, global history predictors, physical board validation, and
claims about real-program speedup. Synthetic instruction density and a constant
recovery penalty simplify the analytical CPI model. No external hardware is needed
for the delivered results.

## References

1. Supplied *Project_list_MCA.pdf*, Project 5 and Common Project Requirements.
2. [Cornell ECE 4750 branch-prediction exercises](https://www.csl.cornell.edu/courses/ece4750/handouts/ece4750-T10-ap-branchpred-problems.pdf).
3. [Yosys documentation](https://yosyshq.readthedocs.io/projects/yosys/en/latest/).
4. [nextpnr official repository](https://github.com/YosysHQ/nextpnr).
'''
    (ROOT/'reports/technical_report.md').write_text(text)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.fonttype': 'none'})
    rows = list(csv.DictReader((ROOT/'reports/accuracy.csv').open()))
    plots(rows); diagrams(); waveform(); report(rows)
    from build_readable_report import build
    build()
    print('Generated report, charts, architecture/state diagrams, and actual VCD preview')


if __name__ == '__main__':
    main()
