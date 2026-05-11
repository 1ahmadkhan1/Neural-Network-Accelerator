# Deep Neural Network Accelerator on an FPGA

## Contents
- [Objectives](#objectives)
- [Model Training](#model-training)
- [How the weights and biases were loaded onto memory](#how-the-weights-and-biases-were-loaded-onto-memory)


## Objectives
- Train a neural network to identify numbers from the MNIST dataset
- Use the weights and biases that were accurately generated to run the model on the softcore of the FPGA
- Create a module that accelerates the calculation of the dotproduct needed for forward propogation
- Calculate the speedup of using the FPGA


## Model Training

Supervised learning is done **offline in Python**. This allows us to run the forward propogation on the FPGA without needing to adjust the weights of the neural network. The  Multilayer Perceptron (MLP) consists of the 784 pixel input layer, two 16 neuron hidden layers and one 10 neuron output layer. The activation of the output layers indicate the relative confidence for each class (i.e tells us what number the model predicts).

<img width="1496" height="1346" alt="image" src="https://github.com/user-attachments/assets/eb38a49a-c6e2-4dcb-938b-f37e3e4b6557" />

*Image from [3blue1brown](https://www.3blue1brown.com/?v=neural-networks) and this is the exact neural network we trained*

## How the weights and biases were loaded onto memory
#### Q8.8 format
After training, the learned weights and biases were originally stored as 32-bit floating-point values. Before loading them into FPGA memory, they were converted into **signed Q8.8 fixed-point format**.

<img width="1082" height="224" alt="image" src="https://github.com/user-attachments/assets/f41e6e0b-32ff-452d-b36b-f30acbcec0ef" />
<br>
This format gives:

- enough precision [-128.0 , +127.99609375] for neural network weights and biases
- simple hardware implementation
- compact 16-bit storage
- faster multiply-and-accumulate operations
- easier loading into FPGA memory using `.mif` files

#### .MIF Files

#### The complete conversion process:


## Issues
- Originally, the Q2.14 representation did not provide a sufficient range for the hidden-layer activations. As a result, many activation values were clipped, which reduced the model’s accuracy to around 45%. To fix this, all data was rescaled and converted to Q8.8, which gave a larger dynamic range and prevented the overflow issue.
- Intel Hex file issue




