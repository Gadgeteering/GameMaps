from PIL import Image

def bmp_to_gba_bin(input_path, output_path):
    with Image.open(input_path) as img:
        # 1. GBA sprites must be indexed (usually 8-bit for 256 colours)
        if img.mode != "P":
            img = img.convert("P")
            
        # 2. Extract Raw Pixel Data (as bytes)
        # Note: GBA expects tiles in 8x8 blocks. If your BMP is a single 
        # large image, you may need to rearrange the bytes into 
        # tiled order first.
        raw_data = img.tobytes()
        
        # 3. Extract and convert Palette (Optional)
        # GBA palette uses 16-bit BGR555 entries.
        palette = img.getpalette()[:768] # Get first 256 RGB triplets
        gba_palette = bytearray()
        for i in range(0, len(palette), 3):
            r, g, b = palette[i:i+3]
            # Convert 8-bit RGB to 5-bit BGR
            val = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)
            gba_palette.extend(val.to_bytes(2, 'little'))

        # 4. Save Sprite Data
        with open(output_path, "wb") as f:
            f.write(raw_data)
        
        # 5. Save Palette Data
        with open(output_path.replace(".bin", ".pal"), "wb") as f:
            f.write(gba_palette)

#
#  Usage
bmp_to_gba_bin("ranger_down0.bmp", "sprite.bin")
