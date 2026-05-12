def read_mif_q8_8(filename):
    words = []
    in_content = False

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            # Remove comments
            if "--" in line:
                line = line.split("--")[0].strip()

            if not line:
                continue

            if line.upper() == "CONTENT BEGIN":
                in_content = True
                continue

            if line.upper() == "END;":
                break

            if in_content and ":" in line:
                # Example line:
                # 000A : FF80;
                parts = line.split(":")
                data_part = parts[1].strip().rstrip(";").strip()

                try:
                    word = int(data_part, 16)
                except ValueError:
                    continue

                # Interpret as signed 16-bit two's complement
                if word & 0x8000:
                    word -= 0x10000

                # Q8.8 dequantization
                words.append(word / 256.0)

    return words


# Compare with original floats
floats = read_mif_q8_8("weights_biases/b1.mif")
print(floats[:16])