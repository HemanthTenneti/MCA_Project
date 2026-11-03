#!/usr/bin/env python3
"""Generate committed, deterministic workloads; derive every BEQ/BNE outcome."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261018


def branch(pc, target, op, lhs, rhs, instructions_before=3):
    lhs, rhs = lhs & 0xffffffff, rhs & 0xffffffff
    assert op in ('BEQ', 'BNE')
    taken = int((lhs == rhs) if op == 'BEQ' else (lhs != rhs))
    assert pc % 4 == 0 and target % 4 == 0
    assert instructions_before >= 0
    return dict(pc=pc, target=target, op=op, lhs=lhs, rhs=rhs,
                taken=taken, instructions_before=instructions_before)


def pattern(outcomes, pc=0x100, target=0x80):
    return [branch(pc, target, 'BNE', int(t), 0) for t in outcomes]


def generate():
    rng = random.Random(SEED)
    workloads = {
        'always_not_taken': pattern([0] * 128),
        'always_taken': pattern([1] * 128),
        'repeated_loop': [branch(0x100, 0x80, 'BNE', i + 1, 10, 4)
                          for _ in range(32) for i in range(10)],
        'alternating': [branch(0x100, 0x80, 'BEQ', i % 2, 0) for i in range(256)],
        'biased_random': pattern([rng.random() < 0.8 for _ in range(512)]),
    }
    nested = []
    for _ in range(8):
        for outer in range(6):
            nested += [branch(0x110, 0xc0, 'BNE', inner + 1, 8, 2) for inner in range(8)]
            nested.append(branch(0x120, 0xa0, 'BNE', outer + 1, 6, 2))
    workloads['nested_loops'] = nested
    # +0x100 aliases both BHT and BTB; opposing outcomes expose interference.
    workloads['bht_collisions'] = [b for _ in range(128) for b in (
        branch(0x100, 0x80, 'BEQ', 7, 7), branch(0x200, 0x180, 'BNE', 7, 7))]
    # +0x40 aliases BTB only; BHT counters can learn both branches.
    workloads['btb_collisions'] = [b for _ in range(128) for b in (
        branch(0x100, 0x80, 'BNE', 1, 0), branch(0x140, 0xc0, 'BEQ', 5, 5))]
    workloads['target_changes'] = [branch(0x100, 0x80 if i < 32 else 0x90, 'BNE', 1, 0)
                                   for i in range(64)]
    # Equal operands after 32-bit masking exercise both instruction semantics.
    workloads['operand_edges'] = [branch(0x104, 0x60, op, lhs, rhs, 1)
        for _ in range(8) for op in ('BEQ', 'BNE')
        for lhs, rhs in ((0, 0), (0xffffffff, -1), (0x80000000, 0), (1, 2))]
    trace_dir = ROOT / 'traces'
    trace_dir.mkdir(exist_ok=True)
    manifest = {'schema_version': 1, 'seed': SEED, 'workloads': {}}
    for name, records in workloads.items():
        manifest['workloads'][name] = {
            'total_instructions': sum(1 + b['instructions_before'] for b in records),
            'branch_count': len(records), 'records': records,
        }
        (trace_dir / f'{name}.mem').write_text(''.join(
            f"{b['pc']:08x} {b['taken']} {b['target']:08x}\n" for b in records))
    (trace_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Generated {len(workloads)} workloads, {sum(map(len, workloads.values()))} branches; seed={SEED}')


if __name__ == '__main__':
    generate()
