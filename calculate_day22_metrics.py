import os
import csv
import numpy as np

metrics_dir = 'runs/Day_22_VisDrone/metrics'

def get_avg_count(csv_file):
    counts = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row:
                counts.append(int(row[1]))
    return np.mean(counts) if counts else 0

clean_avg = get_avg_count(os.path.join(metrics_dir, 'clean_metrics.csv'))

fault_avgs = []
for file in os.listdir(metrics_dir):
    if file != 'clean_metrics.csv' and file.endswith('.csv'):
        fault_avgs.append(get_avg_count(os.path.join(metrics_dir, file)))

fault_overall_avg = np.mean(fault_avgs)

print(f"Clean average objects per frame: {clean_avg:.2f}")
print(f"Faults overall average objects per frame: {fault_overall_avg:.2f}")
print(f"Clean Lock Rate (Baseline): 100.0%")
print(f"Fault Lock Rate (Relative): {(fault_overall_avg / clean_avg) * 100:.1f}%")
