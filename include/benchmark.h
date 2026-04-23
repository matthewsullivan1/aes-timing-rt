#ifndef BENCHMARK_H
#define BENCHMARK_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    IMPL_UNKNOWN = 0,
    IMPL_CT,
    IMPL_BIG
} aes_impl_kind_t;

typedef struct {
    aes_impl_kind_t impl;
    int num_runs;
    int buf_size;
    int cache;
} bench_config_t;

int run_benchmark(const bench_config_t *cfg);

#endif
