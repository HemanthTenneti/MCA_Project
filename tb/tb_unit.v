`timescale 1ns/1ps
`default_nettype none
module tb_unit;
    reg clk = 0;
    always #5 clk = ~clk;
    reg reset = 1, query_valid = 1, update_valid = 0, actual_taken = 0;
    reg [31:0] query_pc = 32'h100, update_pc = 32'h100, actual_target = 32'h80;
    wire [2:0] prediction, hit;
    wire [31:0] next_pc [0:2];
    wire [1:0] state [0:2];
    genvar m;
    generate for (m = 0; m < 3; m = m + 1) begin : modes
        branch_predictor #(.MODE(m)) dut (
            .clk(clk), .reset(reset), .query_valid(query_valid), .query_pc(query_pc),
            .predicted_taken(prediction[m]), .btb_hit(hit[m]), .predicted_next_pc(next_pc[m]), .query_state(state[m]),
            .update_valid(update_valid), .update_pc(update_pc), .actual_taken(actual_taken), .actual_target(actual_target)
        );
    end endgenerate
    reg resolve_valid = 0, resolved_taken = 0;
    reg [31:0] resolved_pc = 32'h100, resolved_target = 32'h80, saved_next = 32'h104;
    wire flush;
    wire [31:0] redirect;
    branch_recovery recovery (.resolve_valid(resolve_valid), .resolved_pc(resolved_pc), .actual_taken(resolved_taken),
        .actual_target(resolved_target), .saved_predicted_next_pc(saved_next), .flush(flush), .redirect_pc(redirect));
    integer checks = 0, s, outcome, n, expected;
    task check;
        input condition;
        input [8*100-1:0] message;
        begin
            checks = checks + 1;
            if (condition !== 1'b1) $fatal(1, "FAIL: %0s", message);
        end
    endtask
    task clear;
        begin
            @(negedge clk); reset = 1; update_valid = 0; query_valid = 1; query_pc = 32'h100;
            @(posedge clk); #1;
            check(state[0] === 0 && state[1] === 0 && state[2] === 1, "reset states");
            check(hit === 0, "reset invalidates BTB");
            @(negedge clk); reset = 0;
        end
    endtask
    task train;
        input [31:0] pc;
        input taken;
        input [31:0] target;
        begin
            @(negedge clk); update_valid = 1; update_pc = pc; actual_taken = taken; actual_target = target;
            @(posedge clk); #1;
            @(negedge clk); update_valid = 0;
        end
    endtask
    initial begin
        $dumpfile("reports/waveforms/unit.vcd"); $dumpvars(0, tb_unit);
        clear;
        check(next_pc[0] === 32'h104 && next_pc[1] === 32'h104 && next_pc[2] === 32'h104, "cold fallthrough has no X");
        // Each state/outcome pair, including both saturation boundaries.
        for (s = 0; s < 4; s = s + 1) begin
            for (outcome = 0; outcome < 2; outcome = outcome + 1) begin
                clear;
                train(32'h100, 0, 32'h80); // WNT -> SNT
                for (n = 0; n < s; n = n + 1) train(32'h100, 1, 32'h80);
                #1; check(state[2] === s[1:0], "prepare two-bit state");
                @(negedge clk); update_valid = 1; update_pc = 32'h100; actual_taken = (outcome != 0);
                #1; check(state[2] === s[1:0], "prediction uses state before clocked update");
                @(posedge clk); #1;
                expected = outcome ? ((s == 3) ? 3 : s + 1) : ((s == 0) ? 0 : s - 1);
                check(state[2] === expected[1:0], "two-bit transition/saturation");
                check(prediction[2] === (expected >= 2), "two-bit MSB prediction");
                check(prediction[1] === (outcome != 0), "one-bit remembers last outcome");
                check(prediction[0] === 0 && next_pc[0] === 32'h104, "baseline never predicts taken");
                @(negedge clk); update_valid = 0;
            end
        end
        clear;
        @(negedge clk); update_pc = 32'h100; actual_taken = 1; actual_target = 32'h80;
        repeat (2) @(posedge clk);
        #1; check(state[2] === 1 && state[1] === 0 && hit === 0, "disabled update changes no state or BTB");
        train(32'h100, 1, 32'h80);
        #1; check(hit === 3'b111 && next_pc[1] === 32'h80 && next_pc[2] === 32'h80, "taken update trains target and direction");
        query_valid = 0; #1;
        check(prediction === 0 && hit === 0 && next_pc[2] === 32'h104, "invalid query falls through");
        query_valid = 1;
        // BTB alias without BHT alias: +64 bytes.
        train(32'h140, 1, 32'hc0);
        #1; check(hit === 0 && next_pc[2] === 32'h104 && prediction[2] === 1, "BTB tag mismatch blocks stale target");
        query_pc = 32'h140; #1;
        check(hit === 3'b111 && next_pc[2] === 32'hc0, "update indexed by resolved PC, not query PC");
        train(32'h140, 0, 32'hdead0000);
        #1; check(hit === 3'b111, "not-taken update retains target");
        train(32'h140, 1, 32'hc0);
        #1; check(next_pc[2] === 32'hc0, "not-taken update did not overwrite stored target");
        // BHT alias: +256 bytes. Opposite outcomes interfere by design.
        clear; train(32'h100, 1, 32'h80); train(32'h200, 0, 32'h180);
        #1; check(state[2] === 1 && prediction[1] === 0, "BHT alias shares counter");
        query_pc = 32'h104; #1; check(state[2] === 1 && state[1] === 0, "word address indexing isolates adjacent branch");
        // Existing prediction must survive target/state changes until recovery.
        clear; train(32'h100, 1, 32'h80);
        #1; saved_next = next_pc[2];
        train(32'h100, 1, 32'h90);
        resolve_valid = 1; resolved_taken = 1; resolved_target = 32'h90; #1;
        check(saved_next === 32'h80 && flush === 1 && redirect === 32'h90, "changed target detects saved next-PC mismatch");
        saved_next = 32'h90; #1; check(flush === 0, "correct taken prediction needs no flush");
        resolved_taken = 0; #1; check(flush === 1 && redirect === 32'h104, "not-taken recovery");
        saved_next = 32'h104; #1; check(flush === 0, "correct fallthrough needs no flush");
        resolved_taken = 1; resolved_target = 32'h104; #1;
        check(flush === 0, "direction mismatch with identical next address needs no recovery");
        resolve_valid = 0; saved_next = 0; #1; check(flush === 0, "invalid resolution cannot flush");
        // Reset takes priority over simultaneous update and clears trained state.
        @(negedge clk); reset = 1; update_valid = 1; actual_taken = 1;
        @(posedge clk); #1;
        query_pc = 32'h100; #1;
        check(state[2] === 1 && state[1] === 0 && hit === 0, "reset wins over update");
        // 32-bit sequential address wraparound.
        query_valid = 0; query_pc = 32'hfffffffc; #1;
        check(next_pc[0] === 0 && next_pc[2] === 0, "PC + 4 wraps at address width");
        $display("PASS unit checks=%0d", checks); $finish;
    end
    initial begin #100000; $fatal(1, "Watchdog timeout"); end
endmodule
`default_nettype wire
