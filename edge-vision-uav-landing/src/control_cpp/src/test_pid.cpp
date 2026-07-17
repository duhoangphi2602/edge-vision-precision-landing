#include "pid_controller.hpp"
#include <iostream>
#include <cmath>
#include <cassert>

using namespace control;

void test_pid_basic() {
    PIDController pid(1.0, 0.1, 0.05, 2.0, 0.05, 0.5);
    
    // dt <= 0.0 handling
    assert(pid.compute(1.0, 0.0) == 0.0);
    
    // Deadband test (error 0.04 < deadband 0.05)
    double cmd1 = pid.compute(0.04, 0.1);
    assert(cmd1 == 0.0);
    
    // Basic proportional test
    pid.reset();
    double cmd2 = pid.compute(1.0, 0.1); // is_first_run = true -> D=0
    // P = 1.0, I = 0.1*1.0*0.1 = 0.01 -> pre_cmd = 1.01. integral becomes 0.1.
    // cmd = 1.0 + 0.1*0.1 = 1.01
    assert(std::abs(cmd2 - 1.01) < 1e-5);
    
    // Saturation test
    pid.reset();
    double cmd3 = pid.compute(10.0, 0.1); // Error very large
    assert(std::abs(cmd3 - 2.0) < 1e-5); // Clamped to v_max = 2.0

    std::cout << "C++ PID Unit Tests PASSED!" << std::endl;
}

int main() {
    test_pid_basic();
    return 0;
}
