// firmware/c/include/config.h

#ifndef CONFIG_H
#define CONFIG_H

#define PICOPASS_VERSION "1.0.0"

#define MAX_PASSWORD_SLOTS 4
#define MAX_PASSWORD_LENGTH 64
#define FLASH_TARGET_OFFSET (1024 * 1024) // 1MB offset (adjust based on board)
#define FLASH_TARGET_SIZE 4096            // 1 sector

// GPIO Config
#define LED_PIN_STATUS 16
#define LED_PIN_ERROR 17
#define LED_PIN_ACTIVITY 18

#define BTN_PIN_UNLOCK 15
#define BTN_PIN_SLOT1 14
#define BTN_PIN_SLOT2 13
#define BTN_PIN_SLOT3 12
#define BTN_PIN_SLOT4 11

#endif
