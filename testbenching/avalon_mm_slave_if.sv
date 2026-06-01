// Avalon-MM slave interface
interface avalon_mm_slave_if(input logic clk, input logic reset);
    logic [4:0]  address;
    logic        read;
    logic        write;
    logic [31:0] writedata;
    logic [3:0]  byteenable;
    logic [31:0] readdata;
    logic        waitrequest;
endinterface