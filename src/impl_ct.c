#include <string.h>
#include "aes_impl.h"

int ct_init(aes_ctx_t *ctx, const uint8_t *key, size_t key_len) {
    (void)ctx;
    (void)key;
    (void)key_len;
    return 0;
}

int ct_encrypt(aes_ctx_t *ctx, const uint8_t *in, uint8_t *out, size_t len) {
    (void)ctx;
    memcpy(out, in, len);
    return 0;
}

void ct_cleanup(aes_ctx_t *ctx) {
    (void)ctx;
}
