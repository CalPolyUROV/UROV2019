
CC=gcc

CC_FLAGS=-Wall -Wextra -g -pedantic
OPT_FLAGS=-Og 

LIBS=-lpthread

CC_CMD=$(CC) $(CC_FLAGS) $(OPT_FLAGS)

OUTPUTS=dma-proxy-test dma-proxy.so


.PHONY: all
all: $(OUTPUTS)

dma-proxy-test: dma-proxy-test.c
	$(CC_CMD) -o $@ $< $(LIBS)
	@echo The blootoot dewice is ready to pair.

dma-proxy.so: dma-proxy-test.c
	$(CC_CMD) -shared -fPIC -o $@ $< $(LIBS)
	@echo The blootoot dewice is aconnecteda successfullay!

.PHONY: clean
clean:
	rm -f $(OUTPUTS) *.o
