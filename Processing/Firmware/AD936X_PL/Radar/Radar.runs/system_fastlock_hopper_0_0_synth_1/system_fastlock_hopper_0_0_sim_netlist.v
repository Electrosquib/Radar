// Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2021.1 (win64) Build 3247384 Thu Jun 10 19:36:33 MDT 2021
// Date        : Wed Aug 19 15:31:41 2026
// Host        : LevisPC running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ system_fastlock_hopper_0_0_sim_netlist.v
// Design      : system_fastlock_hopper_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7z020clg400-2
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_fastlock_hopper
   (gpio_ctl,
    clk,
    enable);
  output [0:0]gpio_ctl;
  input clk;
  input enable;

  wire clk;
  wire [31:0]count;
  wire [31:0]count_0;
  wire \count_reg[12]_i_2_n_0 ;
  wire \count_reg[12]_i_2_n_1 ;
  wire \count_reg[12]_i_2_n_2 ;
  wire \count_reg[12]_i_2_n_3 ;
  wire \count_reg[16]_i_2_n_0 ;
  wire \count_reg[16]_i_2_n_1 ;
  wire \count_reg[16]_i_2_n_2 ;
  wire \count_reg[16]_i_2_n_3 ;
  wire \count_reg[20]_i_2_n_0 ;
  wire \count_reg[20]_i_2_n_1 ;
  wire \count_reg[20]_i_2_n_2 ;
  wire \count_reg[20]_i_2_n_3 ;
  wire \count_reg[24]_i_2_n_0 ;
  wire \count_reg[24]_i_2_n_1 ;
  wire \count_reg[24]_i_2_n_2 ;
  wire \count_reg[24]_i_2_n_3 ;
  wire \count_reg[28]_i_2_n_0 ;
  wire \count_reg[28]_i_2_n_1 ;
  wire \count_reg[28]_i_2_n_2 ;
  wire \count_reg[28]_i_2_n_3 ;
  wire \count_reg[31]_i_2_n_2 ;
  wire \count_reg[31]_i_2_n_3 ;
  wire \count_reg[4]_i_2_n_0 ;
  wire \count_reg[4]_i_2_n_1 ;
  wire \count_reg[4]_i_2_n_2 ;
  wire \count_reg[4]_i_2_n_3 ;
  wire \count_reg[8]_i_2_n_0 ;
  wire \count_reg[8]_i_2_n_1 ;
  wire \count_reg[8]_i_2_n_2 ;
  wire \count_reg[8]_i_2_n_3 ;
  wire [31:1]data0;
  wire enable;
  wire [0:0]gpio_ctl;
  wire p_0_in;
  wire state_i_10_n_0;
  wire state_i_2_n_0;
  wire state_i_3_n_0;
  wire state_i_4_n_0;
  wire state_i_5_n_0;
  wire state_i_6_n_0;
  wire state_i_7_n_0;
  wire state_i_8_n_0;
  wire state_i_9_n_0;
  wire [3:2]\NLW_count_reg[31]_i_2_CO_UNCONNECTED ;
  wire [3:3]\NLW_count_reg[31]_i_2_O_UNCONNECTED ;

  LUT1 #(
    .INIT(2'h1)) 
    \count[0]_i_1 
       (.I0(count[0]),
        .O(count_0[0]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[10]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[10]),
        .O(count_0[10]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[11]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[11]),
        .O(count_0[11]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[12]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[12]),
        .O(count_0[12]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[13]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[13]),
        .O(count_0[13]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[14]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[14]),
        .O(count_0[14]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[15]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[15]),
        .O(count_0[15]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[16]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[16]),
        .O(count_0[16]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[17]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[17]),
        .O(count_0[17]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[18]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[18]),
        .O(count_0[18]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[19]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[19]),
        .O(count_0[19]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[1]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[1]),
        .O(count_0[1]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[20]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[20]),
        .O(count_0[20]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[21]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[21]),
        .O(count_0[21]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[22]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[22]),
        .O(count_0[22]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[23]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[23]),
        .O(count_0[23]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[24]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[24]),
        .O(count_0[24]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[25]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[25]),
        .O(count_0[25]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[26]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[26]),
        .O(count_0[26]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[27]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[27]),
        .O(count_0[27]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[28]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[28]),
        .O(count_0[28]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[29]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[29]),
        .O(count_0[29]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[2]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[2]),
        .O(count_0[2]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[30]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[30]),
        .O(count_0[30]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[31]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[31]),
        .O(count_0[31]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[3]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[3]),
        .O(count_0[3]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[4]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[4]),
        .O(count_0[4]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[5]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[5]),
        .O(count_0[5]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[6]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[6]),
        .O(count_0[6]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[7]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[7]),
        .O(count_0[7]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[8]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[8]),
        .O(count_0[8]));
  LUT5 #(
    .INIT(32'hFFFE0000)) 
    \count[9]_i_1 
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(data0[9]),
        .O(count_0[9]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[0]),
        .Q(count[0]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[10] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[10]),
        .Q(count[10]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[11] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[11]),
        .Q(count[11]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[12] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[12]),
        .Q(count[12]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[12]_i_2 
       (.CI(\count_reg[8]_i_2_n_0 ),
        .CO({\count_reg[12]_i_2_n_0 ,\count_reg[12]_i_2_n_1 ,\count_reg[12]_i_2_n_2 ,\count_reg[12]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[12:9]),
        .S(count[12:9]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[13] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[13]),
        .Q(count[13]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[14] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[14]),
        .Q(count[14]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[15] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[15]),
        .Q(count[15]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[16] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[16]),
        .Q(count[16]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[16]_i_2 
       (.CI(\count_reg[12]_i_2_n_0 ),
        .CO({\count_reg[16]_i_2_n_0 ,\count_reg[16]_i_2_n_1 ,\count_reg[16]_i_2_n_2 ,\count_reg[16]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[16:13]),
        .S(count[16:13]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[17] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[17]),
        .Q(count[17]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[18] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[18]),
        .Q(count[18]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[19] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[19]),
        .Q(count[19]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[1] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[1]),
        .Q(count[1]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[20] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[20]),
        .Q(count[20]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[20]_i_2 
       (.CI(\count_reg[16]_i_2_n_0 ),
        .CO({\count_reg[20]_i_2_n_0 ,\count_reg[20]_i_2_n_1 ,\count_reg[20]_i_2_n_2 ,\count_reg[20]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[20:17]),
        .S(count[20:17]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[21] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[21]),
        .Q(count[21]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[22] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[22]),
        .Q(count[22]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[23] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[23]),
        .Q(count[23]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[24] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[24]),
        .Q(count[24]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[24]_i_2 
       (.CI(\count_reg[20]_i_2_n_0 ),
        .CO({\count_reg[24]_i_2_n_0 ,\count_reg[24]_i_2_n_1 ,\count_reg[24]_i_2_n_2 ,\count_reg[24]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[24:21]),
        .S(count[24:21]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[25] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[25]),
        .Q(count[25]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[26] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[26]),
        .Q(count[26]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[27] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[27]),
        .Q(count[27]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[28] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[28]),
        .Q(count[28]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[28]_i_2 
       (.CI(\count_reg[24]_i_2_n_0 ),
        .CO({\count_reg[28]_i_2_n_0 ,\count_reg[28]_i_2_n_1 ,\count_reg[28]_i_2_n_2 ,\count_reg[28]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[28:25]),
        .S(count[28:25]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[29] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[29]),
        .Q(count[29]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[2] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[2]),
        .Q(count[2]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[30] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[30]),
        .Q(count[30]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[31] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[31]),
        .Q(count[31]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[31]_i_2 
       (.CI(\count_reg[28]_i_2_n_0 ),
        .CO({\NLW_count_reg[31]_i_2_CO_UNCONNECTED [3:2],\count_reg[31]_i_2_n_2 ,\count_reg[31]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_count_reg[31]_i_2_O_UNCONNECTED [3],data0[31:29]}),
        .S({1'b0,count[31:29]}));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[3] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[3]),
        .Q(count[3]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[4] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[4]),
        .Q(count[4]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[4]_i_2 
       (.CI(1'b0),
        .CO({\count_reg[4]_i_2_n_0 ,\count_reg[4]_i_2_n_1 ,\count_reg[4]_i_2_n_2 ,\count_reg[4]_i_2_n_3 }),
        .CYINIT(count[0]),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[4:1]),
        .S(count[4:1]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[5] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[5]),
        .Q(count[5]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[6] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[6]),
        .Q(count[6]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[7] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[7]),
        .Q(count[7]),
        .R(p_0_in));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[8] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[8]),
        .Q(count[8]),
        .R(p_0_in));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \count_reg[8]_i_2 
       (.CI(\count_reg[4]_i_2_n_0 ),
        .CO({\count_reg[8]_i_2_n_0 ,\count_reg[8]_i_2_n_1 ,\count_reg[8]_i_2_n_2 ,\count_reg[8]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(data0[8:5]),
        .S(count[8:5]));
  FDRE #(
    .INIT(1'b0)) 
    \count_reg[9] 
       (.C(clk),
        .CE(1'b1),
        .D(count_0[9]),
        .Q(count[9]),
        .R(p_0_in));
  LUT1 #(
    .INIT(2'h1)) 
    state_i_1
       (.I0(enable),
        .O(p_0_in));
  LUT4 #(
    .INIT(16'hFFFE)) 
    state_i_10
       (.I0(count[13]),
        .I1(count[12]),
        .I2(count[15]),
        .I3(count[14]),
        .O(state_i_10_n_0));
  LUT5 #(
    .INIT(32'hFFFE0001)) 
    state_i_2
       (.I0(state_i_3_n_0),
        .I1(state_i_4_n_0),
        .I2(state_i_5_n_0),
        .I3(state_i_6_n_0),
        .I4(gpio_ctl),
        .O(state_i_2_n_0));
  LUT5 #(
    .INIT(32'hFFFFFFFE)) 
    state_i_3
       (.I0(count[18]),
        .I1(count[19]),
        .I2(count[16]),
        .I3(count[17]),
        .I4(state_i_7_n_0),
        .O(state_i_3_n_0));
  LUT5 #(
    .INIT(32'hFFFFFFFE)) 
    state_i_4
       (.I0(count[26]),
        .I1(count[27]),
        .I2(count[24]),
        .I3(count[25]),
        .I4(state_i_8_n_0),
        .O(state_i_4_n_0));
  LUT5 #(
    .INIT(32'hFFFFBFFF)) 
    state_i_5
       (.I0(count[3]),
        .I1(count[2]),
        .I2(count[0]),
        .I3(count[1]),
        .I4(state_i_9_n_0),
        .O(state_i_5_n_0));
  LUT5 #(
    .INIT(32'hFFFFEFFF)) 
    state_i_6
       (.I0(count[10]),
        .I1(count[11]),
        .I2(count[8]),
        .I3(count[9]),
        .I4(state_i_10_n_0),
        .O(state_i_6_n_0));
  LUT4 #(
    .INIT(16'hFFFE)) 
    state_i_7
       (.I0(count[21]),
        .I1(count[20]),
        .I2(count[23]),
        .I3(count[22]),
        .O(state_i_7_n_0));
  LUT4 #(
    .INIT(16'hFFFE)) 
    state_i_8
       (.I0(count[29]),
        .I1(count[28]),
        .I2(count[31]),
        .I3(count[30]),
        .O(state_i_8_n_0));
  LUT4 #(
    .INIT(16'hDFFF)) 
    state_i_9
       (.I0(count[5]),
        .I1(count[4]),
        .I2(count[7]),
        .I3(count[6]),
        .O(state_i_9_n_0));
  FDRE #(
    .INIT(1'b0)) 
    state_reg
       (.C(clk),
        .CE(1'b1),
        .D(state_i_2_n_0),
        .Q(gpio_ctl),
        .R(p_0_in));
endmodule

(* CHECK_LICENSE_TYPE = "system_fastlock_hopper_0_0,fastlock_hopper,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* IP_DEFINITION_SOURCE = "module_ref" *) 
(* X_CORE_INFO = "fastlock_hopper,Vivado 2021.1" *) 
(* NotValidForBitStream *)
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix
   (clk,
    enable,
    gpio_ctl);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN system_sys_ps7_0_FCLK_CLK0, INSERT_VIP 0" *) input clk;
  input enable;
  output [3:0]gpio_ctl;

  wire \<const0> ;
  wire clk;
  wire enable;
  wire [1:1]\^gpio_ctl ;

  assign gpio_ctl[3] = \^gpio_ctl [1];
  assign gpio_ctl[2] = \^gpio_ctl [1];
  assign gpio_ctl[1] = \^gpio_ctl [1];
  assign gpio_ctl[0] = \<const0> ;
  GND GND
       (.G(\<const0> ));
  decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_fastlock_hopper inst
       (.clk(clk),
        .enable(enable),
        .gpio_ctl(\^gpio_ctl ));
endmodule
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
