#include <string.h>
#include <stdlib.h>

#include "bearssl.h"
#include "aes_impl.h"

// Wrapper for br_aes_big_ctr_init 
// Creates context on heap & initializes, stores pointer in ctx->impl_ctx
int big_init(aes_ctx_t *ctx, const uint8_t *key, size_t key_len) {

    br_aes_big_ctr_keys *impl_ctx;

    if (ctx == NULL || key == NULL){
        return 1;
    }

    impl_ctx = malloc(sizeof(*impl_ctx));
    if(impl_ctx == NULL){
        return 1;
    }

    br_aes_big_ctr_init(impl_ctx, key, key_len);
    ctx->impl_ctx = impl_ctx;

    return 0;
}

// Wrapper for bear ssl encrypt
// Encrypt input buffer and write to out
// IV is hanlded internally for now
int big_encrypt(aes_ctx_t *ctx, const uint8_t *in, uint8_t *out, size_t len) {
    br_aes_big_ctr_keys *impl_ctx;
    unsigned char iv[16] = {0};
    uint32_t cc = 0;

    if (ctx == NULL || ctx->impl_ctx == NULL || in == NULL || out == NULL){
        return 1;
    }

    impl_ctx = (br_aes_big_ctr_keys *)ctx->impl_ctx;
    memcpy(out, in, len);
    br_aes_big_ctr_run(impl_ctx, iv, cc, out, len);

    return 0;
}

void big_cleanup(aes_ctx_t *ctx) {
    if (ctx != NULL && ctx->impl_ctx != NULL){
        free(ctx->impl_ctx);
        ctx->impl_ctx = NULL;
    }
}
