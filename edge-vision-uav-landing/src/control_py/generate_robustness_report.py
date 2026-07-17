import pandas as pd
import os
import argparse

def generate_report(runs_dir, benchmark_csv, out_file):
    report = "# Day 12: Robustness v0.1 & Latency Report\n\n"
    
    report += "## 1. Latency Benchmark (ONNX vs PyTorch)\n"
    if os.path.exists(benchmark_csv):
        df_bench = pd.read_csv(benchmark_csv)
        report += df_bench.to_markdown(index=False) + "\n\n"
        
        onnx_n = df_bench[(df_bench['Model'] == 'YOLO26n') & (df_bench['Format'] == 'ONNX')]
        if not onnx_n.empty:
            p50 = onnx_n.iloc[0]['P50_Latency_ms']
            if p50 < 100:
                report += f"**Conclusion:** YOLO26n ONNX đạt yêu cầu realtime với P50 = {p50}ms (<100ms).\n\n"
            else:
                report += f"**Conclusion:** YOLO26n ONNX chưa đạt yêu cầu realtime (P50 = {p50}ms).\n\n"
    else:
        report += "Benchmark data not found.\n\n"

    report += "## 2. Controller Failsafe Evaluation (Hybrid SITL)\n"
    for file in os.listdir(runs_dir):
        if file.startswith("robustness_run_") and file.endswith(".csv"):
            df_run = pd.read_csv(os.path.join(runs_dir, file))
            scenario_name = file.replace("robustness_run_", "").replace(".csv", "")
            
            # Kiểm tra xem UAV có bị đâm (descend khi không an toàn) hay không
            # Rule: Không được DESCEND nếu Target không tìm thấy liên tục hoặc quá Stale
            unsafe_descends = df_run[(df_run['state'] == 'DESCEND') & (df_run['error_x'] > 0.5)] # Giả định đơn giản
            
            report += f"### Scenario: {scenario_name}\n"
            report += f"- Total steps simulated: {len(df_run)}\n"
            report += f"- Final Altitude: {df_run.iloc[-1]['altitude']}m\n"
            report += f"- Failsafe Triggered (HOLD/SEARCH state): {'Yes' if 'HOLD_ALIGNMENT' in df_run['state'].values or 'SEARCH' in df_run['state'].values else 'No'}\n"
            report += "\n"

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write(report)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", required=True)
    parser.add_argument("--benchmark_csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    generate_report(args.runs_dir, args.benchmark_csv, args.out)
