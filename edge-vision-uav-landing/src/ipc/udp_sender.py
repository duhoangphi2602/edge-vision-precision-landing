import socket
import json
import time

class UDPSender:
    def __init__(self, ip="127.0.0.1", port=5005):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def send_observation(self, observation_dict):
        # Update publish timestamp
        observation_dict["timestamp_publish_ns"] = time.time_ns()
        message = json.dumps(observation_dict).encode('utf-8')
        self.sock.sendto(message, (self.ip, self.port))

if __name__ == "__main__":
    sender = UDPSender()
    dummy_data = {
        "schema_version": "1.0",
        "timestamp_capture_ns": time.time_ns(),
        "normalized_error": {"x": 0.01, "y": -0.01},
        "pose_valid": True
    }
    while True:
        dummy_data["timestamp_capture_ns"] = time.time_ns()
        sender.send_observation(dummy_data)
        print("Đã gửi observation!")
        time.sleep(0.1) # 10Hz