CC=gcc
TARGET=source/main
CFLAGS=-Wall -s -Os
CFLAGS_DEBUG=-Wall -g
LDLIBS=-lcurl -ldl

all: $(TARGET) $(TARGET)-debug

$(TARGET): $(TARGET).c
	$(CC) $(CFLAGS) -o mini source/*.c $(LDLIBS)

$(TARGET)-debug: $(TARGET).c
	$(CC) $(CFLAGS_DEBUG) -o mini-debug source/*.c $(LDLIBS)
