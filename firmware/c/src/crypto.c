// firmware/c/src/crypto.c

#include "crypto.h"
#include "config.h"
#include "mbedtls/aes.h"
#include "mbedtls/sha256.h"
#include "pico/rand.h"
#include <stdio.h>
#include <string.h>

static mbedtls_aes_context aes_ctx;
static uint8_t derived_key[32];
static bool key_cached = false;
static char board_id_salt[17];

void crypto_init(const char *board_id) {
  mbedtls_aes_init(&aes_ctx);
  strncpy(board_id_salt, board_id, sizeof(board_id_salt) - 1);
  key_cached = false;
}

void crypto_derive_key(const char *master_password) {
  // Combine master password + board ID as salt
  char combined[256];
  snprintf(combined, sizeof(combined), "%s%s", master_password, board_id_salt);

  // SHA-256 to derive 32-byte key
  mbedtls_sha256_context sha_ctx;
  mbedtls_sha256_init(&sha_ctx);
  mbedtls_sha256_starts(&sha_ctx, 0);
  // Explicitly cast to const unsigned char* to match mbedtls signature
  mbedtls_sha256_update(&sha_ctx, (const unsigned char *)combined,
                        strlen(combined));
  mbedtls_sha256_finish(&sha_ctx, derived_key);
  mbedtls_sha256_free(&sha_ctx);

  // Set AES key
  mbedtls_aes_setkey_enc(&aes_ctx, derived_key, 256);

  key_cached = true;

  // Clear combined from memory
  memset(combined, 0, sizeof(combined));
}

void crypto_hash_password(const char *password, char *hash_out) {
  uint8_t hash[32];

  mbedtls_sha256_context ctx;
  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts(&ctx, 0);
  mbedtls_sha256_update(&ctx, (const unsigned char *)password,
                        strlen(password));
  mbedtls_sha256_finish(&ctx, hash);
  mbedtls_sha256_free(&ctx);

  // Convert to hex string
  for (int i = 0; i < 32; i++) {
    sprintf(hash_out + (i * 2), "%02x", hash[i]);
  }
  hash_out[64] = '\0';
}

bool crypto_encrypt(const char *plaintext, uint8_t *ciphertext,
                    size_t *ciphertext_len, uint8_t *iv) {
  if (!key_cached) {
    return false;
  }

  // Generate random IV
  for (int i = 0; i < 16; i++) {
    iv[i] = get_rand_32() & 0xFF;
  }

  // PKCS7 padding
  size_t plaintext_len = strlen(plaintext);
  size_t padding_len = 16 - (plaintext_len % 16);
  size_t padded_len = plaintext_len + padding_len;

  uint8_t padded[MAX_PASSWORD_LENGTH];
  memcpy(padded, plaintext, plaintext_len);
  memset(padded + plaintext_len, padding_len, padding_len);

  // Encrypt with AES-256-CBC
  mbedtls_aes_context local_ctx;
  mbedtls_aes_init(&local_ctx);
  mbedtls_aes_setkey_enc(&local_ctx, derived_key, 256);

  uint8_t iv_copy[16];
  memcpy(iv_copy, iv, 16);

  int ret = mbedtls_aes_crypt_cbc(&local_ctx, MBEDTLS_AES_ENCRYPT, padded_len,
                                  iv_copy, padded, ciphertext);

  mbedtls_aes_free(&local_ctx);

  if (ret == 0) {
    *ciphertext_len = padded_len;
    return true;
  }

  return false;
}

bool crypto_decrypt(const uint8_t *ciphertext, size_t ciphertext_len,
                    const uint8_t *iv, char *plaintext) {
  if (!key_cached) {
    return false;
  }

  uint8_t decrypted[MAX_PASSWORD_LENGTH];

  // Decrypt with AES-256-CBC
  mbedtls_aes_context local_ctx;
  mbedtls_aes_init(&local_ctx);
  mbedtls_aes_setkey_dec(&local_ctx, derived_key, 256);

  uint8_t iv_copy[16];
  memcpy(iv_copy, iv, 16);

  int ret =
      mbedtls_aes_crypt_cbc(&local_ctx, MBEDTLS_AES_DECRYPT, ciphertext_len,
                            iv_copy, ciphertext, decrypted);

  mbedtls_aes_free(&local_ctx);

  if (ret != 0) {
    return false;
  }

  // Remove PKCS7 padding
  uint8_t padding_len = decrypted[ciphertext_len - 1];

  // Safety check for padding
  if (padding_len > 16 || padding_len == 0) {
    return false;
  }

  size_t plaintext_len = ciphertext_len - padding_len;

  memcpy(plaintext, decrypted, plaintext_len);
  plaintext[plaintext_len] = '\0';

  // Clear decrypted from memory
  memset(decrypted, 0, sizeof(decrypted));

  return true;
}

void crypto_clear_key_cache() {
  memset(derived_key, 0, sizeof(derived_key));
  key_cached = false;
}
