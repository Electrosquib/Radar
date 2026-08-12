vlib work
vlib activehdl

vlib activehdl/xilinx_vip
vlib activehdl/xpm
vlib activehdl/xlconstant_v1_1_7
vlib activehdl/xil_defaultlib
vlib activehdl/generic_baseblocks_v2_1_0
vlib activehdl/axi_infrastructure_v1_1_0
vlib activehdl/axi_register_slice_v2_1_24
vlib activehdl/fifo_generator_v13_2_5
vlib activehdl/axi_data_fifo_v2_1_23
vlib activehdl/axi_crossbar_v2_1_25
vlib activehdl/lib_cdc_v1_0_2
vlib activehdl/proc_sys_reset_v5_0_13
vlib activehdl/smartconnect_v1_0
vlib activehdl/axi_vip_v1_1_10
vlib activehdl/xlconcat_v2_1_4
vlib activehdl/processing_system7_vip_v1_0_12
vlib activehdl/util_reduced_logic_v2_0_4
vlib activehdl/axi_protocol_converter_v2_1_24

vmap xilinx_vip activehdl/xilinx_vip
vmap xpm activehdl/xpm
vmap xlconstant_v1_1_7 activehdl/xlconstant_v1_1_7
vmap xil_defaultlib activehdl/xil_defaultlib
vmap generic_baseblocks_v2_1_0 activehdl/generic_baseblocks_v2_1_0
vmap axi_infrastructure_v1_1_0 activehdl/axi_infrastructure_v1_1_0
vmap axi_register_slice_v2_1_24 activehdl/axi_register_slice_v2_1_24
vmap fifo_generator_v13_2_5 activehdl/fifo_generator_v13_2_5
vmap axi_data_fifo_v2_1_23 activehdl/axi_data_fifo_v2_1_23
vmap axi_crossbar_v2_1_25 activehdl/axi_crossbar_v2_1_25
vmap lib_cdc_v1_0_2 activehdl/lib_cdc_v1_0_2
vmap proc_sys_reset_v5_0_13 activehdl/proc_sys_reset_v5_0_13
vmap smartconnect_v1_0 activehdl/smartconnect_v1_0
vmap axi_vip_v1_1_10 activehdl/axi_vip_v1_1_10
vmap xlconcat_v2_1_4 activehdl/xlconcat_v2_1_4
vmap processing_system7_vip_v1_0_12 activehdl/processing_system7_vip_v1_0_12
vmap util_reduced_logic_v2_0_4 activehdl/util_reduced_logic_v2_0_4
vmap axi_protocol_converter_v2_1_24 activehdl/axi_protocol_converter_v2_1_24

vlog -work xilinx_vip  -sv2k12 "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/axi4stream_vip_axi4streampc.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/axi_vip_axi4pc.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/xil_common_vip_pkg.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/axi4stream_vip_pkg.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/axi_vip_pkg.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/axi4stream_vip_if.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/axi_vip_if.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/clk_vip_if.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/hdl/rst_vip_if.sv" \

vlog -work xpm  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/ip/xpm/xpm_cdc/hdl/xpm_cdc.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/ip/xpm/xpm_fifo/hdl/xpm_fifo.sv" \
"D:/Xilinx_2021_1/Vivado/2021.1/data/ip/xpm/xpm_memory/hdl/xpm_memory.sv" \

vcom -work xpm -93 \
"D:/Xilinx_2021_1/Vivado/2021.1/data/ip/xpm/xpm_VCOMP.vhd" \

