import numpy as np
from pathlib import Path
import math

Q_FRAC = 8
SCALE = 2 ** Q_FRAC
Q_MIN = -32768
Q_MAX = 32767

def float_to_q8_8(value: float) -> int:
    scaled = value * SCALE
    q = int(math.copysign(math.floor(abs(scaled) + 0.5), scaled))
    q = max(Q_MIN, min(Q_MAX, q))
    return q

def save_q8_8_to_mif(arr, filename, depth=None):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    q_values = [float_to_q8_8(float(v)) for v in arr.flatten()]

    if depth is None:
        depth = len(q_values)

    if len(q_values) > depth:
        raise ValueError(f"{filename}: too many values for depth {depth}")

    while len(q_values) < depth:
        q_values.append(0)

    with open(filename, "w") as f:
        f.write("WIDTH=16;\n")
        f.write(f"DEPTH={depth};\n\n")
        f.write("ADDRESS_RADIX=HEX;\n")
        f.write("DATA_RADIX=HEX;\n\n")
        f.write("CONTENT BEGIN\n")

        for addr, q in enumerate(q_values):
            f.write(f"    {addr:X} : {q & 0xFFFF:04X};\n")

        f.write("END;\n")

data = np.load("training/trained_dnn.npz")

save_q8_8_to_mif(data["predictor/l1/W"], "weights_biases/w1.mif", depth=16*784)
save_q8_8_to_mif(data["predictor/l1/b"], "weights_biases/b1.mif", depth=16)

save_q8_8_to_mif(data["predictor/l2/W"], "weights_biases/w2.mif", depth=16*16)
save_q8_8_to_mif(data["predictor/l2/b"], "weights_biases/b2.mif", depth=16)

save_q8_8_to_mif(data["predictor/l3/W"], "weights_biases/w3.mif", depth=10*16)

# Your b3 memory is 16 words, but b3 has only 10 values, so pad to 16.
save_q8_8_to_mif(data["predictor/l3/b"], "weights_biases/b3.mif", depth=16)

print("Done: generated Q8.8 MIF files.")