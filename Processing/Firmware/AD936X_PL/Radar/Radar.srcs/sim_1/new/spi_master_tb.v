`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 08/20/2026 03:36:44 PM
// Design Name: 
// Module Name: spi_master_tb
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


`timescale 1ns / 1ps

module spi_master_tb;

reg clk = 0;
reg reset = 1;
reg start = 0;
reg [23:0] tx_data = 0;
reg miso = 0;

wire [23:0] rx_data;
wire busy;
wire done;
wire sclk;
wire mosi;
wire cs_n;

always #5 clk = ~clk;

spi_master dut (
    .clk(clk),
    .reset(reset),
    .start(start),
    .tx_data(tx_data),
    .rx_data(rx_data),
    .busy(busy),
    .done(done),
    .sclk(sclk),
    .mosi(mosi),
    .miso(miso),
    .cs_n(cs_n)
);

initial begin
    #100;
    reset = 0;

    #100;
    tx_data = 24'h815A55;;
    start = 1;

    #10;
    start = 0;

    wait(done);

    #500;
    $finish;
end

endmodule
