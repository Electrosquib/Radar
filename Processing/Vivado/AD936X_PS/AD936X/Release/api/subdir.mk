################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../api/no_os_gpio.c \
../api/no_os_i2c.c \
../api/no_os_irq.c \
../api/no_os_spi.c 

OBJS += \
./api/no_os_gpio.o \
./api/no_os_i2c.o \
./api/no_os_irq.o \
./api/no_os_spi.o 

C_DEPS += \
./api/no_os_gpio.d \
./api/no_os_i2c.d \
./api/no_os_irq.d \
./api/no_os_spi.d 


# Each subdirectory must supply rules for building sources it contributes
api/%.o: ../api/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O2 -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\ad9361" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\api" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\AXI_Core" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\iio" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\include" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\src" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\util" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\xilinx" -c -fmessage-length=0 -MT"$@" -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


