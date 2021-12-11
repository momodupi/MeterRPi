# from PID import PID
from algorithms.Q_learning import Agent

import ctypes
import os
import requests

# PI = 'http://192.168.1.8'
PI = 'http://127.0.0.1'
FAN_GPIO = 18
PROMETHEUS_QUERY = ':9090/api/v1/query'
TEMP_THRESHOLD = 60
TEMP_TARGET = 65


class cpu_fan(object):
    def __init__(self) -> None:
        super().__init__()

        # init gpio
        dll_path = os.path.dirname(__file__)
        self.pwm = ctypes.CDLL(f'{dll_path}{os.path.sep}pwm.so')
        self.pwm.gpio_init.argtypes = (ctypes.c_int,)
        self.pwm.gpio_set_pwm.argtypes = (ctypes.c_int, ctypes.c_int)
        self.pwm.gpio_init( ctypes.c_int(FAN_GPIO) )

        # init ip addr
        self.ip_addr = PI

        self.duty = 0

        # setup Q-learning
        self.agent = Agent(0.75, 0.1)

        # self.pid = PID(kp=10., ki=0.1, kd=0, bounds=[0, 100])

        # GPIO.setwarnings(False)
        # GPIO.cleanup()

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(18, GPIO.OUT)

        # # GPIO.output(18, GPIO.HIGH)
        # self.pwm = GPIO.PWM(18, 10000)
        # self.pwm.start(0)
        

    def get_cpu_temp(self):
        # response = requests.get(
        #   self.ip_addr + ':9100/metrics'
        # )
        # print(response.)
        # return 0
        response = requests.get(
            self.ip_addr + PROMETHEUS_QUERY,
            params={'query': 'node_thermal_zone_temp{type="cpu-thermal",zone="0"}'}
        )
        return float(response.json()['data']['result'][0]['value'][1])

    def get_container_num(self):
        response = requests.get(
            self.ip_addr + PROMETHEUS_QUERY,
            params={
                'query': 'engine_daemon_container_states_containers{state="running"}'}
        )
        return float(response.json()['data']['result'][0]['value'][1])

    def get_cpu_usage(self):
        response = requests.get(
            self.ip_addr + PROMETHEUS_QUERY,
            params={
                'query': 'rate(node_cpu_seconds_total{job="node_exporter", mode="idle"}[15s])'}
        )
        cpu_usage = 0.
        cpu_info = response.json()['data']['result']
        for c in cpu_info:
            cpu_usage += float(c['value'][1])
        return 99.99 - cpu_usage/4.*100.

    def control_pid(self, state):
        # pid control
        target_temp = TEMP_TARGET
        temp = state[1]
        duty = state[0]
        # print(temp)

        if temp < TEMP_THRESHOLD:
            return 0
        else:
            self.pid.get_error(target_temp=target_temp, temp=temp)
            return self.pid.control(action=duty)

    def control(self, state, action):
        self.agent.learning(state, action)
        return self.agent.greed(state)
    
    def run(self):
        # get state and action pair
        state = [self.get_cpu_temp(), self.get_cpu_usage()]
        action = self.duty
        self.duty = self.control(state, action)

        # self.duty = 100
        # set pwm with wiringPi
        self.pwm.gpio_set_pwm( ctypes.c_int(FAN_GPIO), ctypes.c_int(self.duty) )

        return self.duty