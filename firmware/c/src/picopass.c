// firmware/c/src/picopass.c

#include "picopass.h"
#include "button.h"
#include "crypto.h"
#include "flash_storage.h"
#include "led.h"
#include "usb_hid.h"
#include <pico/stdlib.h>
#include <stdio.h>
#include <string.h>

void picopass_init(picopass_device_t *dev, const char *board_id) {
  memset(dev, 0, sizeof(picopass_device_t));

  strncpy(dev->board_id, board_id, sizeof(dev->board_id) - 1);
  dev->unlocked = false;
  dev->auto_lock_timeout = 120; // 2 minutes
  dev->last_activity = 0;

  // Initialize hardware
  led_init();
  button_init();
  crypto_init(board_id);
  flash_storage_init();

  // Load data from flash
  flash_storage_load(dev);

  // Initial state: locked
  picopass_lock(dev);
}

bool picopass_unlock(picopass_device_t *dev, const char *master_password) {
  // If master password not set, this is first time
  if (dev->master_hash[0] == 0) {
    if (master_password) {
      crypto_hash_password(master_password, dev->master_hash);
      flash_storage_save(dev);
      printf("✓ Master password set\n");
    }
  } else {
    // Verify password
    if (!master_password) {
      printf("! Master password required\n");
      led_blink_error(3);
      return false;
    }

    char hash[65];
    crypto_hash_password(master_password, hash);

    if (memcmp(hash, dev->master_hash, 64) != 0) {
      printf("✗ Wrong password!\n");
      led_blink_error(5);
      return false;
    }
  }

  dev->unlocked = true;
  dev->last_activity = to_ms_since_boot(get_absolute_time());

  led_set_status(true);
  led_blink_status(2);

  printf("✓ Device UNLOCKED\n");
  return true;
}

void picopass_lock(picopass_device_t *dev) {
  dev->unlocked = false;

  led_set_status(false);
  led_set_error(true);

  // Clear sensitive data from memory
  crypto_clear_key_cache();

  printf("✓ Device LOCKED\n");
}

void picopass_type_password(picopass_device_t *dev, uint8_t slot) {
  if (!dev->unlocked) {
    printf("! Device locked - cannot type slot %d\n", slot);
    led_blink_error(3);
    return;
  }

  if (slot >= MAX_PASSWORD_SLOTS) {
    printf("✗ Invalid slot: %d\n", slot);
    led_blink_error(2);
    return;
  }

  if (!dev->password_slots[slot].occupied) {
    printf("! Slot %d is empty\n", slot);
    led_blink_error(2);
    return;
  }

  // Decrypt password
  char password[MAX_PASSWORD_LENGTH];
  if (!crypto_decrypt(dev->password_slots[slot].encrypted_data,
                      dev->password_slots[slot].data_length,
                      dev->password_slots[slot].iv, password)) {
    printf("✗ Decryption failed\n");
    led_blink_error(4);
    return;
  }

  // Type via USB HID
  printf("⌨ Typing password from slot %d...\n", slot);
  led_set_activity(true);

  hid_type_string(password);

  led_set_activity(false);
  led_blink_status(2);

  printf("✓ Password typed!\n");

  // Clear password from memory
  memset(password, 0, sizeof(password));

  // Update last activity
  dev->last_activity = to_ms_since_boot(get_absolute_time());
}

bool picopass_add_password(picopass_device_t *dev, uint8_t slot,
                           const char *password) {
  if (!dev->unlocked) {
    printf("! Device locked\n");
    return false;
  }

  if (slot >= MAX_PASSWORD_SLOTS) {
    printf("✗ Invalid slot: %d\n", slot);
    return false;
  }

  // Encrypt password
  uint8_t iv[16];
  uint8_t encrypted[MAX_PASSWORD_LENGTH];
  size_t encrypted_len;

  if (!crypto_encrypt(password, encrypted, &encrypted_len, iv)) {
    printf("✗ Encryption failed\n");
    led_blink_error(4);
    return false;
  }

  // Save to slot
  dev->password_slots[slot].occupied = true;
  memcpy(dev->password_slots[slot].encrypted_data, encrypted, encrypted_len);
  dev->password_slots[slot].data_length = encrypted_len;
  memcpy(dev->password_slots[slot].iv, iv, 16);

  // Save to flash
  flash_storage_save(dev);

  printf("✓ Password saved to slot %d\n", slot);
  led_blink_status(3);

  return true;
}

bool picopass_delete_password(picopass_device_t *dev, uint8_t slot) {
  if (!dev->unlocked) {
    return false;
  }

  if (slot >= MAX_PASSWORD_SLOTS) {
    return false;
  }

  memset(&dev->password_slots[slot], 0, sizeof(password_slot_t));
  flash_storage_save(dev);

  printf("✓ Slot %d cleared\n", slot);
  return true;
}

void picopass_check_auto_lock(picopass_device_t *dev) {
  if (!dev->unlocked) {
    return;
  }

  uint32_t now = to_ms_since_boot(get_absolute_time());
  uint32_t elapsed = (now - dev->last_activity) / 1000; // Convert to seconds

  if (elapsed >= dev->auto_lock_timeout) {
    printf("⏰ Auto-lock triggered after %lu seconds\n", elapsed);
    picopass_lock(dev);
  }
}
