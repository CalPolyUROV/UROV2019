
CC=gcc

CC_FLAGS=-Wall -Wextra -g -pedantic
OPT_FLAGS=-Og 

LIBS=-lpthread

CC_CMD=$(CC) $(CC_FLAGS) $(OPT_FLAGS)

OUTPUTS=dma-proxy-test dma-proxy-test.so


.PHONY: all
all: $(OUTPUTS)

dma-proxy-test: dma-proxy-test.c
	$(CC_CMD) -o $@ $< $(LIBS)
	@echo The blootoot dewice is ready to pair.

.PHONY: so
so: dma-proxy-test.so
dma-proxy-test.so: dma-proxy-test.c
	$(CC_CMD) -shared -fPIC -o $@ $< $(LIBS)
	@echo The blootoot dewice is anaconda successfullay!

.PHONY: clean
clean:
	rm -f $(OUTPUTS) *.o
