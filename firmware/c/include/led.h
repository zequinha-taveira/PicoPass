// firmware/c/include/led.h
#ifndef LED_H
#define LED_H

#include <stdbool.h>

void led_init();
void led_set_status(bool on);
void led_set_error(bool on);
void led_set_activity(bool on);
void led_blink_status(int times);
void led_blink_error(int times);
void led_boot_animation();

#endif
