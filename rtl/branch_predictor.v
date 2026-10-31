`default_nettype none
module branch_predictor #(
    parameter integer MODE = 2,
    parameter integer ADDR_WIDTH = 32,
    parameter integer BHT_INDEX_BITS = 6,
    parameter integer BTB_INDEX_BITS = 4
)(
    input wire clk, input wire reset,
    input wire query_valid,
    input wire [ADDR_WIDTH-1:0] query_pc,
    output wire predicted_taken,
    output wire btb_hit,
    output wire [ADDR_WIDTH-1:0] predicted_next_pc,
    output wire [1:0] query_state,
    input wire update_valid,
    input wire [ADDR_WIDTH-1:0] update_pc,
    input wire actual_taken,
    input wire [ADDR_WIDTH-1:0] actual_target
);
    wire direction, target_hit;
    wire [ADDR_WIDTH-1:0] target;
    direction_predictor #(.MODE(MODE), .ADDR_WIDTH(ADDR_WIDTH), .INDEX_BITS(BHT_INDEX_BITS)) direction_unit (
        .clk(clk), .reset(reset), .query_pc(query_pc), .predicted_taken(direction),
        .query_state(query_state), .update_valid(update_valid), .update_pc(update_pc), .actual_taken(actual_taken)
    );
    branch_target_buffer #(.ADDR_WIDTH(ADDR_WIDTH), .INDEX_BITS(BTB_INDEX_BITS)) target_unit (
        .clk(clk), .reset(reset), .query_pc(query_pc), .hit(target_hit), .predicted_target(target),
        .update_valid(update_valid && actual_taken), .update_pc(update_pc), .actual_target(actual_target)
    );
    assign predicted_taken = query_valid && direction;
    assign btb_hit = query_valid && target_hit;
    assign predicted_next_pc = (predicted_taken && btb_hit) ? target : query_pc + {{(ADDR_WIDTH-3){1'b0}}, 3'd4};
endmodule
`default_nettype wire
