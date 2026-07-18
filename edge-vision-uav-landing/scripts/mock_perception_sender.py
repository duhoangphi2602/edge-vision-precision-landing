import socket
import time
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Sending Mock Perception JSON to {UDP_IP}:{UDP_PORT}")

try:
    for i in range(100):
        # Simulate moving towards center
        err_x = 0.5 - (i * 0.005)
        
        payload = {
            "schema_version": "1.0",
            "mission_id": "P1_A_FIXED_ARUCO_LANDING",
            "timestamp_publish_ns": int(time.time() * 1e9),
            "target_found": True,
            "normalized_error": {"x": err_x, "y": 0.1},
            "detection_latency_ms": 12.5
        }
        
        sock.sendto(json.dumps(payload).encode('utf-8'), (UDP_IP, UDP_PORT))
        time.sleep(0.1) # 10Hz
        
except KeyboardInterrupt:
    print("Stopped sender.")
