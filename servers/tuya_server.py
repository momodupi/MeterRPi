import requests
import json
import datetime
import time
import os
import hashlib
import hmac

TOKEN = 0
INSTRUCTION = 1
INFORMATION = 2
STATUS = 3
COMMAND = 4


class tuya_server(object):
    def __init__(self) -> None:
        super().__init__()

        dll_path = os.path.dirname(__file__)
        with open(f'{dll_path}/tuya_token.json') as json_file:
            __TOKEN = json.load(json_file)

        self.h = {
            'device_id': __TOKEN['device_id'],
            'client_id': __TOKEN['client_id'],
            'secret': __TOKEN['clinet_secret'],
            'sign_method': 'HMAC-SHA256',
            # 'HTTPMethod': 'POST',
            'body': None,
            'nonce': '123',
        }
        self.url = {
            TOKEN: 'https://openapi.tuyaus.com/v1.0/token?grant_type=1',
            INSTRUCTION: f'https://openapi.tuyaus.com/v1.0/iot-03/devices/{__TOKEN["device_id"]}/functions',
            INFORMATION: f'https://openapi.tuyaus.com/v1.1/iot-03/devices/{__TOKEN["device_id"]}',
            STATUS: f'https://openapi.tuyaus.com/v1.0/iot-03/devices/{__TOKEN["device_id"]}/status',
            COMMAND: f'https://openapi.tuyaus.com/v1.0/iot-03/devices/{__TOKEN["device_id"]}/commands', 
        }

        self.token = None

        self.__tuya_rqst_token()
        self.__tuya_rqst_instruction()
        self.__tuya_rqst_device_information()

    def __stringToSign(self, url, HTTPMethod):
        headers = {'secret': self.h['secret']}
        return (f'{HTTPMethod}\n' +                                                                 # HTTPMethod
                hashlib.sha256(bytes((self.h['body'] or '').encode('utf-8'))).hexdigest() + '\n' +  # Content-SHA256
                ''.join(['%s:%s\n'%(key, headers[key])                                              # Headers
                        for key in headers.get("Signature-Headers", "").split(":")
                        if key in headers]) + '\n' +
                '/' + url.split('//', 1)[-1].split('/', 1)[-1]) 
    
    def headers_wrapper(self, func):
        t = str(int(datetime.datetime.now().timestamp()*1000))
        url = self.url[func]

        if func == TOKEN:
            message = (
                self.h['client_id'] + t + self.__stringToSign(url, 'GET')
            ).encode('utf-8') 
        elif func == COMMAND:
            message = (
                self.h['client_id'] + self.token['result']['access_token'] + t + self.__stringToSign(url, 'POST')
            ).encode('utf-8') 
        else:
            message = (
                self.h['client_id'] + self.token['result']['access_token'] + t + self.__stringToSign(url, 'GET')
            ).encode('utf-8') 

        secret = self.h['secret'].encode('utf-8') 
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest().upper()

        if func == TOKEN:
            headers = {
                'secret': self.h['secret'],
                'client_id': self.h['client_id'],
                'sign': signature,
                't': t,
                'sign_method': 'HMAC-SHA256'
            }
        else:
            headers = {
                'secret': self.h['secret'],
                'client_id': self.h['client_id'],
                'sign': signature,
                't': t,
                'sign_method': 'HMAC-SHA256',
                'Content-Type': 'application/json',
                'mode': 'cors',
                'access_token': self.token['result']['access_token']
            }

        return headers

    def __tuya_rqst_token(self):
        headers = self.headers_wrapper(TOKEN)
        rqst = requests.get( self.url[TOKEN], headers=headers )
        try:
            rsp_dict = json.loads(rqst.content.decode())
        except:
            print('Failed to request token')
        self.token = rsp_dict
        # print(self.token)
        self.token_expire_time = int(rsp_dict['t'])+int(self.token['result']['expire_time'])*1000

    def __check_token(self):
        if int(str(int(datetime.datetime.now().timestamp()*1000))) >= self.token_expire_time:
            self.__tuya_rqst_token()

    def __tuya_rqst_instruction(self):
        self.__check_token()
        headers = self.headers_wrapper(INSTRUCTION)
        rqst = requests.get( self.url[INSTRUCTION], headers=headers )
        try:
            rsp_dict = json.loads(rqst.content.decode())
        except:
            print('Failed to request instruction')
        self.inst = rsp_dict['result']['functions']


    def __tuya_rqst_device_information(self):
        self.__check_token()
        headers = self.headers_wrapper(INFORMATION)
        rqst = requests.get( self.url[INFORMATION], headers=headers )
        try:
            rsp_dict = json.loads(rqst.content.decode())
        except:
            print('Failed to request information')
        self.info = rsp_dict['result']


    def __tuya_rqst_status(self):
        self.__check_token()
        headers = self.headers_wrapper(STATUS)
        rqst = requests.get( self.url[STATUS], headers=headers )
        try:
            rsp_dict = json.loads(rqst.content.decode())
        except:
            print('Failed to request information')
        # self.status = rsp_dict['result']
        return rsp_dict['result']

    def get_status(self):
        return self.__tuya_rqst_status()
    
    def __cmd2dict(self, switch_cmd):
        data = {'commands': []}
        for switch in switch_cmd:
            data['commands'].append(
                {'code': switch, 'value': switch_cmd[switch]}
            )
        return json.dumps(data)

    def __tuya_send_commnand(self, switch_cmd):
        self.__check_token()
        self.h['body'] = self.__cmd2dict(switch_cmd)
        headers = self.headers_wrapper(COMMAND)

        rqst = requests.post( self.url[COMMAND], headers=headers, data=self.__cmd2dict(switch_cmd) )
        try:
            rsp_dict = json.loads(rqst.content.decode())
        except:
            print('Failed to request information')
        # self.status = rsp_dict['result']
        print(rsp_dict)
        # set body be empty: for future GET requests
        self.h['body'] = ''
        return rsp_dict['result']

    def send_command(self, switch_cmd):
        return self.__tuya_send_commnand(switch_cmd)

