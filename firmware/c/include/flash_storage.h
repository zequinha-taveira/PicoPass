// firmware/c/include/flash_storage.h
#ifndef FLASH_STORAGE_H
#define FLASH_STORAGE_H

#include "picopass.h"

void flash_storage_init();
bool flash_storage_save(picopass_device_t *dev);
bool flash_storage_load(picopass_device_t *dev);

#endif
