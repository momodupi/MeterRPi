from service.mosquitto_service import mqtt_service
import requests
import os
import json

class homeassistant_service(object):
    def __init__(self, mqtt) -> None:
        super().__init__()

        dll_path = os.path.dirname(__file__)
        with open(f'{dll_path}/hass_token.json') as json_file:
            __TOKEN = json.load(json_file)

        self.headers = {
            'Authorization': f'Bearer {__TOKEN["token"]}',
            'Content-Type': 'application/json'
        }

        self.urls = {
            # 'atmos_temp': 'sensor.openweathermap_feels_like_temperature',
            # 'atmos_humi': 'sensor.openweathermap_humidity'
            'weather_home': 'weather.home',
            'desired_temp': 'climate.hvac'
        }
        # self.mqtt = mqtt_service()
        self.mqtt = mqtt

        self.ui_data = { 'temp': 0, 'manual': False, 'auto': False }
        self.sensor_data = {'temp': 0.0, 'humi': 0.0}
        self.get_initial_status()
        

    def __read_state_data(self, state_class):
        url = f'http://localhost:8123/api/states/{state_class}'
        try:
            rqst = requests.get( url, headers=self.headers )
            # rqst.raise_for_status()
        except requests.exceptions.RequestException as e:
            print (f'hass: http requests error: {e}')
            return None
        return rqst.json()
        
        

    def get_atmos_temp(self):
        data = self.__read_state_data(self.urls['weather_home'])
        # self.atmos_temp = int(float(data['state']))
        if data != None:
            return int(float(data['attributes']['temperature']))
        else:
            return 0

    def get_atmos_humi(self):
        data = self.__read_state_data(self.urls['weather_home'])
        if data != None:
            return int(float(data['attributes']['humidity']))
        else:
            return 0

    def get_desired_temp(self):
        data = self.__read_state_data(self.urls['desired_temp'])
        if data != None:
            return int(float(data['attributes']['temperature']))
        else:
            return 0

    def get_fan_mode(self):
        data = self.__read_state_data(self.urls['desired_temp'])
        if data != None:
            return data['state']
        else:
            return False

    def get_initial_status(self):
        self.fan_mode = self.get_fan_mode()
        if self.fan_mode == 'fan_only':
            self.ui_data['manual'] = True
            self.ui_data['auto'] = False
        elif self.fan_mode == 'auto':
            self.ui_data['manual'] = False
            self.ui_data['auto'] = True
        else:
            self.ui_data['manual'] = False
            self.ui_data['auto'] = False

        self.ui_data['temp'] = self.get_desired_temp()

        self.mqtt.send('esp_targ', int(self.ui_data['temp']))

    def set_home_sensor(self):
        # data['temp'] = round(data['temp'],1)
        # data['humi'] = int(data['humi'])
        # data['pres'] = round(data['pres'],2)
        # # self.mqtt.send('sensor', data)
        # self.mqtt.send('sensor_temp', data['temp'])
        # self.mqtt.send('sensor_humi', data['humi'])
        # self.mqtt.send('sensor_pres', data['pres'])

        self.mqtt.send('esp_temp', self.sensor_data['temp'])
        self.mqtt.send('esp_humi', self.sensor_data['humi'])
        self.mqtt.send('esp_targ', self.ui_data['temp'])
        self.mqtt.send('esp_stat', self.fan_mode)

    def get_mqtt_data(self):
        if self.mqtt.s.q.qsize() != 0:
            for _ in range(self.mqtt.s.q.qsize()):
                data = self.mqtt.s.q.get()
                print(data)
                # if 'meterpi/hvac/power' in data:
                #     self.ui_data['power'] = True if data['meterpi/hvac/power'] == 'ON' else False
                if 'meterpi/hvac/fan' in data:
                    if data['meterpi/hvac/fan'] == 'fan_only':
                        self.ui_data['manual'] = True
                        self.ui_data['auto'] = False
                        self.fan_mode = 'fan_only'
                        self.mqtt.send('esp_stat', 'fan_only')
                    elif data['meterpi/hvac/fan'] == 'auto':
                        self.ui_data['manual'] = False
                        self.ui_data['auto'] = True
                        self.fan_mode = 'auto'
                        self.mqtt.send('esp_stat', 'auto')
                    else:
                        self.ui_data['manual'] = False
                        self.ui_data['auto'] = False
                        self.fan_mode = 'off'
                        self.mqtt.send('esp_stat', 'off')
                elif 'meterpi/hvac/temp' in data:    
                    self.ui_data['temp'] = float(data['meterpi/hvac/temp'])
                elif 'meterpi/sensor/temp' in data:    
                    self.sensor_data['temp'] = float(data['meterpi/sensor/temp'])
                elif 'meterpi/sensor/humi' in data:    
                    self.sensor_data['humi'] = float(data['meterpi/sensor/humi'])
                    
        return self.ui_data
        
    # def set_ui_data(self, data):
    #     if self.mqtt.s.q.qsize() != 0:
    #         for _ in range(self.mqtt.s.q.qsize()):
    #             data = self.mqtt.s.q.get()
    #             print(data)
    #             if 'meterpi/hvac/power' in data:
    #                 self.ui_data['power'] = True if data['meterpi/hvac/power'] == 'ON' else False
    #             # if 'meterpi/hvac/fan' in data:
    #             #     if data['meterpi/hvac/fan'] == 'low': 
    #             #         self.ui_data['fan'] = 1
    #             #     elif data['meterpi/hvac/fan'] == 'medium': 
    #             #         self.ui_data['fan'] = 2
    #             #     elif data['meterpi/hvac/fan'] == 'high': 
    #             #         self.ui_data['fan'] = 3
    #             #     else: 
    #             #         self.ui_data['fan'] = 0
    #             if 'meterpi/hvac/temp' in data:    
    #                 self.ui_data['temp'] = float(data['meterpi/hvac/temp'])
        
