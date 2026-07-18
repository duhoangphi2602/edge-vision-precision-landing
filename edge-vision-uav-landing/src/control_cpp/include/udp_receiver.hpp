#ifndef UDP_RECEIVER_HPP
#define UDP_RECEIVER_HPP

#include <string>
#include <netinet/in.h>

struct PerceptionObservation {
    bool valid = false;
    std::string mission_id;
    long long timestamp_publish_ns = 0;
    bool target_found = false;
    double error_x = 0.0;
    double error_y = 0.0;
    double latency_ms = 0.0;
};

class UdpReceiver {
public:
    UdpReceiver(int port);
    ~UdpReceiver();
    bool get_latest_observation(PerceptionObservation& obs);
private:
    int sockfd_;
    struct sockaddr_in servaddr_;
    PerceptionObservation parse_json(const std::string& json_str);
};

#endif
