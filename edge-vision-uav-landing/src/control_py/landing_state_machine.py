import time
from enum import Enum

class LandingState(Enum):
    INIT = 0
    SEARCH = 1
    ACQUIRE = 2
    ALIGN = 3
    HOLD_ALIGNMENT = 4
    DESCEND = 5
    FINAL_APPROACH = 6
    LAND = 7
    FAILSAFE = 8

class LandingStateMachine:
    def __init__(self, stale_timeout=0.2):
        self.state = LandingState.INIT
        self.stale_timeout = stale_timeout
        self.last_valid_obs_time = 0.0
        self.consecutive_alignments = 0
        
    def update(self, current_time, obs):
        # Check stale
        if current_time - self.last_valid_obs_time > self.stale_timeout:
            self.state = LandingState.FAILSAFE
            return self.state

        if obs is None or not obs.get("target_found", False):
            self.state = LandingState.SEARCH
            return self.state
        
        # State logic
        self.last_valid_obs_time = current_time
        if self.state in [LandingState.INIT, LandingState.SEARCH]:
            self.state = LandingState.ACQUIRE
        elif self.state == LandingState.ACQUIRE:
            self.state = LandingState.ALIGN
        elif self.state == LandingState.ALIGN:
            error = abs(obs.get("error_x", 1.0))
            if error < 0.1:
                self.consecutive_alignments += 1
            else:
                self.consecutive_alignments = 0
            
            if self.consecutive_alignments > 5:
                self.state = LandingState.HOLD_ALIGNMENT
        elif self.state == LandingState.HOLD_ALIGNMENT:
            self.state = LandingState.DESCEND

        return self.state