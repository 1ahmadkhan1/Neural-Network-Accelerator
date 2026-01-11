import numpy as np

# Q2.14 settings (int16)
F = 14
S = 1 << F

def q14_int16(x: np.ndarray) -> np.ndarray:
    q = np.round(x * S).astype(np.int32)
    q = np.clip(q, -32768, 32767).astype(np.int16)
    return q

def get_by_suffix_and_shape(d: np.lib.npyio.NpzFile, suffix: str, shape: tuple):
    cands = [k for k in d.files if k.endswith(suffix) and tuple(d[k].shape) == tuple(shape)]
    if len(cands) != 1:
        raise RuntimeError(
            f"Expected 1 key ending with '{suffix}' and shape {shape}, found {len(cands)}: {cands}"
        )
    k = cands[0]
    return k, d[k]

def main():
    d = np.load("trained_dnn.npz")

    # Match your trained net: 784 -> 16 -> 16 -> 10
    kW1, W1 = get_by_suffix_and_shape(d, "/l1/W", (16, 784))
    kb1, b1 = get_by_suffix_and_shape(d, "/l1/b", (16,))

    kW2, W2 = get_by_suffix_and_shape(d, "/l2/W", (16, 16))
    kb2, b2 = get_by_suffix_and_shape(d, "/l2/b", (16,))

    kW3, W3 = get_by_suffix_and_shape(d, "/l3/W", (10, 16))
    kb3, b3 = get_by_suffix_and_shape(d, "/l3/b", (10,))

    print("Matched:")
    print("W1:", kW1, W1.shape, W1.dtype)
    print("b1:", kb1, b1.shape, b1.dtype)
    print("W2:", kW2, W2.shape, W2.dtype)
    print("b2:", kb2, b2.shape, b2.dtype)
    print("W3:", kW3, W3.shape, W3.dtype)
    print("b3:", kb3, b3.shape, b3.dtype)

    # Optional quick sanity peek (remove if you want)
    print("b1 first 5:", b1[:5])
    print("b2 first 5:", b2[:5])

    # Quantize to Q2.14 int16
    W1q = q14_int16(W1).reshape(-1)
    b1q = q14_int16(b1).reshape(-1)
    W2q = q14_int16(W2).reshape(-1)
    b2q = q14_int16(b2).reshape(-1)
    W3q = q14_int16(W3).reshape(-1)
    b3q = q14_int16(b3).reshape(-1)

    # Pack ROM in fixed order (word offsets!)
    OFF_W1 = 0
    OFF_B1 = OFF_W1 + W1q.size
    OFF_W2 = OFF_B1 + b1q.size
    OFF_B2 = OFF_W2 + W2q.size
    OFF_W3 = OFF_B2 + b2q.size
    OFF_B3 = OFF_W3 + W3q.size
    ROM_WORDS = OFF_B3 + b3q.size

    rom = np.zeros(ROM_WORDS, dtype=np.int16)
    rom[OFF_W1:OFF_B1] = W1q
    rom[OFF_B1:OFF_W2] = b1q
    rom[OFF_W2:OFF_B2] = W2q
    rom[OFF_B2:OFF_W3] = b2q
    rom[OFF_W3:OFF_B3] = W3q
    rom[OFF_B3:ROM_WORDS] = b3q

    # Pad depth to power of two (nice for on-chip memory)
    depth = 1
    while depth < ROM_WORDS:
        depth <<= 1

    rom_padded = np.zeros(depth, dtype=np.int16)
    rom_padded[:ROM_WORDS] = rom

    # Write MIF (16-bit words, hex)
    with open("nn_rom_q14.mif", "w") as f:
        f.write(f"WIDTH=16;\nDEPTH={depth};\n")
        f.write("ADDRESS_RADIX=HEX;\nDATA_RADIX=HEX;\n")
        f.write("CONTENT BEGIN\n")
        for addr, val in enumerate(rom_padded):
            u = np.uint16(val).item()  # preserve two's complement
            f.write(f"{addr:04X} : {u:04X};\n")
        f.write("END;\n")

    # Write header with layout offsets (word indices!)
    with open("nn_rom_layout.h", "w") as f:
        f.write("#pragma once\n#include <stdint.h>\n\n")
        f.write(f"#define Q_FRAC_BITS {F}\n")
        f.write(f"#define ROM_OFF_W1 {OFF_W1}\n")
        f.write(f"#define ROM_OFF_B1 {OFF_B1}\n")
        f.write(f"#define ROM_OFF_W2 {OFF_W2}\n")
        f.write(f"#define ROM_OFF_B2 {OFF_B2}\n")
        f.write(f"#define ROM_OFF_W3 {OFF_W3}\n")
        f.write(f"#define ROM_OFF_B3 {OFF_B3}\n")
        f.write(f"#define ROM_WORDS_USED {ROM_WORDS}\n")
        f.write(f"#define ROM_DEPTH_WORDS {depth}\n\n")
        f.write("#define N_IN 784\n#define H1 16\n#define H2 16\n#define N_OUT 10\n")

    print("Wrote nn_rom_q14.mif and nn_rom_layout.h")
    print("ROM words used:", ROM_WORDS, "padded to:", depth)

    # Write HEX init file (one 16-bit word per line, Quartus-style)
    with open("nn_rom_q14.hex", "w") as f:
        for val in rom_padded:
            u = np.uint16(val).item()   # preserve two's complement
            f.write(f"{u:04X}\n")

    print("Wrote nn_rom_q14.hex")


if __name__ == "__main__":
    main()
