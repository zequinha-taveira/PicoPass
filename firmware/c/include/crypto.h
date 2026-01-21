// firmware/c/include/crypto.h
#ifndef CRYPTO_H
#define CRYPTO_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


void crypto_init(const char *board_id);
void crypto_derive_key(const char *master_password);
void crypto_hash_password(const char *password, char *hash_out);
bool crypto_encrypt(const char *plaintext, uint8_t *ciphertext,
                    size_t *ciphertext_len, uint8_t *iv);
bool crypto_decrypt(const uint8_t *ciphertext, size_t ciphertext_len,
                    const uint8_t *iv, char *plaintext);
void crypto_clear_key_cache();

#endif
