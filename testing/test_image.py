import gzip
import struct
import urllib.request
from pathlib import Path
import math

# ------------------------------------------------------------
# URLs for MNIST test set
# ------------------------------------------------------------
IMAGE_URL = "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz"
LABEL_URL = "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz"

# ------------------------------------------------------------
# Q8.8 settings
# ------------------------------------------------------------
SCALE = 2 ** 8      # Q8.8 scale factor = 256
Q_MIN = -32768
Q_MAX = 32767

# ------------------------------------------------------------
# Q8.8 conversion
# ------------------------------------------------------------
def float_to_q8_8(value):
    """
    Convert float to signed Q8.8 fixed-point.

    Q8.8:
        16 total bits
        8 integer/sign bits
        8 fractional bits

    Real value -> fixed-point integer:
        q = round(value * 2^8)
    """
    scaled = value * SCALE

    # round ties away from zero
    q = int(math.copysign(math.floor(abs(scaled) + 0.5), scaled))

    # saturate to signed 16-bit range
    q = max(Q_MIN, min(Q_MAX, q))

    return q

# ------------------------------------------------------------
# Download helpers
# ------------------------------------------------------------
def download(url, filename):
    filename = Path(filename)

    if filename.exists():
        return filename

    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, filename)

    return filename

# ------------------------------------------------------------
# Load one MNIST test image
# ------------------------------------------------------------
def load_mnist_image(image_file, label_file, index):
    with gzip.open(image_file, "rb") as f:
        magic, num_images, rows, cols = struct.unpack(">IIII", f.read(16))

        if magic != 2051:
            raise ValueError("Invalid MNIST image file")

        if index >= num_images:
            raise ValueError("Image index out of range")

        image_size = rows * cols
        f.seek(16 + index * image_size)
        pixels = list(f.read(image_size))

    with gzip.open(label_file, "rb") as f:
        magic, num_labels = struct.unpack(">II", f.read(8))

        if magic != 2049:
            raise ValueError("Invalid MNIST label file")

        f.seek(8 + index)
        label = f.read(1)[0]

    return pixels, label, rows, cols

# ------------------------------------------------------------
# Intel HEX writer
# Each Q8.8 value is 16 bits = 2 bytes
# Stored little-endian:
#   low byte first, high byte second
# ------------------------------------------------------------
def intel_hex_checksum(byte_count, address, record_type, data_bytes):
    total = byte_count
    total += (address >> 8) & 0xFF
    total += address & 0xFF
    total += record_type
    total += sum(data_bytes)

    return ((~total + 1) & 0xFF)

def write_intel_hex(q_values, filename):
    address = 0

    with open(filename, "w") as f:
        for start in range(0, len(q_values), 16):
            chunk = q_values[start:start + 16]
            data_bytes = []

            for q in chunk:
                word = q & 0xFFFF

                # little-endian 16-bit word
                data_bytes.append(word & 0xFF)          # low byte
                data_bytes.append((word >> 8) & 0xFF)   # high byte

            byte_count = len(data_bytes)
            record_type = 0x00

            checksum = intel_hex_checksum(
                byte_count,
                address,
                record_type,
                data_bytes
            )

            data_str = "".join(f"{b:02X}" for b in data_bytes)

            f.write(
                f":{byte_count:02X}"
                f"{address:04X}"
                f"{record_type:02X}"
                f"{data_str}"
                f"{checksum:02X}\n"
            )

            address += byte_count

        f.write(":00000001FF\n")

# ------------------------------------------------------------
# MIF writer
# ------------------------------------------------------------
def write_mif(q_values, filename):
    with open(filename, "w") as f:
        f.write("WIDTH=16;\n")
        f.write(f"DEPTH={len(q_values)};\n\n")

        f.write("ADDRESS_RADIX=HEX;\n")
        f.write("DATA_RADIX=HEX;\n\n")

        f.write("CONTENT BEGIN\n")

        for addr, q in enumerate(q_values):
            word = q & 0xFFFF
            f.write(f"    {addr:03X} : {word:04X};\n")

        f.write("END;\n")

# ------------------------------------------------------------
# Main – generate files for first 10 test images
# ------------------------------------------------------------
if __name__ == "__main__":
    image_file = download(IMAGE_URL, "t10k-images-idx3-ubyte.gz")
    label_file = download(LABEL_URL, "t10k-labels-idx1-ubyte.gz")

    out_dir = Path("test_images")
    out_dir.mkdir(exist_ok=True)

    for idx in range(10):
        pixels, label, rows, cols = load_mnist_image(image_file, label_file, idx)

        # Convert MNIST pixel 0..255 to normalized 0.0..1.0, then Q8.8
        q_values = []

        for p in pixels:
            normalized = p / 255.0
            q = float_to_q8_8(normalized)
            q_values.append(q)

        # File names with zero-padded index
        stem = f"mnist_test_{idx:02d}_q88"

        hex_path = out_dir / f"{stem}.hex"
        mif_path = out_dir / f"{stem}.mif"

        write_intel_hex(q_values, hex_path)
        write_mif(q_values, mif_path)

        print(f"Image {idx:02d} (label={label}) -> {hex_path.name}, {mif_path.name}")

    print("Done. All 10 Q8.8 test images exported.")