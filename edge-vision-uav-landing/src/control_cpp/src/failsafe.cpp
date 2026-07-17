#include "failsafe.hpp"

namespace control {

FailsafeManager::FailsafeManager(int expected_marker_id, double stale_threshold_sec)
    : expected_marker_id_(expected_marker_id), stale_threshold_sec_(stale_threshold_sec) {}

FailsafeReason FailsafeManager::check_observation(const Observation& obs, double current_time_ns) const {
    if (!obs.target_found) {
        return FailsafeReason::TARGET_LOST;
    }
    
    if (obs.marker_id != expected_marker_id_) {
        return FailsafeReason::WRONG_MARKER_ID;
    }
    
    if (!obs.pose_valid) {
        return FailsafeReason::INVALID_POSE;
    }
    
    double age_sec = (current_time_ns - obs.timestamp_capture_ns) / 1e9;
    if (age_sec > stale_threshold_sec_) {
        return FailsafeReason::STALE_OBSERVATION;
    }
    
    return FailsafeReason::NONE;
}

FailsafeReason FailsafeManager::check_heartbeat(double last_msg_time_ns, double current_time_ns, double timeout_limit_sec) const {
    double age_sec = (current_time_ns - last_msg_time_ns) / 1e9;
    if (age_sec > timeout_limit_sec) {
        return FailsafeReason::IPC_TIMEOUT;
    }
    return FailsafeReason::NONE;
}

} // namespace control
