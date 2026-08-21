CC = "C:/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-linux-gnueabihf/bin/arm-none-linux-gnueabihf-gcc.exe"
PSCP = "C:/Program Files/PuTTY/pscp.exe"
PLINK = "C:/Program Files/PuTTY/plink.exe"

SYSROOT = ./pluto-0.38.sysroot

TARGET = fastlock_controller
SRC = fastlock_controller.c

PLUTO_IP = 192.168.2.1
USER = root
PASSWORD = analog

build:
	$(CC) --sysroot="$(SYSROOT)" -mfloat-abi=hard -std=gnu99 -g -Wall -Wextra $(SRC) -o $(TARGET) -lpthread -liio -lm

deploy: build
	$(PSCP) -scp -pw $(PASSWORD) $(TARGET) $(USER)@$(PLUTO_IP):/root/$(TARGET)

run: deploy
	@echo -------------------------------------------------------------------------------------------
	$(PLINK) -batch -pw $(PASSWORD) $(USER)@$(PLUTO_IP) "killall /root/$(TARGET) || true; chmod +x /root/$(TARGET); /root/$(TARGET)"

clean:
	del $(TARGET)