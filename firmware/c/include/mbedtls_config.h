#ifndef MBEDTLS_CONFIG_H
#define MBEDTLS_CONFIG_H

/* System support */
#define MBEDTLS_PLATFORM_C
#define MBEDTLS_PLATFORM_MEMORY
#define MBEDTLS_MEMORY_BUFFER_ALLOC_C

/* mbed TLS feature support */
#define MBEDTLS_AES_C
#define MBEDTLS_SHA256_C
#define MBEDTLS_CIPHER_C

/* Optimization */
#define MBEDTLS_AES_ROM_TABLES

#include <mbedtls/check_config.h>

#endif
