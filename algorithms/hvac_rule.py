class hvac_rule(object):
    def __init__(self) -> None:
        super().__init__()
        self.temp_bd = 2

        self.temp_lb = 18
        self.humi_lb = 30

    def command(self, data):
        # simple rule-based
        # comfort temp: 16-26: turn off!
        if data['atmos']['temp'] >= 16 and data['atmos']['temp'] <=26:
            return False

        # difference of temp: at least 1
        atmos_diff = max(1, abs(data['d_temp'] - data['atmos']['temp']))
        # high temp_diff: small temp tolerance: weather is cold/hot!
        # low temp_diff: high temp tolerance: not need to turn on ac
        temp_range = self.temp_bd / atmos_diff

        desired_diff = abs(data['d_temp']-data['home']['temp'])
        print(f'hvac rule: desired_diff: {desired_diff}, temp range: {temp_range}')

        if data['home']['humi'] >= 30 and desired_diff > temp_range:
            print('hvac: temp lvl 1')
            # self.set_relay_status(True)
            return True
        elif desired_diff > self.temp_range*2:
            print('hvac: temp lvl 2')
            return True
        else:
            print('hvac: temp lvl 0')
            return False