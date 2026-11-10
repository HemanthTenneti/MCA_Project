#!/usr/bin/env python3
"""Readable walkthrough from verified RTL output; --details shows predictor states."""
import argparse
import csv
import json
from pathlib import Path
from presentation import STRATEGIES, heading, state_name, table

ROOT = Path(__file__).resolve().parents[1]


def main(details=False):
    summary = [r for r in csv.DictReader((ROOT/'reports/accuracy.csv').open()) if r['workload'] == 'repeated_loop']
    workload = json.loads((ROOT/'traces/manifest.json').read_text())['workloads']['repeated_loop']
    print('\n' + heading('DYNAMIC BRANCH PREDICTION'))
    print('A repeated-loop walkthrough\n')
    print('The same loop runs 32 times. Each run takes the branch nine times, then exits.')
    print(f"We compare all three predictors on {len(workload['records']):,} branches and {workload['total_instructions']:,} instructions.\n")
    print(heading('How well did each predictor do?'))
    print(table(['Strategy', 'Correct next address', 'Redirects', 'Estimated CPI'], [
        [STRATEGIES[r['strategy']], f"{int(r['next_address_correct']):,}/{int(r['branches']):,} ({float(r['next_address_accuracy']):.2%})",
         f"{int(r['recoveries']):,}", f"{float(r['estimated_cpi']):.5f}"] for r in summary], right=(1,2,3)))
    baseline = next(r for r in summary if r['strategy'] == 'always_not_taken')
    best = next(r for r in summary if r['strategy'] == 'two_bit')
    saved = int(baseline['recoveries']) - int(best['recoveries'])
    print(f'\nThe 2-bit predictor avoids {saved:,} redirects compared with the baseline on this loop.')
    print('A redirect means the saved next address was wrong and recovery was needed.\n')
    print(heading('Watch the first loop exit'))
    print('Each cell says whether the saved next-address prediction was correct.\n')
    raw = {mode: list(csv.DictReader((ROOT/'reports/raw'/f'repeated_loop_{mode}.csv').open()))[:12]
           for mode in STRATEGIES}
    rows = []
    for i, branch in enumerate(workload['records'][:12]):
        actual = 'Exit loop' if not branch['taken'] else 'Take branch'
        verdicts = ['Redirect' if int(raw[mode][i]['flush']) else 'Correct' for mode in STRATEGIES]
        rows.append([i+1, actual, *verdicts])
    print(table(['Visit', 'Actual outcome', 'Always not taken', '1-bit', '2-bit'], rows, right=(0,)))
    print('\nThe 1-bit predictor changes to not taken at the exit, then misses the next loop entry.')
    print('The 2-bit predictor stays weakly taken after the exit and gets the next entry right.')
    if details:
        for mode in STRATEGIES:
            print('\n' + heading(STRATEGIES[mode] + ' state and address details'))
            print(table(['Visit', 'State before update', 'Direction', 'Target', 'Saved next PC', 'Recovery'], [
                [i+1, state_name(mode, int(r['state'])), 'Taken' if int(r['predicted_taken']) else 'Not taken',
                 'Hit' if int(r['btb_hit']) else 'Miss', f"0x{int(r['predicted_next_pc'],16):04X}",
                 'Redirect' if int(r['flush']) else 'None'] for i,r in enumerate(raw[mode])], right=(0,)))
    print('\n' + heading('How to read the numbers'))
    print('CPI means cycles per instruction; a lower estimate is better.')
    print(f"This model uses base CPI {float(summary[0]['base_cpi']):g} and {summary[0]['recovery_penalty']} extra cycles per redirect.")
    print('These are analytical estimates. The harness is not a complete CPU.')
    print('Alternating outcomes are a counterexample: both dynamic predictors lose to the baseline.')
    print('\nExplore all workloads: reports/results.html')
    print('Show counter states:  python3 scripts/demo.py --details\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--details', action='store_true', help='Show human-readable counter states and next addresses')
    args = parser.parse_args()
    main(args.details)
