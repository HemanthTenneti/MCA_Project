`timescale 1ns/1ps
`default_nettype none
module tb_trace;
    parameter integer MODE = 0;
    reg clk = 0;
    always #5 clk = ~clk;
    reg reset = 1, query_valid = 0, update_valid = 0, actual_taken = 0;
    reg [31:0] query_pc = 0, update_pc = 0, actual_target = 0;
    wire predicted_taken, btb_hit;
    wire [31:0] predicted_next_pc;
    wire [1:0] query_state;
    reg [31:0] saved_next = 0;
    wire flush;
    wire [31:0] redirect_pc;
    branch_predictor #(.MODE(MODE)) dut (
        .clk(clk), .reset(reset), .query_valid(query_valid), .query_pc(query_pc),
        .predicted_taken(predicted_taken), .btb_hit(btb_hit), .predicted_next_pc(predicted_next_pc), .query_state(query_state),
        .update_valid(update_valid), .update_pc(update_pc), .actual_taken(actual_taken), .actual_target(actual_target)
    );
    branch_recovery recovery (.resolve_valid(update_valid), .resolved_pc(update_pc), .actual_taken(actual_taken),
        .actual_target(actual_target), .saved_predicted_next_pc(saved_next), .flush(flush), .redirect_pc(redirect_pc));
    reg [2047:0] trace_path, output_path, wave_path;
    integer input_fd, output_fd, scan, row = 0;
    reg [31:0] trace_pc, trace_target;
    integer trace_taken;
    reg saved_direction, saved_hit;
    reg [1:0] saved_state;
    initial begin
        if (!$value$plusargs("TRACE=%s", trace_path)) $fatal(1, "TRACE required");
        if (!$value$plusargs("OUTPUT=%s", output_path)) $fatal(1, "OUTPUT required");
        if ($value$plusargs("WAVE=%s", wave_path)) begin
            $dumpfile(wave_path); $dumpvars(0, tb_trace);
        end
        input_fd = $fopen(trace_path, "r"); output_fd = $fopen(output_path, "w");
        if (!input_fd || !output_fd) $fatal(1, "Cannot open trace/output");
        $fdisplay(output_fd, "row,pc,state,predicted_taken,btb_hit,predicted_next_pc,actual_next_pc,flush");
        repeat (2) @(posedge clk);
        @(negedge clk); reset = 0;
        scan = $fscanf(input_fd, "%h %d %h", trace_pc, trace_taken, trace_target);
        while (scan == 3) begin
            if (trace_taken != 0 && trace_taken != 1) $fatal(1, "Invalid outcome");
            if (trace_pc[1:0] != 0 || trace_target[1:0] != 0) $fatal(1, "Unaligned trace");
            @(negedge clk);
            query_valid = 1; query_pc = trace_pc;
            #1; saved_next = predicted_next_pc; saved_direction = predicted_taken;
            saved_hit = btb_hit; saved_state = query_state;
            @(posedge clk); // Prediction issued. No update yet.
            @(negedge clk); query_valid = 0;
            @(posedge clk); // One cycle after issue.
            @(negedge clk);
            update_valid = 1; update_pc = trace_pc; actual_taken = (trace_taken != 0); actual_target = trace_target;
            #1;
            if (flush !== (saved_next != redirect_pc)) $fatal(1, "Recovery mismatch");
            $fdisplay(output_fd, "%0d,%08h,%0d,%0d,%0d,%08h,%08h,%0d", row, trace_pc,
                saved_state, saved_direction, saved_hit, saved_next, redirect_pc, flush);
            @(posedge clk); // Resolve/update exactly two cycles after issue.
            @(negedge clk); update_valid = 0;
            row = row + 1;
            scan = $fscanf(input_fd, "%h %d %h", trace_pc, trace_taken, trace_target);
        end
        // fscanf may return 0 at trailing whitespace before reaching EOF.
        if (scan != -1 && scan != 0) $fatal(1, "Malformed trace");
        if (scan == 0 && !$feof(input_fd)) $fatal(1, "Malformed trace");
        $fclose(input_fd); $fclose(output_fd);
        $display("PASS trace mode=%0d branches=%0d", MODE, row);
        $finish;
    end
    initial begin #10000000; $fatal(1, "Watchdog timeout"); end
endmodule
`default_nettype wire
