from hardware.cpu_fan import cpu_fan
from hardware.uart import uart_sensor
from servers.prometheus_server import prometheus_server
import time
from datetime import datetime

FAN_CTRL_PERIOD = 10
UART_PERIOD = 5





if __name__ == '__main__':
    # set Q-learning
    cpu_fan = cpu_fan()
    uart = uart_sensor()

    # create server
    FAN_PWM = {'key':'PYTHON_FAN_CONTROL', 'desc': 'Gauge of cooling fan: GPIO 18 PWM'}
    HVAC_STATUS = {'key':'PYTHON_HVAN_CONTROL', 'desc': 'Status of HVAC relays'}
    UART_TEMP = {'key':'PYTHON_UART_TEMP', 'desc': 'Gauge of Temperature'}
    UART_HUMI = {'key':'PYTHON_UART_HUMI', 'desc': 'Gauge of Humidity'}
    UART_PRES = {'key':'PYTHON_UART_PRES', 'desc': 'Gauge of Pressure'}

    metrics = {
        'fan': FAN_PWM,
        'hvac': HVAC_STATUS,
        'u_tmpe': UART_TEMP,
        'u_humi': UART_HUMI,
        'u_pres': UART_PRES
    }
    ps = prometheus_server(6432, metrics)
    ps_data = {
        'fan': 0, 'hvac': 0, 
        'uart': {'temp':0, 'humi':0, 'pres': 0}
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
            pwm = cpu_fan.run()
            ps_data['fan'] = pwm

        # save Q every 10 min
        if datetime.now().minute % 10 == 0 and datetime.now().second < 10:
            cpu_fan.agent.save_q()

        if time_cnt % 5 == 0:
            ps_data['uart']['temp'], ps_data['uart']['humi'], ps_data['uart']['pres'] = \
                uart.get_data()
            ps.receive(ps_data)

        
        
