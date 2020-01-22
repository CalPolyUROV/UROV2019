
CC=gcc
CFLAGS=-fPIC -shared 

OBJS=libdma.o lib.o

OUTPUT=libdma.so

$(OUTPUT): libdma.o lib.o Makefile
	$(CC) $(CFLAGS) -o $(OUTPUT) $(OBJS)
