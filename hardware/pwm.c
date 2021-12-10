#include <stdio.h>
#include <ctype.h>
#include <wiringPi.h>

void gpio_init(int port) {
    wiringPiSetupGpio();
    pinMode(port, PWM_OUTPUT);
    pwmSetClock(640);
    pwmSetRange(100);
    // printf("gpio done!\n");
}


void gpio_set_pwm(int port, int duty) {
    pwmWrite(port, duty);
    // printf("I am running!\n");
    // printf("%d\n", duty);
}
