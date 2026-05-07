def read_intel_hex_q2_14(filename):
    words = []
    with open(filename) as f:
        for line in f:
            if line.startswith(':'):
                byte_count = int(line[1:3], 16)
                if byte_count == 0:  # EOF record
                    break
                data_str = line[9:9+byte_count*2]
                for i in range(0, len(data_str), 4):
                    lo = int(data_str[i:i+2], 16)
                    hi = int(data_str[i+2:i+4], 16)
                    w = (hi << 8) | lo
                    if w & 0x8000:
                        w -= 0x10000
                    words.append(w / 16384.0)
    return words

# Compare with your original floats
floats = read_intel_hex_q2_14("weights_biases/w1.hex")
print(floats[:16])