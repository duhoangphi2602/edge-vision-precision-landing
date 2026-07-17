#pragma once

namespace control {
class PIDController {
public:
    PIDController(double kp, double ki, double kd);
    double compute(double setpoint, double current_value, double dt);
private:
    double kp_, ki_, kd_;
    double integral_, prev_error_;
};
} // namespace control