vlog -work xlconstant_v1_1_7  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/fcfc/hdl/xlconstant_v1_1_vl_rfs.v" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_GND_1_0/sim/system_GND_1_0.v" \
"../../../bd/system/ipshared/common/ad_addsub.v" \
"../../../bd/system/ipshared/xilinx/common/ad_data_clk.v" \
"../../../bd/system/ipshared/xilinx/common/ad_data_in.v" \
"../../../bd/system/ipshared/xilinx/common/ad_data_out.v" \
"../../../bd/system/ipshared/common/ad_datafmt.v" \
"../../../bd/system/ipshared/xilinx/common/ad_dcfilter.v" \
"../../../bd/system/ipshared/common/ad_dds.v" \
"../../../bd/system/ipshared/common/ad_dds_1.v" \
"../../../bd/system/ipshared/common/ad_dds_2.v" \
"../../../bd/system/ipshared/common/ad_dds_cordic_pipe.v" \
"../../../bd/system/ipshared/common/ad_dds_sine.v" \
"../../../bd/system/ipshared/common/ad_dds_sine_cordic.v" \
"../../../bd/system/ipshared/common/ad_iqcor.v" \
"../../../bd/system/ipshared/xilinx/common/ad_mul.v" \
"../../../bd/system/ipshared/common/ad_pnmon.v" \
"../../../bd/system/ipshared/common/ad_pps_receiver.v" \
"../../../bd/system/ipshared/common/ad_rst.v" \
"../../../bd/system/ipshared/common/ad_tdd_control.v" \
"../../../bd/system/ipshared/c736/xilinx/axi_ad9361_cmos_if.v" \
"../../../bd/system/ipshared/c736/xilinx/axi_ad9361_lvds_if.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_rx.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_rx_channel.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_rx_pnmon.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_tdd.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_tdd_if.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_tx.v" \
"../../../bd/system/ipshared/c736/axi_ad9361_tx_channel.v" \
"../../../bd/system/ipshared/common/up_adc_channel.v" \
"../../../bd/system/ipshared/common/up_adc_common.v" \
"../../../bd/system/ipshared/common/up_axi.v" \
"../../../bd/system/ipshared/common/up_clock_mon.v" \
"../../../bd/system/ipshared/common/up_dac_channel.v" \
"../../../bd/system/ipshared/common/up_dac_common.v" \
"../../../bd/system/ipshared/common/up_delay_cntrl.v" \
"../../../bd/system/ipshared/common/up_tdd_cntrl.v" \
"../../../bd/system/ipshared/common/up_xfer_cntrl.v" \
"../../../bd/system/ipshared/common/up_xfer_status.v" \
"../../../bd/system/ipshared/c736/axi_ad9361.v" \
"../../../bd/system/ip/system_axi_ad9361_0/sim/system_axi_ad9361_0.v" \
"../../../bd/system/ipshared/b8ee/sync_bits.v" \
"../../../bd/system/ipshared/b8ee/sync_data.v" \
"../../../bd/system/ipshared/b8ee/sync_event.v" \
"../../../bd/system/ipshared/b8ee/sync_gray.v" \
"../../../bd/system/ipshared/common/ad_mem.v" \
"../../../bd/system/ipshared/0f02/util_axis_fifo_address_generator.v" \
"../../../bd/system/ipshared/0f02/util_axis_fifo.v" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_ad9361_adc_dma_0/sim/system_axi_ad9361_adc_dma_0_pkg.sv" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ipshared/common/ad_mem_asym.v" \
"../../../bd/system/ipshared/68d1/address_generator.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_burst_memory.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_regmap.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_regmap_request.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_reset_manager.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_resize_dest.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_resize_src.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_response_manager.v" \
"../../../bd/system/ipshared/68d1/axi_dmac_transfer.v" \
"../../../bd/system/ipshared/68d1/axi_register_slice.v" \
"../../../bd/system/ipshared/68d1/data_mover.v" \
"../../../bd/system/ipshared/68d1/dest_axi_mm.v" \
"../../../bd/system/ipshared/68d1/dest_axi_stream.v" \
"../../../bd/system/ipshared/68d1/dest_fifo_inf.v" \
"../../../bd/system/ipshared/68d1/dmac_2d_transfer.v" \
"../../../bd/system/ipshared/68d1/request_arb.v" \
"../../../bd/system/ipshared/68d1/request_generator.v" \
"../../../bd/system/ipshared/68d1/response_generator.v" \
"../../../bd/system/ipshared/68d1/response_handler.v" \
"../../../bd/system/ipshared/68d1/splitter.v" \
"../../../bd/system/ipshared/68d1/src_axi_mm.v" \
"../../../bd/system/ipshared/68d1/src_axi_stream.v" \
"../../../bd/system/ipshared/68d1/src_fifo_inf.v" \
"../../../bd/system/ipshared/68d1/axi_dmac.v" \
"../../../bd/system/ip/system_axi_ad9361_adc_dma_0/sim/system_axi_ad9361_adc_dma_0.v" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_ad9361_dac_dma_0/sim/system_axi_ad9361_dac_dma_0_pkg.sv" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_ad9361_dac_dma_0/sim/system_axi_ad9361_dac_dma_0.v" \
"../../../bd/system/ipshared/4463/util_rfifo.v" \
"../../../bd/system/ip/system_axi_ad9361_dac_fifo_0/sim/system_axi_ad9361_dac_fifo_0.v" \

