`default_nettype none
module branch_recovery #(
    parameter integer ADDR_WIDTH = 32
)(
    input wire resolve_valid,
    input wire [ADDR_WIDTH-1:0] resolved_pc,
    input wire actual_taken,
    input wire [ADDR_WIDTH-1:0] actual_target,
    input wire [ADDR_WIDTH-1:0] saved_predicted_next_pc,
    output wire flush,
    output wire [ADDR_WIDTH-1:0] redirect_pc
);
    assign redirect_pc = actual_taken ? actual_target : resolved_pc + {{(ADDR_WIDTH-3){1'b0}}, 3'd4};
    assign flush = resolve_valid && (saved_predicted_next_pc != redirect_pc);
endmodule
`default_nettype wire
