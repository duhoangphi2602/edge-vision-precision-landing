import socket
import json
import time

class UDPReceiver:
    def __init__(self, ip="127.0.0.1", port=5000, stale_threshold_s=0.2):
        self.ip = ip
        self.port = port
        self.stale_threshold_ns = int(stale_threshold_s * 1e9)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.setblocking(False)
        self.last_seq = -1

    def get_latest_observation(self):
        latest_data = None
        # Drain the buffer for latest observation (bounded queue behavior essentially dropping older packets in OS buffer)
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                latest_data = data
            except BlockingIOError:
                break
            except Exception as e:
                break
        
        if not latest_data:
            return None, "NO_DATA"
            
        try:
            obs = json.loads(latest_data.decode('utf-8'))
        except json.JSONDecodeError:
            return None, "MALFORMED"
            
        if "schema_version" not in obs or "sequence_id" not in obs:
            return None, "MALFORMED"
            
        # Out of order check
        if obs["sequence_id"] <= self.last_seq:
            return None, "OUT_OF_ORDER"
            
        self.last_seq = obs["sequence_id"]
        
        # Stale check
        now_ns = time.time_ns()
        publish_time = obs.get("timestamp_publish_ns", 0)
        if (now_ns - publish_time) > self.stale_threshold_ns:
            return obs, "STALE"
            
        return obs, "VALID"
