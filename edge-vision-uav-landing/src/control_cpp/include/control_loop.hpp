#pragma once

namespace control {
class ControlLoop {
public:
    ControlLoop(double rate_hz);
    void update(bool target_found, double error_x, double error_y, long long timestamp_ns);
    void get_velocity_commands(float& vx, float& vy, float& vz, float& yaw_rate) const;
    void run();
private:
    double rate_hz_;
    float current_vx_ = 0.0f;
    float current_vy_ = 0.0f;
    float current_vz_ = 0.0f;
    float current_yaw_rate_ = 0.0f;
};
} // namespace control
