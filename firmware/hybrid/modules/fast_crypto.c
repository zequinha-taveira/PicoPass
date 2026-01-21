// firmware/hybrid/modules/fast_crypto.c

#include "mbedtls/aes.h"
#include "mbedtls/sha256.h"
#include "py/runtime.h"
#include <string.h>


// Helper to allocate memory using MicroPython GC
void *m_malloc(size_t n) { return m_new(uint8_t, n); }

void m_free(void *ptr) {
  // MicroPython GC handles this if allocated with m_new,
  // but m_free is used for standard malloc/free compat if not GC
  // In MP C modules, we usually let GC collect or use m_del.
  // user snippet used m_free, let's map it.
  m_del(uint8_t, ptr, 0); // Size unknown? MP allocator tracks it.
  // Actually m_free isn't standard in py/runtime.h, usually m_del or generic
  // free if system. For simplicity, let's just assume m_new returns GC memory.
  // m_free(ciphertext) was used in user snippet.
  // Since return value is mp_obj_new_bytes(ciphertext, len),
  // new_bytes copies the data. So ciphertext *should* be freed.
  // m_del(uint8_t, ptr, n_bytes) requires size.
  // Let's use system malloc/free if mbedtls needs it, or MP logic.
  // Here I will use m_del with the calculated size in the function.
}

// Function Python: fast_crypto.hash_sha256(data)
STATIC mp_obj_t hash_sha256(mp_obj_t data_obj) {
  mp_buffer_info_t bufinfo;
  mp_get_buffer_raise(data_obj, &bufinfo, MP_BUFFER_READ);

  uint8_t hash[32];
  mbedtls_sha256_context ctx;

  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts(&ctx, 0);
  // Explicit const cast
  mbedtls_sha256_update(&ctx, (const unsigned char *)bufinfo.buf, bufinfo.len);
  mbedtls_sha256_finish(&ctx, hash);
  mbedtls_sha256_free(&ctx);

  return mp_obj_new_bytes(hash, 32);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hash_sha256_obj, hash_sha256);

// Function Python: fast_crypto.aes_encrypt(key, iv, plaintext)
STATIC mp_obj_t aes_encrypt(mp_obj_t key_obj, mp_obj_t iv_obj,
                            mp_obj_t plaintext_obj) {
  mp_buffer_info_t key_buf, iv_buf, plain_buf;

  mp_get_buffer_raise(key_obj, &key_buf, MP_BUFFER_READ);
  mp_get_buffer_raise(iv_obj, &iv_buf, MP_BUFFER_READ);
  mp_get_buffer_raise(plaintext_obj, &plain_buf, MP_BUFFER_READ);

  if (key_buf.len != 32 || iv_buf.len != 16) {
    mp_raise_ValueError("Invalid key or IV size");
  }

  // Allocate output buffer
  size_t out_len = (plain_buf.len + 15) & ~15; // Round up to 16

  // Using m_new to allocate on GC heap
  uint8_t *ciphertext = m_new(uint8_t, out_len);

  // Encrypt
  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, (const unsigned char *)key_buf.buf, 256);

  uint8_t iv_copy[16];
  memcpy(iv_copy, iv_buf.buf, 16);

  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT, out_len, iv_copy,
                        (const unsigned char *)plain_buf.buf, ciphertext);

  mbedtls_aes_free(&ctx);

  // Create bytes object (copies data)
  mp_obj_t result = mp_obj_new_bytes(ciphertext, out_len);

  // Free temp buffer
  m_del(uint8_t, ciphertext, out_len);

  return result;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(aes_encrypt_obj, aes_encrypt);

// Module definition
STATIC const mp_rom_map_elem_t fast_crypto_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_fast_crypto)},
    {MP_ROM_QSTR(MP_QSTR_hash_sha256), MP_ROM_PTR(&hash_sha256_obj)},
    {MP_ROM_QSTR(MP_QSTR_aes_encrypt), MP_ROM_PTR(&aes_encrypt_obj)},
};
STATIC MP_DEFINE_CONST_DICT(fast_crypto_module_globals,
                            fast_crypto_module_globals_table);

const mp_obj_module_t fast_crypto_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&fast_crypto_module_globals,
};

// Register module
MP_REGISTER_MODULE(MP_QSTR_fast_crypto, fast_crypto_module);
