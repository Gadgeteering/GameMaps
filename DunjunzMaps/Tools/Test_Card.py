def generate_beeb_mode2_test_file(filename="test_mode2.bin"):
    # Length &4D80 = 19,840 bytes (Commonly 31 rows of 8x8 cells)
    TOTAL_BYTES = 0x4D80 
    data = bytearray(TOTAL_BYTES)

    # 160 pixels / 8 pixels per cell = 20 cells across
    # 19840 bytes / 32 bytes per cell / 20 cells across = 31 cells down
    CELLS_ACROSS = 20
    CELLS_DOWN = 31

    def encode_mode2_byte(color_idx1, color_idx2):
        """Encodes two 4-bit colors into one interleaved MODE 2 byte."""
        byte = 0
        for i in range(4):
            # Pixel 0 (left) bits at 0, 2, 4, 6
            byte |= ((color_idx1 >> i) & 1) << (i * 2)
            # Pixel 1 (right) bits at 1, 3, 5, 7
            byte |= ((color_idx2 >> i) & 1) << (i * 2 + 1)
        return byte

    ptr = 0
    for cy in range(CELLS_DOWN):
        for cx in range(CELLS_ACROSS):
            # Determine color for this vertical column of cells (0-7)
            # This creates 8 vertical bars across the 20-cell width
            color = (cx // (CELLS_ACROSS // 8)) % 8
            
            # Each cell has 8 rows, each row has 4 bytes (for 8 pixels)
            for row in range(8):
                for b in range(4):
                    if ptr < TOTAL_BYTES:
                        # Fill each byte with two identical color pixels
                        data[ptr] = encode_mode2_byte(color, color)
                        ptr += 1

    with open(filename, "wb") as f:
        f.write(data)
    print(f"File '{filename}' generated. Size: {len(data)} bytes (&{len(data):X})")

generate_beeb_mode2_test_file()
