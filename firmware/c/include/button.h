// firmware/c/include/button.h
#ifndef BUTTON_H
#define BUTTON_H

#include "picopass.h"

void button_init();
void button_check_all(picopass_device_t *dev);

#endif
