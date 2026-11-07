#!/usr/bin/env python3
"""
Experiment Analysis Pipeline - Manan
Generates accuracy metrics, CPI analysis, and comparison tables
"""

import json
import csv
from pathlib import Path
from collections import defaultdict

def load_predictions(workload, strategy):
    """Load RTL and oracle predictions for a workload"""
    path = Path(f"reports/raw/{workload}_{strategy}.json")
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def calculate_accuracy(predictions):
    """Calculate prediction accuracy percentage"""
    if not predictions:
        return 0.0
    correct = sum(1 for p in predictions if p.get('correct', False))
    return (correct / len(predictions)) * 100

def calculate_cpi(workload, strategy, recovery_penalty=2):
    """Calculate Cycles Per Instruction"""
    predictions = load_predictions(workload, strategy)
    mispredicts = sum(1 for p in predictions if not p.get('correct', False))
    accuracy = calculate_accuracy(predictions)
    base_cpi = 1.0
    penalty_cpi = (mispredicts / len(predictions)) * recovery_penalty if predictions else 0
    return base_cpi + penalty_cpi

def analyze_workload(workload):
    """Analyze single workload across all strategies"""
    results = {
        'workload': workload,
        'always_not_taken': {},
        '1bit': {},
        '2bit': {}
    }

    for strategy in ['always_not_taken', '1bit', '2bit']:
        predictions = load_predictions(workload, strategy)
        results[strategy]['accuracy'] = calculate_accuracy(predictions)
        results[strategy]['cpi'] = calculate_cpi(workload, strategy)
        results[strategy]['predictions'] = len(predictions)
        results[strategy]['mispredicts'] = sum(1 for p in predictions if not p.get('correct', False))

    return results

def generate_accuracy_table():
    """Generate accuracy comparison table (CSV)"""
    workloads = [
        'smoke', 'always_taken', 'always_not_taken', 'repeated_loop',
        'nested_loops', 'alternating', 'biased_random', 'target_changes',
        'operand_edges', 'target_collisions'
    ]

    with open('reports/accuracy.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Workload', 'ANT (%)', '1-Bit (%)', '2-Bit (%)'])

        for workload in workloads:
            results = analyze_workload(workload)
            writer.writerow([
                workload,
                f"{results['always_not_taken']['accuracy']:.2f}",
                f"{results['1bit']['accuracy']:.2f}",
                f"{results['2bit']['accuracy']:.2f}"
            ])

def generate_cpi_analysis():
    """Generate CPI analysis with improvements"""
    workloads = ['repeated_loop', 'nested_loops', 'biased_random']

    results = []
    for workload in workloads:
        analysis = analyze_workload(workload)
        ant_cpi = analysis['always_not_taken']['cpi']
        improvement_1bit = ((ant_cpi - analysis['1bit']['cpi']) / ant_cpi) * 100
        improvement_2bit = ((ant_cpi - analysis['2bit']['cpi']) / ant_cpi) * 100

        results.append({
            'workload': workload,
            'baseline_cpi': ant_cpi,
            '1bit_cpi': analysis['1bit']['cpi'],
            '2bit_cpi': analysis['2bit']['cpi'],
            'improvement_1bit_pct': improvement_1bit,
            'improvement_2bit_pct': improvement_2bit
        })

    return results

if __name__ == '__main__':
    print("Generating accuracy metrics...")
    generate_accuracy_table()
    print("✓ Saved to reports/accuracy.csv")

    print("Analyzing CPI improvements...")
    cpi_results = generate_cpi_analysis()
    for result in cpi_results:
        print(f"  {result['workload']}: {result['improvement_2bit_pct']:.1f}% CPI improvement")

    print("\nAnalysis complete.")
