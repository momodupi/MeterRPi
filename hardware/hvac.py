# from service.tuya_service import tuya_service
# from service.pulsar_service import pulsar_service
# import time
from service.homeassistant_service import homeassistant_service

# TOKEN = 0
# INSTRUCTION = 1
# INFORMATION = 2
# STATUS = 3
# COMMAND = 4

# OFF = None
# LOW = 'switch_1'
# NORMAL = 'switch_2'
# HIGH = 'switch_3'

# HVAC_STATUS = {
#     'off': 0,
#     'low': 1,
#     'normal': 2,
#     'high': 3
# }

class hvac(object):
    def __init__(self, mqtt) -> None:
        super().__init__()

        # switch_1: low, switch_2: mid, swithc_3: hight, switch_4: null
        self.switch = False
        self.hass = homeassistant_service()
        self.mqtt = mqtt

        # self.ts = tuya_service()
        # get message from pulsar service
        # self.ps = pulsar_service()
        # self.ps.start()

        # self.get_state()
        
        self.fan = False
        self.working = False
        self.desired_temp = self.hass.get_desired_temp()
        self.temp_range = 2
        # self.atmos_temp = self.hass.get_atmos_temp()
        # self.atmos_humi = self.hass.get_atmos_humi()
        # self.sensor_temp = 0
        # self.sensor_humi = 0
        
    # def get_sensor_data(self, sensor_data):
    #     self.sensor_data = sensor_data

    def set_relay_status(self, cmd):
        print(f'relay status: {cmd}')
        send_cmd = 'on' if cmd else 'off'
        self.mqtt.sends('relay', send_cmd)

    # def get_state(self):
    #     # res = self.ts.get_status()
    #     self.hvac = 'off'
    #     for switch in res:
    #         self.switches[switch['code']] = switch['value']
    #         if switch['code'] == "switch_1" and switch['value']:
    #             self.hvac = 'low'
    #         elif switch['code'] == "switch_2" and switch['value']:
    #             self.hvac = 'normal'
    #         elif switch['code'] == "switch_3" and switch['value']:
    #             self.hvac = 'high'
    #     return self.hvac

    # def __decode_pulsar_data(self, data_set):
    #     for data in data_set:            
    #         self.switches[data['status'][0]['code']] = data['status'][0]['value']

    #     self.hvac = 'off'
    #     for switch in self.switches:
    #         if switch == "switch_1" and self.switches[switch]:
    #             self.hvac = 'low'
    #         elif switch == "switch_2" and self.switches[switch]:
    #             self.hvac = 'normal'
    #         elif switch == "switch_3" and self.switches[switch]:
    #             self.hvac = 'high'
    #     return self.hvac

    # def get_state_message(self):
    #     if self.ps.q.qsize() != 0:
    #         data_set = [self.ps.q.get() for _ in range(self.ps.q.qsize())]            
    #         print(f'hvac info: new msg: {self.__decode_pulsar_data(data_set)}')
        
    #     return HVAC_STATUS[self.hvac]
    

    # def set_state(self, cmd):
    #     switch_cmd = {
    #         'switch_1': False,
    #         'switch_2': False,
    #         'switch_3': False,
    #         'switch_4': False,
    #     }
    #     if self.hvac == cmd:
    #         return
    #     self.hvac = cmd

    #     # for safety, turn off all switches first and deley for 0.5s
    #     self.ts.send_command(switch_cmd)
    #     time.sleep(0.5)

    #     if cmd == 'low':
    #         switch_cmd[LOW] = True
    #     elif cmd == 'normal':
    #         switch_cmd[NORMAL] = True
    #     elif cmd == 'high':
    #         switch_cmd[HIGH] = True
    #     else:
    #         pass
    #     self.ts.send_command(switch_cmd)

    # def get_command(self):
    #     if self.hvac == 'low': return 1
    #     elif self.hvac == 'normal': return 2
    #     elif self.hvac == 'high': return 3
    #     elif self.hvac == 'off': return 0
    #     else: return -1

    # def set_desired_temp(self, temp):
    #     self.desired_temp = temp

    def update(self, home_data):
        self.hass.get_ui_data()
        self.desired_temp = self.hass.ui_data['temp']
        
        self.manual = self.hass.ui_data['manual']
        self.auto = self.hass.ui_data['auto']

        self.atmos_temp = self.hass.get_atmos_temp()
        self.atmos_humi = self.hass.get_atmos_humi()

        # # if switch on
        # if not self.working:
        #     self.set_state('off')
        #     return

        temp = home_data['temp']
        humi = home_data['humi']

        self.hass.set_home_sensor({'temp': temp, 'humi': humi})

        print(f'atmos: temp: {self.atmos_temp}, humi: {self.atmos_humi}')
        print(f'home: temp: {temp}, humi: {humi}')
        print(f'hass: temp:{self.desired_temp}, manual: {self.manual}, auto: {self.auto}')

        # h_temp = atmos_data['temp']

        if self.manual:
            self.set_relay_status(True)
        elif not self.auto:
            self.set_relay_status(False)
            

    def auto_run(self, home_data):
        temp = home_data['temp']
        humi = home_data['humi']

        if self.auto:
            # simple rule-based
            # only work when humidity is higher than 40% 
            # and atmos/home temperatures difference is larger than 2C
            if humi >= 40 and abs(self.desired_temp-temp) > self.temp_range:
                self.set_relay_status(True)
            else:
                self.set_relay_status(False)
                # # temperature range desired_temp +- n*range
                # if temp < self.desired_temp - 3*self.temp_range \
                #     and temp > self.desired_temp + 3*self.temp_range:
                #     self.set_state('high')
                # elif temp < self.desired_temp - 2*self.temp_range \
                #     and temp > self.desired_temp + 2*self.temp_range:
                #     self.set_state('normal')
                # elif temp < self.desired_temp - self.temp_range \
                #     and temp > self.desired_temp + self.temp_range:
                #     self.set_state('low')
                # else:
                #     self.set_state('off')

        

