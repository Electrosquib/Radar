################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../ad9361/ad9361.c \
../ad9361/ad9361_api.c \
../ad9361/ad9361_conv.c \
../ad9361/ad9361_util.c \
../ad9361/iio_ad9361.c 

OBJS += \
./ad9361/ad9361.o \
./ad9361/ad9361_api.o \
./ad9361/ad9361_conv.o \
./ad9361/ad9361_util.o \
./ad9361/iio_ad9361.o 

C_DEPS += \
./ad9361/ad9361.d \
./ad9361/ad9361_api.d \
./ad9361/ad9361_conv.d \
./ad9361/ad9361_util.d \
./ad9361/iio_ad9361.d 


# Each subdirectory must supply rules for building sources it contributes
ad9361/%.o: ../ad9361/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O2 -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\ad9361" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\api" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\AXI_Core" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\iio" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\include" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\src" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\util" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\xilinx" -c -fmessage-length=0 -MT"$@" -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