vlog -work generic_baseblocks_v2_1_0  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/b752/hdl/generic_baseblocks_v2_1_vl_rfs.v" \

vlog -work axi_infrastructure_v1_1_0  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl/axi_infrastructure_v1_1_vl_rfs.v" \

vlog -work axi_register_slice_v2_1_24  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/8f68/hdl/axi_register_slice_v2_1_vl_rfs.v" \

vlog -work fifo_generator_v13_2_5  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/276e/simulation/fifo_generator_vlog_beh.v" \

vcom -work fifo_generator_v13_2_5 -93 \
"../../../../zc702.gen/sources_1/bd/system/ipshared/276e/hdl/fifo_generator_v13_2_rfs.vhd" \

vlog -work fifo_generator_v13_2_5  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/276e/hdl/fifo_generator_v13_2_rfs.v" \

vlog -work axi_data_fifo_v2_1_23  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/94ec/hdl/axi_data_fifo_v2_1_vl_rfs.v" \

vlog -work axi_crossbar_v2_1_25  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/3917/hdl/axi_crossbar_v2_1_vl_rfs.v" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_xbar_0/sim/system_xbar_0.v" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/sim/bd_31bd.v" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_0/sim/bd_31bd_one_0.v" \

vcom -work lib_cdc_v1_0_2 -93 \
"../../../../zc702.gen/sources_1/bd/system/ipshared/ef1e/hdl/lib_cdc_v1_0_rfs.vhd" \

vcom -work proc_sys_reset_v5_0_13 -93 \
"../../../../zc702.gen/sources_1/bd/system/ipshared/8842/hdl/proc_sys_reset_v5_0_vh_rfs.vhd" \

vcom -work xil_defaultlib -93 \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_1/sim/bd_31bd_psr_aclk_0.vhd" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/sc_util_v1_0_vl_rfs.sv" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/ea34/hdl/sc_mmu_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_2/sim/bd_31bd_s00mmu_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/4fd2/hdl/sc_transaction_regulator_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_3/sim/bd_31bd_s00tr_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/8047/hdl/sc_si_converter_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_4/sim/bd_31bd_s00sic_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/b89e/hdl/sc_axi2sc_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_5/sim/bd_31bd_s00a2s_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/sc_node_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_6/sim/bd_31bd_sawn_0.sv" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_7/sim/bd_31bd_swn_0.sv" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_8/sim/bd_31bd_sbn_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/7005/hdl/sc_sc2axi_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_9/sim/bd_31bd_m00s2a_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/7bd7/hdl/sc_exit_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/bd_0/ip/ip_10/sim/bd_31bd_m00e_0.sv" \

vlog -work smartconnect_v1_0  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/c012/hdl/sc_switchboard_v1_0_vl_rfs.sv" \

vlog -work axi_vip_v1_1_10  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/0980/hdl/axi_vip_v1_1_vl_rfs.sv" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp1_interconnect_0/sim/system_axi_hp1_interconnect_0.v" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/sim/bd_c0fd.v" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_0/sim/bd_c0fd_one_0.v" \

vcom -work xil_defaultlib -93 \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_1/sim/bd_c0fd_psr_aclk_0.vhd" \

vlog -work xil_defaultlib  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_2/sim/bd_c0fd_s00mmu_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_3/sim/bd_c0fd_s00tr_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_4/sim/bd_c0fd_s00sic_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_5/sim/bd_c0fd_s00a2s_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_6/sim/bd_c0fd_sarn_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_7/sim/bd_c0fd_srn_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_8/sim/bd_c0fd_m00s2a_0.sv" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/bd_0/ip/ip_9/sim/bd_c0fd_m00e_0.sv" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_axi_hp2_interconnect_0/sim/system_axi_hp2_interconnect_0.v" \

