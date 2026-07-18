import socket
import time
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Starting Hybrid Perception Mock...")
start_time = time.time()

for i in range(100): # 10 seconds at ~10Hz
    curr = time.time() - start_time
    
    delay = 0.1
    if 5.0 < curr < 6.0:
        delay = 0.8 # Stall for 800ms to simulate CPU overload or heavy detection frame
        print(f"[{curr:.1f}s] [Mock Perception] STALLING for 800ms!")
        
    time.sleep(delay)
    
    payload = {
        "schema_version": "1.0",
        "mission_id": "P1_A_FIXED_ARUCO_LANDING",
        "timestamp_publish_ns": int(time.time() * 1e9),
        "target_found": True,
        "normalized_error": {"x": 0.1, "y": 0.1},
        "detection_latency_ms": delay * 1000
    }
    try:
        sock.sendto(json.dumps(payload).encode('utf-8'), (UDP_IP, UDP_PORT))
    except Exception:
        pass
print("Hybrid Perception Mock finished.")
