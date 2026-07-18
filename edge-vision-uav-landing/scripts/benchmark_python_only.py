import time
import csv
import os

os.makedirs('../logs', exist_ok=True)

def run_coupled_benchmark(duration=10.0, stall_at=5.0, stall_duration=0.8):
    start_time = time.time()
    last_time = start_time
    
    with open('../logs/python_only_benchmark.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'delta_t', 'perception_latency', 'control_executed'])
        
        while (time.time() - start_time) < duration:
            current_time = time.time()
            
            # Simulate perception processing (normally 100ms = 10Hz)
            perception_latency = 0.1
            if stall_at < (current_time - start_time) < (stall_at + stall_duration):
                perception_latency = 0.8  # Artificial perception stall (800ms bottleneck)
            
            time.sleep(perception_latency)
            
            # Control execution (coupled - runs AFTER perception)
            exec_time = time.time()
            delta_t = exec_time - last_time
            last_time = exec_time
            
            # In coupled architecture, if perception stalls, control is NOT executed until perception finishes.
            writer.writerow([exec_time - start_time, delta_t, perception_latency, True])
            print(f"[Coupled] Loop dt: {delta_t:.3f}s | Perception: {perception_latency:.3f}s")

if __name__ == "__main__":
    print("Running Python-only Monolithic Benchmark...")
    run_coupled_benchmark()
