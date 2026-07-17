add_library(interface_cpp STATIC
    src/mavlink_builder.cpp
    src/udp_receiver.cpp
)
target_include_directories(interface_cpp PUBLIC include)
