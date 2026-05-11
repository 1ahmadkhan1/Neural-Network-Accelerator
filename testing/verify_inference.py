import sys
from pathlib import Path

# ------------------------------------------------------------
#  Fixed-point constants (identical to hello_world_small.c)
# ------------------------------------------------------------
Q_FRAC = 8
Q_SCALE = 1 << Q_FRAC  # 256
Q_MAX = 32767
Q_MIN = -32768

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHT_DIR = PROJECT_ROOT / "weights_biases"


# ------------------------------------------------------------
#  Intel HEX parser (little-endian 16-bit words)
# ------------------------------------------------------------
def parse_intel_hex(filename):
    """Convert a .hex file into a list of signed 16-bit integers (Q8.8)."""
    words = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line.startswith(":"):
                continue
            byte_count = int(line[1:3], 16)
            if byte_count == 0:
                break
            record_type = int(line[7:9], 16)
            if record_type != 0:
                continue
            data_str = line[9:9 + byte_count * 2]
            for i in range(0, len(data_str), 4):
                lo = int(data_str[i:i + 2], 16)
                hi = int(data_str[i + 2:i + 4], 16)
                word = (hi << 8) | lo
                if word & 0x8000:
                    word -= 0x10000
                words.append(word)
    return words


# ------------------------------------------------------------
#  Pure-software replicas of the C fixed-point functions
# ------------------------------------------------------------
def saturate_q8_8(x):
    if x > Q_MAX:
        return Q_MAX
    if x < Q_MIN:
        return Q_MIN
    return x


def round_shift_q16_to_q8(acc):
    """acc is Q16.16. Round to nearest and shift right by 8."""
    if acc >= 0:
        return (acc + (1 << (Q_FRAC - 1))) >> Q_FRAC
    return -(((-acc) + (1 << (Q_FRAC - 1))) >> Q_FRAC)


def relu_saturate_q8_8(x):
    if x <= 0:
        return 0
    return saturate_q8_8(x)


# ------------------------------------------------------------
#  Layer functions - identical to the C code
# ------------------------------------------------------------
def dense_relu_from_memory(input_words, weight_words, bias_words, input_size, output_size):
    out = []
    for neuron in range(output_size):
        bias = bias_words[neuron]
        acc = bias << Q_FRAC
        for j in range(input_size):
            x = input_words[j]
            w = weight_words[neuron * input_size + j]
            acc += x * w
        q8 = round_shift_q16_to_q8(acc)
        out.append(relu_saturate_q8_8(q8))
    return out


def dense_relu_from_array(input_vec, weight_words, bias_words, input_size, output_size):
    out = []
    for neuron in range(output_size):
        bias = bias_words[neuron]
        acc = bias << Q_FRAC
        for j in range(input_size):
            x = input_vec[j]
            w = weight_words[neuron * input_size + j]
            acc += x * w
        q8 = round_shift_q16_to_q8(acc)
        out.append(relu_saturate_q8_8(q8))
    return out


def dense_logits_from_array(input_vec, weight_words, bias_words, input_size, output_size):
    logits = []
    for neuron in range(output_size):
        bias = bias_words[neuron]
        acc = bias << Q_FRAC
        for j in range(input_size):
            x = input_vec[j]
            w = weight_words[neuron * input_size + j]
            acc += x * w
        logits.append(round_shift_q16_to_q8(acc))
    return logits


# ------------------------------------------------------------
#  Argmax - as in C
# ------------------------------------------------------------
def argmax_int32(values):
    return max(range(len(values)), key=lambda i: values[i])


# ------------------------------------------------------------
#  Main verification
# ------------------------------------------------------------
def main(test_image_hex):
    print("Loading weight/bias .hex files ...")

    w1 = parse_intel_hex(WEIGHT_DIR / "w1.hex")
    b1 = parse_intel_hex(WEIGHT_DIR / "b1.hex")
    w2 = parse_intel_hex(WEIGHT_DIR / "w2.hex")
    b2 = parse_intel_hex(WEIGHT_DIR / "b2.hex")
    w3 = parse_intel_hex(WEIGHT_DIR / "w3.hex")
    b3 = parse_intel_hex(WEIGHT_DIR / "b3.hex")

    image_path = Path(test_image_hex)
    if not image_path.is_absolute():
        image_path = (Path.cwd() / image_path).resolve()

    print("Loading test image ...")
    input_pixels = parse_intel_hex(image_path)
    assert len(input_pixels) == 784, f"Expected 784 input values, got {len(input_pixels)}"

    h1 = dense_relu_from_memory(input_pixels, w1, b1, 784, 16)
    h2 = dense_relu_from_array(h1, w2, b2, 16, 16)
    logits = dense_logits_from_array(h2, w3, b3, 16, 10)

    pred = argmax_int32(logits)

    print("\nLogits (Q8.8 integer format):")
    for i, value in enumerate(logits):
        print(f"  {i}: {value}  (~ {value / Q_SCALE:.4f})")

    print(f"\nPredicted digit: {pred}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_inference.py <path/to/mnist_test_XX_q88.hex>")
        print("Example: python verify_inference.py testing/test_images/mnist_test_00_q88.hex")
        sys.exit(1)
    main(sys.argv[1])
