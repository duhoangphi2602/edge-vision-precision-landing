#include "udp_receiver.hpp"
#include "control_loop.hpp"
#include "mavlink_builder.hpp"
#include <iostream>
#include <chrono>
#include <thread>
#include <csignal>

bool running = true;

void signal_handler(int signum) {
    std::cout << "\n[CTRL-C] Interrupt signal (" << signum << ") received. Graceful shutdown...\n";
    running = false;
}

int main() {
    signal(SIGINT, signal_handler);
    
    UdpReceiver receiver(5005);
    control::ControlLoop loop(30.0);
    control::MavlinkBuilder mav_builder(1, 1);
    
    std::cout << "[INFO] Control node started. Listening on UDP 5005...\n";
    
    while(running) {
        PerceptionObservation obs;
        bool has_data = receiver.get_latest_observation(obs);
        
        long long current_time_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
            
        loop.update(obs.target_found, obs.error_x, obs.error_y, current_time_ns);
        
        float vx, vy, vz, yaw_rate;
        loop.get_velocity_commands(vx, vy, vz, yaw_rate);
        
        if (has_data) {
            std::cout << "[IPC-LOG] Data Rcvd -> ErrorX: " << obs.error_x << " ErrorY: " << obs.error_y 
                      << " | Cmd -> Vx: " << vx << " Vy: " << vy << " Vz: " << vz << "\n";
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(33)); // ~30Hz
    }
    std::cout << "[INFO] Control node stopped cleanly.\n";
    return 0;
}
