import requests
import json
import time
import os
import hashlib
import hmac


class hvac(object):
    def __init__(self) -> None:
        super().__init__()

        dll_path = os.path.dirname(__file__)
        with open(f'{dll_path}/tuya_token.json') as json_file:
            __TOKEN = json.load(json_file)

        self.device_id = __TOKEN['device_id']
        self.client_id = __TOKEN['client_id']
        self.clinet_secret = __TOKEN['clinet_secret']

        self.__rqst_tuya_token()

    def __rqst_tuya_token(self):
        tsp = str(int(time.time()*1000))
        signature = hmac.new(
            self.clinet_secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()
        rqst = requests.get(
            f'https://openapi.tuyaus.com/v1.0/token?grant_type=1',
            headers={
                'sign_method': 'HMAC-SHA256',
                'client_id': self.client_id,
                't': tsp,
                'sign_method': 'HMAC-SHA256'
            }
        )
        print(rqst.text)
        

    def __rqst_tuya_properties(self):
        tsp = int(datetime.datetime.now().timestamp)
        rqst = requests.get(
            f'https://openapi.tuyaus.com/v1.0/iot-03/devices/{self.device_id}/specification',
            headers={
                'sign_method': 'HMAC-SHA256',
                'client_id': self.client_id,
                't': tsp,
                'mode': 'cors',
                'Content-Type': 'application/json',

            }
        )

    def set(self, lvl):
        if lvl == 1:
            pass
        elif lvl == 2:
            pass
        elif lvl == 3:
            pass
        else:
            pass


h = hvac()
