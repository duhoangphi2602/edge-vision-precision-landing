add_library(control_cpp STATIC
    src/pid_controller.cpp
    src/failsafe.cpp
    src/control_loop.cpp
)
target_include_directories(control_cpp PUBLIC include)
