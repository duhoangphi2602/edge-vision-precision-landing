#!/usr/bin/env python3
import time
import random
import argparse

class RuntimeFaultInjector:
    def __init__(self, drop_rate=0.0, delay_ms=0, jitter_ms=0, seed=42):
        self.drop_rate = drop_rate
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.rng = random.Random(seed)
        
    def should_drop(self):
        if self.drop_rate <= 0:
            return False
        return self.rng.random() < self.drop_rate
        
    def apply_delay(self):
        delay = self.delay_ms
        if self.jitter_ms > 0:
            delay += self.rng.uniform(-self.jitter_ms, self.jitter_ms)
        if delay > 0:
            time.sleep(delay / 1000.0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate runtime streaming faults (demo)")
    parser.add_argument("--drop-rate", type=float, default=0.0)
    parser.add_argument("--delay-ms", type=float, default=0.0)
    parser.add_argument("--jitter-ms", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    injector = RuntimeFaultInjector(args.drop_rate, args.delay_ms, args.jitter_ms, args.seed)
    
    print(f"[INFO] Initialized RuntimeFaultInjector with drop={args.drop_rate}, delay={args.delay_ms}ms, jitter={args.jitter_ms}ms, seed={args.seed}")
    
    # Simulate a stream
    for i in range(10):
        if injector.should_drop():
            print(f"Frame {i} DROPPED")
        else:
            start = time.time()
            injector.apply_delay()
            elapsed = (time.time() - start) * 1000
            print(f"Frame {i} DELIVERED (Delayed {elapsed:.1f}ms)")
