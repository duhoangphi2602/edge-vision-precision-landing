#pragma once

#include <cstdint>

namespace control {

// MAVLink LANDING_TARGET (ID #149)
struct LandingTargetMsg {
    uint64_t time_usec;
    float angle_x;          // X-axis angular offset of the target from the center of the image
    float angle_y;          // Y-axis angular offset of the target from the center of the image
    float distance;         // Distance to the target from the vehicle
    float size_x;           // Size of the target along x-axis
    float size_y;           // Size of the target along y-axis
    uint8_t target_num;     // Target ID
    uint8_t frame;          // Coordinate frame (e.g., MAV_FRAME_BODY_FRD)
};

// MAVLink SET_POSITION_TARGET_LOCAL_NED (ID #84)
struct SetPositionTargetLocalNedMsg {
    uint32_t time_boot_ms;
    uint8_t target_system;
    uint8_t target_component;
    uint8_t coordinate_frame; // MAV_FRAME_LOCAL_NED
    uint16_t type_mask;       // Bitmask to indicate which dimensions should be ignored
    float x, y, z;            // Position (m)
    float vx, vy, vz;         // Velocity (m/s)
    float afx, afy, afz;      // Acceleration
    float yaw;                // Yaw setpoint
    float yaw_rate;           // Yaw rate setpoint
};

} // namespace control
