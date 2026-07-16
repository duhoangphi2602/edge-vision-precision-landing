import json

class TrackingEvaluator:
    def __init__(self):
        self.target_switches = 0
        self.frames_lost = 0
        self.frames_total = 0
        self.last_target_id = None
        
    def add_observation(self, obs):
        self.frames_total += 1
        
        state = obs.get("tracking_state")
        target_id = obs.get("target_id")
        
        if state in ["LOST", "OCCLUDED"]:
            self.frames_lost += 1
            
        if target_id is not None:
            if self.last_target_id is not None and target_id != self.last_target_id:
                self.target_switches += 1
            self.last_target_id = target_id
            
    def get_metrics(self):
        return {
            "target_switches": self.target_switches,
            "lost_frame_rate": self.frames_lost / max(1, self.frames_total),
            "frames_total": self.frames_total
        }

if __name__ == "__main__":
    # Smoke test
    evaluator = TrackingEvaluator()
    evaluator.add_observation({"tracking_state": "LOCKED", "target_id": 1})
    evaluator.add_observation({"tracking_state": "LOST", "target_id": 1})
    evaluator.add_observation({"tracking_state": "REACQUIRED", "target_id": 2})
    metrics = evaluator.get_metrics()
    print("Evaluator Test Metrics:", metrics)
    assert metrics["target_switches"] == 1
    assert metrics["lost_frame_rate"] == 1/3
    print("Evaluator logic works.")
