import sys
import os
import ctypes

# this script is used to splite the user access
if __name__ == "__main__":
    FAN_GPIO = 18
    pwm_duty = int(sys.argv[1])

    # init gpio
    dll_path = os.path.dirname(os.path.abspath(__file__))
    # print(f'{dll_path}{os.path.sep}pwm.so')
    gpio_pwm = ctypes.CDLL(f'{dll_path}{os.path.sep}pwm.so')
    gpio_pwm.gpio_init.argtypes = (ctypes.c_int,)
    gpio_pwm.gpio_set_pwm.argtypes = (ctypes.c_int, ctypes.c_int)
    gpio_pwm.gpio_init( ctypes.c_int(FAN_GPIO) )

    gpio_pwm.gpio_set_pwm( ctypes.c_int(FAN_GPIO), ctypes.c_int(pwm_duty) )