# from prometheus_client import start_http_server
# from prometheus_client import Gauge

# class prometheus_service(object):
#     def __init__(self, port, metrics) -> None:
#         super().__init__()

#         self.g_hvac = Gauge(metrics['hvac']['key'], metrics['hvac']['desc'])
#         self.g_hvac.set_function( lambda: self.__get_hvac_status() )

#         self.g_temp = Gauge(metrics['u_tmpe']['key'], metrics['u_tmpe']['desc'])
#         self.g_temp.set_function( lambda: self.__get_uart_temp() )

#         self.g_humi = Gauge(metrics['u_humi']['key'], metrics['u_humi']['desc'])
#         self.g_humi.set_function( lambda: self.__get_uart_humi() )

#         self.g_pres = Gauge(metrics['u_pres']['key'], metrics['u_pres']['desc'])
#         self.g_pres.set_function( lambda: self.__get_uart_pres() )

#         self.g_h_temp = Gauge(metrics['h_temp']['key'], metrics['h_temp']['desc'])
#         self.g_h_temp.set_function( lambda: self.__get_hass_temp() )

#         self.g_h_humi = Gauge(metrics['h_humi']['key'], metrics['h_humi']['desc'])
#         self.g_h_humi.set_function( lambda: self.__get_hass_humi() )

#         start_http_server(port)
#         self.hvac = 0
#         self.temp = 0
#         self.humi = 0
#         self.pres = 0

#         self.h_temp = 0
#         self.h_humi = 0


#     def receive(self, data):
#         self.hvac = data['hvac']
#         self.temp = data['uart']['temp']
#         self.humi = data['uart']['humi']
#         self.pres = data['uart']['pres']
#         self.h_temp = data['hass']['temp']
#         self.h_humi = data['hass']['humi']
        
#     def __get_uart_temp(self):
#         return self.temp
    
#     def __get_uart_humi(self):
#         return self.humi

#     def __get_uart_pres(self):
#         return self.pres

#     def __get_hass_temp(self):
#         return self.h_temp
    
#     def __get_hass_humi(self):
#         return self.h_humi

#     def __get_hvac_status(self):
#         return self.hvac