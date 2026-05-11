import sys
from pathlib import Path

def parse_mif(filename: str):
    """
    Parse a simple MIF file (WIDTH=16, DEPTH=784) and return a list
    of 16-bit unsigned integers, the raw Q8.8 bit patterns.
    """
    words = []

    with open(filename, "r") as f:
        in_content = False

        for line in f:
            line = line.strip()

            if line == "CONTENT BEGIN":
                in_content = True
                continue

            if line == "END;":
                break

            if in_content and line and not line.startswith("--"):
                # Typical line: "00A : 001F;"
                parts = line.split(":")

                if len(parts) >= 2:
                    data_part = parts[1].strip().rstrip(";")

                    try:
                        word = int(data_part, 16)
                        words.append(word)
                    except ValueError:
                        pass

    return words


def q8_8_to_pixel(q: int, scale=256):
    """
    Convert a Q8.8 fixed-point value back to a pixel value in 0-255.

    For MNIST input pixels:
        0.0 -> 0x0000
        1.0 -> 0x0100
    """

    # For MNIST pixels, values are non-negative, so unsigned interpretation is fine.
    val = q / scale

    pixel = round(val * 255)

    return max(0, min(255, pixel))


def visualize_matplotlib(pixels, rows=28, cols=28):
    """
    Show the image with Matplotlib.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    img = np.array(pixels).reshape(rows, cols)

    plt.imshow(img, cmap="gray", vmin=0, vmax=255)
    plt.title("MNIST test image from Q8.8 MIF")
    plt.colorbar()
    plt.show()


# ------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize_mif_q88.py <mif_file>")
        sys.exit(1)

    mif_path = sys.argv[1]

    print(f"Reading {mif_path} ...")

    words = parse_mif(mif_path)

    if len(words) != 784:
        print(f"Warning: expected 784 values, got {len(words)}")

    pixels = [q8_8_to_pixel(w) for w in words]

    visualize_matplotlib(pixels)