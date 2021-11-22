import subprocess
import json
import serial
import time
import threading
import queue


class UART(object):
    def __init__(self, bps=19200) -> None:
        super().__init__()

        self.bps = bps
        self.uart_sync()
        time.sleep(1)
        self.ser = serial.Serial('/dev/ttyACM0', bps, 8, 'N', 1)

        self.q = queue.Queue(10)
        self.rec_flag = True

    def uart_sync(self):
        subprocess.call(['sudo', 'stty', '-F', '/dev/ttyACM0', f'{self.bps}', 'cs8', '-cstopb', '-parenb'])

    def start_receive(self):
        threading.Thread(target=self.__receive_data, daemon=True).start()

    def stop_receive(self):
        self.rec_flag = False

    def __receive_data(self):
        self.uart_sync()
        time.sleep(1)
        while self.rec_flag:
            data_str = str(self.ser.readline()).split('\"')[1].replace(r'\r', '').replace(r'\n', '')
            data = json.loads(data_str.replace("'", '"'))
            self.q.put(data)
            time.sleep(4)

    def get_data(self):
        if self.q.qsize != 0:
            data_set = [self.q.get() for _ in range(self.q.qsize())]
            return data_set
        else:
            return None
            
