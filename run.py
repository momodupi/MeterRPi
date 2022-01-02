from hardware.hvac import hvac
from service.mosquitto_service import mqtt_service
from hardware.uart import uart_sensor
# from service.prometheus_service import prometheus_service
# from service.homeassistant_service import homeassistant_service

import time
from datetime import datetime

from collections import deque

# FAN_CTRL_PERIOD = 10
# UART_PERIOD = 5


if __name__ == '__main__':
    uart = uart_sensor()
    mqtt = mqtt_service()
    ac = hvac(mqtt)
    # hass = homeassistant_service()
    
    # ac.get_ui_status(hass.ui_data)

    # create service
    # HVAC_STATUS = {'key':'PYTHON_HVAC_CONTROL', 'desc': 'Status of HVAC relays'}
    # UART_TEMP = {'key':'PYTHON_UART_TEMP', 'desc': 'Gauge of Temperature'}
    # UART_HUMI = {'key':'PYTHON_UART_HUMI', 'desc': 'Gauge of Humidity'}
    # UART_PRES = {'key':'PYTHON_UART_PRES', 'desc': 'Gauge of Pressure'}
    # HASS_TEMP = {'key':'PYTHON_HASS_TEMP', 'desc': 'Gauge of Atmosphere Temperature'}
    # HASS_HUMI = {'key':'PYTHON_HASS_HUMI', 'desc': 'Gauge of Atmosphere Humidity'}

    # metrics = {
    #     'hvac': HVAC_STATUS,
    #     'u_tmpe': UART_TEMP,
    #     'u_humi': UART_HUMI,
    #     'u_pres': UART_PRES,
    #     'h_temp': HASS_TEMP,
    #     'h_humi': HASS_HUMI
    # }
    # ps = prometheus_service(6432, metrics)
    data = {
        'fan': 0, 'hvac': 0, 
        'hass': {'temp': 0, 'humi': 0},
        'sensor': {'temp': 0, 'humi': 0}
    }

    # get uart data
    uart.start_receive()

    time_cnt = 0
    while True:
        time.sleep(1)
        time_cnt += 1

        # ac.desired_temp = hass.get_desired_temp()
        # ac.working = hass.get_hvac_on_off()

        if time_cnt >= 10:
            time_cnt = 0

        if time_cnt % 5 == 0:
            data['sensor']['temp'], data['sensor']['humi'], data['sensor']['pres'] = \
                uart.get_data()

            ac.update(data['sensor'])
            
            # ac.ps.check_status()
            # data['hvac'] = ac.get_state_message()
            
            # hass.set_home_sensor(data['sensor'])
            # ui_data = hass.get_ui_data()
            # print(ui_data)

            # if ui_data['power'] == True:
            #     ac.set_state( hass.fan_cmd[ui_data['fan']] )
            #     ac.set_desired_temp(ui_data['temp'])
            
        if time_cnt % 10 == 0:
            # # run Q-learning
            # pwm = fan.run()

            # data['hass']['temp'] = hass.get_atmos_temp()
            # data['hass']['humi'] = hass.get_atmos_humi()

            # control hvac every 15 min
            if datetime.now().minute % 15 == 0 and datetime.now().second < 10:
                ac.auto_run(data['sensor'])
            
            
