import requests
import os
import json

class homeassistant_service(object):
    def __init__(self) -> None:
        super().__init__()

        dll_path = os.path.dirname(__file__)
        with open(f'{dll_path}/hass_token.json') as json_file:
            __TOKEN = json.load(json_file)

        self.headers = {
            'Authorization': f'Bearer {__TOKEN["token"]}',
            'Content-Type': 'application/json'
        }

        self.urls = {
            'atmos_temp': 'sensor.openweathermap_feels_like_temperature',
            'atmos_humi': 'sensor.openweathermap_humidity'
        }

    def __read_state_data(self, state_class):
        url = f'http://localhost:8123/api/states/{state_class}'
        rqst = requests.get( url, headers=self.headers )
        return rqst.json()

    def get_atmos_temp(self):
        data = self.__read_state_data(self.urls['atmos_temp'])
        # self.atmos_temp = int(float(data['state']))
        return int(float(data['state']))

    def get_atmos_humi(self):
        data = self.__read_state_data(self.urls['atmos_humi'])
        return int(float(data['state']))

