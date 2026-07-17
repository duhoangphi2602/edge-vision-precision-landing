#pragma once

namespace control {
class PIDController {
public:
    PIDController(double kp, double ki, double kd, double v_max, double deadband = 0.05, double alpha = 0.5);
    
    void reset();
    double compute(double error, double dt);

private:
    double kp_, ki_, kd_;
    double v_max_, deadband_, alpha_;
    double integral_, prev_error_, prev_derivative_;
    bool is_first_run_;
};
} // namespace control
