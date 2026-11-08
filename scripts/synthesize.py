#!/usr/bin/env python3
"""Reproducible iCE40 resource and routed register-to-register timing analysis."""
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/synthesis'
BUILD = ROOT / 'build/synthesis'
NAMES = ('always_not_taken', 'one_bit', 'two_bit', 'fixture_reference')


def command(args, log):
    with log.open('w') as f:
        result = subprocess.run(args, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise RuntimeError(f"{' '.join(args)} failed; see {log}\n{log.read_text()[-4000:]}")


def synthesize():
    for tool in ('yosys', 'nextpnr-ice40'):
        if not shutil.which(tool):
            raise SystemExit(f'{tool} missing. macOS: brew install yosys nextpnr-ice40')
    OUT.mkdir(parents=True, exist_ok=True); BUILD.mkdir(parents=True, exist_ok=True)
    rtl = ' '.join(str(p.relative_to(ROOT)) for p in sorted((ROOT/'rtl').glob('*.v')))
    summary = []
    gate_results = {}
    datadir = subprocess.check_output(['yosys-config', '--datdir'], text=True).strip()
    for index, name in enumerate(NAMES):
        mode, fixture = (0, 1) if index == 3 else (index, 0)
        netlist = BUILD / f'{name}.json'
        stats = OUT / f'{name}_cells.json'
        script = (f'read_verilog {rtl} synth/timing_top.v; '
                  f'chparam -set MODE {mode} -set FIXTURE_ONLY {fixture} timing_top; '
                  f'synth_ice40 -top timing_top -json {netlist}; check -assert; '
                  f'tee -o {stats} stat -json; write_verilog -noattr -noexpr {BUILD / (name + ".v")}')
        print(f'Synthesizing {name}', flush=True)
        command(['yosys', '-p', script], OUT / f'{name}_yosys.log')
        report = OUT / f'{name}_pnr.json'
        command(['nextpnr-ice40', '--hx8k', '--package', 'ct256', '--json', str(netlist),
                 '--freq', '25', '--seed', '1', '--report', str(report),
                 '--asc', str(BUILD/f'{name}.asc')], OUT / f'{name}_pnr.log')
        if index < 3:
            gate_binary = BUILD / f'gate_{name}'
            command(['iverilog', '-g2012', '-DGATE_LEVEL', '-s', 'tb_timing_top',
                     f'-Ptb_timing_top.MODE={mode}', '-o', str(gate_binary),
                     str(BUILD / f'{name}.v'), str(Path(datadir)/'ice40/cells_sim.v'),
                     'tb/tb_timing_top.v'], OUT / f'{name}_gate_compile.log')
            command(['vvp', str(gate_binary)], OUT / f'{name}_gate_test.log')
            gate_results[name] = (OUT / f'{name}_gate_test.log').read_text().strip()
        data = json.loads(report.read_text())
        timing = data.get('fmax', {})
        if not timing:
            raise RuntimeError(f'No clock timing results for {name}')
        clock, numbers = next(iter(timing.items()))
        achieved, constraint = numbers['achieved'], numbers['constraint']
        if achieved < constraint:
            raise RuntimeError(f'{name}: {achieved} MHz fails {constraint} MHz target')
        cells = json.loads(stats.read_text())['modules']['\\timing_top']['num_cells_by_type']
        utilization = data['utilization']
        summary.append(dict(strategy=name, device='iCE40HX8K', package='CT256', seed=1,
            target_mhz=constraint, estimated_fmax_mhz=achieved, clock=clock,
            logic_cells=utilization['ICESTORM_LC']['used'],
            logic_cells_available=utilization['ICESTORM_LC']['available'],
            lut4=cells.get('SB_LUT4', 0), flip_flops=sum(v for k,v in cells.items() if k.startswith('SB_DFF')),
            block_rams=utilization['ICESTORM_RAM']['used'],
            io_cells=utilization['SB_IO']['used']))
        print(f'PASS {name}: {achieved:.2f} MHz; {summary[-1]["logic_cells"]} logic cells', flush=True)
    with (OUT/'summary.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    tools = {}
    for tool, flag in [('yosys', '-V'), ('nextpnr-ice40', '--version')]:
        r = subprocess.run([tool, flag], capture_output=True, text=True, check=True)
        tools[tool] = (r.stdout+r.stderr).strip()
    tools['nextpnr_executable_sha256'] = __import__('hashlib').sha256(Path(shutil.which('nextpnr-ice40')).read_bytes()).hexdigest()
    tools['tool_package_version'] = os.environ.get('NEXTPNR_PACKAGE_VERSION', 'not recorded; see executable hash')
    if shutil.which('brew'):
        r = subprocess.run(['brew', 'list', '--versions', 'nextpnr-ice40'], capture_output=True, text=True)
        if r.returncode == 0:
            tools['tool_package_version'] = r.stdout.strip()
    (OUT/'gate_checks.json').write_text(json.dumps(dict(status='PASS', results=gate_results), indent=2)+'\n')
    (OUT/'tools.json').write_text(json.dumps(tools, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    synthesize()
