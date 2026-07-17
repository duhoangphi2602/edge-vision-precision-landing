#include "pid_controller.hpp"
#include <cmath>
#include <algorithm>

namespace control {

PIDController::PIDController(double kp, double ki, double kd, double v_max, double deadband, double alpha) 
    : kp_(kp), ki_(ki), kd_(kd), v_max_(v_max), deadband_(deadband), alpha_(alpha) {
    reset();
}

void PIDController::reset() {
    integral_ = 0.0;
    prev_error_ = 0.0;
    prev_derivative_ = 0.0;
    is_first_run_ = true;
}

double PIDController::compute(double error, double dt) {
    if (dt <= 0.0) {
        return 0.0;
    }

    if (std::abs(error) < deadband_) {
        error = 0.0;
    }

    double p_term = kp_ * error;

    double raw_derivative = 0.0;
    if (is_first_run_) {
        raw_derivative = 0.0;
        is_first_run_ = false;
    } else {
        raw_derivative = (error - prev_error_) / dt;
    }

    double derivative = alpha_ * raw_derivative + (1.0 - alpha_) * prev_derivative_;
    double d_term = kd_ * derivative;

    double pre_cmd = p_term + d_term + ki_ * (integral_ + error * dt);

    if (std::abs(pre_cmd) < v_max_ || (pre_cmd > 0 && error < 0) || (pre_cmd < 0 && error > 0)) {
        integral_ += error * dt;
    }

    double i_term = ki_ * integral_;
    double cmd = p_term + i_term + d_term;

    double cmd_clamped = std::max(-v_max_, std::min(v_max_, cmd));

    prev_error_ = error;
    prev_derivative_ = derivative;

    return cmd_clamped;
}

} // namespace control
