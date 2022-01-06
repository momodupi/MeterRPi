import paho.mqtt.client as mqtt 
import queue
import json

BROKER = 'localhost'
PORT = 1883
TOPIC_SENSOR = "meterpi/sensor"
TOPIC_HVAC = "esp32/hvac/cmd"
TOPIC_LISTENER = "meterpi/#"


class mqtt_subscriber(object):
    def __init__(self) -> None:
        super().__init__()
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER, PORT)

        self.client.subscribe(TOPIC_LISTENER)
        self.client.on_message = self.on_message

        self.q = queue.Queue(50)

    def start(self):
        self.client.loop_start()
        
    def stop(self):
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print('mqtt subscriber: Connected to MQTT Broker!')
        else:
            print('mqtt subscriber: Failed to connect, return code {rc}\n')
    
    def on_message(self, client, userdata, msg):
        print(f'mqtt subscriber: Received {msg.payload.decode()} from {msg.topic}')
        data = {msg.topic: msg.payload.decode()}
        self.q.put(data)


class mqtt_publisher(object):
    def __init__(self) -> None:
        super().__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER, PORT)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print('mqtt publisher: Connected to MQTT Broker!')
        else:
            print('mqtt publisher: Failed to connect, return code {rc}\n')

    def publish(self, topic, msg):
        result = self.client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status != 0:
            print(f'mqtt publisher: Failed to send message to topic {topic}, status={result}')


class mqtt_service(object):
    def __init__(self) -> None:
        super().__init__()

        self.p = mqtt_publisher()
        self.s = mqtt_subscriber()

        self.s.start()
        print('mqtt: init done')
        
        self.topic_list = {
            'sensor': TOPIC_SENSOR,
            'relay': TOPIC_HVAC,
            'ui_temp': 'meterpi/hvac/temp',
            'ui_power': 'meterpi/hvac/power',
            'ui_fan': 'meterpi/hvac/fan',
            'cmd_fan': 'meterpi/hvac/fan/cmd'
        }

    def sends(self, mode, msg):
        self.p.publish(self.topic_list[mode], msg)

    def send(self, mode, msg):
        self.p.publish(self.topic_list[mode], json.dumps(msg))
    
    def stop(self):
        self.p.client.disconnect()
        self.s.stop()



