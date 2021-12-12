from servers.tuya_server import tuya_server
from servers.pulsar_server import pulsar_server
import time


TOKEN = 0
INSTRUCTION = 1
INFORMATION = 2
STATUS = 3
COMMAND = 4

OFF = None
LOW = 'switch_1'
MIDDLE = 'switch_2'
HIGH = 'switch_3'

HVAC_PROMETHEUS = {
    'off': 0,
    'low': 1,
    'middle': 2,
    'high': 3
}

class hvac(object):
    def __init__(self) -> None:
        super().__init__()

        # switch_1: low, switch_2: mid, swithc_3: hight, switch_4: null
        self.switches = {
            'switch_1': False,
            'switch_2': False,
            'switch_3': False,
            'switch_4': False
        }

        self.ts = tuya_server()
        self.hvac = self.get_state()
        # get message from pulsar server
        self.ps = pulsar_server()
        self.ps.start()

        self.desired_temp = 22
        self.temp_range = 2

    def get_state(self):
        res = self.ts.get_status()
        self.hvac = 'off'
        for switch in res:
            self.switches[switch['code']] = switch['value']
            if switch['code'] == "switch_1" and switch['value']:
                self.hvac = 'low'
            elif switch['code'] == "switch_2" and switch['value']:
                self.hvac = 'middle'
            elif switch['code'] == "switch_3" and switch['value']:
                self.hvac = 'high'
        return self.hvac

    def __decode_pulsar_data(self, data_set):
        
        for data in data_set:
            print('data: ', data)
            print('status: ', data['status'])
            print('status 0: ', data['status'][0])
            
            self.switches[data['status'][0]['code']] = data['status'][0]['value']

        self.hvac = 'off'
        for switch in self.switches:
            if switch == "switch_1" and self.switches[switch]:
                self.hvac = 'low'
            elif switch == "switch_2" and self.switches[switch]:
                self.hvac = 'middle'
            elif switch == "switch_3" and self.switches[switch]:
                self.hvac = 'high'
        return self.hvac

    def get_state_message(self):
        if self.ps.q.qsize() != 0:
            data_set = [self.ps.q.get() for _ in range(self.ps.q.qsize())]            
            print(f'HVAC status: {self.__decode_pulsar_data(data_set)}')
        
        return HVAC_PROMETHEUS[self.hvac]
    

    def set_state(self, cmd):
        switch_cmd = {
            'switch_1': False,
            'switch_2': False,
            'switch_3': False,
            'switch_4': False,
        }
        self.hvac = cmd

        # for safety, turn off all switches first and deley for 0.5s
        self.ts.send_command(switch_cmd)
        time.sleep(0.5)

        if cmd == 'low':
            switch_cmd[LOW] = True
        elif cmd == 'middle':
            switch_cmd[MIDDLE] = True
        elif cmd == 'high':
            switch_cmd[HIGH] = True
        else:
            pass
        self.ts.send_command(switch_cmd)

    def get_command(self):
        if self.hvac == 'low': return 1
        elif self.hvac == 'middle': return 2
        elif self.hvac == 'high': return 3
        elif self.hvac == 'off': return 0
        else: return -1

    def run(self, home_data, atmos_data):
        temp = home_data['temp']
        humi = home_data['humi']
        pres = home_data['pres']

        h_temp = atmos_data['temp']

        # simple rule-based
        # only work when humidity is higher than 40% 
        # and atmos/home temperatures difference is larger than 2C
        if humi >= 40 and abs(self.desired_temp-h_temp) > 2:        
            # temperature range desired_temp +- n*range
            if temp < self.desired_temp - 3*self.temp_range \
                and temp > self.desired_temp + 3*self.temp_range:
                self.set_state('high')
            elif temp < self.desired_temp - 2*self.temp_range \
                and temp > self.desired_temp + 2*self.temp_range:
                self.set_state('middle')
            elif temp < self.desired_temp - self.temp_range \
                and temp > self.desired_temp + self.temp_range:
                self.set_state('low')
            else:
                self.set_state('off')

