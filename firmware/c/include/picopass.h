// firmware/c/include/picopass.h

#ifndef PICOPASS_H
#define PICOPASS_H

#include "config.h"
#include <stdbool.h>
#include <stdint.h>


typedef struct {
  bool occupied;
  uint8_t iv[16];
  uint8_t encrypted_data[MAX_PASSWORD_LENGTH + 16]; // + padding
  size_t data_length;
} password_slot_t;

typedef struct {
  char board_id[17];
  bool unlocked;
  uint32_t last_activity;
  uint32_t auto_lock_timeout;

  uint8_t master_hash[65];
  password_slot_t password_slots[MAX_PASSWORD_SLOTS];
} picopass_device_t;

void picopass_init(picopass_device_t *dev, const char *board_id);
bool picopass_unlock(picopass_device_t *dev, const char *master_password);
void picopass_lock(picopass_device_t *dev);
void picopass_type_password(picopass_device_t *dev, uint8_t slot);
bool picopass_add_password(picopass_device_t *dev, uint8_t slot,
                           const char *password);
bool picopass_delete_password(picopass_device_t *dev, uint8_t slot);
void picopass_check_auto_lock(picopass_device_t *dev);

#endif
