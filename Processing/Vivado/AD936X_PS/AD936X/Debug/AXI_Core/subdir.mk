################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../AXI_Core/axi_adc_core.c \
../AXI_Core/axi_dac_core.c \
../AXI_Core/axi_dmac.c 

OBJS += \
./AXI_Core/axi_adc_core.o \
./AXI_Core/axi_dac_core.o \
./AXI_Core/axi_dmac.o 

C_DEPS += \
./AXI_Core/axi_adc_core.d \
./AXI_Core/axi_dac_core.d \
./AXI_Core/axi_dmac.d 


# Each subdirectory must supply rules for building sources it contributes
AXI_Core/%.o: ../AXI_Core/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: ARM v7 gcc compiler'
	arm-none-eabi-gcc -Wall -O0 -g3 -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\ad9361" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\api" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\AXI_Core" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\iio" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\include" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\src" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\util" -I"F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X\xilinx" -c -fmessage-length=0 -MT"$@" -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -IF:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/sw/platform/standalone_domain/bspinclude/include -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


