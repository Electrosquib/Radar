-- Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
-- Date        : Mon May  6 17:14:59 2024
-- Host        : DESKTOP-EIGR673 running 64-bit major release  (build 9200)
-- Command     : write_vhdl -force -mode synth_stub -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
--               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ system_util_ad9361_adc_fifo_0_stub.vhdl
-- Design      : system_util_ad9361_adc_fifo_0
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z020clg400-2
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix is
  Port ( 
    din_rst : in STD_LOGIC;
    din_clk : in STD_LOGIC;
    din_enable_0 : in STD_LOGIC;
    din_valid_0 : in STD_LOGIC;
    din_data_0 : in STD_LOGIC_VECTOR ( 15 downto 0 );
    din_enable_1 : in STD_LOGIC;
    din_valid_1 : in STD_LOGIC;
    din_data_1 : in STD_LOGIC_VECTOR ( 15 downto 0 );
    din_enable_2 : in STD_LOGIC;
    din_valid_2 : in STD_LOGIC;
    din_data_2 : in STD_LOGIC_VECTOR ( 15 downto 0 );
    din_enable_3 : in STD_LOGIC;
    din_valid_3 : in STD_LOGIC;
    din_data_3 : in STD_LOGIC_VECTOR ( 15 downto 0 );
    din_ovf : out STD_LOGIC;
    dout_rstn : in STD_LOGIC;
    dout_clk : in STD_LOGIC;
    dout_enable_0 : out STD_LOGIC;
    dout_valid_0 : out STD_LOGIC;
    dout_data_0 : out STD_LOGIC_VECTOR ( 15 downto 0 );
    dout_enable_1 : out STD_LOGIC;
    dout_valid_1 : out STD_LOGIC;
    dout_data_1 : out STD_LOGIC_VECTOR ( 15 downto 0 );
    dout_enable_2 : out STD_LOGIC;
    dout_valid_2 : out STD_LOGIC;
    dout_data_2 : out STD_LOGIC_VECTOR ( 15 downto 0 );
    dout_enable_3 : out STD_LOGIC;
    dout_valid_3 : out STD_LOGIC;
    dout_data_3 : out STD_LOGIC_VECTOR ( 15 downto 0 );
    dout_ovf : in STD_LOGIC
  );

end decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix;

architecture stub of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix is
attribute syn_black_box : boolean;
attribute black_box_pad_pin : string;
attribute syn_black_box of stub : architecture is true;
attribute black_box_pad_pin of stub : architecture is "din_rst,din_clk,din_enable_0,din_valid_0,din_data_0[15:0],din_enable_1,din_valid_1,din_data_1[15:0],din_enable_2,din_valid_2,din_data_2[15:0],din_enable_3,din_valid_3,din_data_3[15:0],din_ovf,dout_rstn,dout_clk,dout_enable_0,dout_valid_0,dout_data_0[15:0],dout_enable_1,dout_valid_1,dout_data_1[15:0],dout_enable_2,dout_valid_2,dout_data_2[15:0],dout_enable_3,dout_valid_3,dout_data_3[15:0],dout_ovf";
attribute X_CORE_INFO : string;
attribute X_CORE_INFO of stub : architecture is "util_wfifo,Vivado 2021.1";
begin
end;
