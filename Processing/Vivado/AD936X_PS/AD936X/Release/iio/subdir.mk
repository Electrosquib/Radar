################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../iio/iio.c \
../iio/iio_app.c \
../iio/iio_axi_adc.c \
../iio/iio_axi_dac.c \
../iio/iiod.c 

OBJS += \
./iio/iio.o \
./iio/iio_app.o \
./iio/iio_axi_adc.o \
./iio/iio_axi_dac.o \
./iio/iiod.o 

C_DEPS += \
./iio/iio.d \
./iio/iio_app.d \
./iio/iio_axi_adc.d \
./iio/iio_axi_dac.d \
./iio/iiod.d 


# Each subdirectory must supply rules for building sources it contributes
iio/%.o: ../iio/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O2 -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\ad9361" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\api" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\AXI_Core" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\iio" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\include" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\src" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\util" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\xilinx" -c -fmessage-length=0 -MT"$@" -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


