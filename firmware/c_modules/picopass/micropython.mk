PICOPASS_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(PICOPASS_MOD_DIR)/picopass.c

# Add our module directory to include paths.
CFLAGS_USERMOD += -I$(PICOPASS_MOD_DIR)
