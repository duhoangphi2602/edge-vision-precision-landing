#include "failsafe.hpp"
#include "state_machine.hpp"
#include <iostream>
#include <cassert>

using namespace control;

void test_failsafe() {
    FailsafeManager fm(0, 0.2); // ID 0, 200ms
    double current_time = 1e9; // 1 second
    
    Observation obs_good = {current_time - 0.05e9, current_time, true, 0, true};
    assert(fm.check_observation(obs_good, current_time) == FailsafeReason::NONE);
    
    Observation obs_stale = {current_time - 0.25e9, current_time, true, 0, true};
    assert(fm.check_observation(obs_stale, current_time) == FailsafeReason::STALE_OBSERVATION);
    
    Observation obs_wrong_id = {current_time - 0.05e9, current_time, true, 1, true};
    assert(fm.check_observation(obs_wrong_id, current_time) == FailsafeReason::WRONG_MARKER_ID);
}

void test_statemachine() {
    LandingStateMachine sm;
    assert(sm.get_state() == LandingState::INIT);
    
    sm.update(FailsafeReason::NONE, 0.5, 0.5, 5.0, 0.1);
    assert(sm.get_state() == LandingState::SEARCH);
    
    // Test target lost fallback
    sm.update(FailsafeReason::TARGET_LOST, 0, 0, 5.0, 0.1);
    assert(sm.get_state() == LandingState::SEARCH);
    
    // Force to Hold and test transition
    sm.force_state(LandingState::HOLD_ALIGNMENT);
    sm.update(FailsafeReason::NONE, 0.0, 0.0, 2.0, 1.5);
    assert(sm.get_state() == LandingState::DESCEND);
}

int main() {
    test_failsafe();
    test_statemachine();
    std::cout << "Failsafe and State Machine Unit Tests PASSED!" << std::endl;
    return 0;
}
