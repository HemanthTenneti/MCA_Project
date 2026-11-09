`timescale 1ns/1ps
`default_nettype none
module tb_timing_top;
    parameter integer MODE = 2;
    localparam [1:0] COLD_STATE = (MODE == 2) ? 2'b01 : 2'b00;
    localparam [1:0] TRAINED_STATE = (MODE == 2) ? 2'b10 : ((MODE == 1) ? 2'b01 : 2'b00);
    reg clk = 0;
    always #5 clk = ~clk;
    reg reset = 1, serial_in = 0, load = 0;
    wire serial_out;
`ifdef GATE_LEVEL
    timing_top dut
`else
    timing_top #(.MODE(MODE)) dut
`endif
    (.clk(clk), .reset(reset), .serial_in(serial_in), .load(load), .serial_out(serial_out));
    reg [130:0] command;
    reg [68:0] result;
    integer i;
    task transact;
        input [130:0] bits;
        begin
            for (i = 130; i >= 0; i = i - 1) begin
                @(negedge clk); serial_in = bits[i]; @(posedge clk);
            end
            @(negedge clk); load = 1;
            @(posedge clk);
            @(negedge clk); load = 0;
            @(posedge clk); #1;
            for (i = 68; i >= 0; i = i - 1) begin
                @(negedge clk); result[i] = serial_out;
                @(posedge clk);
            end
        end
    endtask
    initial begin
        repeat (2) @(posedge clk);
        @(negedge clk); reset = 0;
        // First request: query old state, then train taken; flush corrects cold fallthrough.
        command = {1'b1, 1'b1, 1'b1, 32'h104, 32'h80, 32'h100, 32'h100};
        transact(command);
        if (result !== {32'h80, 1'b1, 1'b0, 1'b0, COLD_STATE, 32'h104}) $fatal(1, "wrapper cold response %h", result);
        command = {1'b0, 1'b0, 1'b1, 32'h80, 32'h80, 32'h100, 32'h100};
        transact(command);
        if (result !== {32'h104, 1'b0, 1'b1, (MODE != 0), TRAINED_STATE, ((MODE == 0) ? 32'h104 : 32'h80)}) $fatal(1, "wrapper learned response %h", result);
        // Disabled update must leave the counter at WT throughout the long serial transaction.
        transact(command);
        if (result[33:32] !== TRAINED_STATE) $fatal(1, "wrapper repeated update");
        $display("PASS timing wrapper transactions=3"); $finish;
    end
    initial begin #100000; $fatal(1, "Watchdog timeout"); end
endmodule
`default_nettype wire
