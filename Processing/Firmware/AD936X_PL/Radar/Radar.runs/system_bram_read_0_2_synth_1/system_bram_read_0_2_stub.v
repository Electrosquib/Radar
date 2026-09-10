// Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
// Date        : Wed Sep  9 18:47:22 2026
// Host        : LevisPC running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ system_bram_read_0_2_stub.v
// Design      : system_bram_read_0_2
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z020clg400-2
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* X_CORE_INFO = "bram_read,Vivado 2021.1" *)
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix(clk, enable, profile_index, word_index, 
  bram_data, profile_word, addr, busy, valid, bram_rst)
/* synthesis syn_black_box black_box_pad_pin="clk,enable,profile_index[8:0],word_index[3:0],bram_data[31:0],profile_word[15:0],addr[31:0],busy,valid,bram_rst" */;
  input clk;
  input enable;
  input [8:0]profile_index;
  input [3:0]word_index;
  input [31:0]bram_data;
  output [15:0]profile_word;
  output [31:0]addr;
  output busy;
  output valid;
  output bram_rst;
endmodule
