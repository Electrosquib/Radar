`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: University of Hawaii
// Engineer: Levi Farinas
// 
// Create Date: 09/02/2026 09:56:33 AM
// Design Name: 
// Module Name: fastlock_load
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


module fastlock_load(
    output reg spi_start,
    output reg [23:0] spi_reg,
    output reg [7:0] spi_data,
    input wire enable,
    input wire clk
);


// BRAM Module
reg bram_enable = 0;
reg [8:0] profile_index = 0;
reg [3:0] word_index = 0;
reg [31:0] bram_data;
reg [31:0] bram_addr;

wire [31:0] profile_word;
wire bram_busy;
wire bram_valid;
bram_read bram_reader(
    .clk(clk),
    .enable(bram_enable),
    .profile_index(profile_index),
    .word_index(word_index),
    .bram_data(bram_data),
    .profile_word(profile_word),
    .addr(bram_addr),
    .busy(bram_busy),
    .valid(bram_valid)
);

// AD9361 Fastlock Registers
reg [23:0] CTRL = 24'h25F;
reg [23:0] DATA = 24'h25D;
reg [23:0] ADDR = 24'h25C;
reg [23:0] READ = 24'h25E;


// TX is 0x29x RX is 0x25x
reg [6:0] TR_OFF =7'h40; // TX
// reg [6:0] TR_OFF =7'h00; // RX

// FSM States
reg [3:0] state = 4'b0000;
localparam IDLE           = 4'b0000;
localparam BRAM_READ      = 4'b0001;
localparam WORD0_DATA     = 4'b0010;
localparam WORD0_ADDR     = 4'b0011;
localparam WORD_CTRL      = 4'b0100;
localparam WORD_READ      = 4'b0101;
localparam WORD_DATA      = 4'b0110;
localparam WORD_ADDR      = 4'b0111;
localparam CHECK_WORD     = 4'b1000;
localparam LOADCTL_SET    = 4'b1001;
localparam LOADCTL_CLEAR  = 4'b1010;
localparam NEXT_PROFILE   = 4'b1011;
localparam SPI_WAIT       = 4'b1100;
localparam BRAM_WAIT      = 4'b1101;

reg [15:0] word_data;

always @(posedge clk) begin
    spi_start <= 0;
    bram_enable <= 0;

    case (state)

        IDLE: begin
            profile_index <= 0;
            word_index <= 0;
            if (enable == 1) begin
                state <= BRAM_READ;                
            end
        end

        BRAM_READ: begin
            bram_enable <= 1;
            state <= BRAM_WAIT;            
        end

        BRAM_WAIT: begin
            if (bram_valid) begin
                state <= WORD0_DATA
            end
        end

        WORD0_DATA: begin
            spi_reg <= DATA;
            spi_data <= 
        end




        WORD0_ADDR: begin
            
        end




        WORD_CTRL: begin
            
        end




        WORD_READ: begin
            
        end




        WORD_DATA: begin
            
        end




        WORD_ADDR: begin
            
        end




        CHECK_WORD: begin
            
        end




        LOADCTL_SET: begin
            
        end




        LOADCTL_CLEAR: begin
            
        end




        NEXT_PROFILE: begin
            
        end

end

endmodule
