# Deep Neural Network on an FPGA

## Creating a NIOS II System

### **What the deep neural network accelerator system consists of:**
- Nios II CPU
- 32KB on-chip **instruction memory**
- JTAG UART + debug memory slave
- **SDRAM controller**
- 7-bit output **PIO** exported as `hex`
- Phase Locked Loop (PLL) that synchronizes an output signal's frequency and phase with a reference input signal
    - `outclk0`: 50 MHz, 0 ps drives CPU and most modules
    - `outclk1`: 50 MHz, **-3000 ps** drives SDRAM clock (`sdram_clk`) to compensate board routing delay

![alt text](image.png)

## Model Training

Training is done **offline in Python** (supervised learning). After convergence, the script **exports the learned weights/biases** into a single file that the Nios II program expects.

**Outputs:**
- `trained_dnn.npz` to store multiple NumPy arrays in a single, compressed archive


