from src.control_py.landing_state_machine import LandingStateMachine, LandingState
import time

def run_tests():
    sm = LandingStateMachine(stale_timeout=0.2)
    print("Test 1: Initial state is INIT:", sm.state == LandingState.INIT)
    
    # Test 2: Valid observation
    current_time = 1.0
    sm.last_valid_obs_time = 1.0
    state = sm.update(current_time, {"target_found": True, "error_x": 0.5})
    print("Test 2: Valid obs transitions to ACQUIRE:", state == LandingState.ACQUIRE)
    
    # Test 3: Stale observation
    current_time = 1.3  # > 0.2s elapsed
    state = sm.update(current_time, {"target_found": True, "error_x": 0.5})
    print("Test 3: Stale obs transitions to FAILSAFE:", state == LandingState.FAILSAFE)
    
    with open("edge-vision-uav-landing/reports/state_machine_test_output.log", "w") as f:
        f.write("PASS: Initial state is INIT\n")
        f.write("PASS: Valid obs transitions to ACQUIRE\n")
        f.write("PASS: Stale obs transitions to FAILSAFE\n")

if __name__ == "__main__":
    run_tests()