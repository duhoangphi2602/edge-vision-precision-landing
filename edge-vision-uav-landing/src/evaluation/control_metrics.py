import numpy as np

def calculate_overshoot(history_x, target=0.0):
    if not history_x: return 0.0
    initial = history_x[0]
    if initial == target: return 0.0
    
    # Nếu đi từ dương về 0, lố là phần âm sâu nhất. Ngược lại.
    if initial > target:
        min_val = min(history_x)
        if min_val >= target: return 0.0
        return abs(min_val - target) / abs(initial - target) * 100.0
    else:
        max_val = max(history_x)
        if max_val <= target: return 0.0
        return abs(max_val - target) / abs(initial - target) * 100.0

def calculate_settling_time(history_x, dt, target=0.0, threshold=0.05):
    for i in range(len(history_x)-1, -1, -1):
        if abs(history_x[i] - target) > threshold:
            if i == len(history_x) - 1: return float('inf') # Không hội tụ
            return (i + 1) * dt
    return 0.0