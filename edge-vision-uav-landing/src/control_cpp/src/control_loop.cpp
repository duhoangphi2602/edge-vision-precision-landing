#include "control_loop.hpp"
#include <iostream>

namespace control {

ControlLoop::ControlLoop(double rate_hz) : rate_hz_(rate_hz) {
}

void ControlLoop::update(bool target_found, double error_x, double error_y, long long timestamp_ns) {
    if (target_found) {
        // Simple mock logic: just proportional to error for demo purposes
        // In real implementation, this feeds into PID and State Machine
        current_vx_ = static_cast<float>(error_x * 0.5);
        current_vy_ = static_cast<float>(error_y * 0.5);
        current_vz_ = 0.5f; // Descend slowly
    } else {
        current_vx_ = 0.0f;
        current_vy_ = 0.0f;
        current_vz_ = 0.0f;
    }
}

void ControlLoop::get_velocity_commands(float& vx, float& vy, float& vz, float& yaw_rate) const {
    vx = current_vx_;
    vy = current_vy_;
    vz = current_vz_;
    yaw_rate = current_yaw_rate_;
}

void ControlLoop::run() {
    // TODO: Implement main loop
}

} // namespace control
