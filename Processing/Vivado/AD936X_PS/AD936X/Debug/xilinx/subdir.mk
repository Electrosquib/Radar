################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../xilinx/axi_io.c \
../xilinx/delay.c \
../xilinx/no_os_timer.c \
../xilinx/no_os_uart.c \
../xilinx/xilinx_gpio.c \
../xilinx/xilinx_gpio_irq.c \
../xilinx/xilinx_i2c.c \
../xilinx/xilinx_irq.c \
../xilinx/xilinx_spi.c \
../xilinx/xilinx_spi_pl.c 

OBJS += \
./xilinx/axi_io.o \
./xilinx/delay.o \
./xilinx/no_os_timer.o \
./xilinx/no_os_uart.o \
./xilinx/xilinx_gpio.o \
./xilinx/xilinx_gpio_irq.o \
./xilinx/xilinx_i2c.o \
./xilinx/xilinx_irq.o \
./xilinx/xilinx_spi.o \
./xilinx/xilinx_spi_pl.o 

C_DEPS += \
./xilinx/axi_io.d \
./xilinx/delay.d \
./xilinx/no_os_timer.d \
./xilinx/no_os_uart.d \
./xilinx/xilinx_gpio.d \
./xilinx/xilinx_gpio_irq.d \
./xilinx/xilinx_i2c.d \
./xilinx/xilinx_irq.d \
./xilinx/xilinx_spi.d \
./xilinx/xilinx_spi_pl.d 


# Each subdirectory must supply rules for building sources it contributes
xilinx/%.o: ../xilinx/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O0 -g3 -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\ad9361" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\api" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\AXI_Core" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\iio" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\include" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\src" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\util" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\xilinx" -c -fmessage-length=0 -MT"$@" -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


