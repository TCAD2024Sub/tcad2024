

module top_level_synth
(
  input clk,
  input rst,
  output out
);

  localparam width = 8;
  localparam depth = 4;
  reg [depth-1:0] rd_addr0;
  reg [depth-1:0] rd_addr1;
  wire [8-1:0] mem_2r_1w_out0;
  wire [8-1:0] mem_2r_1w_out1;
  reg wr;
  reg [depth-1:0] wr_addr;
  reg [width-1:0] wr_data;
  wire [8-1:0] data;

  mem_2r_1w
  #(
    .width(width),
    .depth(depth)
  )
  mem_2r_1w
  (
    .clk(clk),
    .rd_addr0(rd_addr0),
    .rd_addr1(rd_addr1),
    .out0(mem_2r_1w_out0),
    .out1(mem_2r_1w_out1),
    .wr(wr),
    .wr_addr(wr_addr),
    .wr_data(wr_data)
  );


  always @(posedge clk) begin
    if(rst) begin
      rd_addr0 <= 0;
      rd_addr1 <= 0;
      wr <= 0;
      wr_addr <= 0;
      wr_data <= 0;
    end else begin
      rd_addr0 <= rd_addr0 + 1;
      rd_addr1 <= rd_addr1 + 1;
      wr <= wr + 1;
      wr_addr <= wr_addr + 1;
      wr_data <= wr_data + 1;
    end
  end

  assign data = mem_2r_1w_out0|mem_2r_1w_out1;
  assign out = ^data;

  initial begin
    rd_addr0 = 0;
    rd_addr1 = 0;
    wr = 0;
    wr_addr = 0;
    wr_data = 0;
  end


endmodule



module mem_2r_1w #
(
  parameter width = 8,
  parameter depth = 4
)
(
  input clk,
  input [depth-1:0] rd_addr0,
  input [depth-1:0] rd_addr1,
  output [8-1:0] out0,
  output [8-1:0] out1,
  input wr,
  input [depth-1:0] wr_addr,
  input [width-1:0] wr_data
);

  reg [width-1:0] mem [0:2**depth-1];
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end



endmodule


