#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "pico/stdlib.h"
#include "bsp/board.h"
#include "tusb.h"

// Hardware Pins
#define LED_PIN 25
#define BUTTON_PIN 15

// State
static char pending_password[128] = {0};
static bool has_pending = false;

// Function prototypes
void hid_task(void);
void cdc_task(void);
void type_password(const char* str);

int main(void) {
    board_init();
    tusb_init();

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);

    while (1) {
        tud_task(); // tinyusb device task
        cdc_task();
        hid_task();
    }

    return 0;
}

//--------------------------------------------------------------------+
// CDC Task (Serial Communication)
//--------------------------------------------------------------------+
void cdc_task(void) {
    if (tud_cdc_available()) {
        char buf[256];
        uint32_t count = tud_cdc_read(buf, sizeof(buf) - 1);
        buf[count] = 0;

        if (strncmp(buf, "TYPE:", 5) == 0) {
            strncpy(pending_password, buf + 5, sizeof(pending_password) - 1);
            // Remove newline if present
            char* nl = strchr(pending_password, '\n');
            if (nl) *nl = 0;
            char* cr = strchr(pending_password, '\r');
            if (cr) *cr = 0;

            has_pending = true;
            tud_cdc_write_str("READY_TO_TYPE\n");
            tud_cdc_write_flush();
            
            // Visual feedback
            gpio_put(LED_PIN, 1);
        } else if (strncmp(buf, "PING", 4) == 0) {
            tud_cdc_write_str("PONG\n");
            tud_cdc_write_flush();
        }
    }
}

//--------------------------------------------------------------------+
// HID Task (Keyboard + Button)
//--------------------------------------------------------------------+
void hid_task(void) {
    static uint32_t start_ms = 0;
    static bool button_pressed_previously = false;

    // Simple debounce and task interval
    if (board_millis() - start_ms < 10) return;
    start_ms = board_millis();

    bool current_button_state = !gpio_get(BUTTON_PIN); // Active low

    if (current_button_state && !button_pressed_previously) {
        if (has_pending) {
            type_password(pending_password);
            has_pending = false;
            gpio_put(LED_PIN, 0); // Turn off LED after typing
            tud_cdc_write_str("TYPING_DONE\n");
            tud_cdc_write_flush();
        }
    }

    button_pressed_previously = current_button_state;
}

// Simplified typing logic
void type_password(const char* str) {
    while (*str) {
        uint8_t keycode = 0;
        uint8_t modifier = 0;

        if (*str >= 'a' && *str <= 'z') keycode = 4 + (*str - 'a');
        else if (*str >= 'A' && *str <= 'Z') {
            keycode = 4 + (*str - 'A');
            modifier = KEYBOARD_MODIFIER_LEFTSHIFT;
        }
        else if (*str >= '1' && *str <= '9') keycode = 30 + (*str - '1');
        else if (*str == '0') keycode = 39;
        
        if (keycode) {
            uint8_t key_report[6] = { keycode, 0, 0, 0, 0, 0 };
            tud_hid_keyboard_report(REPORT_ID_KEYBOARD, modifier, key_report);
            board_delay(10);
            tud_hid_keyboard_report(REPORT_ID_KEYBOARD, 0, NULL);
            board_delay(10);
        }
        str++;
    }
    
    // Press Enter
    uint8_t enter_report[6] = { HID_KEY_ENTER, 0, 0, 0, 0, 0 };
    tud_hid_keyboard_report(REPORT_ID_KEYBOARD, 0, enter_report);
    board_delay(10);
    tud_hid_keyboard_report(REPORT_ID_KEYBOARD, 0, NULL);
}

// Callbacks required by TinyUSB
void tud_hid_report_complete_cb(uint8_t instance, uint8_t const* report, uint8_t len) {
    (void) instance; (void) report; (void) len;
}

uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t* buffer, uint16_t reqlen) {
    (void) instance; (void) report_id; (void) report_type; (void) buffer; (void) reqlen;
    return 0;
}

void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t const* buffer, uint16_t bufsize) {
    (void) instance; (void) report_id; (void) report_type; (void) buffer; (void) bufsize;
}
