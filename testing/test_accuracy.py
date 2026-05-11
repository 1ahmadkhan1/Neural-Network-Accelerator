import gzip
import math
import struct
from pathlib import Path

# ------------------------------------------------------------
#  Q8.8 constants & conversion (exactly like hello_world_small.c)
# ------------------------------------------------------------
Q_FRAC = 8
Q_SCALE = 1 << Q_FRAC  # 256
Q_MAX = 32767
Q_MIN = -32768

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHT_DIR = PROJECT_ROOT / "weights_biases"
DATA_DIR = PROJECT_ROOT / "training_test_data"


def float_to_q8_8(value):
    """Identical to the Python conversion used when creating hex files."""
    scaled = value * Q_SCALE
    q = int(math.copysign(math.floor(abs(scaled) + 0.5), scaled))
    if q > Q_MAX:
        return Q_MAX
    if q < Q_MIN:
        return Q_MIN
    return q


def saturate_q8_8(x):
    if x > Q_MAX:
        return Q_MAX
    if x < Q_MIN:
        return Q_MIN
    return x


def round_shift_q16_to_q8(acc):
    """Exactly matches the C code rounding."""
    if acc >= 0:
        return (acc + (1 << (Q_FRAC - 1))) >> Q_FRAC
    return -(((-acc) + (1 << (Q_FRAC - 1))) >> Q_FRAC)


def relu_saturate_q8_8(x):
    if x <= 0:
        return 0
    return saturate_q8_8(x)


# ------------------------------------------------------------
#  Intel HEX parser (little-endian 16-bit words)
# ------------------------------------------------------------
def parse_intel_hex(filename):
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
#  Layer functions (mirror your C code)
# ------------------------------------------------------------
def dense_relu_from_memory(input_q8, w_q8, b_q8, in_size, out_size):
    out = []
    for neuron in range(out_size):
        bias = b_q8[neuron]
        acc = bias << Q_FRAC  # Q16.16
        for j in range(in_size):
            x = input_q8[j]
            w = w_q8[neuron * in_size + j]
            acc += x * w
        q8 = round_shift_q16_to_q8(acc)
        out.append(relu_saturate_q8_8(q8))
    return out


def dense_relu_from_array(input_q8, w_q8, b_q8, in_size, out_size):
    return dense_relu_from_memory(input_q8, w_q8, b_q8, in_size, out_size)


def dense_logits_from_array(input_q8, w_q8, b_q8, in_size, out_size):
    logits = []
    for neuron in range(out_size):
        bias = b_q8[neuron]
        acc = bias << Q_FRAC
        for j in range(in_size):
            x = input_q8[j]
            w = w_q8[neuron * in_size + j]
            acc += x * w
        logits.append(round_shift_q16_to_q8(acc))
    return logits


def argmax_int32(values):
    return max(range(len(values)), key=lambda i: values[i])


# ------------------------------------------------------------
#  MNIST test set loader from the raw .gz files
# ------------------------------------------------------------
def load_mnist_test_set(image_path, label_path):
    with gzip.open(image_path, "rb") as f:
        magic, num, rows, cols = struct.unpack(">IIII", f.read(16))
        if magic != 2051:
            raise ValueError(f"Invalid MNIST image file magic: {magic}")
        images = []
        for _ in range(num):
            pixels = list(f.read(rows * cols))
            images.append(pixels)
    with gzip.open(label_path, "rb") as f:
        magic, num = struct.unpack(">II", f.read(8))
        if magic != 2049:
            raise ValueError(f"Invalid MNIST label file magic: {magic}")
        labels = list(f.read(num))
    return images, labels, rows, cols


# ------------------------------------------------------------
#  Main accuracy test
# ------------------------------------------------------------
if __name__ == "__main__":
    w1 = parse_intel_hex(WEIGHT_DIR / "w1.hex")
    b1 = parse_intel_hex(WEIGHT_DIR / "b1.hex")
    w2 = parse_intel_hex(WEIGHT_DIR / "w2.hex")
    b2 = parse_intel_hex(WEIGHT_DIR / "b2.hex")
    w3 = parse_intel_hex(WEIGHT_DIR / "w3.hex")
    b3 = parse_intel_hex(WEIGHT_DIR / "b3.hex")

    test_images, test_labels, rows, cols = load_mnist_test_set(
        DATA_DIR / "t10k-images-idx3-ubyte.gz",
        DATA_DIR / "t10k-labels-idx1-ubyte.gz",
    )
    print(f"Loaded {len(test_images)} test images")

    correct = 0
    for idx, (pixels, label) in enumerate(zip(test_images, test_labels)):
        input_q8 = [float_to_q8_8(p / 255.0) for p in pixels]

        h1 = dense_relu_from_memory(input_q8, w1, b1, 784, 16)
        h2 = dense_relu_from_array(h1, w2, b2, 16, 16)
        logits = dense_logits_from_array(h2, w3, b3, 16, 10)
        pred = argmax_int32(logits)

        if pred == label:
            correct += 1

        if (idx + 1) % 1000 == 0:
            acc_so_far = correct / (idx + 1) * 100
            print(f"... {idx + 1}/{len(test_images)} current accuracy: {acc_so_far:.2f}%")

    final_acc = correct / len(test_images) * 100
    print(f"\nFinal accuracy on 10000 test images: {final_acc:.2f}%")

    if final_acc < 90:
        print("\n** WARNING: Accuracy is very low! **")
        print("Possible reasons:")
        print("1. Training used different preprocessing than raw [0,1] pixels.")
        print("2. Weight array layout mismatch (e.g., row-major vs column-major).")
        print("3. Q8.8 export or parsing mismatch between Python and C.")
        print("4. Different network architecture than expected.")
        print("Check the training script's preprocessing and network definition.")
