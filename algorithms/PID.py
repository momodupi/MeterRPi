class PID(object):
    def __init__(self, kp, ki, kd, bounds) -> None:
        super().__init__()
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.inte = 0
        self.prior_error = 0
        self.error = 0
        self.diff = 0

        self.ub = bounds[1]
        self.lb = bounds[0]

    def get_error(self, target_temp, temp):
        self.error = temp - target_temp
        self.diff = self.error - self.prior_error
        self.inte = min(max(self.inte + self.error, 0), 100)

    def control(self, action):
        a = action + self.kp*self.error + self.ki*self.inte + self.kd*self.diff
        return max(self.lb, min(self.ub, a))
