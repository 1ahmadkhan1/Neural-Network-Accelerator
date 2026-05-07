import numpy as np
from pathlib import Path
def float_to_q2_14(value: float) -> int:
    """
    Convert a float to Q2.14 fixed‑point (16‑bit signed integer).
    Range: [-2.0, 2.0 - 2^-14]
    Values outside are saturated.
    """
    # Scale factor for q2.14 is 2^14 = 16384
    scale = 2**14

    # Multiply and round to nearest integer (ties round away from zero)
    q = round(value * scale)

    # Saturate to int16 range
    if q > 32767:
        q = 32767
    elif q < -32768:
        q = -32768

    # In Python, store as a signed 32‑bit int, but it fits in 16 bits
    return q

# This function is for reference
def q2_14_to_hex(q: int) -> str:
    """
    Convert a Q2.14 fixed point integer (signed 16 bit) to its
    4 character hexadecimal representation (e.g. '2EC9' or 'C000').

    This hex string represents the exact 16bit two's complement
    bit pattern that the FPGA ROM will store.
    """
    # Mask to 16 bits, keeping the two’s complement pattern
    word = q & 0xFFFF
    # Format as zero‑padded uppercase hex (4 digits)
    return f"{word:04X}"


def intel_hex_checksum(byte_count, address, record_type, data_bytes):
    total = byte_count
    total += (address >> 8) & 0xFF
    total += address & 0xFF
    total += record_type
    total += sum(data_bytes)

    return ((~total + 1) & 0xFF)

def save_q2_14_to_intel_hex(arr, filename):
    """
    Convert float array to Q2.14 and save as Intel HEX.

    Each Q2.14 value is stored as 2 bytes.
    This version writes little-endian bytes:
    low byte first, high byte second.
    """
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    q_values = [float_to_q2_14(v) for v in arr.flatten()]

    address = 0

    with open(filename, "w") as f:
        for chunk_start in range(0, len(q_values), 16):
            chunk = q_values[chunk_start:chunk_start + 16]

            data_bytes = []

            for q in chunk:
                word = q & 0xFFFF

                # little-endian storage
                low_byte = word & 0xFF
                high_byte = (word >> 8) & 0xFF

                data_bytes.append(low_byte)
                data_bytes.append(high_byte)

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

        # EOF record
        f.write(":00000001FF\n")

data = np.load("training/trained_dnn.npz")

print("Keys in the archive:")
print(data.files)

save_q2_14_to_intel_hex(data["predictor/l1/W"], "weights_biases/w1.hex")
save_q2_14_to_intel_hex(data["predictor/l1/b"], "weights_biases/b1.hex")
save_q2_14_to_intel_hex(data["predictor/l2/W"], "weights_biases/w2.hex")
save_q2_14_to_intel_hex(data["predictor/l2/b"], "weights_biases/b2.hex")
save_q2_14_to_intel_hex(data["predictor/l3/W"], "weights_biases/w3.hex")
save_q2_14_to_intel_hex(data["predictor/l3/b"], "weights_biases/b3.hex")

