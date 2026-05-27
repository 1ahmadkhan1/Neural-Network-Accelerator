module accelerator_tb (

);

    logic        clk;
    logic        reset;

    // CPU register interface
    avalon_mm_slave_if s1_if(clk, reset);

    // Memory master interface
    avalon_mm_master_if acc_master_if(clk, reset);

    logic        write_seen;

    // Memory map 
    localparam logic [31:0] INPUT_BASE   = 32'h0000_0000;
    localparam logic [31:0] WEIGHTS_BASE = 32'h0000_0100;
    localparam logic [31:0] BIAS_BASE    = 32'h0000_0200;

    // Accelerator register map
    localparam logic [4:0] REG_START        = 5'b00000; // start signal
    localparam logic [4:0] REG_INPUT_BASE   = 5'b00001; // base address of input vector
    localparam logic [4:0] REG_WEIGHTS_BASE = 5'b00010; // base address of weight matrix
    localparam logic [4:0] REG_BIAS_BASE    = 5'b00011; // base address of bias vector
    localparam logic [4:0] REG_INPUT_SIZE   = 5'b00100; // number of inputs per neuron
    localparam logic [4:0] REG_OUTPUT_SIZE  = 5'b00101; // number of output neurons
    localparam logic [4:0] REG_RELU_ENABLE  = 5'b00110; // ReLU enable

    localparam logic signed [15:0] expected_0 = expected_neuron(
        '{16'sh0200, 16'sh0300},    // inputs:  [2.0, 3.0]
        '{16'sh0400, 16'sh0500},    // weights: [4.0, 5.0]
        16'sh0100, 2, 1'b0          // bias=1.0, size=2, no ReLU
    );

    localparam logic signed [15:0] expected_1 = expected_neuron(
        '{16'sh0200, 16'sh0300},    // inputs:  [2.0, 3.0]
        '{16'sh0100, 16'sh0300},    // weights: [1.0, 3.0]
        16'sh0200, 2, 1'b0          // bias=2.0, size=2, no ReLU
    );

    // Instantiate the accelerator
    accelerator dut (
        .clk_clk(clk),
        .reset_reset(reset),

        .s1_address(s1_if.address),
        .s1_read(s1_if.read),
        .s1_write(s1_if.write),
        .s1_writedata(s1_if.writedata),
        .s1_byteenable(s1_if.byteenable),
        .s1_readdata(s1_if.readdata),
        .s1_waitrequest(s1_if.waitrequest),

        .acc_master_readdata(acc_master_if.readdata),
        .acc_master_waitrequest(acc_master_if.waitrequest),
        .acc_master_readdatavalid(acc_master_if.readdatavalid),
        .acc_master_address(acc_master_if.address),
        .acc_master_read(acc_master_if.read),
        .acc_master_write(acc_master_if.write),
        .acc_master_writedata(acc_master_if.writedata),
        .acc_master_byteenable(acc_master_if.byteenable)
    );
    

    // CPU model
    task automatic cpu_write (
        input logic [4:0]  address,
        input logic [31:0] data
    );

        @(negedge clk);
        s1_address   = address;
        s1_write     = 1'b1;
        s1_writedata = data;

        @(posedge clk);
        @(negedge clk);
        s1_write     = 1'b0;
    endtask

    task automatic cpu_read (
        input logic [4:0]  address,
        output logic [31:0] data
    );

        @(negedge clk);
        s1_address   = address;
        s1_read      = 1'b1;

        @(posedge clk);
        @(negedge clk);
        data         = s1_readdata;
        s1_read      = 1'b0;
    endtask

    function automatic logic signed [15:0] expected_neuron(
        input logic signed [15:0] inputs[],
        input logic signed [15:0] weights[],
        input logic signed [15:0] bias,
        input int                 size,
        input logic               relu_enable
    );
        logic signed [63:0] acc;

        // Start with bias shifted to Q16.16 — exactly like the DUT
        acc = $signed({{48{bias[15]}}, bias}) <<< 8;

        for (int j = 0; j < size; j++)
            acc = acc + ($signed(inputs[j]) * $signed(weights[j]));

        // Round and shift back to Q8.8
        if (acc >= 0)
            acc = (acc + 128) >>> 8;
        else if (relu_enable)
            return 16'sd0;
        else
            acc = -((-acc + 128) >>> 8);

        // Saturate
        if (acc > 32'sd32767)       return 16'sd32767;
        else if (acc < -32'sd32768) return -16'sd32768;
        else                        return acc[15:0];
    endfunction

    // Wait for done
    task automatic wait_done();
        logic [31:0] poll_data;
        poll_data = 32'd0;

        while (!poll_data[0]) begin
            cpu_read(5'b00000, poll_data); // Poll start signal to check if accelerator is done
        end
    endtask

    // Memory model 
    logic [7:0] memory [0:4095];    // 4KB memory byte-addressable like on chip memory

    always_ff @(posedge clk) begin
        if (reset) begin
            acc_master_readdata      <= 32'd0;
            acc_master_readdatavalid <= 1'b0;
        end
        else begin
            // Default value for memory read
            acc_master_readdatavalid <= 1'b0;

            if (acc_master_read) begin
                // Read data reads 32 bits (4 bytes) from memory, so we need to concatenate 4 bytes together
                automatic logic [31:0] address = {acc_master_address[31:2], 2'b00}; // Align address to 4 bytes
                // Aside: This made me realize the accelerator could be optimized if we saved the 32 bit input and used it in the next cycle.

                acc_master_readdata <= {memory[address + 32'd3], memory[address + 32'd2], 
                                        memory[address + 32'd1], memory[address]}; // Little-endian
                acc_master_readdatavalid <= 1'b1;
            end
        end
    end

    int write_count = 0;

    always @(negedge clk) begin
        if (acc_master_write) begin
            logic signed [15:0] expected;
            logic signed [15:0] actual;

            expected = (write_count == 0) ? expected_0 : expected_1;

            if (acc_master_byteenable === 4'b0011)
                actual = acc_master_writedata[15:0];
            else
                actual = acc_master_writedata[31:16];

            if (actual === expected)
                $display("PASS neuron %0d: got 0x%04h", write_count, actual);
            else
                $error("FAIL neuron %0d: expected 0x%04h, got 0x%04h",
                    write_count, expected, actual);

            write_count++;
        end
    end

    // Clock generation
    initial begin
        clk = 1'b0;     // Start with clock low
    end
    always begin
        #10 clk = ~clk; // 50 MHz clock
    end

    initial begin
        for (int i = 0; i < 4096; i++)
            memory[i] = 8'h00;

        // Inputs: [2.0, 3.0] shared by both neurons
        memory[INPUT_BASE + 0] = 8'h00;  memory[INPUT_BASE + 1] = 8'h02;
        memory[INPUT_BASE + 2] = 8'h00;  memory[INPUT_BASE + 3] = 8'h03;

        // Neuron 0 weights: [4.0, 5.0]
        memory[WEIGHTS_BASE + 0] = 8'h00;  memory[WEIGHTS_BASE + 1] = 8'h04;
        memory[WEIGHTS_BASE + 2] = 8'h00;  memory[WEIGHTS_BASE + 3] = 8'h05;

        // Neuron 1 weights: [1.0, 3.0]
        memory[WEIGHTS_BASE + 4] = 8'h00;  memory[WEIGHTS_BASE + 5] = 8'h01;
        memory[WEIGHTS_BASE + 6] = 8'h00;  memory[WEIGHTS_BASE + 7] = 8'h03;

        // Neuron 0 bias: 1.0
        memory[BIAS_BASE + 0] = 8'h00;  memory[BIAS_BASE + 1] = 8'h01;

        // Neuron 1 bias: 2.0
        memory[BIAS_BASE + 2] = 8'h00;  memory[BIAS_BASE + 3] = 8'h02;
    end

    initial begin
        reset = 1'b1;

        // Initialize inputs
        s1_address      = 5'b0;
        s1_read         = 1'b0;
        s1_write        = 1'b0;
        s1_writedata    = 32'b0;
        s1_byteenable   = 4'b1111;

        acc_master_waitrequest   = 1'b0;

        // Hold reset high for a 5 clock edges
        repeat (5) @(posedge clk);
        @(negedge clk); // Ensure reset is deasserted on a negedge
        reset = 1'b0;   // Release reset

        @(posedge clk); // Wait for one clock cycle

        // ------ CPU writes data ------ //

        cpu_write(REG_INPUT_BASE, INPUT_BASE);     // Base address of input vector
        cpu_write(REG_WEIGHTS_BASE, WEIGHTS_BASE); // Base address of weight matrix
        cpu_write(REG_BIAS_BASE, BIAS_BASE);       // Base address of bias vector
        cpu_write(REG_INPUT_SIZE, 32'd2);          // Number of inputs per neuron
        cpu_write(REG_OUTPUT_SIZE, 32'd2);         // Number of output neurons
        cpu_write(REG_RELU_ENABLE, 32'd0);         // ReLU disable

        // ------ Start Hardware Accelerator ------ //

        cpu_write(REG_START, 32'd1);        // Start signal
        wait_done();                        // Wait for accelerator to get done
        cpu_write(REG_START, 32'd0);
        #100;
        $stop;

    end

endmodule


