// Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
// Date        : Mon May  6 17:14:58 2024
// Host        : DESKTOP-EIGR673 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub
//               f:/FPGA_Code/MyCore_7020_V3/AD936X_PL/projects/fmcomms2/zc702/zc702.gen/sources_1/bd/system/ip/system_util_ad9361_divclk_0/system_util_ad9361_divclk_0_stub.v
// Design      : system_util_ad9361_divclk_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z020clg400-2
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* X_CORE_INFO = "util_clkdiv,Vivado 2021.1" *)
module system_util_ad9361_divclk_0(clk, clk_sel, clk_out)
/* synthesis syn_black_box black_box_pad_pin="clk,clk_sel,clk_out" */;
  input clk;
  input clk_sel;
  output clk_out;
endmodule