vcom -work xil_defaultlib -93 \
"../../../bd/system/ip/system_sys_200m_rstgen_0/sim/system_sys_200m_rstgen_0.vhd" \

vlog -work xlconcat_v2_1_4  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/4b67/hdl/xlconcat_v2_1_vl_rfs.v" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_sys_concat_intc_0/sim/system_sys_concat_intc_0.v" \

vlog -work processing_system7_vip_v1_0_12  -sv2k12 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl/processing_system7_vip_v1_0_vl_rfs.sv" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_sys_ps7_0/sim/system_sys_ps7_0.v" \

vcom -work xil_defaultlib -93 \
"../../../bd/system/ip/system_sys_rstgen_0/sim/system_sys_rstgen_0.vhd" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ipshared/d170/util_wfifo.v" \
"../../../bd/system/ip/system_util_ad9361_adc_fifo_0/sim/system_util_ad9361_adc_fifo_0.v" \
"../../../bd/system/common/ad_perfect_shuffle.v" \
"../../../bd/system/ipshared/util_pack_common/pack_ctrl.v" \
"../../../bd/system/ipshared/util_pack_common/pack_interconnect.v" \
"../../../bd/system/ipshared/util_pack_common/pack_network.v" \
"../../../bd/system/ipshared/util_pack_common/pack_shell.v" \
"../../../bd/system/ipshared/a685/util_cpack2_impl.v" \
"../../../bd/system/ipshared/a685/util_cpack2.v" \
"../../../bd/system/ip/system_util_ad9361_adc_pack_0/sim/system_util_ad9361_adc_pack_0.v" \
"../../../bd/system/ipshared/7b43/util_upack2_impl.v" \
"../../../bd/system/ipshared/7b43/util_upack2.v" \
"../../../bd/system/ip/system_util_ad9361_dac_upack_0/sim/system_util_ad9361_dac_upack_0.v" \
"../../../bd/system/ipshared/067c/util_clkdiv.v" \
"../../../bd/system/ip/system_util_ad9361_divclk_0/sim/system_util_ad9361_divclk_0.v" \

vcom -work xil_defaultlib -93 \
"../../../bd/system/ip/system_util_ad9361_divclk_reset_0/sim/system_util_ad9361_divclk_reset_0.vhd" \

vlog -work util_reduced_logic_v2_0_4  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/4c94/hdl/util_reduced_logic_v2_0_vl_rfs.v" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_util_ad9361_divclk_sel_0/sim/system_util_ad9361_divclk_sel_0.v" \
"../../../bd/system/ip/system_util_ad9361_divclk_sel_concat_0/sim/system_util_ad9361_divclk_sel_concat_0.v" \
"../../../bd/system/ipshared/common/util_pulse_gen.v" \
"../../../bd/system/ipshared/d3f6/util_tdd_sync.v" \
"../../../bd/system/ip/system_util_ad9361_tdd_sync_0/sim/system_util_ad9361_tdd_sync_0.v" \
"../../../bd/system/sim/system.v" \

vlog -work axi_protocol_converter_v2_1_24  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../../zc702.gen/sources_1/bd/system/ipshared/6e0d/hdl/axi_protocol_converter_v2_1_vl_rfs.v" \

vlog -work xil_defaultlib  -v2k5 "+incdir+../../../bd/system/ipshared/68d1" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/ec67/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/80cc/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/22b9/hdl/verilog" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/f42d/hdl" "+incdir+../../../../zc702.gen/sources_1/bd/system/ipshared/68d1" "+incdir+D:/Xilinx_2021_1/Vivado/2021.1/data/xilinx_vip/include" \
"../../../bd/system/ip/system_auto_pc_3/sim/system_auto_pc_3.v" \
"../../../bd/system/ip/system_auto_pc_0/sim/system_auto_pc_0.v" \
"../../../bd/system/ip/system_auto_pc_1/sim/system_auto_pc_1.v" \
"../../../bd/system/ip/system_auto_pc_2/sim/system_auto_pc_2.v" \

vlog -work xil_defaultlib \
"glbl.v"

