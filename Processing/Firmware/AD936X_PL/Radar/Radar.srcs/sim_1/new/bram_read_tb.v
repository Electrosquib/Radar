//////////////////////////////////////////////////////////////////////////////////
// Company: University of Hawaii
// Engineer: Levi Farinas
// 
// Create Date: 09/02/2026 08:48:09 AM
// Design Name: 
// Module Name: bram_read_tb
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

module bram_read_tb;

reg clk = 0;
reg enable = 0;
reg [8:0] profile_index = 0;
reg [3:0] word_index = 0;
reg [31:0] bram_data = 0;

wire [15:0] profile_word;
wire [12:0] addr;
wire busy;
wire valid;

bram_read dut(
    .clk(clk),
    .enable(enable),
    .profile_index(profile_index),
    .word_index(word_index),
    .bram_data(bram_data),
    .profile_word(profile_word),
    .addr(addr),
    .busy(busy),
    .valid(valid)
);

always #5 clk = ~clk;

initial begin
    #20;

    profile_index = 9'd5;
    word_index = 4'd3;
    enable = 1;

    #10;
    enable = 0;

    #10;
    bram_data = 32'h0000ABCD;

    #100;

    profile_index = 9'd20;
    word_index = 4'd12;
    enable = 1;

    #10;
    enable = 0;

    #10;
    bram_data = 32'h00001234;

    #100;

    $finish;
end

endmodule
