#pragma once

namespace interface {
class UDPReceiver {
public:
    UDPReceiver(int port);
    bool receive();
private:
    int port_;
};
} // namespace interface
