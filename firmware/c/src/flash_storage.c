// firmware/c/src/flash_storage.c

#include "flash_storage.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include <string.h>


// Use the last sector of flash?
// Or config.h FLASH_TARGET_OFFSET
// Note: We should probably put a magic header to verify data.
#define STORAGE_MAGIC 0x5049434F // PICO

typedef struct {
  uint32_t magic;
  uint32_t version;
  picopass_device_t data;
  uint32_t crc; // checking later
} storage_header_t;

void flash_storage_init() {
  // Nothing to init for raw flash usually
}

bool flash_storage_save(picopass_device_t *dev) {
  storage_header_t header;
  header.magic = STORAGE_MAGIC;
  header.version = 1;
  memcpy(&header.data, dev, sizeof(picopass_device_t));
  header.crc = 0; // TODO impl CRC

  // We need a buffer that is multiple of PAGE size (256)
  // sizeof(storage_header_t) calculation
  // Must be sector aligned for erase (4096) and page aligned for write (256)

  uint32_t total_size = sizeof(storage_header_t);
  uint32_t write_size =
      (total_size + FLASH_PAGE_SIZE - 1) & ~(FLASH_PAGE_SIZE - 1);

  if (write_size > FLASH_TARGET_SIZE) {
    printf("Error: Data too large for flash sector\n");
    return false;
  }

  uint8_t *buffer = (uint8_t *)calloc(1, write_size);
  memcpy(buffer, &header, total_size);

  uint32_t ints = save_and_disable_interrupts();
  flash_range_erase(FLASH_TARGET_OFFSET, FLASH_TARGET_SIZE);
  flash_range_program(FLASH_TARGET_OFFSET, buffer, write_size);
  restore_interrupts(ints);

  free(buffer);
  return true;
}

bool flash_storage_load(picopass_device_t *dev) {
  const uint8_t *flash_target_contents =
      (const uint8_t *)(XIP_BASE + FLASH_TARGET_OFFSET);

  const storage_header_t *header =
      (const storage_header_t *)flash_target_contents;

  if (header->magic != STORAGE_MAGIC) {
    return false;
  }

  memcpy(dev, &header->data, sizeof(picopass_device_t));
  return true;
}
