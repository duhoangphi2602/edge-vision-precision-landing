cmake_minimum_required(VERSION 3.16)
project(EdgeVisionUAVLanding VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Sẽ liên kết OpenCV, ONNXRuntime và MAVSDK ở các module sau
add_subdirectory(src/interface_cpp)
add_subdirectory(src/control_cpp)
