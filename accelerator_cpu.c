#include <stdint.h>
#include <stdio.h>

#include "system.h"
#include "io.h"

/*
 * Accelerated DNN inference on Nios II.
 *
 * Network:
 * input: 784
 * layer 1: 16 neurons + ReLU
 * layer 2: 16 neurons + ReLU
 * layer 3: 10 logits, no ReLU
 *
 * Data format:
 * signed Q8.8 fixed-point
 */

#define INPUT_SIZE 784
#define H1_SIZE 16
#define H2_SIZE 16
#define OUTPUT_SIZE 10

/*
 * Accelerator register map:
 *
 * reg 0: start
 * reg 1: input_base
 * reg 2: weights_base
 * reg 3: bias_base
 * reg 4: input_size
 * reg 5: output_size
 * reg 6: relu_enable
 *
 * s1_readdata returns done in bit 0.
 */
#define ACC_REG_START 0
#define ACC_REG_INPUT_BASE 1
#define ACC_REG_WEIGHTS_BASE 2
#define ACC_REG_BIAS_BASE 3
#define ACC_REG_INPUT_SIZE 4
#define ACC_REG_OUTPUT_SIZE 5
#define ACC_REG_RELU_ENABLE 6

#define ACC_BASE ACC_0_BASE

/*
 * DE1-SoC HEX displays are active-low.
 */
static const uint8_t seven_seg_hex[16] = {
    0x40, // 0
    0x79, // 1
    0x24, // 2
    0x30, // 3
    0x19, // 4
    0x12, // 5
    0x02, // 6
    0x78, // 7
    0x00, // 8
    0x10, // 9
    0x08, // A
    0x03, // b
    0x46, // C
    0x21, // d
    0x06, // E
    0x0E  // F
};

static inline void write_prediction_to_outputs(int prediction)
{
    IOWR(SEV_SEG_BASE, 0, seven_seg_hex[prediction & 0xF]);
}

static inline int16_t read_q8_8(uint32_t base, int index)
{
    /*
     * Each Q8.8 value is 16 bits = 2 bytes.
     */
    return (int16_t)IORD_16DIRECT(base, index * 2);
}

static int argmax_q8_8_from_memory(uint32_t base, int size)
{
    int best_index = 0;
    int16_t best_value = read_q8_8(base, 0);

    for (int i = 1; i < size; i++)
    {
        int16_t value = read_q8_8(base, i);

        if (value > best_value)
        {
            best_value = value;
            best_index = i;
        }
    }

    return best_index;
}

static void print_q8_8_vector(const char *name, uint32_t base, int size)
{
    printf("%s:\n", name);

    for (int i = 0; i < size; i++)
    {
        int16_t raw = read_q8_8(base, i);

        /*
         * Print raw Q8.8 integer.
         * Real value = raw / 256.0
         */
        printf("%d: %d\n", i, raw);
    }
}

static void accelerator_wait_done(void)
{
    /*
     * FSM returns done in bit 0 of s1_readdata.
     * Since s1_readdata ignores address, any IORD from ACC_BASE works.
     */
    while ((IORD(ACC_BASE, 0) & 0x1) == 0)
    {
        /*
         * Busy wait.
         */
    }
}

static void accelerator_run_layer(
    uint32_t input_base,
    uint32_t weights_base,
    uint32_t bias_base,
    uint32_t input_size,
    uint32_t output_size,
    uint32_t relu_enable)
{
    /*
     * Make sure start is low before configuring the layer.
     */
    IOWR(ACC_BASE, ACC_REG_START, 0);

    /*
     * Configure accelerator registers.
     */
    IOWR(ACC_BASE, ACC_REG_INPUT_BASE, input_base);
    IOWR(ACC_BASE, ACC_REG_WEIGHTS_BASE, weights_base);
    IOWR(ACC_BASE, ACC_REG_BIAS_BASE, bias_base);
    IOWR(ACC_BASE, ACC_REG_INPUT_SIZE, input_size);
    IOWR(ACC_BASE, ACC_REG_OUTPUT_SIZE, output_size);
    IOWR(ACC_BASE, ACC_REG_RELU_ENABLE, relu_enable);

    /*
     * Start the FSM.
     *
     * Since done is encoded in state[4], keep start high while running.
     * The FSM reaches done_out_st, done becomes 1, and software sees it.
     */
    IOWR(ACC_BASE, ACC_REG_START, 1);

    accelerator_wait_done();

    /*
     * Drop start back to 0 so the FSM can return to idle / be ready
     * for the next layer.
     */
    IOWR(ACC_BASE, ACC_REG_START, 0);
}

int main(void)
{
    int prediction;

    printf("Starting accelerated Nios II DNN inference using Q8.8...\n");

    printf("B3_BASE from system.h = 0x%08x\n", B3_BASE);
    printf("Testing CPU read from B3 before accelerator...\n");

    volatile uint32_t b3_test_word = IORD_32DIRECT(B3_BASE, 0);

    printf("B3 first word before accelerator = 0x%08x\n", b3_test_word);
    printf("B3 CPU read test passed\n");

    /*
     * Layer 1:
     *
     * input_layer -> W1/B1 -> result written back into B1
     *
     * Your FSM uses bias_base both as the bias input and output destination.
     */
    printf("Running layer 1...\n");

    accelerator_run_layer(
        INPUT_LAYER_BASE,
        W1_BASE,
        B1_BASE,
        INPUT_SIZE,
        H1_SIZE,
        1);

    /*
     * Layer 2:
     *
     * B1 now contains h1.
     * B1 -> W2/B2 -> result written back into B2
     */
    printf("Running layer 2...\n");

    accelerator_run_layer(
        B1_BASE,
        W2_BASE,
        B2_BASE,
        H1_SIZE,
        H2_SIZE,
        1);

    /*
     * Layer 3:
     *
     * B2 now contains h2.
     * B2 -> W3/B3 -> logits written back into B3
     *
     * Final layer has no ReLU.
     */
    printf("Running layer 3...\n");

    accelerator_run_layer(
        B2_BASE,
        W3_BASE,
        B3_BASE,
        H2_SIZE,
        OUTPUT_SIZE,
        0);

    /*
     * Final logits are stored in B3 memory.
     */
    print_q8_8_vector("Logits", B3_BASE, OUTPUT_SIZE);

    prediction = argmax_q8_8_from_memory(B3_BASE, OUTPUT_SIZE);

    printf("Predicted label: %d\n", prediction);

    write_prediction_to_outputs(prediction);

    while (1)
    {
        /*
         * Keep displaying prediction.
         */
        write_prediction_to_outputs(prediction);

        /*
         * Keep switch-to-LED sanity test alive.
         */
        int sw = IORD(SWITCHES_BASE, 0);
        IOWR(LEDS_BASE, 0, sw);
    }

    return 0;
}
