#include "mavlink_builder.hpp"
#include <iostream>
#include <cassert>

using namespace control;

int main() {
    MavlinkBuilder builder(1, 1); // target_sys=1, target_comp=1
    
    // Giả lập output của StateMachine & PID: Descending, vx=0.1, vy=-0.2, vz=0.5, yaw_rate=0.0
    auto msg = builder.build_velocity_command(100.5, 0.1, -0.2, 0.5, 0.0);
    
    assert(msg.time_boot_ms == 100500);
    assert(msg.coordinate_frame == 1);
    assert(msg.vx == 0.1f);
    assert(msg.vy == -0.2f);
    assert(msg.vz == 0.5f);
    // Mask logic verification
    assert((msg.type_mask & 0x0007) == 0x0007); // position ignored
    
    std::cout << builder.to_command_log(msg) << std::endl;
    std::cout << "MAVLink Bridge tests PASSED!" << std::endl;
    return 0;
}
