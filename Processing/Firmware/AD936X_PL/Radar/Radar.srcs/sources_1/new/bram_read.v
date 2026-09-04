`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Levi Farinas
// 
// Create Date: 08/28/2026 07:25:33 PM
// Design Name: 
// Module Name: bram_read
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



module bram_read(
    input wire clk,
    input wire enable,
    input wire [8:0] profile_index,
    input wire [3:0] word_index,
    
    
    (* X_INTERFACE_IGNORE = "true" *)
    input wire [31:0] bram_data,
    output reg [15:0] profile_word,
    
    (* X_INTERFACE_IGNORE = "true" *)
    output reg [31:0] addr,
    output reg busy,
    output reg valid,
    output reg bram_rst
);

reg [2:0] delay_count = 0;

always @(posedge clk) begin
    valid <= 0;
    bram_rst <= 1;
    if (enable && !busy) begin
        addr <= {profile_index, word_index};
        delay_count <= 0;
        busy <= 1;
    end else if (busy) begin
        if (delay_count == 3) begin
        // Waits for 4 clock cycles before data is valid
            profile_word <= bram_data[15:0];
            busy <= 0;
            valid <= 1;
        end else begin
            delay_count <= delay_count + 1;
        end
    end
end

initial begin
    addr = 0;
    busy = 0;
    valid = 0;
    profile_word = 0;
end

endmodule




