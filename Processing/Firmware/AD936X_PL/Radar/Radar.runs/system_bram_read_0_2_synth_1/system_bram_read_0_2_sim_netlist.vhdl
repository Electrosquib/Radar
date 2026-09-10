-- Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
-- Date        : Wed Sep  9 18:47:22 2026
-- Host        : LevisPC running 64-bit major release  (build 9200)
-- Command     : write_vhdl -force -mode funcsim -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
--               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ system_bram_read_0_2_sim_netlist.vhdl
-- Design      : system_bram_read_0_2
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7z020clg400-2
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_bram_read is
  port (
    busy_reg_0 : out STD_LOGIC;
    profile_word : out STD_LOGIC_VECTOR ( 15 downto 0 );
    addr : out STD_LOGIC_VECTOR ( 12 downto 0 );
    valid : out STD_LOGIC;
    enable : in STD_LOGIC;
    clk : in STD_LOGIC;
    bram_data : in STD_LOGIC_VECTOR ( 15 downto 0 );
    D : in STD_LOGIC_VECTOR ( 12 downto 0 )
  );
end decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_bram_read;

architecture STRUCTURE of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_bram_read is
  signal busy_i_1_n_0 : STD_LOGIC;
  signal \^busy_reg_0\ : STD_LOGIC;
  signal delay_count : STD_LOGIC_VECTOR ( 2 downto 0 );
  signal \delay_count[0]_i_1_n_0\ : STD_LOGIC;
  signal \delay_count[1]_i_1_n_0\ : STD_LOGIC;
  signal \delay_count[2]_i_1_n_0\ : STD_LOGIC;
  signal \profile_word[15]_i_1_n_0\ : STD_LOGIC;
  signal valid0 : STD_LOGIC;
  attribute X_INTERFACE_IGNORE : string;
  attribute X_INTERFACE_IGNORE of \addr_reg[0]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[10]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[11]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[12]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[1]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[2]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[3]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[4]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[5]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[6]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[7]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[8]\ : label is "true";
  attribute X_INTERFACE_IGNORE of \addr_reg[9]\ : label is "true";
  attribute SOFT_HLUTNM : string;
  attribute SOFT_HLUTNM of busy_i_1 : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of \delay_count[0]_i_1\ : label is "soft_lutpair1";
  attribute SOFT_HLUTNM of \delay_count[1]_i_1\ : label is "soft_lutpair0";
  attribute SOFT_HLUTNM of \delay_count[2]_i_1\ : label is "soft_lutpair0";
begin
  busy_reg_0 <= \^busy_reg_0\;
\addr[12]_i_1\: unisim.vcomponents.LUT2
    generic map(
      INIT => X"2"
    )
        port map (
      I0 => enable,
      I1 => \^busy_reg_0\,
      O => valid0
    );
\addr_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(0),
      Q => addr(0),
      R => '0'
    );
\addr_reg[10]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(10),
      Q => addr(10),
      R => '0'
    );
\addr_reg[11]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(11),
      Q => addr(11),
      R => '0'
    );
\addr_reg[12]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(12),
      Q => addr(12),
      R => '0'
    );
\addr_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(1),
      Q => addr(1),
      R => '0'
    );
\addr_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(2),
      Q => addr(2),
      R => '0'
    );
\addr_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(3),
      Q => addr(3),
      R => '0'
    );
\addr_reg[4]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(4),
      Q => addr(4),
      R => '0'
    );
\addr_reg[5]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(5),
      Q => addr(5),
      R => '0'
    );
\addr_reg[6]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(6),
      Q => addr(6),
      R => '0'
    );
\addr_reg[7]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(7),
      Q => addr(7),
      R => '0'
    );
\addr_reg[8]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(8),
      Q => addr(8),
      R => '0'
    );
\addr_reg[9]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => valid0,
      D => D(9),
      Q => addr(9),
      R => '0'
    );
busy_i_1: unisim.vcomponents.LUT5
    generic map(
      INIT => X"BFFFBF00"
    )
        port map (
      I0 => delay_count(2),
      I1 => delay_count(0),
      I2 => delay_count(1),
      I3 => \^busy_reg_0\,
      I4 => enable,
      O => busy_i_1_n_0
    );
busy_reg: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => busy_i_1_n_0,
      Q => \^busy_reg_0\,
      R => '0'
    );
\delay_count[0]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"750075AA"
    )
        port map (
      I0 => delay_count(0),
      I1 => delay_count(2),
      I2 => delay_count(1),
      I3 => \^busy_reg_0\,
      I4 => enable,
      O => \delay_count[0]_i_1_n_0\
    );
\delay_count[1]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"6E006EAA"
    )
        port map (
      I0 => delay_count(1),
      I1 => delay_count(0),
      I2 => delay_count(2),
      I3 => \^busy_reg_0\,
      I4 => enable,
      O => \delay_count[1]_i_1_n_0\
    );
\delay_count[2]_i_1\: unisim.vcomponents.LUT5
    generic map(
      INIT => X"700070F0"
    )
        port map (
      I0 => delay_count(1),
      I1 => delay_count(0),
      I2 => delay_count(2),
      I3 => \^busy_reg_0\,
      I4 => enable,
      O => \delay_count[2]_i_1_n_0\
    );
\delay_count_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => \delay_count[0]_i_1_n_0\,
      Q => delay_count(0),
      R => '0'
    );
\delay_count_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => \delay_count[1]_i_1_n_0\,
      Q => delay_count(1),
      R => '0'
    );
