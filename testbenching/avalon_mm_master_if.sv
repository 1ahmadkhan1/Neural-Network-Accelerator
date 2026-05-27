// Avalon-MM master interface
interface avalon_mm_master_if(input logic clk, input logic reset);
    logic [31:0] readdata;
    logic        waitrequest;
    logic        readdatavalid;
    logic [31:0] address;
    logic        read;
    logic        write;
    logic [31:0] writedata;
    logic [3:0]  byteenable;
endinterface