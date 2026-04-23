#ifndef AES_IMPL_H
#define AES_IMPL_H

#include <stddef.h>
#include <stdint.h>
#include "benchmark.h"

typedef struct {
    void *impl_ctx;
} aes_ctx_t;

typedef struct {
    const char *name;
    int (*init)(aes_ctx_t *ctx, const uint8_t *key, size_t key_len);
    int (*encrypt)(aes_ctx_t *ctx, const uint8_t *in, uint8_t *out, size_t len);
    void (*cleanup)(aes_ctx_t *ctx);
} aes_impl_vtable_t;

const aes_impl_vtable_t *get_aes_impl(aes_impl_kind_t kind);

#endif
