from prometheus_client import start_http_server
from prometheus_client import Gauge

class prometheus_server(object):
    def __init__(self, port, metrics) -> None:
        super().__init__()

        self.g_fan = Gauge(metrics['fan']['key'], metrics['fan']['desc'])
        self.g_fan.set_function( lambda: self.__get_fan_pwm() )

        self.g_temp = Gauge(metrics['u_tmpe']['key'], metrics['u_tmpe']['desc'])
        self.g_temp.set_function( lambda: self.__get_uart_temp() )

        self.g_humi = Gauge(metrics['u_humi']['key'], metrics['u_humi']['desc'])
        self.g_humi.set_function( lambda: self.__get_uart_humi() )

        self.g_pres = Gauge(metrics['u_pres']['key'], metrics['u_pres']['desc'])
        self.g_pres.set_function( lambda: self.__get_uart_pres() )

        self.g_pres = Gauge(metrics['a_temp']['key'], metrics['a_temp']['desc'])
        self.g_pres.set_function( lambda: self.__get_ada_temp() )

        self.g_pres = Gauge(metrics['a_lamp']['key'], metrics['a_lamp']['desc'])
        self.g_pres.set_function( lambda: self.__get_ada_lamp() )

        start_http_server(port)
        self.pwm = 0
        self.temp = 0
        self.humi = 0
        self.pres = 0
        self.d_temp = 0
        self.lamp = True

    def receive(self, data):
        self.pwm = data['fan']
        self.temp = data['uart']['temp']
        self.humi = data['uart']['humi']
        self.pres = data['uart']['pres']
        self.d_temp = data['ada']['temp']
        self.lamp = data['ada']['lamp']
        
    def __get_fan_pwm(self):
        return self.pwm

    def __get_uart_temp(self):
        return self.temp
    
    def __get_uart_humi(self):
        return self.humi

    def __get_uart_pres(self):
        return self.pres
  
    def __get_ada_temp(self):
        return self.d_temp

    def __get_ada_lamp(self):
        return 1 if self.lamp else 0