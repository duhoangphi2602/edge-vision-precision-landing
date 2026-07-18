cmake_minimum_required(VERSION 3.10)
project(control_cpp)

add_library(control_cpp STATIC
    src/pid_controller.cpp
    src/failsafe.cpp
    src/state_machine.cpp
    src/control_loop.cpp
)
target_include_directories(control_cpp PUBLIC include)

add_executable(test_pid src/test_pid.cpp)
target_link_libraries(test_pid control_cpp)

add_executable(test_failsafe src/test_failsafe.cpp)
target_link_libraries(test_failsafe control_cpp)

# --- Day 18 Additions ---
target_sources(control_cpp PRIVATE src/mavlink_builder.cpp)

add_executable(test_mavlink_bridge src/test_mavlink_bridge.cpp)
target_link_libraries(test_mavlink_bridge control_cpp)

add_executable(control_node src/main_control_node.cpp src/udp_receiver.cpp src/control_loop.cpp src/pid_controller.cpp src/state_machine.cpp src/failsafe.cpp src/mavlink_builder.cpp)
target_include_directories(control_node PUBLIC include)
