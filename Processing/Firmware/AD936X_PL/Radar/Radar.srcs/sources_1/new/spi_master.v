`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Levi Farinas
// 
// Create Date: 08/20/2026 03:29:40 PM
// Design Name: 
// Module Name: spi_master
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


module spi_master (
    input wire clk,
    input wire reset,
    input wire start,
    input wire [23:0] tx_data,
    output reg [23:0] rx_data,
    output reg busy,
    output reg done,
    output reg sclk,
    output reg mosi,
    input wire miso,
    output reg cs_n
);

reg [23:0] tx_shift;
reg [23:0] rx_shift;
reg [4:0] bit_count;
reg [7:0] divider;

always @(posedge clk) begin
    if (reset) begin
        sclk <= 0;
        cs_n <= 1;
        mosi <= 0;
        busy <= 0;
        done <= 0;
        divider <= 0;
        bit_count <= 0;
    end else begin
        done <= 0;

        if (start && !busy) begin
            busy <= 1;
            cs_n <= 0;
            tx_shift <= tx_data;
            rx_shift <= 0;
            bit_count <= 23;
            mosi <= tx_data[23];
            divider <= 0;
        end else if (busy) begin
            if (divider == 0) begin
            // 0 for 50MHz SPI
            // 4 for 10MHz SPI
                divider <= 0;

                if (!sclk) begin
                    sclk <= 1;
                    rx_shift <= {rx_shift[22:0], miso};
                end else begin
                    sclk <= 0;

                    if (bit_count == 0) begin
                        cs_n <= 1;
                        busy <= 0;
                        done <= 1;
                        rx_data <= rx_shift; //{rx_shift[6:0], miso};
                    end else begin
                        bit_count <= bit_count - 1;
                        tx_shift <= {tx_shift[22:0], 1'b0};
                        mosi <= tx_shift[22];
                    end
                end
            end else begin
                divider <= divider + 1;
            end
        end
    end
end

endmodule
