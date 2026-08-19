# File saved with Nlview 7.8.0 2024-04-26 e1825d835c VDI=44 GEI=38 GUI=JA:24.0 threadsafe
# 
# non-default properties - (restore without -noprops)
property -colorscheme classic
property attrcolor #000000
property attrfontsize 8
property autobundle 1
property backgroundcolor #ffffff
property boxcolor0 #575d6c
property boxcolor1 #575d6c
property boxcolor2 #000000
property boxinstcolor #1c1f28
property boxpincolor #1c1f28
property buscolor #009633
property closeenough 5
property createnetattrdsp 2048
property decorate 1
property elidetext 40
property fillcolor1 #e5c7ff
property fillcolor2 #cde5ff
property fillcolor3 #f0f0f0
property gatecellname 2
property instattrmax 30
property instdrag 15
property instorder 1
property marksize 12
property maxfontsize 18
property maxzoom 7.5
property netcolor #8bc34a
property objecthighlight0 #fe00f6
property objecthighlight1 #ffea00
property objecthighlight2 #84e413
property objecthighlight3 #1661ff
property objecthighlight4 #d9b7ff
property objecthighlight5 #ffa358
property objecthighlight6 #ff2b2b
property objecthighlight7 #00e0ff
property objecthighlight8 #c0ca33
property objecthighlight9 #b16eff
property objecthighlight10 #46a466
property objecthighlight11 #caff78
property objecthighlight12 #ab47bc
property objecthighlight13 #b4602c
property objecthighlight14 #c20f8c
property objecthighlight15 #00ffaa
property objecthighlight16 #ff9fe4
property objecthighlight17 #ff8019
property objecthighlight18 #26b3ff
property objecthighlight19 #e5551c
property overlaycolor #8bc34a
property pbuscolor #000000
property pbusnamecolor #1c1f28
property pinattrmax 20
property pinorder 2
property pinpermute 0
property portcolor #000000
property portnamecolor #1c1f28
property ripindexfontsize 4
property rippercolor #000000
property rubberbandcolor #1c1f28
property rubberbandfontsize 20
property selectattr 0
property selectionappearance 2
property selectioncolor #396cef
property sheetheight 44
property sheetwidth 68
property showmarks 1
property shownetname 0
property showpagenumbers 1
property showripindex 1
property timelimit 1
#
module new system_top work:system_top:NOFILE -nosplit
load symbol IOBUF {hdi_primitives:netlist:no file specified} HIERBOX pin IO inout.right pin O output.right pin I input.left pin T input.left fillcolor 2
load symbol IOBUF {hdi_primitives:abstract:no file specified} HIERBOX pin IO inout.right pin O output.right pin I input.left pin T input.left fillcolor 2
load symbol system_wrapper work:system_wrapper:NOFILE HIERBOX pin ddr_cas_n inout.left pin ddr_ck_n inout.left pin ddr_ck_p inout.left pin ddr_cke inout.left pin ddr_cs_n inout.left pin ddr_odt inout.left pin ddr_ras_n inout.left pin ddr_reset_n inout.left pin ddr_we_n inout.left pin enable output.right pin fixed_io_ddr_vrn inout.left pin fixed_io_ddr_vrp inout.left pin fixed_io_ps_clk inout.left pin fixed_io_ps_porb inout.left pin fixed_io_ps_srstb inout.right pin rx_clk_in_n input.left pin rx_clk_in_p input.left pin rx_frame_in_n input.left pin rx_frame_in_p input.left pin spi0_clk_o output.right pin spi0_csn_0_o output.right pin spi0_sdi_i input.left pin spi0_sdo_o output.right pin tx_clk_out_n output.right pin tx_clk_out_p output.right pin tx_frame_out_n output.right pin tx_frame_out_p output.right pin txnrx output.right pinBus bbstub_GPIO_O[46] output.right [14:0] pinBus bbstub_GPIO_T[46] output.right [14:0] pinBus ddr_addr inout.right [14:0] pinBus ddr_ba inout.right [2:0] pinBus ddr_dm inout.right [3:0] pinBus ddr_dq inout.right [31:0] pinBus ddr_dqs_n inout.right [3:0] pinBus ddr_dqs_p inout.right [3:0] pinBus fixed_io_mio inout.right [53:0] pinBus gpio_i input.left [14:0] pinBus rx_data_in_n input.left [5:0] pinBus rx_data_in_p input.left [5:0] pinBus tx_data_out_n output.right [5:0] pinBus tx_data_out_p output.right [5:0] boxcolor 1 fillcolor 2 minwidth 13%
load symbol OBUF hdi_primitives BUF pin O output pin I input fillcolor 1
load symbol IBUF hdi_primitives BUF pin O output pin I input fillcolor 1
load port ddr_cas_n inout -pg 1 -lvl 4 -x 1360 -y 2550
load port ddr_ck_n inout -pg 1 -lvl 4 -x 1360 -y 2520
load port ddr_ck_p inout -pg 1 -lvl 4 -x 1360 -y 1690
load port ddr_cke inout -pg 1 -lvl 4 -x 1360 -y 1720
load port ddr_cs_n inout -pg 1 -lvl 4 -x 1360 -y 2580
load port ddr_odt inout -pg 1 -lvl 4 -x 1360 -y 1750
load port ddr_ras_n inout -pg 1 -lvl 4 -x 1360 -y 1780
load port ddr_reset_n inout -pg 1 -lvl 4 -x 1360 -y 1810
load port ddr_we_n inout -pg 1 -lvl 4 -x 1360 -y 1840
load port enable output -pg 1 -lvl 4 -x 1360 -y 2080
load port fixed_io_ddr_vrn inout -pg 1 -lvl 4 -x 1360 -y 1870
load port fixed_io_ddr_vrp inout -pg 1 -lvl 4 -x 1360 -y 2490
load port fixed_io_ps_clk inout -pg 1 -lvl 4 -x 1360 -y 2610
load port fixed_io_ps_porb inout -pg 1 -lvl 4 -x 1360 -y 2640
load port fixed_io_ps_srstb inout -pg 1 -lvl 4 -x 1360 -y 2140
load port gpio_en_agc inout -pg 1 -lvl 4 -x 1360 -y 1380
load port gpio_resetb inout -pg 1 -lvl 4 -x 1360 -y 1490
load port gpio_sync inout -pg 1 -lvl 4 -x 1360 -y 1600
load port rx_clk_in_n input -pg 1 -lvl 0 -x 0 -y 2170
load port rx_clk_in_p input -pg 1 -lvl 0 -x 0 -y 2200
load port rx_frame_in_n input -pg 1 -lvl 0 -x 0 -y 2290
load port rx_frame_in_p input -pg 1 -lvl 0 -x 0 -y 2320
load port spi_clk output -pg 1 -lvl 4 -x 1360 -y 2170
load port spi_csn output -pg 1 -lvl 4 -x 1360 -y 2210
load port spi_miso input -pg 1 -lvl 0 -x 0 -y 2350
load port spi_mosi output -pg 1 -lvl 4 -x 1360 -y 2250
load port tx_clk_out_n output -pg 1 -lvl 4 -x 1360 -y 2280
load port tx_clk_out_p output -pg 1 -lvl 4 -x 1360 -y 2310
load port tx_frame_out_n output -pg 1 -lvl 4 -x 1360 -y 2400
load port tx_frame_out_p output -pg 1 -lvl 4 -x 1360 -y 2430
load port txnrx output -pg 1 -lvl 4 -x 1360 -y 2460
load portBus ddr_addr inout [14:0] -attr @name ddr_addr[14:0] -pg 1 -lvl 4 -x 1360 -y 1900
load portBus ddr_ba inout [2:0] -attr @name ddr_ba[2:0] -pg 1 -lvl 4 -x 1360 -y 1930
load portBus ddr_dm inout [3:0] -attr @name ddr_dm[3:0] -pg 1 -lvl 4 -x 1360 -y 1960
load portBus ddr_dq inout [31:0] -attr @name ddr_dq[31:0] -pg 1 -lvl 4 -x 1360 -y 1990
load portBus ddr_dqs_n inout [3:0] -attr @name ddr_dqs_n[3:0] -pg 1 -lvl 4 -x 1360 -y 2020
load portBus ddr_dqs_p inout [3:0] -attr @name ddr_dqs_p[3:0] -pg 1 -lvl 4 -x 1360 -y 2050
load portBus fixed_io_mio inout [53:0] -attr @name fixed_io_mio[53:0] -pg 1 -lvl 4 -x 1360 -y 2110
load portBus gpio_ctl inout [3:0] -attr @name gpio_ctl[3:0] -pg 1 -lvl 4 -x 1360 -y 60
load portBus gpio_status inout [7:0] -attr @name gpio_status[7:0] -pg 1 -lvl 4 -x 1360 -y 500
load portBus rx_data_in_n input [5:0] -attr @name rx_data_in_n[5:0] -pg 1 -lvl 0 -x 0 -y 2230
load portBus rx_data_in_p input [5:0] -attr @name rx_data_in_p[5:0] -pg 1 -lvl 0 -x 0 -y 2260
load portBus tx_data_out_n output [5:0] -attr @name tx_data_out_n[5:0] -pg 1 -lvl 4 -x 1360 -y 2340
load portBus tx_data_out_p output [5:0] -attr @name tx_data_out_p[5:0] -pg 1 -lvl 4 -x 1360 -y 2370
load inst gpio_ctl_IOBUF[0]_inst IOBUF {hdi_primitives:netlist:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 50
load inst gpio_ctl_IOBUF[1]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 160
load inst gpio_ctl_IOBUF[2]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 270
load inst gpio_ctl_IOBUF[3]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 380
load inst gpio_en_agc_IOBUF_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 1370
load inst gpio_resetb_IOBUF_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 1480
load inst gpio_status_IOBUF[0]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 490
load inst gpio_status_IOBUF[1]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 600
load inst gpio_status_IOBUF[2]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 710
load inst gpio_status_IOBUF[3]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 820
load inst gpio_status_IOBUF[4]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 930
load inst gpio_status_IOBUF[5]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 1040
load inst gpio_status_IOBUF[6]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 1150
load inst gpio_status_IOBUF[7]_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 1260
load inst gpio_sync_IOBUF_inst IOBUF {hdi_primitives:abstract:no file specified} -autohide -attr @cell(#1c1f28) IOBUF -pg 1 -lvl 2 -x 630 -y 1590
load inst i_system_wrapper system_wrapper work:system_wrapper:NOFILE -autohide -attr @cell(#1c1f28) system_wrapper -pinBusAttr bbstub_GPIO_O[46] @name bbstub_GPIO_O[46][14:0] -pinBusAttr bbstub_GPIO_T[46] @name bbstub_GPIO_T[46][14:0] -pinBusAttr ddr_addr @name ddr_addr[14:0] -pinBusAttr ddr_ba @name ddr_ba[2:0] -pinBusAttr ddr_dm @name ddr_dm[3:0] -pinBusAttr ddr_dq @name ddr_dq[31:0] -pinBusAttr ddr_dqs_n @name ddr_dqs_n[3:0] -pinBusAttr ddr_dqs_p @name ddr_dqs_p[3:0] -pinBusAttr fixed_io_mio @name fixed_io_mio[53:0] -pinBusAttr gpio_i @name gpio_i[14:0] -pinBusAttr rx_data_in_n @name rx_data_in_n[5:0] -pinBusAttr rx_data_in_p @name rx_data_in_p[5:0] -pinBusAttr tx_data_out_n @name tx_data_out_n[5:0] -pinBusAttr tx_data_out_p @name tx_data_out_p[5:0] -pg 1 -lvl 2 -x 630 -y 1910
load inst spi_clk_OBUF_inst OBUF hdi_primitives -attr @cell(#1c1f28) OBUF -pg 1 -lvl 3 -x 1100 -y 2140
load inst spi_csn_OBUF_inst OBUF hdi_primitives -attr @cell(#1c1f28) OBUF -pg 1 -lvl 3 -x 1100 -y 2210
load inst spi_miso_IBUF_inst IBUF hdi_primitives -attr @cell(#1c1f28) IBUF -pg 1 -lvl 1 -x 80 -y 2340
load inst spi_mosi_OBUF_inst OBUF hdi_primitives -attr @cell(#1c1f28) OBUF -pg 1 -lvl 3 -x 1100 -y 2280
load net ddr_addr[0] -attr @rip(#1c1f28) ddr_addr[0] -port ddr_addr[0] -pin i_system_wrapper ddr_addr[0]
load net ddr_addr[10] -attr @rip(#1c1f28) ddr_addr[10] -port ddr_addr[10] -pin i_system_wrapper ddr_addr[10]
load net ddr_addr[11] -attr @rip(#1c1f28) ddr_addr[11] -port ddr_addr[11] -pin i_system_wrapper ddr_addr[11]
load net ddr_addr[12] -attr @rip(#1c1f28) ddr_addr[12] -port ddr_addr[12] -pin i_system_wrapper ddr_addr[12]
load net ddr_addr[13] -attr @rip(#1c1f28) ddr_addr[13] -port ddr_addr[13] -pin i_system_wrapper ddr_addr[13]
load net ddr_addr[14] -attr @rip(#1c1f28) ddr_addr[14] -port ddr_addr[14] -pin i_system_wrapper ddr_addr[14]
load net ddr_addr[1] -attr @rip(#1c1f28) ddr_addr[1] -port ddr_addr[1] -pin i_system_wrapper ddr_addr[1]
load net ddr_addr[2] -attr @rip(#1c1f28) ddr_addr[2] -port ddr_addr[2] -pin i_system_wrapper ddr_addr[2]
load net ddr_addr[3] -attr @rip(#1c1f28) ddr_addr[3] -port ddr_addr[3] -pin i_system_wrapper ddr_addr[3]
load net ddr_addr[4] -attr @rip(#1c1f28) ddr_addr[4] -port ddr_addr[4] -pin i_system_wrapper ddr_addr[4]
load net ddr_addr[5] -attr @rip(#1c1f28) ddr_addr[5] -port ddr_addr[5] -pin i_system_wrapper ddr_addr[5]
load net ddr_addr[6] -attr @rip(#1c1f28) ddr_addr[6] -port ddr_addr[6] -pin i_system_wrapper ddr_addr[6]
load net ddr_addr[7] -attr @rip(#1c1f28) ddr_addr[7] -port ddr_addr[7] -pin i_system_wrapper ddr_addr[7]
load net ddr_addr[8] -attr @rip(#1c1f28) ddr_addr[8] -port ddr_addr[8] -pin i_system_wrapper ddr_addr[8]
load net ddr_addr[9] -attr @rip(#1c1f28) ddr_addr[9] -port ddr_addr[9] -pin i_system_wrapper ddr_addr[9]
load net ddr_ba[0] -attr @rip(#1c1f28) ddr_ba[0] -port ddr_ba[0] -pin i_system_wrapper ddr_ba[0]
load net ddr_ba[1] -attr @rip(#1c1f28) ddr_ba[1] -port ddr_ba[1] -pin i_system_wrapper ddr_ba[1]
load net ddr_ba[2] -attr @rip(#1c1f28) ddr_ba[2] -port ddr_ba[2] -pin i_system_wrapper ddr_ba[2]
load net ddr_cas_n -port ddr_cas_n -pin i_system_wrapper ddr_cas_n
netloc ddr_cas_n 1 1 3 300 2550 NJ 2550 NJ
load net ddr_ck_n -port ddr_ck_n -pin i_system_wrapper ddr_ck_n
netloc ddr_ck_n 1 1 3 440 2510 NJ 2510 1260J
load net ddr_ck_p -port ddr_ck_p -pin i_system_wrapper ddr_ck_p
netloc ddr_ck_p 1 1 3 380 1700 NJ 1700 1340J
load net ddr_cke -port ddr_cke -pin i_system_wrapper ddr_cke
netloc ddr_cke 1 1 3 500 1720 NJ 1720 NJ
load net ddr_cs_n -port ddr_cs_n -pin i_system_wrapper ddr_cs_n
netloc ddr_cs_n 1 1 3 380 2580 NJ 2580 NJ
load net ddr_dm[0] -attr @rip(#1c1f28) ddr_dm[0] -port ddr_dm[0] -pin i_system_wrapper ddr_dm[0]
load net ddr_dm[1] -attr @rip(#1c1f28) ddr_dm[1] -port ddr_dm[1] -pin i_system_wrapper ddr_dm[1]
load net ddr_dm[2] -attr @rip(#1c1f28) ddr_dm[2] -port ddr_dm[2] -pin i_system_wrapper ddr_dm[2]
load net ddr_dm[3] -attr @rip(#1c1f28) ddr_dm[3] -port ddr_dm[3] -pin i_system_wrapper ddr_dm[3]
load net ddr_dq[0] -attr @rip(#1c1f28) ddr_dq[0] -port ddr_dq[0] -pin i_system_wrapper ddr_dq[0]
load net ddr_dq[10] -attr @rip(#1c1f28) ddr_dq[10] -port ddr_dq[10] -pin i_system_wrapper ddr_dq[10]
load net ddr_dq[11] -attr @rip(#1c1f28) ddr_dq[11] -port ddr_dq[11] -pin i_system_wrapper ddr_dq[11]
load net ddr_dq[12] -attr @rip(#1c1f28) ddr_dq[12] -port ddr_dq[12] -pin i_system_wrapper ddr_dq[12]
load net ddr_dq[13] -attr @rip(#1c1f28) ddr_dq[13] -port ddr_dq[13] -pin i_system_wrapper ddr_dq[13]
load net ddr_dq[14] -attr @rip(#1c1f28) ddr_dq[14] -port ddr_dq[14] -pin i_system_wrapper ddr_dq[14]
load net ddr_dq[15] -attr @rip(#1c1f28) ddr_dq[15] -port ddr_dq[15] -pin i_system_wrapper ddr_dq[15]
load net ddr_dq[16] -attr @rip(#1c1f28) ddr_dq[16] -port ddr_dq[16] -pin i_system_wrapper ddr_dq[16]
load net ddr_dq[17] -attr @rip(#1c1f28) ddr_dq[17] -port ddr_dq[17] -pin i_system_wrapper ddr_dq[17]
load net ddr_dq[18] -attr @rip(#1c1f28) ddr_dq[18] -port ddr_dq[18] -pin i_system_wrapper ddr_dq[18]
load net ddr_dq[19] -attr @rip(#1c1f28) ddr_dq[19] -port ddr_dq[19] -pin i_system_wrapper ddr_dq[19]
load net ddr_dq[1] -attr @rip(#1c1f28) ddr_dq[1] -port ddr_dq[1] -pin i_system_wrapper ddr_dq[1]
load net ddr_dq[20] -attr @rip(#1c1f28) ddr_dq[20] -port ddr_dq[20] -pin i_system_wrapper ddr_dq[20]
load net ddr_dq[21] -attr @rip(#1c1f28) ddr_dq[21] -port ddr_dq[21] -pin i_system_wrapper ddr_dq[21]
load net ddr_dq[22] -attr @rip(#1c1f28) ddr_dq[22] -port ddr_dq[22] -pin i_system_wrapper ddr_dq[22]
load net ddr_dq[23] -attr @rip(#1c1f28) ddr_dq[23] -port ddr_dq[23] -pin i_system_wrapper ddr_dq[23]
load net ddr_dq[24] -attr @rip(#1c1f28) ddr_dq[24] -port ddr_dq[24] -pin i_system_wrapper ddr_dq[24]
load net ddr_dq[25] -attr @rip(#1c1f28) ddr_dq[25] -port ddr_dq[25] -pin i_system_wrapper ddr_dq[25]
load net ddr_dq[26] -attr @rip(#1c1f28) ddr_dq[26] -port ddr_dq[26] -pin i_system_wrapper ddr_dq[26]
load net ddr_dq[27] -attr @rip(#1c1f28) ddr_dq[27] -port ddr_dq[27] -pin i_system_wrapper ddr_dq[27]
load net ddr_dq[28] -attr @rip(#1c1f28) ddr_dq[28] -port ddr_dq[28] -pin i_system_wrapper ddr_dq[28]
load net ddr_dq[29] -attr @rip(#1c1f28) ddr_dq[29] -port ddr_dq[29] -pin i_system_wrapper ddr_dq[29]
load net ddr_dq[2] -attr @rip(#1c1f28) ddr_dq[2] -port ddr_dq[2] -pin i_system_wrapper ddr_dq[2]
load net ddr_dq[30] -attr @rip(#1c1f28) ddr_dq[30] -port ddr_dq[30] -pin i_system_wrapper ddr_dq[30]
load net ddr_dq[31] -attr @rip(#1c1f28) ddr_dq[31] -port ddr_dq[31] -pin i_system_wrapper ddr_dq[31]
load net ddr_dq[3] -attr @rip(#1c1f28) ddr_dq[3] -port ddr_dq[3] -pin i_system_wrapper ddr_dq[3]
load net ddr_dq[4] -attr @rip(#1c1f28) ddr_dq[4] -port ddr_dq[4] -pin i_system_wrapper ddr_dq[4]
load net ddr_dq[5] -attr @rip(#1c1f28) ddr_dq[5] -port ddr_dq[5] -pin i_system_wrapper ddr_dq[5]
load net ddr_dq[6] -attr @rip(#1c1f28) ddr_dq[6] -port ddr_dq[6] -pin i_system_wrapper ddr_dq[6]
load net ddr_dq[7] -attr @rip(#1c1f28) ddr_dq[7] -port ddr_dq[7] -pin i_system_wrapper ddr_dq[7]
load net ddr_dq[8] -attr @rip(#1c1f28) ddr_dq[8] -port ddr_dq[8] -pin i_system_wrapper ddr_dq[8]
load net ddr_dq[9] -attr @rip(#1c1f28) ddr_dq[9] -port ddr_dq[9] -pin i_system_wrapper ddr_dq[9]
load net ddr_dqs_n[0] -attr @rip(#1c1f28) ddr_dqs_n[0] -port ddr_dqs_n[0] -pin i_system_wrapper ddr_dqs_n[0]
load net ddr_dqs_n[1] -attr @rip(#1c1f28) ddr_dqs_n[1] -port ddr_dqs_n[1] -pin i_system_wrapper ddr_dqs_n[1]
load net ddr_dqs_n[2] -attr @rip(#1c1f28) ddr_dqs_n[2] -port ddr_dqs_n[2] -pin i_system_wrapper ddr_dqs_n[2]
load net ddr_dqs_n[3] -attr @rip(#1c1f28) ddr_dqs_n[3] -port ddr_dqs_n[3] -pin i_system_wrapper ddr_dqs_n[3]
load net ddr_dqs_p[0] -attr @rip(#1c1f28) ddr_dqs_p[0] -port ddr_dqs_p[0] -pin i_system_wrapper ddr_dqs_p[0]
load net ddr_dqs_p[1] -attr @rip(#1c1f28) ddr_dqs_p[1] -port ddr_dqs_p[1] -pin i_system_wrapper ddr_dqs_p[1]
load net ddr_dqs_p[2] -attr @rip(#1c1f28) ddr_dqs_p[2] -port ddr_dqs_p[2] -pin i_system_wrapper ddr_dqs_p[2]
load net ddr_dqs_p[3] -attr @rip(#1c1f28) ddr_dqs_p[3] -port ddr_dqs_p[3] -pin i_system_wrapper ddr_dqs_p[3]
load net ddr_odt -port ddr_odt -pin i_system_wrapper ddr_odt
netloc ddr_odt 1 1 3 480 1750 NJ 1750 NJ
load net ddr_ras_n -port ddr_ras_n -pin i_system_wrapper ddr_ras_n
netloc ddr_ras_n 1 1 3 420 1780 NJ 1780 NJ
load net ddr_reset_n -port ddr_reset_n -pin i_system_wrapper ddr_reset_n
netloc ddr_reset_n 1 1 3 400 1810 NJ 1810 NJ
load net ddr_we_n -port ddr_we_n -pin i_system_wrapper ddr_we_n
netloc ddr_we_n 1 1 3 360 1840 NJ 1840 NJ
load net enable -port enable -pin i_system_wrapper enable
netloc enable 1 2 2 1020J 2060 1320J
load net fixed_io_ddr_vrn -port fixed_io_ddr_vrn -pin i_system_wrapper fixed_io_ddr_vrn
netloc fixed_io_ddr_vrn 1 1 3 460 1860 NJ 1860 1340J
load net fixed_io_ddr_vrp -port fixed_io_ddr_vrp -pin i_system_wrapper fixed_io_ddr_vrp
netloc fixed_io_ddr_vrp 1 1 3 500 2490 NJ 2490 NJ
load net fixed_io_mio[0] -attr @rip(#1c1f28) fixed_io_mio[0] -port fixed_io_mio[0] -pin i_system_wrapper fixed_io_mio[0]
load net fixed_io_mio[10] -attr @rip(#1c1f28) fixed_io_mio[10] -port fixed_io_mio[10] -pin i_system_wrapper fixed_io_mio[10]
load net fixed_io_mio[11] -attr @rip(#1c1f28) fixed_io_mio[11] -port fixed_io_mio[11] -pin i_system_wrapper fixed_io_mio[11]
load net fixed_io_mio[12] -attr @rip(#1c1f28) fixed_io_mio[12] -port fixed_io_mio[12] -pin i_system_wrapper fixed_io_mio[12]
load net fixed_io_mio[13] -attr @rip(#1c1f28) fixed_io_mio[13] -port fixed_io_mio[13] -pin i_system_wrapper fixed_io_mio[13]
load net fixed_io_mio[14] -attr @rip(#1c1f28) fixed_io_mio[14] -port fixed_io_mio[14] -pin i_system_wrapper fixed_io_mio[14]
load net fixed_io_mio[15] -attr @rip(#1c1f28) fixed_io_mio[15] -port fixed_io_mio[15] -pin i_system_wrapper fixed_io_mio[15]
load net fixed_io_mio[16] -attr @rip(#1c1f28) fixed_io_mio[16] -port fixed_io_mio[16] -pin i_system_wrapper fixed_io_mio[16]
load net fixed_io_mio[17] -attr @rip(#1c1f28) fixed_io_mio[17] -port fixed_io_mio[17] -pin i_system_wrapper fixed_io_mio[17]
load net fixed_io_mio[18] -attr @rip(#1c1f28) fixed_io_mio[18] -port fixed_io_mio[18] -pin i_system_wrapper fixed_io_mio[18]
load net fixed_io_mio[19] -attr @rip(#1c1f28) fixed_io_mio[19] -port fixed_io_mio[19] -pin i_system_wrapper fixed_io_mio[19]
load net fixed_io_mio[1] -attr @rip(#1c1f28) fixed_io_mio[1] -port fixed_io_mio[1] -pin i_system_wrapper fixed_io_mio[1]
load net fixed_io_mio[20] -attr @rip(#1c1f28) fixed_io_mio[20] -port fixed_io_mio[20] -pin i_system_wrapper fixed_io_mio[20]
load net fixed_io_mio[21] -attr @rip(#1c1f28) fixed_io_mio[21] -port fixed_io_mio[21] -pin i_system_wrapper fixed_io_mio[21]
load net fixed_io_mio[22] -attr @rip(#1c1f28) fixed_io_mio[22] -port fixed_io_mio[22] -pin i_system_wrapper fixed_io_mio[22]
load net fixed_io_mio[23] -attr @rip(#1c1f28) fixed_io_mio[23] -port fixed_io_mio[23] -pin i_system_wrapper fixed_io_mio[23]
load net fixed_io_mio[24] -attr @rip(#1c1f28) fixed_io_mio[24] -port fixed_io_mio[24] -pin i_system_wrapper fixed_io_mio[24]
load net fixed_io_mio[25] -attr @rip(#1c1f28) fixed_io_mio[25] -port fixed_io_mio[25] -pin i_system_wrapper fixed_io_mio[25]
load net fixed_io_mio[26] -attr @rip(#1c1f28) fixed_io_mio[26] -port fixed_io_mio[26] -pin i_system_wrapper fixed_io_mio[26]
load net fixed_io_mio[27] -attr @rip(#1c1f28) fixed_io_mio[27] -port fixed_io_mio[27] -pin i_system_wrapper fixed_io_mio[27]
load net fixed_io_mio[28] -attr @rip(#1c1f28) fixed_io_mio[28] -port fixed_io_mio[28] -pin i_system_wrapper fixed_io_mio[28]
load net fixed_io_mio[29] -attr @rip(#1c1f28) fixed_io_mio[29] -port fixed_io_mio[29] -pin i_system_wrapper fixed_io_mio[29]
load net fixed_io_mio[2] -attr @rip(#1c1f28) fixed_io_mio[2] -port fixed_io_mio[2] -pin i_system_wrapper fixed_io_mio[2]
load net fixed_io_mio[30] -attr @rip(#1c1f28) fixed_io_mio[30] -port fixed_io_mio[30] -pin i_system_wrapper fixed_io_mio[30]
load net fixed_io_mio[31] -attr @rip(#1c1f28) fixed_io_mio[31] -port fixed_io_mio[31] -pin i_system_wrapper fixed_io_mio[31]
load net fixed_io_mio[32] -attr @rip(#1c1f28) fixed_io_mio[32] -port fixed_io_mio[32] -pin i_system_wrapper fixed_io_mio[32]
load net fixed_io_mio[33] -attr @rip(#1c1f28) fixed_io_mio[33] -port fixed_io_mio[33] -pin i_system_wrapper fixed_io_mio[33]
load net fixed_io_mio[34] -attr @rip(#1c1f28) fixed_io_mio[34] -port fixed_io_mio[34] -pin i_system_wrapper fixed_io_mio[34]
load net fixed_io_mio[35] -attr @rip(#1c1f28) fixed_io_mio[35] -port fixed_io_mio[35] -pin i_system_wrapper fixed_io_mio[35]
load net fixed_io_mio[36] -attr @rip(#1c1f28) fixed_io_mio[36] -port fixed_io_mio[36] -pin i_system_wrapper fixed_io_mio[36]
load net fixed_io_mio[37] -attr @rip(#1c1f28) fixed_io_mio[37] -port fixed_io_mio[37] -pin i_system_wrapper fixed_io_mio[37]
load net fixed_io_mio[38] -attr @rip(#1c1f28) fixed_io_mio[38] -port fixed_io_mio[38] -pin i_system_wrapper fixed_io_mio[38]
load net fixed_io_mio[39] -attr @rip(#1c1f28) fixed_io_mio[39] -port fixed_io_mio[39] -pin i_system_wrapper fixed_io_mio[39]
load net fixed_io_mio[3] -attr @rip(#1c1f28) fixed_io_mio[3] -port fixed_io_mio[3] -pin i_system_wrapper fixed_io_mio[3]
load net fixed_io_mio[40] -attr @rip(#1c1f28) fixed_io_mio[40] -port fixed_io_mio[40] -pin i_system_wrapper fixed_io_mio[40]
load net fixed_io_mio[41] -attr @rip(#1c1f28) fixed_io_mio[41] -port fixed_io_mio[41] -pin i_system_wrapper fixed_io_mio[41]
load net fixed_io_mio[42] -attr @rip(#1c1f28) fixed_io_mio[42] -port fixed_io_mio[42] -pin i_system_wrapper fixed_io_mio[42]
load net fixed_io_mio[43] -attr @rip(#1c1f28) fixed_io_mio[43] -port fixed_io_mio[43] -pin i_system_wrapper fixed_io_mio[43]
load net fixed_io_mio[44] -attr @rip(#1c1f28) fixed_io_mio[44] -port fixed_io_mio[44] -pin i_system_wrapper fixed_io_mio[44]
load net fixed_io_mio[45] -attr @rip(#1c1f28) fixed_io_mio[45] -port fixed_io_mio[45] -pin i_system_wrapper fixed_io_mio[45]
load net fixed_io_mio[46] -attr @rip(#1c1f28) fixed_io_mio[46] -port fixed_io_mio[46] -pin i_system_wrapper fixed_io_mio[46]
load net fixed_io_mio[47] -attr @rip(#1c1f28) fixed_io_mio[47] -port fixed_io_mio[47] -pin i_system_wrapper fixed_io_mio[47]
load net fixed_io_mio[48] -attr @rip(#1c1f28) fixed_io_mio[48] -port fixed_io_mio[48] -pin i_system_wrapper fixed_io_mio[48]
load net fixed_io_mio[49] -attr @rip(#1c1f28) fixed_io_mio[49] -port fixed_io_mio[49] -pin i_system_wrapper fixed_io_mio[49]
load net fixed_io_mio[4] -attr @rip(#1c1f28) fixed_io_mio[4] -port fixed_io_mio[4] -pin i_system_wrapper fixed_io_mio[4]
load net fixed_io_mio[50] -attr @rip(#1c1f28) fixed_io_mio[50] -port fixed_io_mio[50] -pin i_system_wrapper fixed_io_mio[50]
load net fixed_io_mio[51] -attr @rip(#1c1f28) fixed_io_mio[51] -port fixed_io_mio[51] -pin i_system_wrapper fixed_io_mio[51]
load net fixed_io_mio[52] -attr @rip(#1c1f28) fixed_io_mio[52] -port fixed_io_mio[52] -pin i_system_wrapper fixed_io_mio[52]
load net fixed_io_mio[53] -attr @rip(#1c1f28) fixed_io_mio[53] -port fixed_io_mio[53] -pin i_system_wrapper fixed_io_mio[53]
load net fixed_io_mio[5] -attr @rip(#1c1f28) fixed_io_mio[5] -port fixed_io_mio[5] -pin i_system_wrapper fixed_io_mio[5]
load net fixed_io_mio[6] -attr @rip(#1c1f28) fixed_io_mio[6] -port fixed_io_mio[6] -pin i_system_wrapper fixed_io_mio[6]
load net fixed_io_mio[7] -attr @rip(#1c1f28) fixed_io_mio[7] -port fixed_io_mio[7] -pin i_system_wrapper fixed_io_mio[7]
load net fixed_io_mio[8] -attr @rip(#1c1f28) fixed_io_mio[8] -port fixed_io_mio[8] -pin i_system_wrapper fixed_io_mio[8]
load net fixed_io_mio[9] -attr @rip(#1c1f28) fixed_io_mio[9] -port fixed_io_mio[9] -pin i_system_wrapper fixed_io_mio[9]
load net fixed_io_ps_clk -port fixed_io_ps_clk -pin i_system_wrapper fixed_io_ps_clk
netloc fixed_io_ps_clk 1 1 3 400 2610 NJ 2610 NJ
load net fixed_io_ps_porb -port fixed_io_ps_porb -pin i_system_wrapper fixed_io_ps_porb
netloc fixed_io_ps_porb 1 1 3 460 2640 NJ 2640 NJ
load net fixed_io_ps_srstb -port fixed_io_ps_srstb -pin i_system_wrapper fixed_io_ps_srstb
netloc fixed_io_ps_srstb 1 2 2 1060J 2100 1280J
load net gpio_ctl[0] -attr @rip(#1c1f28) gpio_ctl[0] -port gpio_ctl[0] -pin gpio_ctl_IOBUF[0]_inst IO
load net gpio_ctl[1] -attr @rip(#1c1f28) gpio_ctl[1] -port gpio_ctl[1] -pin gpio_ctl_IOBUF[1]_inst IO
load net gpio_ctl[2] -attr @rip(#1c1f28) gpio_ctl[2] -port gpio_ctl[2] -pin gpio_ctl_IOBUF[2]_inst IO
load net gpio_ctl[3] -attr @rip(#1c1f28) gpio_ctl[3] -port gpio_ctl[3] -pin gpio_ctl_IOBUF[3]_inst IO
load net gpio_ctl_IBUF[0] -attr @rip(#1c1f28) 8 -pin gpio_ctl_IOBUF[0]_inst O -pin i_system_wrapper gpio_i[8]
load net gpio_ctl_IBUF[1] -attr @rip(#1c1f28) 9 -pin gpio_ctl_IOBUF[1]_inst O -pin i_system_wrapper gpio_i[9]
load net gpio_ctl_IBUF[2] -attr @rip(#1c1f28) 10 -pin gpio_ctl_IOBUF[2]_inst O -pin i_system_wrapper gpio_i[10]
load net gpio_ctl_IBUF[3] -attr @rip(#1c1f28) 11 -pin gpio_ctl_IOBUF[3]_inst O -pin i_system_wrapper gpio_i[11]
load net gpio_ctl_OBUF[0] -attr @rip(#1c1f28) bbstub_GPIO_O[46][8] -pin gpio_ctl_IOBUF[0]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][8]
load net gpio_ctl_OBUF[1] -attr @rip(#1c1f28) bbstub_GPIO_O[46][9] -pin gpio_ctl_IOBUF[1]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][9]
load net gpio_ctl_OBUF[2] -attr @rip(#1c1f28) bbstub_GPIO_O[46][10] -pin gpio_ctl_IOBUF[2]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][10]
load net gpio_ctl_OBUF[3] -attr @rip(#1c1f28) bbstub_GPIO_O[46][11] -pin gpio_ctl_IOBUF[3]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][11]
load net gpio_ctl_TRI[0] -attr @rip(#1c1f28) bbstub_GPIO_T[46][8] -pin gpio_ctl_IOBUF[0]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][8]
load net gpio_ctl_TRI[1] -attr @rip(#1c1f28) bbstub_GPIO_T[46][9] -pin gpio_ctl_IOBUF[1]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][9]
load net gpio_ctl_TRI[2] -attr @rip(#1c1f28) bbstub_GPIO_T[46][10] -pin gpio_ctl_IOBUF[2]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][10]
load net gpio_ctl_TRI[3] -attr @rip(#1c1f28) bbstub_GPIO_T[46][11] -pin gpio_ctl_IOBUF[3]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][11]
load net gpio_en_agc -port gpio_en_agc -pin gpio_en_agc_IOBUF_inst IO
netloc gpio_en_agc 1 2 2 NJ 1380 NJ
load net gpio_en_agc_IBUF -attr @rip(#1c1f28) 12 -pin gpio_en_agc_IOBUF_inst O -pin i_system_wrapper gpio_i[12]
load net gpio_en_agc_OBUF -attr @rip(#1c1f28) bbstub_GPIO_O[46][12] -pin gpio_en_agc_IOBUF_inst I -pin i_system_wrapper bbstub_GPIO_O[46][12]
load net gpio_en_agc_TRI -attr @rip(#1c1f28) bbstub_GPIO_T[46][12] -pin gpio_en_agc_IOBUF_inst T -pin i_system_wrapper bbstub_GPIO_T[46][12]
load net gpio_resetb -port gpio_resetb -pin gpio_resetb_IOBUF_inst IO
netloc gpio_resetb 1 2 2 NJ 1490 NJ
load net gpio_resetb_IBUF -attr @rip(#1c1f28) 14 -pin gpio_resetb_IOBUF_inst O -pin i_system_wrapper gpio_i[14]
load net gpio_resetb_OBUF -attr @rip(#1c1f28) bbstub_GPIO_O[46][14] -pin gpio_resetb_IOBUF_inst I -pin i_system_wrapper bbstub_GPIO_O[46][14]
load net gpio_resetb_TRI -attr @rip(#1c1f28) bbstub_GPIO_T[46][14] -pin gpio_resetb_IOBUF_inst T -pin i_system_wrapper bbstub_GPIO_T[46][14]
load net gpio_status[0] -attr @rip(#1c1f28) gpio_status[0] -port gpio_status[0] -pin gpio_status_IOBUF[0]_inst IO
load net gpio_status[1] -attr @rip(#1c1f28) gpio_status[1] -port gpio_status[1] -pin gpio_status_IOBUF[1]_inst IO
load net gpio_status[2] -attr @rip(#1c1f28) gpio_status[2] -port gpio_status[2] -pin gpio_status_IOBUF[2]_inst IO
load net gpio_status[3] -attr @rip(#1c1f28) gpio_status[3] -port gpio_status[3] -pin gpio_status_IOBUF[3]_inst IO
load net gpio_status[4] -attr @rip(#1c1f28) gpio_status[4] -port gpio_status[4] -pin gpio_status_IOBUF[4]_inst IO
load net gpio_status[5] -attr @rip(#1c1f28) gpio_status[5] -port gpio_status[5] -pin gpio_status_IOBUF[5]_inst IO
load net gpio_status[6] -attr @rip(#1c1f28) gpio_status[6] -port gpio_status[6] -pin gpio_status_IOBUF[6]_inst IO
load net gpio_status[7] -attr @rip(#1c1f28) gpio_status[7] -port gpio_status[7] -pin gpio_status_IOBUF[7]_inst IO
load net gpio_status_IBUF[0] -attr @rip(#1c1f28) 0 -pin gpio_status_IOBUF[0]_inst O -pin i_system_wrapper gpio_i[0]
load net gpio_status_IBUF[1] -attr @rip(#1c1f28) 1 -pin gpio_status_IOBUF[1]_inst O -pin i_system_wrapper gpio_i[1]
load net gpio_status_IBUF[2] -attr @rip(#1c1f28) 2 -pin gpio_status_IOBUF[2]_inst O -pin i_system_wrapper gpio_i[2]
load net gpio_status_IBUF[3] -attr @rip(#1c1f28) 3 -pin gpio_status_IOBUF[3]_inst O -pin i_system_wrapper gpio_i[3]
load net gpio_status_IBUF[4] -attr @rip(#1c1f28) 4 -pin gpio_status_IOBUF[4]_inst O -pin i_system_wrapper gpio_i[4]
load net gpio_status_IBUF[5] -attr @rip(#1c1f28) 5 -pin gpio_status_IOBUF[5]_inst O -pin i_system_wrapper gpio_i[5]
load net gpio_status_IBUF[6] -attr @rip(#1c1f28) 6 -pin gpio_status_IOBUF[6]_inst O -pin i_system_wrapper gpio_i[6]
load net gpio_status_IBUF[7] -attr @rip(#1c1f28) 7 -pin gpio_status_IOBUF[7]_inst O -pin i_system_wrapper gpio_i[7]
load net gpio_status_OBUF[0] -attr @rip(#1c1f28) bbstub_GPIO_O[46][0] -pin gpio_status_IOBUF[0]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][0]
load net gpio_status_OBUF[1] -attr @rip(#1c1f28) bbstub_GPIO_O[46][1] -pin gpio_status_IOBUF[1]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][1]
load net gpio_status_OBUF[2] -attr @rip(#1c1f28) bbstub_GPIO_O[46][2] -pin gpio_status_IOBUF[2]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][2]
load net gpio_status_OBUF[3] -attr @rip(#1c1f28) bbstub_GPIO_O[46][3] -pin gpio_status_IOBUF[3]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][3]
load net gpio_status_OBUF[4] -attr @rip(#1c1f28) bbstub_GPIO_O[46][4] -pin gpio_status_IOBUF[4]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][4]
load net gpio_status_OBUF[5] -attr @rip(#1c1f28) bbstub_GPIO_O[46][5] -pin gpio_status_IOBUF[5]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][5]
load net gpio_status_OBUF[6] -attr @rip(#1c1f28) bbstub_GPIO_O[46][6] -pin gpio_status_IOBUF[6]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][6]
load net gpio_status_OBUF[7] -attr @rip(#1c1f28) bbstub_GPIO_O[46][7] -pin gpio_status_IOBUF[7]_inst I -pin i_system_wrapper bbstub_GPIO_O[46][7]
load net gpio_status_TRI[0] -attr @rip(#1c1f28) bbstub_GPIO_T[46][0] -pin gpio_status_IOBUF[0]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][0]
load net gpio_status_TRI[1] -attr @rip(#1c1f28) bbstub_GPIO_T[46][1] -pin gpio_status_IOBUF[1]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][1]
load net gpio_status_TRI[2] -attr @rip(#1c1f28) bbstub_GPIO_T[46][2] -pin gpio_status_IOBUF[2]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][2]
load net gpio_status_TRI[3] -attr @rip(#1c1f28) bbstub_GPIO_T[46][3] -pin gpio_status_IOBUF[3]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][3]
load net gpio_status_TRI[4] -attr @rip(#1c1f28) bbstub_GPIO_T[46][4] -pin gpio_status_IOBUF[4]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][4]
load net gpio_status_TRI[5] -attr @rip(#1c1f28) bbstub_GPIO_T[46][5] -pin gpio_status_IOBUF[5]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][5]
load net gpio_status_TRI[6] -attr @rip(#1c1f28) bbstub_GPIO_T[46][6] -pin gpio_status_IOBUF[6]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][6]
load net gpio_status_TRI[7] -attr @rip(#1c1f28) bbstub_GPIO_T[46][7] -pin gpio_status_IOBUF[7]_inst T -pin i_system_wrapper bbstub_GPIO_T[46][7]
load net gpio_sync -port gpio_sync -pin gpio_sync_IOBUF_inst IO
netloc gpio_sync 1 2 2 NJ 1600 NJ
load net gpio_sync_IBUF -attr @rip(#1c1f28) 13 -pin gpio_sync_IOBUF_inst O -pin i_system_wrapper gpio_i[13]
load net gpio_sync_OBUF -attr @rip(#1c1f28) bbstub_GPIO_O[46][13] -pin gpio_sync_IOBUF_inst I -pin i_system_wrapper bbstub_GPIO_O[46][13]
load net gpio_sync_TRI -attr @rip(#1c1f28) bbstub_GPIO_T[46][13] -pin gpio_sync_IOBUF_inst T -pin i_system_wrapper bbstub_GPIO_T[46][13]
load net rx_clk_in_n -pin i_system_wrapper rx_clk_in_n -port rx_clk_in_n
netloc rx_clk_in_n 1 0 2 NJ 2170 280J
load net rx_clk_in_p -pin i_system_wrapper rx_clk_in_p -port rx_clk_in_p
netloc rx_clk_in_p 1 0 2 NJ 2200 260J
load net rx_data_in_n[0] -attr @rip(#1c1f28) rx_data_in_n[0] -pin i_system_wrapper rx_data_in_n[0] -port rx_data_in_n[0]
load net rx_data_in_n[1] -attr @rip(#1c1f28) rx_data_in_n[1] -pin i_system_wrapper rx_data_in_n[1] -port rx_data_in_n[1]
load net rx_data_in_n[2] -attr @rip(#1c1f28) rx_data_in_n[2] -pin i_system_wrapper rx_data_in_n[2] -port rx_data_in_n[2]
load net rx_data_in_n[3] -attr @rip(#1c1f28) rx_data_in_n[3] -pin i_system_wrapper rx_data_in_n[3] -port rx_data_in_n[3]
load net rx_data_in_n[4] -attr @rip(#1c1f28) rx_data_in_n[4] -pin i_system_wrapper rx_data_in_n[4] -port rx_data_in_n[4]
load net rx_data_in_n[5] -attr @rip(#1c1f28) rx_data_in_n[5] -pin i_system_wrapper rx_data_in_n[5] -port rx_data_in_n[5]
load net rx_data_in_p[0] -attr @rip(#1c1f28) rx_data_in_p[0] -pin i_system_wrapper rx_data_in_p[0] -port rx_data_in_p[0]
load net rx_data_in_p[1] -attr @rip(#1c1f28) rx_data_in_p[1] -pin i_system_wrapper rx_data_in_p[1] -port rx_data_in_p[1]
load net rx_data_in_p[2] -attr @rip(#1c1f28) rx_data_in_p[2] -pin i_system_wrapper rx_data_in_p[2] -port rx_data_in_p[2]
load net rx_data_in_p[3] -attr @rip(#1c1f28) rx_data_in_p[3] -pin i_system_wrapper rx_data_in_p[3] -port rx_data_in_p[3]
load net rx_data_in_p[4] -attr @rip(#1c1f28) rx_data_in_p[4] -pin i_system_wrapper rx_data_in_p[4] -port rx_data_in_p[4]
load net rx_data_in_p[5] -attr @rip(#1c1f28) rx_data_in_p[5] -pin i_system_wrapper rx_data_in_p[5] -port rx_data_in_p[5]
load net rx_frame_in_n -pin i_system_wrapper rx_frame_in_n -port rx_frame_in_n
netloc rx_frame_in_n 1 0 2 20J 2280 NJ
load net rx_frame_in_p -pin i_system_wrapper rx_frame_in_p -port rx_frame_in_p
netloc rx_frame_in_p 1 0 2 40J 2300 NJ
load net spi_clk -port spi_clk -pin spi_clk_OBUF_inst O
netloc spi_clk 1 3 1 1260J 2140n
load net spi_clk_OBUF -pin i_system_wrapper spi0_clk_o -pin spi_clk_OBUF_inst I
netloc spi_clk_OBUF 1 2 1 NJ 2140
load net spi_csn -port spi_csn -pin spi_csn_OBUF_inst O
netloc spi_csn 1 3 1 NJ 2210
load net spi_csn_OBUF -pin i_system_wrapper spi0_csn_0_o -pin spi_csn_OBUF_inst I
netloc spi_csn_OBUF 1 2 1 1060J 2160n
load net spi_miso -port spi_miso -pin spi_miso_IBUF_inst I
netloc spi_miso 1 0 1 20J 2340n
load net spi_miso_IBUF -pin i_system_wrapper spi0_sdi_i -pin spi_miso_IBUF_inst O
netloc spi_miso_IBUF 1 1 1 240J 2320n
load net spi_mosi -port spi_mosi -pin spi_mosi_OBUF_inst O
netloc spi_mosi 1 3 1 1260J 2250n
load net spi_mosi_OBUF -pin i_system_wrapper spi0_sdo_o -pin spi_mosi_OBUF_inst I
netloc spi_mosi_OBUF 1 2 1 1040J 2180n
load net tx_clk_out_n -pin i_system_wrapper tx_clk_out_n -port tx_clk_out_n
netloc tx_clk_out_n 1 2 2 1020J 2320 1280J
load net tx_clk_out_p -pin i_system_wrapper tx_clk_out_p -port tx_clk_out_p
netloc tx_clk_out_p 1 2 2 1000J 2340 1300J
load net tx_data_out_n[0] -attr @rip(#1c1f28) tx_data_out_n[0] -pin i_system_wrapper tx_data_out_n[0] -port tx_data_out_n[0]
load net tx_data_out_n[1] -attr @rip(#1c1f28) tx_data_out_n[1] -pin i_system_wrapper tx_data_out_n[1] -port tx_data_out_n[1]
load net tx_data_out_n[2] -attr @rip(#1c1f28) tx_data_out_n[2] -pin i_system_wrapper tx_data_out_n[2] -port tx_data_out_n[2]
load net tx_data_out_n[3] -attr @rip(#1c1f28) tx_data_out_n[3] -pin i_system_wrapper tx_data_out_n[3] -port tx_data_out_n[3]
load net tx_data_out_n[4] -attr @rip(#1c1f28) tx_data_out_n[4] -pin i_system_wrapper tx_data_out_n[4] -port tx_data_out_n[4]
load net tx_data_out_n[5] -attr @rip(#1c1f28) tx_data_out_n[5] -pin i_system_wrapper tx_data_out_n[5] -port tx_data_out_n[5]
load net tx_data_out_p[0] -attr @rip(#1c1f28) tx_data_out_p[0] -pin i_system_wrapper tx_data_out_p[0] -port tx_data_out_p[0]
load net tx_data_out_p[1] -attr @rip(#1c1f28) tx_data_out_p[1] -pin i_system_wrapper tx_data_out_p[1] -port tx_data_out_p[1]
load net tx_data_out_p[2] -attr @rip(#1c1f28) tx_data_out_p[2] -pin i_system_wrapper tx_data_out_p[2] -port tx_data_out_p[2]
load net tx_data_out_p[3] -attr @rip(#1c1f28) tx_data_out_p[3] -pin i_system_wrapper tx_data_out_p[3] -port tx_data_out_p[3]
load net tx_data_out_p[4] -attr @rip(#1c1f28) tx_data_out_p[4] -pin i_system_wrapper tx_data_out_p[4] -port tx_data_out_p[4]
load net tx_data_out_p[5] -attr @rip(#1c1f28) tx_data_out_p[5] -pin i_system_wrapper tx_data_out_p[5] -port tx_data_out_p[5]
load net tx_frame_out_n -pin i_system_wrapper tx_frame_out_n -port tx_frame_out_n
netloc tx_frame_out_n 1 2 2 940J 2400 NJ
load net tx_frame_out_p -pin i_system_wrapper tx_frame_out_p -port tx_frame_out_p
netloc tx_frame_out_p 1 2 2 920J 2430 NJ
load net txnrx -pin i_system_wrapper txnrx -port txnrx
netloc txnrx 1 2 2 900J 2460 NJ
load netBundle @ddr_addr 15 ddr_addr[14] ddr_addr[13] ddr_addr[12] ddr_addr[11] ddr_addr[10] ddr_addr[9] ddr_addr[8] ddr_addr[7] ddr_addr[6] ddr_addr[5] ddr_addr[4] ddr_addr[3] ddr_addr[2] ddr_addr[1] ddr_addr[0] -autobundled
netbloc @ddr_addr 1 2 2 900J 1900 NJ
load netBundle @ddr_ba 3 ddr_ba[2] ddr_ba[1] ddr_ba[0] -autobundled
netbloc @ddr_ba 1 2 2 920J 1930 NJ
load netBundle @ddr_dm 4 ddr_dm[3] ddr_dm[2] ddr_dm[1] ddr_dm[0] -autobundled
netbloc @ddr_dm 1 2 2 940J 1960 NJ
load netBundle @ddr_dq 32 ddr_dq[31] ddr_dq[30] ddr_dq[29] ddr_dq[28] ddr_dq[27] ddr_dq[26] ddr_dq[25] ddr_dq[24] ddr_dq[23] ddr_dq[22] ddr_dq[21] ddr_dq[20] ddr_dq[19] ddr_dq[18] ddr_dq[17] ddr_dq[16] ddr_dq[15] ddr_dq[14] ddr_dq[13] ddr_dq[12] ddr_dq[11] ddr_dq[10] ddr_dq[9] ddr_dq[8] ddr_dq[7] ddr_dq[6] ddr_dq[5] ddr_dq[4] ddr_dq[3] ddr_dq[2] ddr_dq[1] ddr_dq[0] -autobundled
netbloc @ddr_dq 1 2 2 960J 1990 NJ
load netBundle @ddr_dqs_n 4 ddr_dqs_n[3] ddr_dqs_n[2] ddr_dqs_n[1] ddr_dqs_n[0] -autobundled
netbloc @ddr_dqs_n 1 2 2 980J 2020 NJ
load netBundle @ddr_dqs_p 4 ddr_dqs_p[3] ddr_dqs_p[2] ddr_dqs_p[1] ddr_dqs_p[0] -autobundled
netbloc @ddr_dqs_p 1 2 2 1000J 2040 1340J
load netBundle @fixed_io_mio 54 fixed_io_mio[53] fixed_io_mio[52] fixed_io_mio[51] fixed_io_mio[50] fixed_io_mio[49] fixed_io_mio[48] fixed_io_mio[47] fixed_io_mio[46] fixed_io_mio[45] fixed_io_mio[44] fixed_io_mio[43] fixed_io_mio[42] fixed_io_mio[41] fixed_io_mio[40] fixed_io_mio[39] fixed_io_mio[38] fixed_io_mio[37] fixed_io_mio[36] fixed_io_mio[35] fixed_io_mio[34] fixed_io_mio[33] fixed_io_mio[32] fixed_io_mio[31] fixed_io_mio[30] fixed_io_mio[29] fixed_io_mio[28] fixed_io_mio[27] fixed_io_mio[26] fixed_io_mio[25] fixed_io_mio[24] fixed_io_mio[23] fixed_io_mio[22] fixed_io_mio[21] fixed_io_mio[20] fixed_io_mio[19] fixed_io_mio[18] fixed_io_mio[17] fixed_io_mio[16] fixed_io_mio[15] fixed_io_mio[14] fixed_io_mio[13] fixed_io_mio[12] fixed_io_mio[11] fixed_io_mio[10] fixed_io_mio[9] fixed_io_mio[8] fixed_io_mio[7] fixed_io_mio[6] fixed_io_mio[5] fixed_io_mio[4] fixed_io_mio[3] fixed_io_mio[2] fixed_io_mio[1] fixed_io_mio[0] -autobundled
netbloc @fixed_io_mio 1 2 2 1040J 2080 1300J
load netBundle @gpio_ctl 4 gpio_ctl[3] gpio_ctl[2] gpio_ctl[1] gpio_ctl[0] -autobundled
netbloc @gpio_ctl 1 2 2 900 60 NJ
load netBundle @gpio_status 8 gpio_status[7] gpio_status[6] gpio_status[5] gpio_status[4] gpio_status[3] gpio_status[2] gpio_status[1] gpio_status[0] -autobundled
netbloc @gpio_status 1 2 2 900 500 NJ
load netBundle @rx_data_in_n 6 rx_data_in_n[5] rx_data_in_n[4] rx_data_in_n[3] rx_data_in_n[2] rx_data_in_n[1] rx_data_in_n[0] -autobundled
netbloc @rx_data_in_n 1 0 2 NJ 2230 240J
load netBundle @rx_data_in_p 6 rx_data_in_p[5] rx_data_in_p[4] rx_data_in_p[3] rx_data_in_p[2] rx_data_in_p[1] rx_data_in_p[0] -autobundled
netbloc @rx_data_in_p 1 0 2 NJ 2260 NJ
load netBundle @tx_data_out_n 6 tx_data_out_n[5] tx_data_out_n[4] tx_data_out_n[3] tx_data_out_n[2] tx_data_out_n[1] tx_data_out_n[0] -autobundled
netbloc @tx_data_out_n 1 2 2 980J 2360 1320J
load netBundle @tx_data_out_p 6 tx_data_out_p[5] tx_data_out_p[4] tx_data_out_p[3] tx_data_out_p[2] tx_data_out_p[1] tx_data_out_p[0] -autobundled
netbloc @tx_data_out_p 1 2 2 960J 2380 1340J
load netBundle @gpio_status_OBUF 15 gpio_resetb_OBUF gpio_sync_OBUF gpio_en_agc_OBUF gpio_ctl_OBUF[3] gpio_ctl_OBUF[2] gpio_ctl_OBUF[1] gpio_ctl_OBUF[0] gpio_status_OBUF[7] gpio_status_OBUF[6] gpio_status_OBUF[5] gpio_status_OBUF[4] gpio_status_OBUF[3] gpio_status_OBUF[2] gpio_status_OBUF[1] gpio_status_OBUF[0] -autobundled
netbloc @gpio_status_OBUF 1 1 2 320 2530 860
load netBundle @gpio_status_TRI,gpio_ctl_TRI 15 gpio_resetb_TRI gpio_sync_TRI gpio_en_agc_TRI gpio_ctl_TRI[3] gpio_ctl_TRI[2] gpio_ctl_TRI[1] gpio_ctl_TRI[0] gpio_status_TRI[7] gpio_status_TRI[6] gpio_status_TRI[5] gpio_status_TRI[4] gpio_status_TRI[3] gpio_status_TRI[2] gpio_status_TRI[1] gpio_status_TRI[0] -autobundled
netbloc @gpio_status_TRI,gpio_ctl_TRI 1 1 2 480 1680 880
load netBundle @gpio_status_IBUF 15 gpio_resetb_IBUF gpio_sync_IBUF gpio_en_agc_IBUF gpio_ctl_IBUF[3] gpio_ctl_IBUF[2] gpio_ctl_IBUF[1] gpio_ctl_IBUF[0] gpio_status_IBUF[7] gpio_status_IBUF[6] gpio_status_IBUF[5] gpio_status_IBUF[4] gpio_status_IBUF[3] gpio_status_IBUF[2] gpio_status_IBUF[1] gpio_status_IBUF[0] -autobundled
netbloc @gpio_status_IBUF 1 1 2 340 1660 880
levelinfo -pg 1 0 80 630 1100 1360
pagesize -pg 1 -db -bbox -sgen -160 0 1530 2660
show
zoom 0.350996
scrollpos -136 234
#
# initialize ictrl to current module system_top work:system_top:NOFILE
ictrl init topinfo |
