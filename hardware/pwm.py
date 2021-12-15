import sys
import ctypes

# this script is used to splite the user access
if __name__ == "__main__":
    FAN_GPIO = 18
    pwm_duty = int(sys.argv[1])

    gpio_pwm = ctypes.CDLL('hardware/pwm.so')
    gpio_pwm.gpio_init.argtypes = (ctypes.c_int,)
    gpio_pwm.gpio_set_pwm.argtypes = (ctypes.c_int, ctypes.c_int)
    gpio_pwm.gpio_init( ctypes.c_int(FAN_GPIO) )

    gpio_pwm.gpio_set_pwm( ctypes.c_int(FAN_GPIO), ctypes.c_int(pwm_duty) )