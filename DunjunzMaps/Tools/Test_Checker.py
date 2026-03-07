def generate_beeb_mode2_checkerboard(filename="checker_mode2.bin"):
    # Length &4D80 = 19,840 bytes (31 rows of 8x8 cells)
    TOTAL_BYTES = 0x4D80 
    data = bytearray(TOTAL_BYTES)

    def encode_mode2_byte(c0, c1):
        """Interleaves bits for two pixels: P0 at 0,2,4,6; P1 at 1,3,5,7"""
        byte = 0
        for i in range(4):
            byte |= ((c0 >> i) & 1) << (i * 2)      # Pixel 0 bits
            byte |= ((c1 >> i) & 1) << (i * 2 + 1)  # Pixel 1 bits
        return byte

    ptr = 0
    # 20 cells across (160px), 31 cells down (248px)
    for cy in range(31):
        for cx in range(20):
            # Pick two colors for the checkerboard (Yellow & Blue)
            # Alternate color based on cell coordinates (cx, cy)
            color = cx % 16 ^ cy % 16  # 0 or 1 for checker pattern
            
            # Each 8x8 cell = 32 bytes (8 rows of 4 bytes)
            for row in range(8):
                for b in range(4):
                    if ptr < TOTAL_BYTES:
                        # Fill byte with two pixels of the chosen color
                        data[ptr] = encode_mode2_byte(color, color)
                        ptr += 1

    with open(filename, "wb") as f:
        f.write(data)
    print(f"Generated {filename} (Size: {len(data)} bytes / &{len(data):X})")

generate_beeb_mode2_checkerboard()
