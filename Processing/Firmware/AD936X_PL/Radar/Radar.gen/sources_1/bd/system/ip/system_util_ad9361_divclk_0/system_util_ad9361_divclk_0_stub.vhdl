-- Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
-- Date        : Tue Aug 18 21:19:02 2026
-- Host        : LevisPC running 64-bit major release  (build 9200)
-- Command     : write_vhdl -force -mode synth_stub {c:/Users/Levi
--               Farinas/Documents/GitHub/Radar/Processing/Firmware/AD936X_PL/Radar/Radar.gen/sources_1/bd/system/ip/system_util_ad9361_divclk_0/system_util_ad9361_divclk_0_stub.vhdl}
-- Design      : system_util_ad9361_divclk_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z020clg400-2
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity system_util_ad9361_divclk_0 is
  Port ( 
    clk : in STD_LOGIC;
    clk_sel : in STD_LOGIC;
    clk_out : out STD_LOGIC
  );

end system_util_ad9361_divclk_0;

architecture stub of system_util_ad9361_divclk_0 is
attribute syn_black_box : boolean;
attribute black_box_pad_pin : string;
attribute syn_black_box of stub : architecture is true;
attribute black_box_pad_pin of stub : architecture is "clk,clk_sel,clk_out";
attribute X_CORE_INFO : string;
attribute X_CORE_INFO of stub : architecture is "util_clkdiv,Vivado 2021.1";
begin
end;
