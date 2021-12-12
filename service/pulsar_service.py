import base64
import hashlib
import ssl
import websocket
import json
import time
import os
import queue
import threading
# try:
#     import thread
# except ImportError:
#     import _thread as thread


# env
MQ_ENV_PROD = "event"
MQ_ENV_TEST = "event-test"
MQ_ENV = MQ_ENV_TEST

# basic config
WSS_SERVER_URL = "wss://mqe.tuyaus.com:8285/"
WEB_SOCKET_QUERY_PARAMS = "?ackTimeoutMillis=3000&subscriptionType=Failover"
SSL_OPT = {"cert_reqs": ssl.CERT_NONE}

CONNECT_TIMEOUT_SECONDS = 3
CHECK_INTERVAL_SECONDS = 3

PING_INTERVAL_SECONDS = 30
PING_TIMEOUT_SECONDS = 3

RECONNECT_MAX_TIMES = 1000



class pulsar_service(object):
    def __init__(self) -> None:
        super().__init__()

        dll_path = os.path.dirname(__file__)
        with open(f'{dll_path}/tuya_token.json') as json_file:
            __TOKEN = json.load(json_file)

        # accessId, accessKey，serverUrl，MQ_ENV
        self.ACCESS_ID = __TOKEN['client_id']
        self.ACCESS_KEY = __TOKEN['clinet_secret']

        header = {'Connection': 'Upgrade',
                'username': self.ACCESS_ID,
                'password': self.gen_pwd()}

        self.reconnect_count = 1
        self.connect_status = 0

        self.q = queue.Queue(10)

        websocket.setdefaulttimeout(CONNECT_TIMEOUT_SECONDS)
        
        self.ws = websocket.WebSocketApp(self.get_topic_url(),
                                    header=header,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)

    # topic env
    def get_topic_url(self):
        return WSS_SERVER_URL + 'ws/v2/consumer/persistent/' + self.ACCESS_ID + '/out/' + MQ_ENV + '/' + self.ACCESS_ID + '-sub' + WEB_SOCKET_QUERY_PARAMS


    # handler message
    def message_handler(self, payload):
        dataMap = json.loads(payload)
        # print(dataMap)

        decryptContentDataStr = dataMap['data']
        data = self.decrypt_by_aes(decryptContentDataStr, self.ACCESS_KEY)
        print(f'\ndecryptContentData={data}')
        
        if 'protocol' in dataMap:
            if dataMap['protocol'] == 4:
                self.q.put(json.loads(data))    


    # decrypt
    def decrypt_by_aes(self, raw, key):
        import base64
        from Crypto.Cipher import AES
        raw = base64.b64decode(raw)
        key = key[8:24]
        cipher = AES.new(key, AES.MODE_ECB)
        raw = cipher.decrypt(raw)
        res_str = raw.decode('utf-8')
        res_str = eval(repr(res_str).replace('\\r', ''))
        res_str = eval(repr(res_str).replace('\\n', ''))
        res_str = eval(repr(res_str).replace('\\f', ''))
        return res_str


    def md5_hex(self, md5_str):
        md = hashlib.md5()
        md.update(md5_str.encode('utf-8'))
        return md.hexdigest()


    def gen_pwd(self,):
        md5_hex_key = self.md5_hex(self.ACCESS_KEY)
        mix_str = self.ACCESS_ID+md5_hex_key
        return self.md5_hex(mix_str)[8:24]


    def on_error(self, ws, error):
        print("on error is: %s" % error)


    def reconnect(self):
        print(f'ws-client connect status is not ok.\ntrying to reconnect for the {self.reconnect_count} time')
        self.reconnect_count += 1
        if self.reconnect_count < RECONNECT_MAX_TIMES:
            threading.Thread(target=self.connect, daemon=True).start()


    def on_message(self, ws, message):
        message_json = json.loads(message)
        payload = self.base64_decode_as_string(message_json['payload'])
        print(f'---\nreceived message origin payload: {payload}')
        # handler payload
        self.message_handler(payload)
        try:
            self.message_handler(payload)
        except Exception as e:
            print(f'handler message, a business exception has occurred,e:{e}')


    def on_close(self, obj):
        print('Connection closed!')
        obj.close()
        self.connect_status = 0


    def connect(self):
        print('---\nws-client connecting...')
        self.ws.run_forever(sslopt=SSL_OPT, ping_interval=PING_INTERVAL_SECONDS, ping_timeout=PING_TIMEOUT_SECONDS)


    def send_ack(self, message_id):
        json_str = json.dumps({'messageId': message_id})
        self.ws.send(json_str)


    def base64_decode_as_string(self, byte_string):
        byte_string = base64.b64decode(byte_string)
        return byte_string.decode('ascii')

    def start(self):
        threading.Thread(target=self.connect, daemon=True).start()

    def check_status(self):
        try:
            if self.ws.sock.status == 101:
                print('ws-client connect status is ok.')
                self.reconnect_count = 1
                self.connect_status = 1
        except Exception:
            self.connect_status = 0
            self.reconnect()
    

# ps = pulsar_server()
# ps.start()
# while True:
#     ps.check_status()
#     time.sleep(3)