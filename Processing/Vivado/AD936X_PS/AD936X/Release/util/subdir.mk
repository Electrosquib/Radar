################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../util/no_os_circular_buffer.c \
../util/no_os_crc16.c \
../util/no_os_crc24.c \
../util/no_os_crc8.c \
../util/no_os_fifo.c \
../util/no_os_font_8x8.c \
../util/no_os_lf256fifo.c \
../util/no_os_list.c \
../util/no_os_sin_lut.c \
../util/no_os_util.c 

OBJS += \
./util/no_os_circular_buffer.o \
./util/no_os_crc16.o \
./util/no_os_crc24.o \
./util/no_os_crc8.o \
./util/no_os_fifo.o \
./util/no_os_font_8x8.o \
./util/no_os_lf256fifo.o \
./util/no_os_list.o \
./util/no_os_sin_lut.o \
./util/no_os_util.o 

C_DEPS += \
./util/no_os_circular_buffer.d \
./util/no_os_crc16.d \
./util/no_os_crc24.d \
./util/no_os_crc8.d \
./util/no_os_fifo.d \
./util/no_os_font_8x8.d \
./util/no_os_lf256fifo.d \
./util/no_os_list.d \
./util/no_os_sin_lut.d \
./util/no_os_util.d 


# Each subdirectory must supply rules for building sources it contributes
util/%.o: ../util/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O2 -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\ad9361" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\api" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\AXI_Core" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\iio" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\include" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\src" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\util" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\xilinx" -c -fmessage-length=0 -MT"$@" -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


