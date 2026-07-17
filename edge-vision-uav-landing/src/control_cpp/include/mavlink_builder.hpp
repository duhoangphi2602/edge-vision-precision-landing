#pragma once

#include "mavlink_messages.hpp"
#include "state_machine.hpp"
#include <string>

namespace control {

class MavlinkBuilder {
public:
    MavlinkBuilder(uint8_t target_sys, uint8_t target_comp);

    // Xây dựng bản tin vận tốc (velocity setpoint)
    SetPositionTargetLocalNedMsg build_velocity_command(
        double current_time_sec,
        double vx, double vy, double vz, double yaw_rate
    ) const;

    // In ra string command log để test không cần truyền UDP
    std::string to_command_log(const SetPositionTargetLocalNedMsg& msg) const;

private:
    uint8_t target_system_;
    uint8_t target_component_;
};

} // namespace control
