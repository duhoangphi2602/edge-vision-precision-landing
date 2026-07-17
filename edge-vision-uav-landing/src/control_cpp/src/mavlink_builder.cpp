#include "mavlink_builder.hpp"
#include <sstream>

namespace control {

MavlinkBuilder::MavlinkBuilder(uint8_t target_sys, uint8_t target_comp)
    : target_system_(target_sys), target_component_(target_comp) {}

SetPositionTargetLocalNedMsg MavlinkBuilder::build_velocity_command(
    double current_time_sec,
    double vx, double vy, double vz, double yaw_rate) const 
{
    SetPositionTargetLocalNedMsg msg;
    msg.time_boot_ms = static_cast<uint32_t>(current_time_sec * 1000.0);
    msg.target_system = target_system_;
    msg.target_component = target_component_;
    // MAV_FRAME_LOCAL_NED = 1
    msg.coordinate_frame = 1; 
    
    // Ignore Position (bit 0-2), Accel (bit 6-8), Yaw (bit 10). 
    // Enable Velocity (bit 3-5 is 0) and Yaw Rate (bit 11 is 0).
    // Type mask: 0b0000_0101_1100_0111 = 0x05C7
    msg.type_mask = 0x0400 | 0x01C0 | 0x0007; 

    msg.x = 0; msg.y = 0; msg.z = 0;
    msg.vx = static_cast<float>(vx);
    msg.vy = static_cast<float>(vy);
    msg.vz = static_cast<float>(vz);
    msg.afx = 0; msg.afy = 0; msg.afz = 0;
    msg.yaw = 0;
    msg.yaw_rate = static_cast<float>(yaw_rate);

    return msg;
}

std::string MavlinkBuilder::to_command_log(const SetPositionTargetLocalNedMsg& msg) const {
    std::stringstream ss;
    ss << "[CMD-LOG] Time: " << msg.time_boot_ms << " ms | "
       << "Mode: VELOCITY | "
       << "Vx: " << msg.vx << " Vy: " << msg.vy << " Vz: " << msg.vz 
       << " | YawRate: " << msg.yaw_rate << " | Mask: 0x" << std::hex << msg.type_mask;
    return ss.str();
}

} // namespace control
