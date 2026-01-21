// firmware/c/src/main.c

#include "hardware/flash.h"
#include "hardware/sync.h"
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "tusb.h"
#include <stdio.h>
#include <string.h>


#include "button.h"
#include "config.h"
#include "led.h"
#include "picopass.h"
#include "serial.h"


// ============================================
// GLOBAL STATE
// ============================================

picopass_device_t device;
char board_id[17];

// ============================================
// INITIALIZATION
// ============================================

void get_board_id() {
  pico_unique_board_id_t id;
  pico_get_unique_board_id(&id);

  for (int i = 0; i < 8; i++) {
    sprintf(board_id + (i * 2), "%02X", id.id[i]);
  }
  board_id[16] = '\0';
}

void print_banner() {
  printf("\n");
  printf("╔════════════════════════════════════════╗\n");
  printf("║         PicoPass v%s              ║\n", PICOPASS_VERSION);
  printf("║    Hardware Password Manager           ║\n");
  printf("║    Board ID: %-24s║\n", board_id);
  printf("╚════════════════════════════════════════╝\n");
  printf("\n");
}

// ============================================
// MAIN LOOP
// ============================================

int main() {
  // Initialize stdio
  stdio_init_all();
  sleep_ms(2000); // Wait for USB

  // Get board ID
  get_board_id();
  print_banner();

  printf("Initializing hardware...\n");

  // Initialize TinyUSB
  tusb_init();

  // Initialize PicoPass
  picopass_init(&device, board_id);

  printf("✓ Hardware initialized\n");
  printf("✓ PicoPass ready!\n");
  printf("========================================\n\n");

  // Boot animation
  led_boot_animation();

  // Main loop
  uint32_t last_auto_lock_check = 0;

  while (1) {
    // TinyUSB tasks
    tud_task();

    // Process serial commands
    serial_process_commands(&device);

    // Check buttons
    button_check_all(&device);

    // Auto-lock check (every second)
    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (now - last_auto_lock_check >= 1000) {
      picopass_check_auto_lock(&device);
      last_auto_lock_check = now;
    }

    // Small delay to not hog CPU
    sleep_ms(1);
  }

  return 0;
}
