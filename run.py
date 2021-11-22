from fan import FAN
from prometheus_server import prometheus_server
from adafruit_server import adafruit_server
from uart import UART
import time
from datetime import datetime

FAN_CTRL_PERIOD = 10
UART_PERIOD = 5


def decode_uart_data(ps_data, uart_data):
    temp = 0
    humi = 0
    pres = 0
    if len(uart_data) > 0:
        for u_d in uart_data:
            temp += (u_d['tem1'] + u_d['tem2'])/2
            humi += u_d['hum']
            pres += u_d['pre']
        ps_data['uart']['temp'] = temp/len(uart_data)
        ps_data['uart']['humi'] = humi/len(uart_data)
        ps_data['uart']['pres'] = pres/len(uart_data)


if __name__ == '__main__':
    # set Q-learning
    fan = FAN()
    uart = UART()
    ada = adafruit_server()

    # create server
    FAN_PWM = {'key':'PYTHON_FAN_CONTROL', 'desc': 'Gauge of cooling fan: GPIO 18 PWM'}
    HVAC_STATUS = {'key':'PYTHON_HVAN_CONTROL', 'desc': 'Status of HVAC relays'}
    UART_TEMP = {'key':'PYTHON_UART_TEMP', 'desc': 'Gauge of Temperature'}
    UART_HUMI = {'key':'PYTHON_UART_HUMI', 'desc': 'Gauge of Humidity'}
    UART_PRES = {'key':'PYTHON_UART_PRES', 'desc': 'Gauge of Pressure'}
    ADA_TEMP = {'key':'PYTHON_ADA_TEMP', 'desc': 'Gauge of Desired Temperature'}
    ADA_LAMP = {'key':'PYTHON_ADA_LAMP', 'desc': 'Status of lamp relays'}

    metrics = {
        'fan': FAN_PWM,
        'hvac': HVAC_STATUS,
        'u_tmpe': UART_TEMP,
        'u_humi': UART_HUMI,
        'u_pres': UART_PRES,
        'a_temp': ADA_TEMP,
        'a_lamp': ADA_LAMP
    }
    ps = prometheus_server(6432, metrics)
    ps_data = {
        'fan': None, 'hvac': None, 
        'uart': {'temp':0, 'humi':0, 'pres': 0},
        'ada': {'temp': 0, 'lamp': False}
    }

    # create adafruit server
    ada.feeding()

    # get uart data
    uart.start_receive()

    time_cnt = 0
    while True:
        time.sleep(1)
        if time_cnt >= 10:
            time_cnt = 0

        # get data from adafruit feed
        ada_rqst = ada.feed_data
        ada_temp, ada_lamp = ada_rqst['temp'], ada_rqst['lamp']


        if time_cnt % 10 == 0:
            # run Q-learning
            pwm = fan.run()
            ps_data['fan'] = pwm

        # save Q every 10 min
        if datetime.now().minute % 10 == 0 and datetime.now().second < 10:
            fan.agent.save_q()

        if time_cnt % 5 == 0:
            ps_data['ada']['temp'] = ada_temp
            ps_data['ada']['lamp'] = ada_lamp
            decode_uart_data(ps_data, uart.get_data())
            print(ps_data)
            ps.receive(ps_data)

        time_cnt += 1
        
