// firmware/c/src/led.c

#include "led.h"
#include "config.h"
#include "hardware/pwm.h"
#include "pico/stdlib.h"


// Helper to set PWM duty
static void set_pwm_duty(uint gpio, uint16_t duty) {
  pwm_set_gpio_level(gpio, duty);
}

void led_init() {
  // Initialize pins as PWM
  gpio_set_function(LED_PIN_STATUS, GPIO_FUNC_PWM);
  gpio_set_function(LED_PIN_ERROR, GPIO_FUNC_PWM);
  gpio_set_function(LED_PIN_ACTIVITY, GPIO_FUNC_PWM);

  // Get slice numbers
  uint slice_status = pwm_gpio_to_slice_num(LED_PIN_STATUS);
  uint slice_error = pwm_gpio_to_slice_num(LED_PIN_ERROR);
  uint slice_activity = pwm_gpio_to_slice_num(LED_PIN_ACTIVITY);

  // Config: 1kHz freq (assuming 125MHz data clock)
  // 125MHz / 125000 = 1000Hz. Wrap = 12500.
  // Wait, typical PWM range 0-65535 is nice.
  // Let's use default config but enable slices.

  pwm_config config = pwm_get_default_config();
  // Default: runs at sys clock. Wrap at 65535?

  pwm_init(slice_status, &config, true);
  if (slice_error != slice_status)
    pwm_init(slice_error, &config, true);
  if (slice_activity != slice_status && slice_activity != slice_error)
    pwm_init(slice_activity, &config, true);

  led_set_status(false);
  led_set_error(false);
  led_set_activity(false);
}

void led_set_status(bool on) { set_pwm_duty(LED_PIN_STATUS, on ? 65535 : 0); }

void led_set_error(bool on) { set_pwm_duty(LED_PIN_ERROR, on ? 65535 : 0); }

void led_set_activity(bool on) {
  set_pwm_duty(LED_PIN_ACTIVITY, on ? 65535 : 0);
}

void led_blink_status(int times) {
  for (int i = 0; i < times; i++) {
    led_set_status(false);
    sleep_ms(100);
    led_set_status(true);
    sleep_ms(100);
  }
}

void led_blink_error(int times) {
  for (int i = 0; i < times; i++) {
    led_set_error(false);
    sleep_ms(100);
    led_set_error(true);
    sleep_ms(100);
  }
  led_set_error(false);
}

void led_boot_animation() {
  // Simple fade in/out
  for (int i = 0; i < 65535; i += 500) {
    set_pwm_duty(LED_PIN_STATUS, i);
    set_pwm_duty(LED_PIN_ACTIVITY, i);
    set_pwm_duty(LED_PIN_ERROR, i);
    sleep_us(200);
  }
  for (int i = 65535; i > 0; i -= 500) {
    set_pwm_duty(LED_PIN_STATUS, i);
    set_pwm_duty(LED_PIN_ACTIVITY, i);
    set_pwm_duty(LED_PIN_ERROR, i);
    sleep_us(200);
  }
  led_set_status(false);
  led_set_error(false);
  led_set_activity(false);
}
