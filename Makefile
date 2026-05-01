CC = gcc
CFLAGS = -Wall -Wextra -O2 -Iinclude -Ithird_party/bearssl/inc
LDFLAGS = third_party/bearssl/build/libbearssl.a

#Common source files
COMMON_SRC = \
    src/aes_impl.c \
    src/impl_ct.c \
    src/impl_big.c \
    src/timer.c

#Benchmark
BENCH_SRC = \
    src/main.c \
    src/benchmark.c \
    $(COMMON_SRC)

BENCH_OUT = build/aes_bench

#timing analysis
TIMING_SRC = \
    src/timing_main.c \
    src/timing_diff.c \
    $(COMMON_SRC)

TIMING_OUT = build/timing_bench


all: $(BENCH_OUT) $(TIMING_OUT)

#Build aes_bench
$(BENCH_OUT): $(BENCH_SRC)
	mkdir -p build
	$(CC) $(CFLAGS) $(BENCH_SRC) -o $(BENCH_OUT) $(LDFLAGS)

#Build timing_bench
$(TIMING_OUT): $(TIMING_SRC)
	mkdir -p build
	$(CC) $(CFLAGS) $(TIMING_SRC) -o $(TIMING_OUT) $(LDFLAGS)

clean:
	rm -rf build

#Run target for performance benchmark
run:
	./$(BENCH_OUT) --impl ct --n 10 --sz 16 --cache 0

#Run target for timing experiment
run-timing: $(TIMING_OUT)
	./$(TIMING_OUT) 10000 1000