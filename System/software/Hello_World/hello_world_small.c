#include <stdint.h>
#include <stdio.h>

#include "system.h"
#include "io.h"

/*
 * Network:
 * input: 784
 * layer 1: 16 neurons + ReLU
 * layer 2: 16 neurons + ReLU
 * layer 3: 10 logits
 *
 * All weights, biases, and input pixels are stored in signed Q8.8 fixed-point.
 */

#define INPUT_SIZE   784
#define H1_SIZE      16
#define H2_SIZE      16
#define OUTPUT_SIZE  10

#define Q_FRAC 8
#define Q_MAX  32767
#define Q_MIN -32768

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

static inline int16_t read_q8_8(uint32_t base, int index)
{
    /*
     * Each Q8.8 value is 16 bits = 2 bytes.
     * index 0 is at base + 0
     * index 1 is at base + 2
     * index 2 is at base + 4
     */
    return (int16_t) IORD_16DIRECT(base, index * 2);
}

static inline void write_prediction_to_outputs(int prediction)
{
    /*
     * Show predicted digit on HEX display connected to sev_seg PIO.
     */
    IOWR(SEV_SEG_BASE, 0, seven_seg_hex[prediction & 0xF]);
}

static int16_t saturate_q8_8(int32_t x)
{
    if (x > Q_MAX) return Q_MAX;
    if (x < Q_MIN) return Q_MIN;
    return (int16_t)x;
}

static int32_t round_shift_q16_to_q8(int64_t acc)
{
    /*
     * Q8.8 * Q8.8 = Q16.16.
     * Shift right by 8 to return to Q8.8 scale.
     *
     * This does round-to-nearest instead of plain truncation.
     */
    if (acc >= 0) {
        return (int32_t)((acc + (1LL << (Q_FRAC - 1))) >> Q_FRAC);
    } else {
        return (int32_t)(-(((-acc) + (1LL << (Q_FRAC - 1))) >> Q_FRAC));
    }
}

static int16_t relu_saturate_q8_8(int32_t x)
{
    if (x <= 0) return 0;
    return saturate_q8_8(x);
}

static void dense_relu_from_memory(
    uint32_t input_base,
    uint32_t weight_base,
    uint32_t bias_base,
    int16_t *output,
    int input_size,
    int output_size
)
{
    for (int neuron = 0; neuron < output_size; neuron++) {

        /*
         * Bias is Q8.8.
         * Shift left by 8 so it matches accumulated products in Q16.16.
         */
        int16_t bias = read_q8_8(bias_base, neuron);
        int64_t acc = ((int64_t)bias) << Q_FRAC;

        for (int j = 0; j < input_size; j++) {
            int16_t x = read_q8_8(input_base, j);

            /*
             * Weights are flattened row-major:
             * W[neuron][j] -> W[neuron * input_size + j]
             */
            int16_t w = read_q8_8(weight_base, neuron * input_size + j);

            acc += (int32_t)x * (int32_t)w;
        }

        int32_t q8 = round_shift_q16_to_q8(acc);
        output[neuron] = relu_saturate_q8_8(q8);
    }
}

static void dense_relu_from_array(
    const int16_t *input,
    uint32_t weight_base,
    uint32_t bias_base,
    int16_t *output,
    int input_size,
    int output_size
)
{
    for (int neuron = 0; neuron < output_size; neuron++) {

        int16_t bias = read_q8_8(bias_base, neuron);
        int64_t acc = ((int64_t)bias) << Q_FRAC;

        for (int j = 0; j < input_size; j++) {
            int16_t x = input[j];
            int16_t w = read_q8_8(weight_base, neuron * input_size + j);

            acc += (int32_t)x * (int32_t)w;
        }

        int32_t q8 = round_shift_q16_to_q8(acc);
        output[neuron] = relu_saturate_q8_8(q8);
    }
}

static void dense_logits_from_array(
    const int16_t *input,
    uint32_t weight_base,
    uint32_t bias_base,
    int32_t *output,
    int input_size,
    int output_size
)
{
    for (int neuron = 0; neuron < output_size; neuron++) {

        int16_t bias = read_q8_8(bias_base, neuron);
        int64_t acc = ((int64_t)bias) << Q_FRAC;

        for (int j = 0; j < input_size; j++) {
            int16_t x = input[j];
            int16_t w = read_q8_8(weight_base, neuron * input_size + j);

            acc += (int32_t)x * (int32_t)w;
        }

        /*
         * Final layer has no ReLU.
         * Keep logits as int32_t for argmax.
         */
        output[neuron] = round_shift_q16_to_q8(acc);
    }
}

static int argmax_int32(const int32_t *x, int size)
{
    int best_index = 0;
    int32_t best_value = x[0];

    for (int i = 1; i < size; i++) {
        if (x[i] > best_value) {
            best_value = x[i];
            best_index = i;
        }
    }

    return best_index;
}

int main(void)
{
    int16_t h1[H1_SIZE];
    int16_t h2[H2_SIZE];
    int32_t logits[OUTPUT_SIZE];

    int prediction;

    printf("Starting Nios II DNN inference using Q8.8...\n");

    /*
     * Layer 1:
     * input_layer memory -> W1/b1 -> h1
     */
    dense_relu_from_memory(
        INPUT_LAYER_BASE,
        W1_BASE,
        B1_BASE,
        h1,
        INPUT_SIZE,
        H1_SIZE
    );

    /*
     * Layer 2:
     * h1 -> W2/b2 -> h2
     */
    dense_relu_from_array(
        h1,
        W2_BASE,
        B2_BASE,
        h2,
        H1_SIZE,
        H2_SIZE
    );

    /*
     * Layer 3:
     * h2 -> W3/b3 -> logits
     */
    dense_logits_from_array(
        h2,
        W3_BASE,
        B3_BASE,
        logits,
        H2_SIZE,
        OUTPUT_SIZE
    );

    prediction = argmax_int32(logits, OUTPUT_SIZE);

    printf("Logits:\n");
    for (int i = 0; i < OUTPUT_SIZE; i++) {
        printf("%d: %ld\n", i, (long)logits[i]);
    }

    printf("Predicted label: %d\n", prediction);

    write_prediction_to_outputs(prediction);

    while (1) {
        /*
         * Keep displaying the prediction forever.
         */
        write_prediction_to_outputs(prediction);

        /*
         * Keep switch-to-LED test alive too.
         */
        int sw = IORD(SWITCHES_BASE, 0);
        IOWR(LEDS_BASE, 0, sw);
    }

    return 0;
}
