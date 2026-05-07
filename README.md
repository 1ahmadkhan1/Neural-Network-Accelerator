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
#### Q2.14 format
After training, the learned weights and biases were originally stored as 32-bit floating-point values. Before loading them into FPGA memory, they were converted into **signed Q2.14 fixed-point format**.

<img width="1172" height="205" alt="image" src="https://github.com/user-attachments/assets/7e803951-87ee-47df-b95e-377a9e25ef7a" />
<br>
This format gives:

- enough precision [-2.0 , +1.99994] for neural network weights and biases
- simple hardware implementation
- compact 16-bit storage
- faster multiply-and-accumulate operations
- easier loading into FPGA memory using `.hex` files

#### Intel hex files
The converted Q2.14 weights and biases were then written into Intel HEX files so they could be used to initialize FPGA memory.
<img width="1447" height="246" alt="image" src="https://github.com/user-attachments/assets/82e81393-34e6-40da-86ea-28ad9685865a" />
<br>
This allows the trained neural network parameters to be stored as compact fixed-point values and loaded directly into FPGA memory for hardware inference.
<br>
#### The complete conversion process:
<img width="1422" height="183" alt="image" src="https://github.com/user-attachments/assets/d5aebabe-46fd-47f2-86cf-aa88f1415a7f" />




