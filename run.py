from hardware.cpu_fan import cpu_fan
from hardware.hvac import hvac
from hardware.uart import uart_sensor
from service.prometheus_service import prometheus_service
from service.homeassistant_service import homeassistant_service

import time
from datetime import datetime

from collections import deque

FAN_CTRL_PERIOD = 10
UART_PERIOD = 5


if __name__ == '__main__':
    # set Q-learning
    fan = cpu_fan()
    uart = uart_sensor()
    ac = hvac()
    hass = homeassistant_service()

    # create service
    FAN_PWM = {'key':'PYTHON_FAN_CONTROL', 'desc': 'Gauge of cooling fan: GPIO 18 PWM'}
    HVAC_STATUS = {'key':'PYTHON_HVAN_CONTROL', 'desc': 'Status of HVAC relays'}
    UART_TEMP = {'key':'PYTHON_UART_TEMP', 'desc': 'Gauge of Temperature'}
    UART_HUMI = {'key':'PYTHON_UART_HUMI', 'desc': 'Gauge of Humidity'}
    UART_PRES = {'key':'PYTHON_UART_PRES', 'desc': 'Gauge of Pressure'}
    HASS_TEMP = {'key':'PYTHON_HASS_TEMP', 'desc': 'Gauge of Atmosphere Temperature'}
    HASS_HUMI = {'key':'PYTHON_HASS_HUMI', 'desc': 'Gauge of Atmosphere Humidity'}

    metrics = {
        'fan': FAN_PWM,
        'hvac': HVAC_STATUS,
        'u_tmpe': UART_TEMP,
        'u_humi': UART_HUMI,
        'u_pres': UART_PRES,
        'h_temp': HASS_TEMP,
        'h_humi': HASS_HUMI
    }
    ps = prometheus_service(6432, metrics)
    ps_data = {
        'fan': 0, 'hvac': 0, 
        'uart': {'temp':0, 'humi':0, 'pres': 0},
        'hass': {'temp': 0, 'humi': 0, 'pres': 0}
    }

    # get uart data
    uart.start_receive()

    time_cnt = 0
    while True:
        time.sleep(1)
        time_cnt += 1

        if time_cnt >= 10:
            time_cnt = 0

        if time_cnt % 10 == 0:
            # run Q-learning
            pwm = fan.run()
            ps_data['fan'] = pwm

            ps_data['hass']['temp'] = hass.get_atmos_temp()
            ps_data['hass']['humi'] = hass.get_atmos_humi()

            # save Q every 10 min
            if datetime.now().minute % 10 == 0 and datetime.now().second < 10:
                fan.agent.save_q()

            # control hvac every 20 min
            if datetime.now().minute % 20 == 0 and datetime.now().second < 10:
                ac.run(ps_data['uart'], ps_data['hass'])

        if time_cnt % 5 == 0:
            ps_data['uart']['temp'], ps_data['uart']['humi'], ps_data['uart']['pres'] = \
                uart.get_data()

            ac.ps.check_status()
            ps_data['hvac'] = ac.get_state_message()
            print(ps_data['hvac'])
            
            print(ps_data)
            ps.receive(ps_data)

            

        
        
