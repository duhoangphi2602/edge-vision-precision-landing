import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import time
import json
import socket
import csv
import numpy as np
from src.ipc.udp_sender import UDPSender
from src.ipc.udp_receiver import UDPReceiver

def test_corner_cases():
    receiver = UDPReceiver(port=5001)
    sender = UDPSender(port=5001)
    
    # 1. Normal
    sender.send_observation({"data": "valid"})
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "VALID", f"Expected VALID, got {status}"
    
    # 2. Out of order (send seq 1 manually after normal send which bumped seq)
    old_obs = {"sequence_id": 1, "schema_version": "1.0", "timestamp_publish_ns": time.time_ns()}
    sender.sock.sendto(json.dumps(old_obs).encode(), ("127.0.0.1", 5001))
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "OUT_OF_ORDER", f"Expected OUT_OF_ORDER, got {status}"
    
    # 3. Malformed
    sender.sock.sendto(b"malformed_string_not_json", ("127.0.0.1", 5001))
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "MALFORMED", f"Expected MALFORMED, got {status}"
    
    # 4. Stale
    stale_obs = {"schema_version": "1.0", "sequence_id": 100, "timestamp_publish_ns": time.time_ns() - int(0.3 * 1e9)}
    sender.sock.sendto(json.dumps(stale_obs).encode(), ("127.0.0.1", 5001))
    time.sleep(0.01)
    obs, status = receiver.get_latest_observation()
    assert status == "STALE", f"Expected STALE, got {status}"

    print("All corner case tests passed.")

def benchmark_ipc():
    receiver = UDPReceiver(port=5002)
    sender = UDPSender(port=5002)
    latencies = []
    
    print("Running latency benchmark (1000 packets)...")
    for i in range(1000):
        start_ns = time.time_ns()
        sender.send_observation({"test": "data"})
        
        # busy wait until received for benchmark precision
        while True:
            obs, status = receiver.get_latest_observation()
            if status == "VALID":
                end_ns = time.time_ns()
                latencies.append((end_ns - start_ns) / 1e6) # ms
                break
            time.sleep(0.0001)
            
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    
    print(f"IPC Latency - P50: {p50:.3f} ms, P95: {p95:.3f} ms")
    
    import os
    os.makedirs("../../reports", exist_ok=True)
    with open("../../reports/ipc_benchmark.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value_ms"])
        writer.writerow(["P50_latency", f"{p50:.3f}"])
        writer.writerow(["P95_latency", f"{p95:.3f}"])
    print("Benchmark saved to reports/ipc_benchmark.csv")

if __name__ == "__main__":
    test_corner_cases()
    benchmark_ipc()
