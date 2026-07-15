class PIDController:
    def __init__(self, kp, ki, kd, v_max, deadband=0.05, alpha=0.5):

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.v_max = v_max
        self.deadband = deadband
        self.alpha = alpha
        self.reset()

    def reset(self):
        """Gọi khi target loss để xóa memory, tránh vọt lố khi bắt lại mục tiêu."""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.is_first_run = True

    def compute(self, error, dt):
        if dt <= 0.0:
            return 0.0

        # Deadband policy
        if abs(error) < self.deadband:
            error = 0.0

        p_term = self.kp * error

        # First-sample derivative handling
        if self.is_first_run:
            raw_derivative = 0.0
            self.is_first_run = False
        else:
            raw_derivative = (error - self.prev_error) / dt

        # Low-pass filter cho đạo hàm
        derivative = self.alpha * raw_derivative + (1 - self.alpha) * self.prev_derivative
        d_term = self.kd * derivative

        # Anti-windup (Clamping với unwind support)
        pre_cmd = p_term + d_term + self.ki * (self.integral + error * dt)
        
        # Chỉ cộng dồn I nếu hệ thống chưa bị bão hòa, 
        # HOẶC nếu lỗi đang có xu hướng kéo hệ thống ra khỏi bão hòa (đảo chiều)
        if abs(pre_cmd) < self.v_max or (pre_cmd > 0 and error < 0) or (pre_cmd < 0 and error > 0):
            self.integral += error * dt

        i_term = self.ki * self.integral

        cmd = p_term + i_term + d_term
        
        # Saturation
        cmd_clamped = max(-self.v_max, min(self.v_max, cmd))

        self.prev_error = error
        self.prev_derivative = derivative

        return cmd_clamped