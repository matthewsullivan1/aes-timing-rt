#!/bin/bash
set -e

CORE=3
AES=./build/aes_bench
CORUNNER=~/IsolBench/bench/bandwidth
OUT=results_corun

mkdir -p "$OUT"

#echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor || true

for IMPL in ct big; do
    for LOAD in 1024 2048 4096 8192 16384; do
        echo "Running $IMPL with co-runner load $LOAD"

        sudo chrt -f 60 taskset -c $CORE $CORUNNER \
            -m $LOAD -a read -i 10 -j 50 -l 20 -c $CORE &
        CORUN_PID=$!

        sleep 1

        sudo chrt -f 80 taskset -c $CORE $AES \
            --impl "$IMPL" \
            --sz 16 \
            --n 100000 \
            --cache 0 \
            > "$OUT/${IMPL}_load_${LOAD}.log"

        sudo kill $CORUN_PID 2>/dev/null || true
        wait $CORUN_PID 2>/dev/null || true
    done
done
