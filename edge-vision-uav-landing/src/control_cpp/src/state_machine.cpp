#include "state_machine.hpp"
#include <cmath>
#include <algorithm>

namespace control {

LandingStateMachine::LandingStateMachine() 
    : current_state_(LandingState::INIT), alignment_timer_(0.0), consecutive_valid_frames_(0) {}

LandingState LandingStateMachine::update(FailsafeReason failsafe_status, double error_x, double error_y, double altitude, double dt) {
    // If we have a critical failsafe, force abort/failsafe unless we are already searching
    if (failsafe_status != FailsafeReason::NONE) {
        if (failsafe_status == FailsafeReason::TARGET_LOST || failsafe_status == FailsafeReason::STALE_OBSERVATION) {
            consecutive_valid_frames_ = 0;
            alignment_timer_ = 0.0;
            if (current_state_ != LandingState::LAND) {
                current_state_ = LandingState::SEARCH;
                return current_state_;
            }
        } else {
            current_state_ = LandingState::FAILSAFE;
            return current_state_;
        }
    }

    // Target is valid and recent
    consecutive_valid_frames_++;
    double error_mag = std::sqrt(error_x*error_x + error_y*error_y);

    switch (current_state_) {
        case LandingState::INIT:
            current_state_ = LandingState::SEARCH;
            break;
            
        case LandingState::SEARCH:
            if (consecutive_valid_frames_ >= acquire_frames_req_) {
                current_state_ = LandingState::ACQUIRE;
            }
            break;
            
        case LandingState::ACQUIRE:
            current_state_ = LandingState::ALIGN;
            break;
            
        case LandingState::ALIGN:
            if (error_mag < align_threshold_) {
                current_state_ = LandingState::HOLD_ALIGNMENT;
                alignment_timer_ = 0.0;
            }
            break;
            
        case LandingState::HOLD_ALIGNMENT:
            if (error_mag >= align_threshold_) {
                current_state_ = LandingState::ALIGN;
            } else {
                alignment_timer_ += dt;
                if (alignment_timer_ >= hold_time_req_) {
                    current_state_ = LandingState::DESCEND;
                }
            }
            break;
            
        case LandingState::DESCEND:
            if (error_mag >= align_threshold_ * 2.0) { // Hysteresis
                current_state_ = LandingState::ALIGN;
            } else if (altitude < descend_alt_) {
                current_state_ = LandingState::FINAL_APPROACH;
            }
            break;
            
        case LandingState::FINAL_APPROACH:
            if (altitude < land_alt_) {
                current_state_ = LandingState::LAND;
            }
            break;
            
        case LandingState::LAND:
        case LandingState::FAILSAFE:
            // Terminal states
            break;
    }
    
    return current_state_;
}

} // namespace control
