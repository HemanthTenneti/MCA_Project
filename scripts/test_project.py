#!/usr/bin/env python3
"""Directed RTL checks plus independently hand-calculated oracle cases."""
import json
from pathlib import Path
import subprocess
import unittest
from reference_model import Predictor
from generate_traces import branch

ROOT = Path(__file__).resolve().parents[1]


class ReferenceChecks(unittest.TestCase):
    def test_repeated_loop_counts(self):
        records = [branch(0x100, 0x80, 'BNE', i, 9) for _ in range(32) for i in range(10)]
        # 288 taken branches; 1-bit misses entry+exit each invocation;
        # 2-bit misses initial training and each of the 32 exits.
        for mode, misses in enumerate((288, 64, 33)):
            model = Predictor(mode)
            self.assertEqual(sum(model.step(b)['flush'] for b in records), misses)

    def test_alternation_is_adversarial(self):
        for mode, misses in enumerate((4, 8, 8)):
            model = Predictor(mode)
            rows = [branch(0x100, 0x80, 'BNE', int(i % 2 == 0), 0) for i in range(8)]
            self.assertEqual(sum(model.step(b)['flush'] for b in rows), misses)

    def test_operand_semantics(self):
        self.assertEqual(branch(0x100, 0x80, 'BEQ', -1, 0xffffffff)['taken'], 1)
        self.assertEqual(branch(0x100, 0x80, 'BNE', 0, 1)['taken'], 1)
        self.assertEqual(branch(0x100, 0x80, 'BEQ', 0, 1)['taken'], 0)

    def test_direction_is_not_next_address(self):
        model = Predictor(2)
        first = model.step(branch(0x100, 0x104, 'BNE', 1, 0))
        self.assertEqual(first['predicted_taken'], 0)
        self.assertEqual(first['flush'], 0)
        model.step(branch(0x100, 0x80, 'BNE', 1, 0))
        changed = model.step(branch(0x100, 0x90, 'BNE', 1, 0))
        self.assertEqual(changed['predicted_taken'], 1)
        self.assertEqual(changed['flush'], 1)

    def test_btb_tag_replacement(self):
        model = Predictor(2)
        for pc, target in ((0x100, 0x80), (0x140, 0xc0)):
            model.step(branch(pc, target, 'BNE', 1, 0))
        row = model.step(branch(0x100, 0x80, 'BNE', 1, 0))
        self.assertEqual(row['btb_hit'], 0)
        self.assertEqual(row['predicted_taken'], 1)
        self.assertEqual(row['flush'], 1)


def run():
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'reports/waveforms').mkdir(parents=True, exist_ok=True)
    rtl = sorted((ROOT/'rtl').glob('*.v'))
    outputs = []
    for name, extra in [('unit', []), ('timing_top', [ROOT/'synth/timing_top.v'])]:
        target = ROOT/'build'/name
        args = ['iverilog', '-g2012', '-s', f'tb_{name}', '-o', str(target), *map(str, rtl+extra), f'tb/tb_{name}.v']
        subprocess.run(args, cwd=ROOT, check=True)
        r = subprocess.run(['vvp', str(target)], cwd=ROOT, text=True, capture_output=True, check=True)
        outputs.append(r.stdout.strip()); print(r.stdout.strip())
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    (ROOT/'reports/unit_checks.json').write_text(json.dumps(dict(status='PASS',
        rtl_output=outputs, python_tests=result.testsRun), indent=2)+'\n')


if __name__ == '__main__':
    run()
