// firmware/c/src/button.c

#include "button.h"
#include "config.h"
#include "pico/stdlib.h"
#include <stdio.h>


#define NUM_BUTTONS 5
#define DEBOUNCE_MS 50
#define LONG_PRESS_MS 1000

static const uint8_t BUTTON_PINS[NUM_BUTTONS] = {
    BTN_PIN_UNLOCK, BTN_PIN_SLOT1, BTN_PIN_SLOT2, BTN_PIN_SLOT3, BTN_PIN_SLOT4};

static uint32_t press_start_time[NUM_BUTTONS] = {0};
static bool last_state[NUM_BUTTONS] = {true}; // default HIGH (pull-up)
static uint32_t last_change_time[NUM_BUTTONS] = {0};

void button_init() {
  for (int i = 0; i < NUM_BUTTONS; i++) {
    gpio_init(BUTTON_PINS[i]);
    gpio_set_dir(BUTTON_PINS[i], GPIO_IN);
    gpio_pull_up(BUTTON_PINS[i]);
    last_state[i] = true;
  }
}

void button_check_all(picopass_device_t *dev) {
  uint32_t now = to_ms_since_boot(get_absolute_time());

  for (int i = 0; i < NUM_BUTTONS; i++) {
    bool current = gpio_get(BUTTON_PINS[i]); // true = released, false = pressed

    if (current != last_state[i]) {
      // State changed
      if ((now - last_change_time[i]) > DEBOUNCE_MS) {
        last_state[i] = current;
        last_change_time[i] = now;

        if (!current) {
          // Pressed
          press_start_time[i] = now;
        } else {
          // Released
          uint32_t duration = now - press_start_time[i];

          // Button logic
          if (i == 0) { // Unlock button
            if (duration >= LONG_PRESS_MS) {
              if (dev->unlocked) {
                picopass_lock(dev);
              } else {
                // Trigger waiting pattern?
                // Not implemented in C version explicitly, but can print
                printf("! Waiting for serial password...\n");
              }
            }
          } else { // Slot buttons (1-4)
            if (duration > DEBOUNCE_MS) {
              // Button index 1 -> Slot 0
              picopass_type_password(dev, i - 1);
            }
          }
        }
      }
    }
  }
}
