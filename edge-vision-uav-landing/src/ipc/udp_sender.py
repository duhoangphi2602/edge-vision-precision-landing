import socket
import json
import time

class UDPSender:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence_id = 0

    def send_observation(self, obs_data):
        self.sequence_id += 1
        obs_data["sequence_id"] = self.sequence_id
        obs_data["schema_version"] = "1.0"
        if "timestamp_publish_ns" not in obs_data:
            obs_data["timestamp_publish_ns"] = time.time_ns()
        
        payload = json.dumps(obs_data).encode('utf-8')
        self.sock.sendto(payload, (self.ip, self.port))
