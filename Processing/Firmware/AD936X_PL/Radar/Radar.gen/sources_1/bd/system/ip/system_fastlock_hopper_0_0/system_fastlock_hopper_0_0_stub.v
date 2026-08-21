// Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
// Date        : Wed Aug 19 15:31:41 2026
// Host        : LevisPC running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub {c:/Users/Levi
//               Farinas/Documents/GitHub/Radar/Processing/Firmware/AD936X_PL/Radar/Radar.gen/sources_1/bd/system/ip/system_fastlock_hopper_0_0/system_fastlock_hopper_0_0_stub.v}
// Design      : system_fastlock_hopper_0_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z020clg400-2
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* X_CORE_INFO = "fastlock_hopper,Vivado 2021.1" *)
module system_fastlock_hopper_0_0(clk, enable, gpio_ctl)
/* synthesis syn_black_box black_box_pad_pin="clk,enable,gpio_ctl[3:0]" */;
  input clk;
  input enable;
  output [3:0]gpio_ctl;
endmodule
