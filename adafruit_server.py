import sys
from Adafruit_IO import MQTTClient

class adafruit_server(object):
    def __init__(self) -> None:
        super().__init__()

        ADAFRUIT_IO_USERNAME = "momodupi"
        ADAFRUIT_IO_KEY = "aio_NDkG04jPLPkg3aNLSMDo8TaCr9Im"

        self.feed_data = {'temp': 26, 'lamp': False}
        self.client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

        self.client.on_connect = self.__connected
        self.client.on_message = self.__message


    def feeding(self):
        self.client.connect()
        self.client.loop_background()
    
    
    def __connected(self, client):
        for feed_id in ['MeteRpi_temp', 'MeteRpi_lamp']:
            self.client.subscribe(feed_id)
        print('Waiting for feed data…')


    def __message(self, client, feed_id, payload):
        if feed_id == 'MeteRpi_lamp':
            self.feed_data['lamp'] = True if payload == 'on' else False
        elif feed_id == 'MeteRpi_temp':
            self.feed_data['temp'] = int(payload)
        else:
            pass
        print(self.feed_data)

