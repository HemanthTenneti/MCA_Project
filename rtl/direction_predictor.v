`default_nettype none
// MODE: 0=always not taken, 1=last outcome, 2=two-bit saturating counter.
module direction_predictor #(
    parameter integer MODE = 2,
    parameter integer ADDR_WIDTH = 32,
    parameter integer INDEX_BITS = 6
)(
    input wire clk, input wire reset,
    input wire [ADDR_WIDTH-1:0] query_pc,
    output wire predicted_taken,
    output wire [1:0] query_state,
    input wire update_valid,
    input wire [ADDR_WIDTH-1:0] update_pc,
    input wire actual_taken
);
    generate
        if (MODE == 0) begin : baseline
            assign predicted_taken = 1'b0;
            assign query_state = 2'b00;
        end else begin : dynamic_table
            localparam integer ENTRIES = 2 ** INDEX_BITS;
            localparam integer STATE_BITS = (MODE == 1) ? 1 : 2;
            reg [STATE_BITS-1:0] history [0:ENTRIES-1];
            wire [INDEX_BITS-1:0] read_index = query_pc[INDEX_BITS+1:2];
            wire [INDEX_BITS-1:0] write_index = update_pc[INDEX_BITS+1:2];
            integer i;
            if (MODE == 1) begin : one_bit
                assign predicted_taken = history[read_index][0];
                assign query_state = {1'b0, history[read_index][0]};
                always @(posedge clk) begin
                    if (reset) begin
                        for (i = 0; i < ENTRIES; i = i + 1) history[i] <= 1'b0;
                    end else if (update_valid) history[write_index] <= actual_taken;
                end
            end else begin : two_bit
                assign predicted_taken = history[read_index][1];
                assign query_state = history[read_index];
                always @(posedge clk) begin
                    if (reset) begin
                        for (i = 0; i < ENTRIES; i = i + 1) history[i] <= 2'b01;
                    end else if (update_valid) begin
                        if (actual_taken && history[write_index] != 2'b11)
                            history[write_index] <= history[write_index] + 1'b1;
                        else if (!actual_taken && history[write_index] != 2'b00)
                            history[write_index] <= history[write_index] - 1'b1;
                    end
                end
            end
        end
    endgenerate
endmodule
`default_nettype wire
