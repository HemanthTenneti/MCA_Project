`default_nettype none
module branch_target_buffer #(
    parameter integer ADDR_WIDTH = 32,
    parameter integer INDEX_BITS = 4
)(
    input wire clk, input wire reset,
    input wire [ADDR_WIDTH-1:0] query_pc,
    output wire hit,
    output wire [ADDR_WIDTH-1:0] predicted_target,
    input wire update_valid,
    input wire [ADDR_WIDTH-1:0] update_pc,
    input wire [ADDR_WIDTH-1:0] actual_target
);
    localparam integer ENTRIES = 2 ** INDEX_BITS;
    localparam integer TAG_BITS = ADDR_WIDTH - INDEX_BITS - 2;
    reg [ENTRIES-1:0] valid;
    reg [TAG_BITS-1:0] tags [0:ENTRIES-1];
    reg [ADDR_WIDTH-1:0] targets [0:ENTRIES-1];
    wire [INDEX_BITS-1:0] read_index = query_pc[INDEX_BITS+1:2];
    wire [INDEX_BITS-1:0] write_index = update_pc[INDEX_BITS+1:2];
    assign hit = valid[read_index] && (tags[read_index] == query_pc[ADDR_WIDTH-1:INDEX_BITS+2]);
    assign predicted_target = hit ? targets[read_index] : {ADDR_WIDTH{1'b0}};
    // Invalid entries hide uninitialized data; only valid bits require reset.
    always @(posedge clk) begin
        if (reset) valid <= {ENTRIES{1'b0}};
        else if (update_valid) begin
            valid[write_index] <= 1'b1;
            tags[write_index] <= update_pc[ADDR_WIDTH-1:INDEX_BITS+2];
            targets[write_index] <= actual_target;
        end
    end
endmodule
`default_nettype wire
