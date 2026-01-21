// firmware/c/src/serial.c

#include "serial.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#define CMD_BUFFER_SIZE 512

static char cmd_buffer[CMD_BUFFER_SIZE];
static int cmd_pos = 0;

// Simple helper to find JSON value string
// Expects "key":"value" or "key": number
static bool get_json_str(const char *json, const char *key, char *out_val,
                         int max_len) {
  char search_key[64];
  snprintf(search_key, sizeof(search_key), "\"%s\":", key);

  char *p = strstr(json, search_key);
  if (!p)
    return false;

  p += strlen(search_key);

  // Skip whitespace
  while (*p == ' ')
    p++;

  if (*p == '"') {
    p++; // skip quote
    int i = 0;
    while (*p != '"' && *p != 0 && i < max_len - 1) {
      out_val[i++] = *p++;
    }
    out_val[i] = 0;
    return true;
  }
  return false;
}

static int get_json_int(const char *json, const char *key, int default_val) {
  char search_key[64];
  snprintf(search_key, sizeof(search_key), "\"%s\":", key);
  char *p = strstr(json, search_key);
  if (!p)
    return default_val;

  p += strlen(search_key);
  while (*p == ' ')
    p++;

  return atoi(p);
}

void serial_process_commands(picopass_device_t *dev) {
  // Non-blocking read
  int c = getchar_timeout_us(0);
  if (c == PICO_ERROR_TIMEOUT)
    return;

  if (c == '\n' || c == '\r') {
    cmd_buffer[cmd_pos] = 0;
    if (cmd_pos > 0) {
      // Process command
      char type[32];
      if (get_json_str(cmd_buffer, "type", type, sizeof(type))) {
        if (strcmp(type, "PING") == 0) {
          printf("{\"status\":\"PONG\", \"version\":\"%s\"}\n",
                 PICOPASS_VERSION);
        } else if (strcmp(type, "GET_ID") == 0) {
          printf("{\"board_id\":\"%s\", \"version\":\"%s\"}\n", dev->board_id,
                 PICOPASS_VERSION);
        } else if (strcmp(type, "UNLOCK") == 0) {
          char password[64];
          if (get_json_str(cmd_buffer, "password", password,
                           sizeof(password))) {
            bool success = picopass_unlock(dev, password);
            printf("{\"status\":\"%s\"}\n", success ? "ok" : "error");
          } else {
            // Try without password (if already setup?? no, logic requires it if
            // set)
            bool success = picopass_unlock(dev, NULL);
            printf("{\"status\":\"%s\"}\n", success ? "ok" : "error");
          }
        } else if (strcmp(type, "LOCK") == 0) {
          picopass_lock(dev);
          printf("{\"status\":\"ok\"}\n");
        } else if (strcmp(type, "STATUS") == 0) {
          printf(
              "{\"unlocked\":%s, \"slots\":[%d,%d,%d,%d], \"timeout\":%d}\n",
              dev->unlocked ? "true" : "false", dev->password_slots[0].occupied,
              dev->password_slots[1].occupied, dev->password_slots[2].occupied,
              dev->password_slots[3].occupied, dev->auto_lock_timeout);
        } else if (strcmp(type, "ADD_PASSWORD") == 0) {
          int slot = get_json_int(cmd_buffer, "slot", -1);
          char password[64];
          bool has_pw =
              get_json_str(cmd_buffer, "password", password, sizeof(password));
          if (slot >= 0 && has_pw) {
            bool success = picopass_add_password(dev, slot, password);
            printf("{\"status\":\"%s\"}\n", success ? "ok" : "error");
          } else {
            printf("{\"status\":\"error\", \"message\":\"missing args\"}\n");
          }
        } else if (strcmp(type, "DELETE_PASSWORD") == 0) {
          int slot = get_json_int(cmd_buffer, "slot", -1);
          bool success = picopass_delete_password(dev, slot);
          printf("{\"status\":\"%s\"}\n", success ? "ok" : "error");
        } else if (strcmp(type, "TYPE_PASSWORD") == 0) {
          int slot = get_json_int(cmd_buffer, "slot", -1);
          picopass_type_password(dev, slot);
          printf("{\"status\":\"ok\"}\n");
        } else if (strcmp(type, "SET_TIMEOUT") == 0) {
          int timeout = get_json_int(cmd_buffer, "timeout", 120);
          dev->auto_lock_timeout = timeout;
          flash_storage_save(dev);
          printf("{\"status\":\"ok\", \"timeout\":%d}\n", timeout);
        } else {
          printf("{\"status\":\"error\", \"message\":\"unknown command\"}\n");
        }
      }
      cmd_pos = 0;
    }
  } else {
    if (cmd_pos < CMD_BUFFER_SIZE - 1) {
      cmd_buffer[cmd_pos++] = (char)c;
    }
  }
}
