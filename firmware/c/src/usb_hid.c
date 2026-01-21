// firmware/c/src/usb_hid.c

#include "usb_hid.h"
#include "tusb.h"
#include <ctype.h>
#include <string.h>

// HID Report: [modifier, reserved, key1-key6]
static uint8_t hid_report[8] = {0};

// Keycode mapping
static uint8_t char_to_keycode(char c) {
  if (c >= 'a' && c <= 'z') {
    return 0x04 + (c - 'a'); // a=0x04, z=0x1D
  }
  if (c >= 'A' && c <= 'Z') {
    return 0x04 + (c - 'A'); // Same as lowercase
  }
  if (c >= '1' && c <= '9') {
    return 0x1E + (c - '1'); // 1=0x1E, 9=0x26
  }

  switch (c) {
  case '0':
    return 0x27;
  case ' ':
    return 0x2C;
  case '-':
    return 0x2D;
  case '=':
    return 0x2E;
  case '[':
    return 0x2F;
  case ']':
    return 0x30;
  case '\\':
    return 0x31;
  case ';':
    return 0x33;
  case '\'':
    return 0x34;
  case ',':
    return 0x36;
  case '.':
    return 0x37;
  case '/':
    return 0x38;
  case '!':
    return 0x1E; // Shift + 1
  case '@':
    return 0x1F; // Shift + 2
  case '#':
    return 0x20; // Shift + 3
  case '$':
    return 0x21; // Shift + 4
  case '%':
    return 0x22; // Shift + 5
  case '^':
    return 0x23; // Shift + 6
  case '&':
    return 0x24; // Shift + 7
  case '*':
    return 0x25; // Shift + 8
  case '(':
    return 0x26; // Shift + 9
  case ')':
    return 0x27; // Shift + 0
  default:
    return 0;
  }
}

static bool needs_shift(char c) {
  return isupper(c) || strchr("!@#$%^&*()", c) != NULL;
}

static void send_key(uint8_t keycode, bool shift) {
  // Press
  memset(hid_report, 0, sizeof(hid_report));
  hid_report[0] = shift ? 0x02 : 0x00; // Left Shift modifier
  hid_report[2] = keycode;

  tud_hid_keyboard_report(1, hid_report[0], &hid_report[2]);
  sleep_ms(10);

  // Release
  memset(hid_report, 0, sizeof(hid_report));
  tud_hid_keyboard_report(1, 0, &hid_report[2]);
  sleep_ms(10);
}

void hid_type_string(const char *text) {
  for (size_t i = 0; i < strlen(text); i++) {
    char c = text[i];
    uint8_t keycode = char_to_keycode(c);

    if (keycode) {
      send_key(keycode, needs_shift(c));
    }
  }
}

void hid_press_enter() {
  send_key(0x28, false); // Enter key
}

void hid_press_tab() {
  send_key(0x2B, false); // Tab key
}

// TinyUSB HID callbacks (Weak linkage usually overrides these)
uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id,
                               hid_report_type_t report_type, uint8_t *buffer,
                               uint16_t reqlen) {
  (void)instance;
  (void)report_id;
  (void)report_type;
  (void)buffer;
  (void)reqlen;
  return 0;
}

void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id,
                           hid_report_type_t report_type, uint8_t const *buffer,
                           uint16_t bufsize) {
  (void)instance;
  (void)report_id;
  (void)report_type;
  (void)buffer;
  (void)bufsize;
}
