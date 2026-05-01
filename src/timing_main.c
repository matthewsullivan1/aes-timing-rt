#include <stdlib.h>
#include "timing_diff.h"

int main(int argc, char **argv) {
    timing_config_t cfg;

    cfg.impl = IMPL_BIG;
    cfg.samples = 10000;
    cfg.inner_runs = 1000;

    if (argc >= 2) {
        cfg.samples = atoi(argv[1]);
    }

    if (argc >= 3) {
        cfg.inner_runs = atoi(argv[2]);
    }

    return run_timing_bench(&cfg);
}