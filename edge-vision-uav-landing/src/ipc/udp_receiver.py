import socket
import json
import time

class UDPReceiver:
    def __init__(self, ip="127.0.0.1", port=5005, stale_threshold_ms=200):
        self.ip = ip
        self.port = port
        self.stale_threshold_ms = stale_threshold_ms
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(0.5) # timeout tránh block hoàn toàn

    def receive_latest(self):
        latest_data = None
        try:
            # Rút cạn buffer để luôn lấy gói tin mới nhất (Drop gói cũ nếu kẹt)
            while True:
                data, _ = self.sock.recvfrom(4096)
                latest_data = data
        except socket.timeout:
            pass
        except BlockingIOError:
            pass

        if latest_data:
            obs = json.loads(latest_data.decode('utf-8'))
            current_ns = time.time_ns()
            latency_ms = (current_ns - obs.get("timestamp_capture_ns", current_ns)) / 1e6
            
            if latency_ms > self.stale_threshold_ms:
                print(f"[FAILSAFE] Dữ liệu quá cũ ({latency_ms:.1f}ms > {self.stale_threshold_ms}ms)")
                return None
            return obs
        return None

if __name__ == "__main__":
    receiver = UDPReceiver()
    receiver.sock.setblocking(False)
    print("Đang chờ UDP data ở port 5005...")
    while True:
        obs = receiver.receive_latest()
        if obs:
            print(f"Nhận observation hợp lệ! Normalized Error: {obs['normalized_error']}")
        time.sleep(0.02) # 50Hz control loop logic