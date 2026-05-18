module acc (
    input  logic        clk_clk,
    input  logic        reset_reset,

    // CPU register interface
    input  logic [4:0]  s1_address,     // 32 addresses for 32 possible registers
    input  logic        s1_read,
    input  logic        s1_write,
    input  logic [31:0] s1_writedata,
    input  logic [3:0]  s1_byteenable,
    
    output logic [31:0] s1_readdata,
    output logic        s1_waitrequest,

    // Memory master interface
    input  logic [31:0] acc_master_readdata,
    input  logic        acc_master_waitrequest,
    input  logic        acc_master_readdatavalid,

    output logic [31:0] acc_master_address,
    output logic        acc_master_read,
    output logic        acc_master_write,
    output logic [31:0] acc_master_writedata,
    output logic [3:0]  acc_master_byteenable
);

    logic clk;
    logic reset;

    assign clk   = clk_clk;
    assign reset = reset_reset;

    // --------------------------------------------------- //
    //  Assigning internal registers for the accelerator   //
    // --------------------------------------------------- //

    logic        start;        // start pulse from NIOSII CPU
    logic [31:0] input_base;   // base address of input vector
    logic [31:0] weights_base; // base address of weight matrix
    logic [31:0] bias_base;    // base address of bias vector
    logic [31:0] input_size;   // number of inputs per neuron
    logic [31:0] output_size;  // number of output neurons
    logic        relu_enable;  // apply ReLU if 1
    logic        done;         // accelerator finished flag
    
	assign s1_waitrequest = 1'b0;

    always_ff @(posedge clk) begin
        if (reset) begin
            start        <= 1'b0;
            input_base   <= 32'b0;
            weights_base <= 32'b0;
            bias_base    <= 32'b0;
            input_size   <= 32'b0;
            output_size  <= 32'b0;
            relu_enable  <= 1'b0;
        end
        else if (s1_write) begin
            case(s1_address)
                5'd0: start        <= s1_writedata[0];
                5'd1: input_base   <= s1_writedata;
                5'd2: weights_base <= s1_writedata;
                5'd3: bias_base    <= s1_writedata;
                5'd4: input_size   <= s1_writedata;
                5'd5: output_size  <= s1_writedata;
                5'd6: relu_enable  <= s1_writedata[0];
                default: begin
                    // Do nothing for undefined addresses
                end
            endcase
        end
    end


    // --------------------------------------------------- //
    //             Actual Accelerator FSM                  //
    // --------------------------------------------------- //

    // Parameters for  arithmetic
    localparam signed [31:0] q_max = 32'sd32767;  // Maximum value for saturation
    localparam signed [31:0] q_min = -32'sd32768; // Minimum value for saturation
    localparam int q_fractional_bits = 8;         // Number of fractional bits in Q8.8

    // Defining local state encodings
    localparam [4:0] idle_st         = 5'b0_0000;
    localparam [4:0] outer_loop_st   = 5'b0_0001;
    localparam [4:0] read_1_st       = 5'b0_0010;
    localparam [4:0] inner_loop_st   = 5'b0_0011;
    localparam [4:0] read_2_st       = 5'b0_0100;
    localparam [4:0] read_3_st       = 5'b0_0101;
    localparam [4:0] dot_st          = 5'b0_0110;
    localparam [4:0] done_inn_st     = 5'b0_0111;
    localparam [4:0] saturate_st     = 5'b0_1000;
    localparam [4:0] write_st        = 5'b0_1001;
    localparam [4:0] write_wait_st   = 5'b0_1010;
    localparam [4:0] done_out_st     = 5'b1_1011;
    localparam [4:0] wait_start_st   = 5'b1_1100;

    assign s1_readdata = {31'b0, done}; // Return the done signal when the CPU reads from the accelerator's register interface
    assign done = state[4];             // The done_out_st is the only state with the MSB set, so we can use that bit to indicate when we're done

    logic [4:0] state = idle_st;

    // Counters for iterating through input and weight matrices
    logic [31:0] output_address;
    logic [31:0] neuron_i;
    logic [31:0] input_j;

    logic signed [15:0] bias;
    logic signed [63:0] accumulation;

    logic signed [31:0] output_temp; // Current neuron index
    logic signed [15:0] neuron_activation;

    logic signed [31:0] x;
    logic signed [31:0] w;

    always_ff @(posedge clk) begin
        if (reset) begin
            output_address <= 32'b0;
            neuron_i <= 32'b0;
            input_j <= 32'b0;
            bias <= 16'b0;
            accumulation <= 64'b0;
            output_temp <= 32'b0;
            neuron_activation <= 16'b0;
            x <= 32'b0;
            w <= 32'b0;
            state <= idle_st;
            acc_master_read <= 1'b0;
            acc_master_write <= 1'b0;
            acc_master_address <= 32'b0;
            acc_master_writedata <= 32'b0;
            acc_master_byteenable <= 4'b1111;
            output_address <= 32'b0;
        end
        else begin
            case (state)

                idle_st: begin
                    // wait for start signal
                    if (start) begin
                        state <= outer_loop_st;
                    end else begin
                        state <= idle_st;
                        output_address <= 32'b0;
                        neuron_i <= 32'b0;
                        input_j <= 32'b0;
                        bias <= 16'b0;
                        accumulation <= 64'b0;
                        output_temp <= 32'b0;
                        neuron_activation <= 16'b0;
                        x <= 32'b0;
                        w <= 32'b0;
                        state <= idle_st;
                        acc_master_read <= 1'b0;
                        acc_master_write <= 1'b0;
                        acc_master_address <= 32'b0;
                        acc_master_writedata <= 32'b0;
                        acc_master_byteenable <= 4'b1111;
                        output_address <= 32'b0;
                        
                    end 
                end

                outer_loop_st: begin
                    if (neuron_i == output_size) begin
                        state <= done_out_st;
                    end else begin
                        state <= read_1_st;

                        // Read Q8.8 value 
                        acc_master_read <= 1'b1;
                        acc_master_address <= bias_base + (neuron_i << 1); // Each bias is 2 bytes
                    end
                end

                read_1_st: begin
                                        
                    if (acc_master_waitrequest) begin
                        acc_master_read <= 1'b1;   // keep request alive
                    end else begin
                        acc_master_read <= 1'b0;   // request accepted, now wait for data
                    end
                    
                    if(acc_master_readdatavalid) begin
                        // Capture the correct bias value for the current neuron
                        // Accumulation is the sign-extended bias to 64 bits and arithmatic left shift to convert Q16.16 format
                        if (acc_master_address[1] == 1'b0) begin
                            bias <= acc_master_readdata[15:0];
                            accumulation <= $signed({{48{acc_master_readdata[15]}}, acc_master_readdata[15:0]}) <<< q_fractional_bits;
                        end else begin
                            bias <= acc_master_readdata[31:16];
                            accumulation <= $signed({{48{acc_master_readdata[31]}}, acc_master_readdata[31:16]}) <<< q_fractional_bits;
                        end
                        state <= inner_loop_st;
                        output_address <= acc_master_address; // Store the bias base address for the output of the current neuron
                    end
                end

                inner_loop_st: begin
                    if (input_j == input_size) begin
                        state <= done_inn_st;
                    end else begin
                        state <= read_2_st;

                        // Read input value
                        acc_master_read <= 1'b1;
                        acc_master_address <= input_base + (input_j << 1); // Each input is 2 bytes
                    end
                end

                read_2_st: begin
                                        
                    if (acc_master_waitrequest) begin
                        acc_master_read <= 1'b1;   // keep request alive
                    end else begin
                        acc_master_read <= 1'b0;   // request accepted, now wait for data
                    end

                    if (acc_master_readdatavalid) begin
                        // Capture the correct input value
                        if (acc_master_address[1] == 1'b0) begin
                            x <= $signed(acc_master_readdata[15:0]);
                        end else begin
                            x <= $signed(acc_master_readdata[31:16]);
                        end

                        state <= read_3_st;

                        // Read weight value for current neuron and input
                        acc_master_read <= 1'b1;
                        acc_master_address <= weights_base + ((neuron_i * input_size + input_j) << 1); // Each weight is 2 bytes
                    end
                end

                read_3_st: begin

                    if (acc_master_waitrequest) begin
                        acc_master_read <= 1'b1;   // keep request alive
                    end else begin
                        acc_master_read <= 1'b0;   // request accepted, now wait for data
                    end

                    if (acc_master_readdatavalid) begin
                        // Capture the correct weight value
                        if (acc_master_address[1] == 1'b0) begin
                            w <= $signed(acc_master_readdata[15:0]);
                        end else begin
                            w <= $signed(acc_master_readdata[31:16]);
                        end

                        state <= dot_st;
                    end
                end

                dot_st: begin
                    acc_master_read <= 1'b0; // Deassert read signal
                    // Perform multiplication and accumulate the result
                    accumulation <= accumulation + (x * w);

                    // Move to the next input
                    input_j <= input_j + 1;
                    state <= inner_loop_st;
                end

                done_inn_st: begin
                    // Round and shift to return to Q8.8 scale
                    if (accumulation >= 0) begin
                        output_temp <= (accumulation + (64'sd1 <<< (q_fractional_bits - 1))) >>> q_fractional_bits; // Add 0.5 for rounding and shift
                    end else if (accumulation < 0 && relu_enable) begin
                        output_temp <= 32'sd0; // ReLU clamps negative values to 0
                    end else begin
                        output_temp <= -((-accumulation + (64'sd1 <<< (q_fractional_bits - 1))) >>> q_fractional_bits); // Add 0.5 for rounding and shift then negate again
                    end
                    state <= saturate_st;
                end

                saturate_st: begin
                    // Saturate neuron activation so it fits within our range
                    if (output_temp > q_max) begin
                        neuron_activation <= 16'sd32767;
                    end else if (output_temp < q_min) begin
                        neuron_activation <= -16'sd32768; // Saturate to minimum value
                    end else begin
                        neuron_activation <= output_temp;
                    end

                    // Get ready to write the output value back to memory
                    state <= write_st;
                    acc_master_address <= output_address; // Write to the same address as the bias for the current neuron
                end

                write_st: begin
                    // Write the neuron activation value back to memory so it can be used as input for the next layer
                    if(acc_master_address[1] == 1'b0) begin
                        acc_master_writedata <= {16'b0, neuron_activation}; // Write to lower half of the word
                        acc_master_byteenable <= 4'b0011;                   // Enable writing to lower half
                    end else begin
                        acc_master_writedata <= {neuron_activation, 16'b0}; // Write to upper half of the word
                        acc_master_byteenable <= 4'b1100;                   // Enable writing to upper half
                    end
                    acc_master_write <= 1'b1;
                    state <= write_wait_st;
                end

                write_wait_st: begin
                    // Wait for the write to complete before moving on to the next neuron
                    if (!acc_master_waitrequest) begin
                        acc_master_write <= 1'b0;       // Deassert write signal
                        state <= outer_loop_st;         // Move on to the next neuron
                        neuron_i <= neuron_i + 1;
                        input_j <= 32'b0;                // Reset input counter for the next neuron
                    end 
                end

                done_out_st: begin
                    state <= wait_start_st;
                end

                wait_start_st: begin
                    if (~start) state <= idle_st;
                end

                default: begin
                    state <= idle_st;
                end
            endcase
        end

    end


endmodule