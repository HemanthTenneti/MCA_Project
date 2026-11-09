`default_nettype none
// Evaluation wrapper only: serial transport avoids a pin-limited test fixture.
// Shift a 131-bit request MSB first, pulse load, wait one rising edge, then
// sample serial_out before each rising edge for 69 response bits MSB first.
// Request: {taken, update_valid, query_valid, saved_next[31:0], target[31:0],
//           update_pc[31:0], query_pc[31:0]}.
// Response: {redirect_pc[31:0], flush, hit, taken_prediction, state[1:0], next_pc[31:0]}.
module timing_top #(
    parameter integer MODE = 2,
    parameter integer FIXTURE_ONLY = 0
)(
    input wire clk, input wire reset, input wire serial_in, input wire load,
    output wire serial_out
);
    reg [130:0] input_shift;
    reg [130:0] request;
    reg transaction_valid;
    reg [68:0] response;
    wire predicted_taken, btb_hit, flush;
    wire [1:0] query_state;
    wire [31:0] predicted_next_pc, redirect_pc;
    wire [68:0] result;
    generate if (FIXTURE_ONLY == 0) begin : full_design
        branch_predictor #(.MODE(MODE)) predictor (
            .clk(clk), .reset(reset), .query_valid(request[128] && transaction_valid), .query_pc(request[31:0]),
            .predicted_taken(predicted_taken), .btb_hit(btb_hit), .predicted_next_pc(predicted_next_pc), .query_state(query_state),
            .update_valid(request[129] && transaction_valid), .update_pc(request[63:32]),
            .actual_taken(request[130]), .actual_target(request[95:64])
        );
        branch_recovery recovery (
            .resolve_valid(request[129] && transaction_valid), .resolved_pc(request[63:32]),
            .actual_taken(request[130]), .actual_target(request[95:64]),
            .saved_predicted_next_pc(request[127:96]), .flush(flush), .redirect_pc(redirect_pc)
        );
        assign result = {redirect_pc, flush, btb_hit, predicted_taken, query_state, predicted_next_pc};
    end else begin : fixture_reference
        // Exercise every request bit so the reference fixture is not folded away.
        // This measures a standalone transport fixture, not exact additive overhead.
        assign result = request[68:0] ^ {7'b0, request[130:69]};
    end endgenerate
    assign serial_out = response[68];
    always @(posedge clk) begin
        if (reset) begin
            input_shift <= 0; request <= 0; transaction_valid <= 0; response <= 0;
        end else begin
            transaction_valid <= load;
            if (load) request <= input_shift;
            else input_shift <= {input_shift[129:0], serial_in};
            if (transaction_valid) response <= result;
            else response <= {response[67:0], 1'b0};
        end
    end
endmodule
`default_nettype wire
