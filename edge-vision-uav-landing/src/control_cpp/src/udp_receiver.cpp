#include "udp_receiver.hpp"
#include <iostream>
#include <sys/socket.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>

UdpReceiver::UdpReceiver(int port) {
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&servaddr_, 0, sizeof(servaddr_));
    servaddr_.sin_family = AF_INET;
    servaddr_.sin_addr.s_addr = INADDR_ANY;
    servaddr_.sin_port = htons(port);
    
    bind(sockfd_, (const struct sockaddr *)&servaddr_, sizeof(servaddr_));
    
    // Set non-blocking
    int flags = fcntl(sockfd_, F_GETFL, 0);
    fcntl(sockfd_, F_SETFL, flags | O_NONBLOCK);
}

UdpReceiver::~UdpReceiver() {
    close(sockfd_);
}

PerceptionObservation UdpReceiver::parse_json(const std::string& json_str) {
    PerceptionObservation obs;
    // Basic string search for demonstration to avoid external deps.
    // In production, use nlohmann/json or rapidjson.
    if (json_str.find("\"target_found\": true") != std::string::npos) {
        obs.target_found = true;
    }
    
    auto ts_pos = json_str.find("\"timestamp_publish_ns\": ");
    if (ts_pos != std::string::npos) {
        obs.timestamp_publish_ns = std::stoll(json_str.substr(ts_pos + 24, 15)); // rough parse
    }

    auto norm_pos = json_str.find("\"normalized_error\":");
    if (norm_pos != std::string::npos) {
        auto x_pos = json_str.find("\"x\":", norm_pos);
        if (x_pos != std::string::npos) obs.error_x = std::stod(json_str.substr(x_pos + 4, 8));
        auto y_pos = json_str.find("\"y\":", norm_pos);
        if (y_pos != std::string::npos) obs.error_y = std::stod(json_str.substr(y_pos + 4, 8));
    }
    obs.valid = true;
    return obs;
}

bool UdpReceiver::get_latest_observation(PerceptionObservation& obs) {
    char buffer[1024];
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);
    
    int n = recvfrom(sockfd_, (char *)buffer, 1024, MSG_DONTWAIT, (struct sockaddr *) &cliaddr, &len);
    if (n > 0) {
        buffer[n] = '\0';
        std::string json_str(buffer);
        obs = parse_json(json_str);
        return true;
    }
    return false;
}
