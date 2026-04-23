#include "aes_impl.h"

const aes_impl_vtable_t *get_aes_impl(aes_impl_kind_t kind);

int ct_init(aes_ctx_t *ctx, const uint8_t *key, size_t key_len);
int ct_encrypt(aes_ctx_t *ctx, const uint8_t *in, uint8_t *out, size_t len);
void ct_cleanup(aes_ctx_t *ctx);

int big_init(aes_ctx_t *ctx, const uint8_t *key, size_t key_len);
int big_encrypt(aes_ctx_t *ctx, const uint8_t *in, uint8_t *out, size_t len);
void big_cleanup(aes_ctx_t *ctx);

static const aes_impl_vtable_t CT_IMPL = {
    .name = "ct",
    .init = ct_init,
    .encrypt = ct_encrypt,
    .cleanup = ct_cleanup
};

static const aes_impl_vtable_t BIG_IMPL = {
    .name = "big",
    .init = big_init,
    .encrypt = big_encrypt,
    .cleanup = big_cleanup
};

const aes_impl_vtable_t *get_aes_impl(aes_impl_kind_t kind) {
    switch (kind) {
        case IMPL_CT:
            return &CT_IMPL;
        case IMPL_BIG:
            return &BIG_IMPL;
        default:
            return 0;
    }
}
