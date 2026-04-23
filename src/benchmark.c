#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "benchmark.h"
#include "aes_impl.h"
#include "timer.h"

int run_benchmark(const bench_config_t *cfg) {
    	const aes_impl_vtable_t *impl;
    	aes_ctx_t ctx;
    	uint8_t key[16] = {0};
    	uint8_t *in = NULL;
    	uint8_t *out = NULL;
    	uint64_t start, end;
    	int i;

    	if (cfg == NULL) {
        	return 1;
    	}

    	impl = get_aes_impl(cfg->impl);
    	if (impl == NULL) {
        	fprintf(stderr, "Failed to resolve AES implementation\n");
        	return 1;
    	}

    	in = malloc(cfg->buf_size);
    	out = malloc(cfg->buf_size);
    	if (in == NULL || out == NULL) {
        	fprintf(stderr, "Failed to allocate buffers\n");
        	free(in);
        	free(out);
        	return 1;
    	}

    	memset(in, 0x41, cfg->buf_size);
    	memset(out, 0, cfg->buf_size);
    	memset(&ctx, 0, sizeof(ctx));

    	if (impl->init(&ctx, key, sizeof(key)) != 0) {
        	fprintf(stderr, "Failed to initialize implementation: %s\n", impl->name);
        	free(in);
        	free(out);
        	return 1;
    	}

    	for (i = 0; i < cfg->num_runs; i++) {
        	start = timer_now();
        	if (impl->encrypt(&ctx, in, out, cfg->buf_size) != 0) {
            		fprintf(stderr, "Encryption failed on run %d\n", i);
            		impl->cleanup(&ctx);
            		free(in);
            		free(out);
            		return 1;
        	}
        	end = timer_now();

        	printf("run=%d ticks=%llu\n", i, (unsigned long long)(end - start));
    	}

    	impl->cleanup(&ctx);
    	free(in);
    	free(out);

    	return 0;
}
