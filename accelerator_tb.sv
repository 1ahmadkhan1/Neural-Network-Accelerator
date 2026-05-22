module accelerator_tb (

);

    logic        clk;
    logic        reset;

    // CPU register interface
    logic [4:0]  s1_address;
    logic        s1_read;
    logic        s1_write;
    logic [31:0] s1_writedata;
    logic [3:0]  s1_byteenable;
    logic [31:0] s1_readdata;
    logic        s1_waitrequest;

    // Memory master interface
    logic [31:0] acc_master_readdata;
    logic        acc_master_waitrequest;
    logic        acc_master_readdatavalid;
    logic [31:0] acc_master_address;
    logic        acc_master_read;
    logic        acc_master_write;
    logic [31:0] acc_master_writedata;
    logic [3:0]  acc_master_byteenable;

    logic        write_seen;

    // Memory map 
    localparam logic [31:0] INPUT_BASE   = 32'h0000_0000;
    localparam logic [31:0] WEIGHTS_BASE = 32'h0000_0100;
    localparam logic [31:0] BIAS_BASE    = 32'h0000_0200;

    // Register map s1 interface
    // address 0x00000: start signal
    // address 0x00001: base address of input vector
    // address 0x00010: base address of weight matrix
    // address 0x00011: base address of bias vector
    // address 0x00100: number of inputs per neuron
    // address 0x00101: number of output neurons
    // address 0x00110: ReLU enable

    // Q8.8 values
    localparam logic [15:0] Q_1 = 16'h0100; // 1.0
    localparam logic [15:0] Q_2 = 16'h0200; // 2.0
    localparam logic [15:0] Q_3 = 16'h0300; // 3.0
    localparam logic [15:0] Q_4 = 16'h0400; // 4.0
    localparam logic [15:0] Q_5 = 16'h0500; // 5.0

    localparam logic [15:0] EXPECTED_OUT = 16'h1800;

    // Instantiate the accelerator
    accelerator dut (
        .clk_clk(clk),
        .reset_reset(reset),

        .s1_address(s1_address),
        .s1_read(s1_read),
        .s1_write(s1_write),
        .s1_writedata(s1_writedata),
        .s1_byteenable(s1_byteenable),
        .s1_readdata(s1_readdata),
        .s1_waitrequest(s1_waitrequest),

        .acc_master_readdata(acc_master_readdata),
        .acc_master_waitrequest(acc_master_waitrequest),
        .acc_master_readdatavalid(acc_master_readdatavalid),
        .acc_master_address(acc_master_address),
        .acc_master_read(acc_master_read),
        .acc_master_write(acc_master_write),
        .acc_master_writedata(acc_master_writedata),
        .acc_master_byteenable(acc_master_byteenable)
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

    // Memory model 
    always_ff @(posedge clk) begin
        if (reset) begin
            acc_master_readdata      <= 32'd0;
            acc_master_readdatavalid <= 1'b0;
        end
        else begin
            // Default value for memory read
            acc_master_readdatavalid <= 1'b0;

            if (acc_master_read) begin
                case(acc_master_address)
                    BIAS_BASE: begin
                        acc_master_readdata      <= {16'd0, Q_1}; // Bias = 1.0
                        acc_master_readdatavalid <= 1'b1;
                    end
                    INPUT_BASE, INPUT_BASE + 32'd2: begin
                        acc_master_readdata      <= {Q_3, Q_2};
                        acc_master_readdatavalid <= 1'b1;
                    end
                    WEIGHTS_BASE, WEIGHTS_BASE + 32'd2: begin
                        acc_master_readdata      <= {Q_5, Q_4};
                        acc_master_readdatavalid <= 1'b1;
                    end
                    default: begin
                    acc_master_readdata      <= 32'hFFFFFFFF; // Invalid data for unmapped addresses
                    acc_master_readdatavalid <= 1'b1;
                end
                endcase
            end
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
        reset = 1'b1;

        // Initialize inputs
        s1_address      = 5'b0;
        s1_read         = 1'b0;
        s1_write        = 1'b0;
        s1_writedata    = 32'b0;
        s1_byteenable   = 4'b1111;

        acc_master_waitrequest   = 1'b0;

        // Hold reset high for a 3 clock edges
        repeat (3) @(posedge clk);

        reset = 1'b0;   // Release reset

        @(posedge clk); // Wait for one clock cycle

        // ------ CPU writes data ------ //

        cpu_write(5'b00001, INPUT_BASE);   // Base address of input vector
        cpu_write(5'b00010, WEIGHTS_BASE); // Base address of weight matrix
        cpu_write(5'b00011, BIAS_BASE);    // Base address of bias vector
        cpu_write(5'b00100, 32'd2);        // Number of inputs per neuron
        cpu_write(5'b00101, 32'd1);        // Number of output neurons
        cpu_write(5'b00110, 32'd0);        // ReLU disable

        // ------ Start Hardware Accelerator ------ //

        cpu_write(5'b00000, 32'd1);        // Start signal

        write_seen = 1'b0;

        // Check on negedge so DUT outputs are stable after posedge updates
        repeat (100) begin
            @(negedge clk);

            if (acc_master_write) begin
                write_seen = 1'b1;

                if (acc_master_address !== BIAS_BASE) begin
                    $error("Wrong write address. Expected %h, got %h",
                        BIAS_BASE, acc_master_address);
                end

                if (acc_master_byteenable !== 4'b0011) begin
                    $error("Wrong byteenable. Expected 0011, got %b",
                        acc_master_byteenable);
                end

                if (acc_master_writedata[15:0] !== EXPECTED_OUT) begin
                    $error("Wrong output. Expected %h, got %h",
                        EXPECTED_OUT, acc_master_writedata[15:0]);
                end
                else begin
                    $display("PASS: output is correct. Got %h",
                            acc_master_writedata[15:0]);
                end

                $stop;
            end
        end

        if (!write_seen) begin
            $error("Timeout: accelerator never wrote an output.");
            $stop;
        end

    end





endmodule