\delay_count_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => \delay_count[2]_i_1_n_0\,
      Q => delay_count(2),
      R => '0'
    );
\profile_word[15]_i_1\: unisim.vcomponents.LUT4
    generic map(
      INIT => X"0800"
    )
        port map (
      I0 => delay_count(1),
      I1 => delay_count(0),
      I2 => delay_count(2),
      I3 => \^busy_reg_0\,
      O => \profile_word[15]_i_1_n_0\
    );
\profile_word_reg[0]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(0),
      Q => profile_word(0),
      R => '0'
    );
\profile_word_reg[10]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(10),
      Q => profile_word(10),
      R => '0'
    );
\profile_word_reg[11]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(11),
      Q => profile_word(11),
      R => '0'
    );
\profile_word_reg[12]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(12),
      Q => profile_word(12),
      R => '0'
    );
\profile_word_reg[13]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(13),
      Q => profile_word(13),
      R => '0'
    );
\profile_word_reg[14]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(14),
      Q => profile_word(14),
      R => '0'
    );
\profile_word_reg[15]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(15),
      Q => profile_word(15),
      R => '0'
    );
\profile_word_reg[1]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(1),
      Q => profile_word(1),
      R => '0'
    );
\profile_word_reg[2]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(2),
      Q => profile_word(2),
      R => '0'
    );
\profile_word_reg[3]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(3),
      Q => profile_word(3),
      R => '0'
    );
\profile_word_reg[4]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(4),
      Q => profile_word(4),
      R => '0'
    );
\profile_word_reg[5]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(5),
      Q => profile_word(5),
      R => '0'
    );
\profile_word_reg[6]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(6),
      Q => profile_word(6),
      R => '0'
    );
\profile_word_reg[7]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(7),
      Q => profile_word(7),
      R => '0'
    );
\profile_word_reg[8]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(8),
      Q => profile_word(8),
      R => '0'
    );
\profile_word_reg[9]\: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => \profile_word[15]_i_1_n_0\,
      D => bram_data(9),
      Q => profile_word(9),
      R => '0'
    );
valid_reg: unisim.vcomponents.FDRE
    generic map(
      INIT => '0'
    )
        port map (
      C => clk,
      CE => '1',
      D => \profile_word[15]_i_1_n_0\,
      Q => valid,
      R => '0'
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix is
  port (
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
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix : entity is "system_bram_read_0_2,bram_read,{}";
  attribute DowngradeIPIdentifiedWarnings : string;
  attribute DowngradeIPIdentifiedWarnings of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix : entity is "yes";
  attribute IP_DEFINITION_SOURCE : string;
  attribute IP_DEFINITION_SOURCE of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix : entity is "module_ref";
  attribute X_CORE_INFO : string;
  attribute X_CORE_INFO of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix : entity is "bram_read,Vivado 2021.1";
end decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix;

architecture STRUCTURE of decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix is
  signal \<const0>\ : STD_LOGIC;
  signal \<const1>\ : STD_LOGIC;
  signal \^addr\ : STD_LOGIC_VECTOR ( 12 downto 0 );
  attribute X_INTERFACE_INFO : string;
  attribute X_INTERFACE_INFO of bram_rst : signal is "xilinx.com:signal:reset:1.0 bram_rst RST";
  attribute X_INTERFACE_PARAMETER : string;
  attribute X_INTERFACE_PARAMETER of bram_rst : signal is "XIL_INTERFACENAME bram_rst, POLARITY ACTIVE_LOW, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of clk : signal is "xilinx.com:signal:clock:1.0 clk CLK";
  attribute X_INTERFACE_PARAMETER of clk : signal is "XIL_INTERFACENAME clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN system_sys_ps7_0_FCLK_CLK0, INSERT_VIP 0";
  attribute X_INTERFACE_INFO of valid : signal is "analog.com:interface:fifo_rd:1.0 interface_fifo_rd VALID";
  attribute X_INTERFACE_IGNORE : string;
  attribute X_INTERFACE_IGNORE of bram_data : signal is "true";
begin
  addr(31) <= \<const0>\;
  addr(30) <= \<const0>\;
  addr(29) <= \<const0>\;
  addr(28) <= \<const0>\;
  addr(27) <= \<const0>\;
  addr(26) <= \<const0>\;
  addr(25) <= \<const0>\;
  addr(24) <= \<const0>\;
  addr(23) <= \<const0>\;
  addr(22) <= \<const0>\;
  addr(21) <= \<const0>\;
  addr(20) <= \<const0>\;
  addr(19) <= \<const0>\;
  addr(18) <= \<const0>\;
  addr(17) <= \<const0>\;
  addr(16) <= \<const0>\;
  addr(15) <= \<const0>\;
  addr(14) <= \<const0>\;
  addr(13) <= \<const0>\;
  addr(12 downto 0) <= \^addr\(12 downto 0);
  bram_rst <= \<const1>\;
GND: unisim.vcomponents.GND
     port map (
      G => \<const0>\
    );
VCC: unisim.vcomponents.VCC
     port map (
      P => \<const1>\
    );
inst: entity work.decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_bram_read
     port map (
      D(12 downto 4) => profile_index(8 downto 0),
      D(3 downto 0) => word_index(3 downto 0),
      addr(12 downto 0) => \^addr\(12 downto 0),
      bram_data(15 downto 0) => bram_data(15 downto 0),
      busy_reg_0 => busy,
      clk => clk,
      enable => enable,
      profile_word(15 downto 0) => profile_word(15 downto 0),
      valid => valid
    );
end STRUCTURE;
