/*
 * PicoPass C Module
 * Implements secure licensing logic and low-level helpers.
 */

#include "py/runtime.h"
#include <string.h>

// Secret salt hidden in compiled binary
#define SECRET_SALT "PicoPass_Device_Secure_2026"

// Forward declaration of internal helper
bool verify_license_c(const char* board_id, const char* board_type, const char* key);

/**
 * picopass.verify_license(board_id, board_type, key)
 * 
 * Verifies if the provided key matches the expected HMAC for the board.
 * Returns: boolean
 */
static mp_obj_t picopass_verify_license(mp_obj_t board_id_obj, mp_obj_t board_type_obj, mp_obj_t key_obj) {
    const char* board_id = mp_obj_str_get_str(board_id_obj);
    const char* board_type = mp_obj_str_get_str(board_type_obj);
    const char* key = mp_obj_str_get_str(key_obj);
    
    bool result = verify_license_c(board_id, board_type, key);
    
    return result ? mp_const_true : mp_const_false;
}
static MP_DEFINE_CONST_FUN_OBJ_3(picopass_verify_license_obj, picopass_verify_license);

/**
 * picopass.get_module_info()
 * 
 * Returns version info about the C module.
 */
static mp_obj_t picopass_get_module_info(void) {
    return mp_obj_new_str("PicoPass C Module v1.0", 22);
}
static MP_DEFINE_CONST_FUN_OBJ_0(picopass_get_module_info_obj, picopass_get_module_info);

// Module Globals Table
static const mp_rom_map_elem_t picopass_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_picopass) },
    { MP_ROM_QSTR(MP_QSTR_verify_license), MP_ROM_PTR(&picopass_verify_license_obj) },
    { MP_ROM_QSTR(MP_QSTR_info), MP_ROM_PTR(&picopass_get_module_info_obj) },
};
static MP_DEFINE_CONST_DICT(picopass_module_globals, picopass_module_globals_table);

// Module Definition
const mp_obj_module_t picopass_user_c_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&picopass_module_globals,
};

// Register module
MP_REGISTER_MODULE(MP_QSTR_picopass, picopass_user_c_module);

// =========================================================================
// Internal Implementation (TODO: Add actual SHA256 logic)
// =========================================================================

bool verify_license_c(const char* board_id, const char* board_type, const char* key) {
    // Placeholder implementation
    // Plan:
    // 1. Concatenate board_id + ":" + board_type + ":" + SECRET_SALT
    // 2. Calculate SHA256
    // 3. Take first 16 chars of hex digest
    // 4. Compare with key
    
    // For now, return false to indicate "not implemented fully"
    // The Python fallback should be used until this is ready.
    return false;
}
