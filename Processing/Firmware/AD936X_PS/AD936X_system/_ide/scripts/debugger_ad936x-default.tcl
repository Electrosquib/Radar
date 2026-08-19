# Usage with Vitis IDE:
# In Vitis IDE create a Single Application Debug launch configuration,
# change the debug type to 'Attach to running target' and provide this 
# tcl script in 'Execute Script' option.
# Path of this script: F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X_system\_ide\scripts\debugger_ad936x-default.tcl
# 
# 
# Usage with xsct:
# To debug using xsct, launch xsct and run below command
# source F:\FPGA_Code\7020_AD936X_SDR\AD936X_PS\AD936X_system\_ide\scripts\debugger_ad936x-default.tcl
# 
connect -url tcp:127.0.0.1:3121
targets -set -nocase -filter {name =~"APU*"}
rst -system
after 3000
targets -set -filter {jtag_cable_name =~ "Digilent JTAG-SMT1 000000000069A" && level==0 && jtag_device_ctx=="jsn-JTAG-SMT1-000000000069A-4ba00477-0"}
fpga -file F:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/AD936X/_ide/bitstream/system_top.bit
targets -set -nocase -filter {name =~"APU*"}
loadhw -hw F:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/platform/export/platform/hw/system_top.xsa -mem-ranges [list {0x40000000 0xbfffffff}] -regs
configparams force-mem-access 1
targets -set -nocase -filter {name =~"APU*"}
source F:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/AD936X/_ide/psinit/ps7_init.tcl
ps7_init
ps7_post_config
targets -set -nocase -filter {name =~ "*A9*#0"}
dow F:/FPGA_Code/7020_AD936X_SDR/AD936X_PS/AD936X/Release/AD936X.elf
configparams force-mem-access 0
targets -set -nocase -filter {name =~ "*A9*#0"}
con
