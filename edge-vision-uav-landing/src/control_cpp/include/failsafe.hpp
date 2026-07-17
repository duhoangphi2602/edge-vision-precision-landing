#pragma once

#include <string>

namespace control {

enum class FailsafeReason {
    NONE,
    TARGET_LOST,
    STALE_OBSERVATION,
    WRONG_MARKER_ID,
    INVALID_POSE,
    IPC_TIMEOUT
};

struct Observation {
    double timestamp_capture_ns;
    double timestamp_publish_ns;
    bool target_found;
    int marker_id;
    bool pose_valid;
};

class FailsafeManager {
public:
    FailsafeManager(int expected_marker_id, double stale_threshold_sec);
    
    FailsafeReason check_observation(const Observation& obs, double current_time_ns) const;
    
    // Heartbeat check (e.g., IPC)
    FailsafeReason check_heartbeat(double last_msg_time_ns, double current_time_ns, double timeout_limit_sec) const;

private:
    int expected_marker_id_;
    double stale_threshold_sec_;
};

} // namespace control
