#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "aes_impl.h"
#include "timing_diff.h"
#include "timer.h"

int run_timing_bench(const timing_config_t *cfg) {
    const aes_impl_vtable_t *impl;
    aes_ctx_t ctx;

    uint8_t key[16] = {
        0x01, 0x01, 0x01, 0x01,
        0x01, 0x01, 0x01, 0x01,
        0x01, 0x01, 0x01, 0x01,
        0x01, 0x01, 0x01, 0x01
    };

    uint8_t in[16] = {0x01};

    /*
    uint8_t in[16] = {
        0x00, 0x00, 0x22, 0x10,
        0x7c, 0x08, 0xde, 0xad,
        0xbe, 0xef, 0x55, 0xaa,
        0x19, 0x37, 0xc0, 0xff
    };*/
    uint8_t out[16] = {0};

    volatile uint8_t sink = 0;

    uint64_t start, end;

    if (cfg == NULL) {
        return 1;
    }

    impl = get_aes_impl(cfg->impl);
    if (impl == NULL) {
        fprintf(stderr, "Failed to resolve AES implementation\n");
        return 1;
    }

    if (cfg->impl != IMPL_BIG) {
        fprintf(stderr, "Warning: not using Big AES implementation\n");
    }

    memset(&ctx, 0, sizeof(ctx));

    if (impl->init(&ctx, key, sizeof(key)) != 0) {
        fprintf(stderr, "Failed to initialize implementation: %s\n", impl->name);
        return 1;
    }

    // Warmup
    for (int i = 0; i < 1000; i++) {
        impl->encrypt(&ctx, in, out, sizeof(in));
        sink ^= out[0];
    }

    printf("# impl=%s samples=%d inner_runs=%d\n",
           impl->name,
           cfg->samples,
           cfg->inner_runs);

    printf("sample,val,idx,ticks\n");

    for (int sample = 0; sample < cfg->samples; sample++) {
        for (int v = 0; v < 256; v++) {
            int val = (v + sample) & 0xff;
            uint8_t idx = ((uint8_t)val) ^ key[0];
            in[0] = (uint8_t)val;

            start = timer_now();

            for (int r = 0; r < cfg->inner_runs; r++) {
                impl->encrypt(&ctx, in, out, sizeof(in));
                sink ^= out[0];
            }

            end = timer_now();
            

            printf("%d,%d,%u,%lu\n",
                sample,
                val,
                idx,
                (unsigned long)(end - start));
        }
    }

    fprintf(stderr, "# sink=%u\n", sink);

    impl->cleanup(&ctx);
    return 0;
}