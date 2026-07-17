#include "failsafe.hpp"

namespace control {
bool Failsafe::check_timeout(double last_msg_time, double current_time, double timeout_limit) {
    return (current_time - last_msg_time) > timeout_limit;
}
} // namespace control
