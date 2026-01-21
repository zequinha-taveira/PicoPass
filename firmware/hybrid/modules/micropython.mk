FAST_CRYPTO_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(FAST_CRYPTO_MOD_DIR)/fast_crypto.c

# Add our module directory to include paths.
CFLAGS_USERMOD += -I$(FAST_CRYPTO_MOD_DIR)

# Link against mbedtls (part of Pico SDK, but for MP build we rely on internal mbedtls)
# MicroPython usually has mbedtls internal or port-specific.
# This assumes the port provides mbedtls includes.
