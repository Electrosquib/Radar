TARGET := SFCW
SRC := SFCW.c
SYSROOT ?= ./pluto-0.38.sysroot

ifeq ($(origin CC), default)
CC := armv7-unknown-linux-gnueabihf-gcc
endif

CPPFLAGS ?=
CFLAGS ?= -O2 -g -Wall -Wextra -Wpedantic -std=gnu99 -mfloat-abi=hard
LDLIBS ?= -liio -lm

.PHONY: build clean

build: $(TARGET)

$(TARGET): $(SRC) Makefile
	"$(CC)" --sysroot="$(SYSROOT)" $(CPPFLAGS) $(CFLAGS) $(SRC) -o $(TARGET) $(LDLIBS)

clean:
	rm -f $(TARGET)
