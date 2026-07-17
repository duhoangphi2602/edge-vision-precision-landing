#include "udp_receiver.hpp"

namespace interface {
UDPReceiver::UDPReceiver(int port) : port_(port) {}
bool UDPReceiver::receive() {
    // TODO: Bind and recvfrom
    return false;
}
} // namespace interface
