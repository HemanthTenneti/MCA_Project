"""Shared, dependency-free labels and tables for reader-facing output."""
import os
import sys

STRATEGIES = {'always_not_taken': 'Always not taken', 'one_bit': '1-bit predictor', 'two_bit': '2-bit predictor'}
WORKLOADS = {
    'always_not_taken': 'Always not taken', 'always_taken': 'Always taken',
    'repeated_loop': 'Repeated loop', 'alternating': 'Alternating outcomes',
    'biased_random': 'Mostly taken random branches', 'nested_loops': 'Nested loops',
    'bht_collisions': 'History table collisions', 'btb_collisions': 'Target buffer collisions',
    'target_changes': 'Changing targets', 'operand_edges': 'BEQ and BNE operand checks',
}


def heading(text):
    if sys.stdout.isatty() and 'NO_COLOR' not in os.environ:
        return f'\033[1;36m{text}\033[0m'
    return text


def table(headers, rows, right=()):
    data = [[str(c) for c in row] for row in [headers, *rows]]
    widths = [max(len(row[i]) for row in data) for i in range(len(headers))]
    def line(row):
        return '  '.join(value.rjust(widths[i]) if i in right else value.ljust(widths[i])
                         for i, value in enumerate(row)).rstrip()
    return '\n'.join([line(data[0]), '  '.join('-' * w for w in widths), *map(line, data[1:])])


def state_name(mode, value):
    if mode == 'always_not_taken':
        return 'Fixed prediction'
    if mode == 'one_bit':
        return 'Last was taken' if value else 'Last was not taken'
    return ('Strong not taken', 'Weak not taken', 'Weak taken', 'Strong taken')[value]
