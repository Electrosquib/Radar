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
    input wire spi_valid,
    input wire clk,
    input wire [8:0] num_profiles, // Must be a multiple of 8, and less than 512
    input wire [31:0] bram_data,
    output wire [31:0] bram_addr
);


// BRAM Module
reg bram_enable = 0;
reg [2:0] profile_index = 0;
reg [8:0] profile_page = 0;
reg [3:0] word_index = 0;

wire [15:0] profile_word;
wire bram_busy;
wire bram_valid;
bram_read bram_reader(
    .clk(clk),
    .enable(bram_enable),
    .profile_index(profile_page + profile_index),
    .word_index(word_index),
    .bram_data(bram_data),
    .profile_word(profile_word),
    .addr(bram_addr),
    .busy(bram_busy),
    .valid(bram_valid)
);

// FSM States
reg [3:0] state = 4'b0000;
reg [3:0] next_state = 4'b0000;

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
// localparam NEXT_PAGE      = 4'b1110;


reg [6:0] TR_OFF =7'h00; // RX
reg RX_PROFS_DONE = 0;

// AD9361 Fastlock Registers
// TX is 0x29x RX is 0x25x
reg [11:0] CTRL = 12'h25F;
reg [11:0] DATA = 12'h25D;
reg [11:0] ADDR = 12'h25C;
reg [11:0] READ = 12'h25E;


always @(posedge clk) begin
    spi_start <= 0;
    bram_enable <= 0;

    case (state)

        IDLE: begin
            // profile_index <= 0; // Not updated here because multiple loads will make profile_index >> 8. Current load profile_index is found by % 8.
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
                if (word_index == 0) begin
                    state <= WORD0_DATA;
                end else begin
                    state <= WORD_CTRL;
                end
            end
        end

        WORD0_DATA: begin
            spi_reg <= DATA;
            spi_data <= profile_word[7:0];
            next_state <= WORD0_ADDR;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        WORD0_ADDR: begin
            spi_reg <= ADDR;
            spi_data <= {1'b0, profile_index, word_index};
            word_index <= word_index + 1'b1;
            next_state <= BRAM_READ;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        WORD_CTRL: begin
            spi_reg <= CTRL;
            spi_data <= 8'h03;
            next_state <= WORD_READ;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        WORD_READ: begin
            spi_reg <= READ;
            spi_data <= 8'h00;
            next_state <= WORD_DATA;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        WORD_DATA: begin
           spi_reg <= DATA;
           spi_data <= profile_word[7:0];
           next_state <= WORD_ADDR;
           state <= SPI_WAIT;
           spi_start <= 1;
        end

        WORD_ADDR: begin
            spi_reg <= ADDR;
            spi_data <= {1'b0, profile_index, word_index};
            next_state <= CHECK_WORD;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        CHECK_WORD: begin
           if (word_index != 15) begin
                word_index <= word_index + 1'b1;
                state <= BRAM_READ;
           end else begin
                state <= LOADCTL_SET;
           end
        end

        LOADCTL_SET: begin
            spi_reg <= CTRL;
            spi_data <= 8'h03;
            next_state <= LOADCTL_CLEAR;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        LOADCTL_CLEAR: begin
            spi_reg <= CTRL;
            spi_data <= 8'h00;
            next_state <= NEXT_PROFILE;
            state <= SPI_WAIT;
            spi_start <= 1;
        end

        NEXT_PROFILE: begin
            if (profile_index == 7) begin
                profile_index <= 0;
                RX_PROFS_DONE <= !RX_PROFS_DONE;
                if (RX_PROFS_DONE == 1) begin
                    profile_page <= profile_page + 9'd8;
                        CTRL <= 12'h25F;
                        DATA <= 12'h25D;
                        ADDR <= 12'h25C;
                        READ <= 12'h25E;
                end else begin
                   // TX is 0x29x RX is 0x25x
                    CTRL <= 12'h29F;
                    DATA <= 12'h29D;
                    ADDR <= 12'h29C;
                    READ <= 12'h29E;
                end
            end else begin
                profile_index <= profile_index + 1;
            end
            word_index <= 0;
            if (RX_PROFS_DONE && ((profile_page + profile_index + 1'b1) >= num_profiles)) begin
                state <= IDLE;
            end else begin
                state <= BRAM_READ;
            end
        end

        SPI_WAIT: begin
            spi_start <= 0;
            if (spi_valid) begin
                state <= next_state;
                spi_start <= 0;
            end
        end
    
        default: begin
            state <= IDLE;
        end

    endcase
end
endmodule
