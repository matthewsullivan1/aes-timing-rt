CC = gcc
CFLAGS = -Wall -Wextra -O2 -Iinclude -Ithird_party/bearssl/inc
LDFLAGS = third_party/bearssl/build/libbearssl.a

SRC = src/main.c \
      src/benchmark.c \
      src/aes_impl.c \
      src/impl_ct.c \
      src/impl_big.c \
      src/timer.c

OUT = build/aes_bench

all: $(OUT)

$(OUT): $(SRC)
	mkdir -p build
	$(CC) $(CFLAGS) $(SRC) -o $(OUT) $(LDFLAGS)

clean:
	rm -rf build

run:
	./$(OUT) --impl ct --n 10 --sz 16 --cache 0
