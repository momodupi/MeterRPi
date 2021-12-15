import subprocess
import json
import serial
import time
import threading
import queue


class uart_sensor(object):
    def __init__(self, bps=19200) -> None:
        super().__init__()

        self.bps = bps
        self.uart_sync()
        time.sleep(1)
        self.ser = serial.Serial('/dev/ttyACM0', bps, 8, 'N', 1)

        self.q = queue.Queue(10)
        self.rec_flag = True

        self.temp = 0
        self.humi = 0
        self.pres = 0

    def __decode_uart_data(self, data):
        temp = 0
        humi = 0
        pres = 0
        if len(data) > 0:
            for u_d in data:
                temp += (u_d['tem1'] + u_d['tem2'])/2
                humi += u_d['hum']
                pres += u_d['pre']
            temp = temp/len(data)
            humi = humi/len(data)
            pres = pres/len(data)
            return temp, humi, pres
        else:
            return self.temp, self.humi, self.pres
            
    def uart_sync(self):
        subprocess.call(['sudo', 'stty', '-F', '/dev/ttyACM0', f'{self.bps}', 'cs8', '-cstopb', '-parenb'])
        print('uart info: synchronized')

    def start_receive(self):
        threading.Thread(target=self.__receive_data, daemon=True).start()

    def stop_receive(self):
        self.rec_flag = False

    def __receive_data(self):
        self.uart_sync()
        time.sleep(3)
        while self.rec_flag:
            rd_line = self.ser.readline()

            try:
                data_str = str(rd_line).split('\"')[1].replace(r'\r', '').replace(r'\n', '')
                # print(data_str)
                data = json.loads(data_str.replace("'", '"'))
            except Exception as e:
                print(f'uart error: {e}')
                self.uart_sync()
                continue
            self.q.put(data)
            time.sleep(3)

    def get_data(self):
        if self.q.qsize() != 0:
            data_set = [self.q.get() for _ in range(self.q.qsize())]
            temp, humi, pres = self.__decode_uart_data(data_set)
            return temp, humi, pres
        else:
            return self.temp, self.humi, self.pres
            
