#ifndef TIMING_DIFF_H
#define TIMING_DIFF_H

#include "aes_impl.h"

typedef struct {
    aes_impl_kind_t impl;
    int samples;
    int inner_runs;
} timing_config_t;

int run_timing_bench(const timing_config_t *cfg);

#endif