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

```mermaid
%%{init: {"theme":"base","flowchart":{"nodeSpacing":90,"rankSpacing":110,"curve":"basis"},"themeVariables":{"fontSize":"22px"}}}%%
flowchart TB

  classDef node fill:#fff7d6,stroke:#111111,stroke-width:2px,color:#111111;
  classDef io   fill:#e8f3ff,stroke:#111111,stroke-width:2px,color:#111111;
  classDef bus  fill:#f2f2f2,stroke:#111111,stroke-width:2px,color:#111111;
  classDef tag  fill:#eadcff,stroke:#111111,stroke-width:2px,color:#111111;

  TD["Training Data (MNIST)"]:::io --> PY["training_dnn/<br/>train_model.py"]:::node
  PY --> P["Learned Params<br/>(weights + biases)"]:::tag
  P --> EX["export_weights.py<br/>(pack -> binary layout)"]:::node
  EX --> BIN["nn.bin"]:::tag

  BIN --> MON["FPGA Monitor Program<br/>Load file into memory"]:::bus
  MON --> SDR["SDRAM<br/>nn.bin @ 0x08000000"]:::bus

  IMG["test_xx.bin<br/>@ 0x08800000"]:::tag --> SDR

  SDR --> C["Nios II C Inference<br/>run_nn.c"]:::node
  C --> HEX["7-seg PIO<br/>(predicted digit)"]:::io

