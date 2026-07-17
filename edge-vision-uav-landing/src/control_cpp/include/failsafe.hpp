#pragma once

namespace control {
class Failsafe {
public:
    static bool check_timeout(double last_msg_time, double current_time, double timeout_limit);
};
} // namespace control
