import numpy as np

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

# def q2_14_to_float(q: int) -> float:
#     """
#     Convert a Q2.14 fixed‑point integer back to float.
#     The input is treated as a signed 16‑bit value (only lower 16 bits matter).
#     """
#     # Interpret as signed 16‑bit integer
#     if q & 0x8000:          # if sign bit is set (negative)
#         q = q - 0x10000     # two's complement: extend to 32-bit signed
#     return q / (2**14)      # 16384.0

print(float_to_q2_14(1.5))  # Should print 24576
print(float_to_q2_14(-1.5)) # Should print -24576
