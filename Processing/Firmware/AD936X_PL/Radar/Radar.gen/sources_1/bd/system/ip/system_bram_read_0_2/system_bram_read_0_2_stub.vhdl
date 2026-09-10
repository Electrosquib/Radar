-- Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
-- Date        : Wed Sep  9 18:47:22 2026
-- Host        : LevisPC running 64-bit major release  (build 9200)
-- Command     : write_vhdl -force -mode synth_stub {c:/Users/Levi
--               Farinas/Documents/GitHub/Radar/Processing/Firmware/AD936X_PL/Radar/Radar.gen/sources_1/bd/system/ip/system_bram_read_0_2/system_bram_read_0_2_stub.vhdl}
-- Design      : system_bram_read_0_2
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z020clg400-2
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity system_bram_read_0_2 is
  Port ( 
    clk : in STD_LOGIC;
    enable : in STD_LOGIC;
    profile_index : in STD_LOGIC_VECTOR ( 8 downto 0 );
    word_index : in STD_LOGIC_VECTOR ( 3 downto 0 );
    bram_data : in STD_LOGIC_VECTOR ( 31 downto 0 );
    profile_word : out STD_LOGIC_VECTOR ( 15 downto 0 );
    addr : out STD_LOGIC_VECTOR ( 31 downto 0 );
    busy : out STD_LOGIC;
    valid : out STD_LOGIC;
    bram_rst : out STD_LOGIC
  );

end system_bram_read_0_2;

architecture stub of system_bram_read_0_2 is
attribute syn_black_box : boolean;
attribute black_box_pad_pin : string;
attribute syn_black_box of stub : architecture is true;
attribute black_box_pad_pin of stub : architecture is "clk,enable,profile_index[8:0],word_index[3:0],bram_data[31:0],profile_word[15:0],addr[31:0],busy,valid,bram_rst";
attribute X_CORE_INFO : string;
attribute X_CORE_INFO of stub : architecture is "bram_read,Vivado 2021.1";
begin
end;
