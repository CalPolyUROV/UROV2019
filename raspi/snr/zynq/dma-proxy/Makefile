
CC=gcc
LINKER=$(CC)

CC_FLAGS=-Wall -Wextra -g -pedantic
OPT_FLAGS=-Og 

LINKER_FLAGS=-flto

CC_CMD=$(CC) $(CC_FLAGS) $(OPT_FLAGS) -c
LINKER_CMD=$(LINKER) $(LINKER_FLAGS) -o

HEADERS=dma-proxy.h
.PHONY: all
all: dma-proxy dma-proxy-test

dma-proxy: dma-proxy.o
	$(LINKER_CMD) $@ $<

dma-proxy-test: dma-proxy-test.o
	$(LINKER_CMD) $@ $<

dma-proxy.o: dma-proxy.c $(HEADERS)
	$(CC_CMD) -o $@ $<
	
dma-proxy-test.o: dma-proxy-test.c $(HEADERS)
	$(CC_CMD) -o $@ $<