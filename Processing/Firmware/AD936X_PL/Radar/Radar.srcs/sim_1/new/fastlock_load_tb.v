`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Hawaii
// Engineer: Levi Farinas
// 
// Create Date: 09/04/2026 02:57:42 PM
// Design Name: 
// Module Name: fastlock_load_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module fastlock_load_tb;

reg clk = 0;
reg reset = 1;
reg enable = 0;
reg miso = 0;
reg [8:0] num_profiles = 9'd8;
reg [31:0] bram_data = 0;

wire spi_start;
wire [23:0] spi_reg;
wire [7:0] spi_data;
wire [31:0] bram_addr;

wire [23:0] spi_tx_data;
wire [23:0] spi_rx_data;
wire spi_busy;
wire spi_done;
wire sclk;
wire mosi;
wire cs_n;

assign spi_tx_data = {spi_reg[15:0], spi_data};

fastlock_load dut(
    .spi_start(spi_start),
    .spi_reg(spi_reg),
    .spi_data(spi_data),
    .enable(enable),
    .spi_valid(spi_done),
    .clk(clk),
    .num_profiles(num_profiles),
    .bram_data(bram_data),
    .bram_addr(bram_addr)
);

spi_master spi(
    .clk(clk),
    .reset(reset),
    .start(spi_start),
    .tx_data(spi_tx_data),
    .rx_data(spi_rx_data),
    .busy(spi_busy),
    .done(spi_done),
    .sclk(sclk),
    .mosi(mosi),
    .miso(miso),
    .cs_n(cs_n)
);

always #5 clk = ~clk;

always @(*) begin
    bram_data = 32'h000000A0 + bram_addr;
end

initial begin
    #20;
    reset = 0;

    #20;
    enable = 1;
    #10;
    enable = 0;

    #1000000;
    $finish;
end

initial begin
    $monitor(
        "t=%0t state=%0d profile=%0d page=%0d word=%0d start=%b busy=%b done=%b cs=%b sclk=%b",
        $time,
        dut.state,
        dut.profile_index,
        dut.profile_page,
        dut.word_index,
        spi_start,
        spi_busy,
        spi_done,
        cs_n,
        sclk
    );
end

endmodule
