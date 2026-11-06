#!/usr/bin/env python3
"""Compile RTL, check every prediction against the oracle, export raw metrics."""
import argparse
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path
from reference_model import Predictor
from presentation import STRATEGIES, WORKLOADS, table

ROOT = Path(__file__).resolve().parents[1]
MODES = ('always_not_taken', 'one_bit', 'two_bit')
FIELDS = ('workload', 'strategy', 'branches', 'instructions', 'taken', 'direction_correct',
          'direction_accuracy', 'next_address_correct', 'next_address_accuracy', 'btb_hits',
          'btb_hit_rate', 'recoveries', 'branch_frequency', 'base_cpi', 'recovery_penalty',
          'estimated_cpi', 'estimated_speedup')


def execute(args):
    result = subprocess.run(list(map(str, args)), cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(map(str,args))}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def run(base_cpi=1.0, penalty=2):
    if not math.isfinite(base_cpi) or base_cpi <= 0 or penalty < 0:
        raise ValueError('base CPI must be positive and recovery penalty nonnegative')
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'reports/raw').mkdir(parents=True, exist_ok=True)
    (ROOT / 'reports/waveforms').mkdir(exist_ok=True)
    manifest = json.loads((ROOT / 'traces/manifest.json').read_text())
    workloads = manifest['workloads']
    rtl = sorted((ROOT / 'rtl').glob('*.v'))
    summary, checked = [], 0
    for mode, strategy in enumerate(MODES):
        binary = ROOT / 'build' / f'trace_{mode}'
        execute(['iverilog', '-g2012', '-s', 'tb_trace', f'-Ptb_trace.MODE={mode}',
                 '-o', binary, *rtl, ROOT / 'tb/tb_trace.v'])
        for name, workload in workloads.items():
            output = ROOT / 'reports/raw' / f'{name}_{strategy}.csv'
            args = ['vvp', binary, f'+TRACE=traces/{name}.mem', f'+OUTPUT={output}']
            if name == 'repeated_loop':
                args.append(f'+WAVE=reports/waveforms/{strategy}.vcd')
            execute(args)
            rows = list(csv.DictReader(output.open()))
            assert len(rows) == len(workload['records']), f'{name}: missing branch rows'
            oracle = Predictor(mode)
            correct_direction = correct_next = hits = recoveries = 0
            for i, (row, branch) in enumerate(zip(rows, workload['records'], strict=True)):
                derived = int((branch['lhs'] == branch['rhs']) if branch['op'] == 'BEQ'
                              else (branch['lhs'] != branch['rhs']))
                assert derived == branch['taken'], f'{name}:{i}: operand/outcome mismatch'
                assert int(row['row']) == i, f'{name}:{i}: row order mismatch'
                expected = oracle.step(branch)
                actual = {key: int(row[key], 16 if key.endswith('pc') else 10) for key in expected}
                assert actual == expected, f'{name}/{strategy}/{i}: RTL={actual}; oracle={expected}'
                correct_direction += actual['predicted_taken'] == branch['taken']
                correct_next += actual['predicted_next_pc'] == actual['actual_next_pc']
                hits += actual['btb_hit']; recoveries += actual['flush']; checked += 1
            count = len(rows)
            instructions = workload['total_instructions']
            assert count and instructions == sum(1 + b['instructions_before'] for b in workload['records'])
            cpi = base_cpi + recoveries * penalty / instructions
            summary.append(dict(workload=name, strategy=strategy, branches=count, instructions=instructions,
                taken=sum(b['taken'] for b in workload['records']), direction_correct=correct_direction,
                direction_accuracy=correct_direction / count, next_address_correct=correct_next,
                next_address_accuracy=correct_next / count, btb_hits=hits, btb_hit_rate=hits / count,
                recoveries=recoveries, branch_frequency=count / instructions, base_cpi=base_cpi,
                recovery_penalty=penalty, estimated_cpi=cpi, estimated_speedup=0))
    baselines = {r['workload']: r['estimated_cpi'] for r in summary if r['strategy'] == MODES[0]}
    for row in summary:
        row['estimated_speedup'] = baselines[row['workload']] / row['estimated_cpi']
    with (ROOT / 'reports/accuracy.csv').open('w') as f:
        writer = csv.DictWriter(f, FIELDS); writer.writeheader(); writer.writerows(summary)
    versions = {}
    for tool in ('iverilog', 'vvp'):
        result = subprocess.run([tool, '-V'], text=True, capture_output=True, check=True)
        versions[tool] = (result.stdout + result.stderr).splitlines()[0]
    (ROOT / 'reports/verification.json').write_text(json.dumps(dict(
        status='PASS', comparisons=checked, workloads=len(workloads), strategies=len(MODES),
        seed=manifest['seed'], manifest_sha256=hashlib.sha256((ROOT/'traces/manifest.json').read_bytes()).hexdigest(),
        base_cpi=base_cpi, recovery_penalty=penalty, tools=versions), indent=2) + '\n')
    print(f'PASS: {checked:,} RTL/reference comparisons across {len(workloads)} workloads.')
    display_rows = []
    for name in workloads:
        results = [next(r for r in summary if r['workload'] == name and r['strategy'] == mode) for mode in MODES]
        display_rows.append([WORKLOADS.get(name, name), *[f"{r['next_address_accuracy']:.2%}" for r in results]])
    print('\nCorrect next-address predictions (higher is better)')
    print(table(['Workload', 'Always not taken', '1-bit', '2-bit'], display_rows, right=(1,2,3)))
    print('\nRaw data: reports/accuracy.csv; visual report is generated by make report.')
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--base-cpi', type=float, default=1.0)
    p.add_argument('--penalty', type=int, default=2)
    a = p.parse_args()
    run(a.base_cpi, a.penalty)
