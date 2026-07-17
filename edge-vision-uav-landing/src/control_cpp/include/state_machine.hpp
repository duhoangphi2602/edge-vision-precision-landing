#pragma once

#include "failsafe.hpp"

namespace control {

enum class LandingState {
    INIT,
    SEARCH,
    ACQUIRE,
    ALIGN,
    HOLD_ALIGNMENT,
    DESCEND,
    FINAL_APPROACH,
    LAND,
    FAILSAFE
};

class LandingStateMachine {
public:
    LandingStateMachine();
    
    LandingState update(FailsafeReason failsafe_status, double error_x, double error_y, double altitude, double dt);
    
    LandingState get_state() const { return current_state_; }
    void force_state(LandingState s) { current_state_ = s; }

private:
    LandingState current_state_;
    double alignment_timer_;
    int consecutive_valid_frames_;
    
    // Config parameters (could be injected)
    double align_threshold_ = 0.1; 
    double hold_time_req_ = 1.0;
    int acquire_frames_req_ = 5;
    double descend_alt_ = 1.0;
    double land_alt_ = 0.2;
};

} // namespace control
