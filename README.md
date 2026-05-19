# Deep Neural Network Accelerator on an FPGA

## Contents
- [Objectives](#objectives)
- [Model Training](#model-training)
- [Math Used During Inference](#math-used-during-inference)
- [Accelerator Accuracy](#accelerator-accuracy)
- [Accelerator FSM](#accelerator-fsm)
- [How the weights and biases were loaded onto memory](#how-the-weights-and-biases-were-loaded-onto-memory)
- [Issues](#issues)


## Objectives
- Train a compact neural network that classifies handwritten MNIST digits
- Convert the trained floating-point weights and biases into signed Q8.8 fixed-point data for FPGA memory
- Design a custom hardware accelerator that performs dense-layer multiply-accumulate and optional ReLU for Nios II inference
- Run end-to-end inference on the FPGA-oriented datapath while keeping high classification accuracy


## Model Training

Supervised learning is done **offline in Python**. This lets the FPGA focus only on inference, while training and weight updates happen on the computer first.

The trained Multilayer Perceptron (MLP) has:
- an input layer of 784 pixels
- a first hidden layer of 16 neurons with ReLU
- a second hidden layer of 16 neurons with ReLU
- an output layer of 10 logits, one for each digit from 0 to 9

The output layer does **not** apply ReLU. Instead, the predicted digit is the index of the largest output value.

<img width="1496" height="1346" alt="image" src="https://github.com/user-attachments/assets/eb38a49a-c6e2-4dcb-938b-f37e3e4b6557" />

*Image from [3blue1brown](https://www.3blue1brown.com/?v=neural-networks). This is the same network shape used in this project.*


## Math Used During Inference

For an input image `x` with 784 normalized pixel values, the network computes:

```text
h^(1) = ReLU(W1 x + b1)    where W1 is 16 x 784 and b1 is length 16
h^(2) = ReLU(W2 h^(1) + b2) where W2 is 16 x 16  and b2 is length 16
z      = W3 h^(2) + b3      where W3 is 10 x 16  and b3 is length 10
prediction = argmax(z)
```

For one neuron, the accelerator is really computing the same dense-layer equation over and over:

```text
a_i = b_i + sum(x_j * w_i,j)   for j = 0 to N - 1
```

Then:
- if the layer is a hidden layer, `ReLU(a_i) = max(0, a_i)` is applied
- if the layer is the output layer, the value is left unchanged and treated as a logit

### Fixed-point math used in hardware

The FPGA does not store weights and activations as floating-point values. Everything is converted to **signed Q8.8 fixed-point**:

```text
fixed_value = round(real_value * 2^8) = round(real_value * 256)
real_value  ~= fixed_value / 256
```

This means:
- 8 integer bits are used, including the sign bit
- 8 fractional bits are used
- each value is stored in 16 bits
- the representable range is about `-128.0` to `+127.996`

### What happens during one multiply-accumulate

The accelerator works on one output neuron at a time.

1. The bias starts the accumulator:

```text
acc = bias << 8
```

`bias` is Q8.8, so shifting left by 8 turns it into Q16.16.

2. For each input element:

```text
acc = acc + (x * w)
```

Since `x` and `w` are both Q8.8, their product is Q16.16, which matches the accumulator scale.

3. After the full dot product is complete, the accumulator is rounded back to Q8.8:

```text
if acc >= 0:
    out = (acc + 128) >> 8
else:
    out = -(((-acc) + 128) >> 8)
```

4. ReLU is optionally applied:

```text
if relu_enable and out < 0:
    out = 0
```

5. The result is saturated so it still fits in signed 16-bit Q8.8:

```text
out = clamp(out, -32768, 32767)
```

### Layer-by-layer flow in this design

- Layer 1 computes `h^(1)` from the 784 input pixels
- Layer 2 computes `h^(2)` from the 16 outputs of layer 1
- Layer 3 computes the 10 output logits from the 16 outputs of layer 2
- The predicted digit is the index of the largest logit

The software runs the accelerator once per layer. After each run, the new activations are written back into memory and reused as the next layer's input.

#### Visual summary

<img width="2053" height="1320" alt="Math summary 1" src="https://github.com/user-attachments/assets/59530c0c-7d91-4026-9b9e-cd0a573eba09" />
<img width="2046" height="876" alt="Math summary 2" src="https://github.com/user-attachments/assets/3eeb0753-8d90-4566-9ae1-c5d6b922d07c" />


## Accelerator Accuracy

Using the exported Q8.8 weights and biases together with the same fixed-point layer math used by the accelerator, the design correctly classified **9527 out of 10000** MNIST test images:

```text
Accuracy = 9527 / 10000 = 95.27%
```

This means the fixed-point accelerator path preserves almost all of the trained model's performance. The floating-point training log reached **95.31%** validation accuracy, so the Q8.8 implementation is only **0.04 percentage points lower**.


## Accelerator FSM

The custom accelerator is controlled by a finite-state machine (FSM) in [accelerator.sv](./accelerator.sv). Each accelerator run computes **one full dense layer**. Software provides:

- `start`
- `input_base`
- `weights_base`
- `bias_base`
- `input_size`
- `output_size`
- `relu_enable`

The FSM then walks through the input vector, weight matrix, and bias vector to produce every output neuron.

### Every state and what it does

| State | What it does |
| --- | --- |
| `idle_st` | Waits for `start = 1`. While idle, it clears counters, accumulator registers, and Avalon master control signals so a new layer can begin from a clean state. |
| `outer_loop_st` | Controls the outer loop over output neurons. If `neuron_i == output_size`, the whole layer is finished. Otherwise, it starts a memory read for the current neuron's bias. |
| `read_1_st` | Waits for the bias read to complete. When `acc_master_readdatavalid` arrives, it extracts the correct 16-bit bias, sign-extends it, and initializes `accumulation = bias << 8` so the accumulator is in Q16.16 format. It also stores the address that will later be used for writeback. |
| `inner_loop_st` | Controls the inner loop over the current neuron's inputs. If `input_j == input_size`, the dot product for this neuron is finished. Otherwise, it starts a memory read for the next input value. |
| `read_2_st` | Waits for the input read to complete. Once the input word returns, it captures `x` and immediately starts the read for the matching weight `w(neuron_i, input_j)`. |
| `read_3_st` | Waits for the weight read to complete. Once the weight is available, it captures `w` and moves to the arithmetic state. |
| `dot_st` | Performs one multiply-accumulate step: `accumulation <= accumulation + x * w`. Then it increments `input_j` and loops back to `inner_loop_st`. |
| `done_inn_st` | Finishes the current neuron. It rounds the Q16.16 accumulator back to Q8.8, and if `relu_enable = 1`, it clamps negative values to zero. |
| `saturate_st` | Saturates the rounded result into the legal Q8.8 range `[-32768, 32767]` and stores it in `neuron_activation`. It also prepares the address used for memory writeback. |
| `write_st` | Packs the 16-bit activation into either the lower half or upper half of the 32-bit Avalon write bus and sets `byteenable` so only the correct halfword is written. |
| `write_wait_st` | Waits until the write is accepted by memory. Then it deasserts `acc_master_write`, increments `neuron_i`, resets `input_j`, and returns to `outer_loop_st` for the next neuron. |
| `done_out_st` | Indicates that all output neurons for the current layer are complete. This is the completion state reached after the outer loop finishes. |
| `wait_start_st` | Holds the FSM in a safe completed state until software lowers `start` back to `0`. This prevents the accelerator from immediately retriggering on the same start pulse. |

### FSM flow in words

The control flow is:

```text
idle
  -> read current bias
  -> for each input:
       read input
       read weight
       multiply and accumulate
  -> round / optional ReLU / saturate
  -> write output activation
  -> repeat for next neuron
  -> signal done
  -> wait for start to go low
  -> return to idle
```

<p align="center">
<img width="894" height="1072" alt="Accelerator FSM" src="https://github.com/user-attachments/assets/65179474-a174-4489-9655-73c2b9fc7d9d" />
</p>

### Why the FSM is structured this way

- The accelerator reuses a single multiply-accumulate datapath instead of building many multipliers in parallel
- Bias, input, and weight values are streamed from memory only when needed
- The same FSM works for all three network layers because the CPU only changes the base addresses, sizes, and the `relu_enable` flag
- Hidden layers run with ReLU enabled, and the final output layer runs with ReLU disabled


## How the weights and biases were loaded onto memory

#### Q8.8 format

After training, the learned weights and biases were originally stored as 32-bit floating-point values. Before loading them into FPGA memory, they were converted into **signed Q8.8 fixed-point format**.

<img width="1082" height="224" alt="image" src="https://github.com/user-attachments/assets/f41e6e0b-32ff-452d-b36b-f30acbcec0ef" />
<br>

This format gives:
- enough precision and dynamic range for weights, biases, and neuron activations
- simple hardware implementation
- compact 16-bit storage
- faster multiply-and-accumulate operations
- easier loading into FPGA memory using `.mif` files


#### The complete conversion process

<img width="1164" height="328" alt="image" src="https://github.com/user-attachments/assets/61890873-5001-470a-b94a-e93b0aa6cf07" />


## Issues

- Originally, the `Q2.14` representation did not provide a sufficient range for hidden-layer activations. Many values were clipped, which reduced the model's accuracy to around 45%. The project was then rescaled to Q8.8 after measuring activation ranges across the dataset and adding extra margin.
- The generated `.hex` files were initially written in Intel HEX format, which is byte-addressed and includes record metadata such as byte count, address, record type, and checksum. Quartus on-chip memories were configured as 16-bit word-addressed memories, so the files were interpreted incorrectly and caused wrapping, truncation, and corrupted initialized contents.
- During debugging, the Python `verify_inference.py` script and the Nios II inference code produced different logits for the same input image. This showed that the problem was not only the neural network math, but also how the fixed-point data was being loaded into FPGA memory.
