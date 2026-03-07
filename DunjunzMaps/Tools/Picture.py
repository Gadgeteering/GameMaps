#!/usr/bin/env python
from PIL import Image
from PIL.Image import Resampling
import time
import os, sys
import numpy as np


def extract_tiles(image_path, output_dir,tile_width,tile_height, tolerance=0):
    print("Extracting start...")
    start_time = time.time()
    if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    # Load image and convert to RGB (or RGBA)
    GBA_WIDTH = 240
    GBA_HEIGHT = 160
    size =(240,160)
    graphics_file = open(os.path.join(output_dir, f"front.h"), "w")
    graphics_file.write("// Auto-generated level Graphics\n")   
    graphics_file.write(f"//Convert from  {image_path}\n")
    graphics_file.write("const u16 frontData[] =\n")
    graphics_file.write(f"{{\n")
    img = Image.open(image_path).convert('P')
    img=img.resize(size,Resampling.NEAREST)
    palette = img.getpalette()[:768]
    width, height = img.size
    print(f" Resized to Width:{width} Height:{height}")
    pixels = np.array(img, dtype=np.uint8)
    
    # 1. Write Pixel Data (Packed as u16)
    for y in range(height):
        for x in range(0, width, 2):
            p1 = pixels[y][x]
            p2 = pixels[y][x+1]
            packed = (p2 << 8) | p1
            graphics_file.write(f"0x{packed:04X},")
        graphics_file.write("\n")

    graphics_file.write("};\n\n")

    # 2. Write Palette Data
    graphics_file.write("const u16 frontPalette[] =\n{\n    ")
    if len(palette) < 768:
        palette.extend([0] * (768 - len(palette)))
        
    for i in range(0, 768, 3):
        r, g, b = palette[i], palette[i+1], palette[i+2]
        gba_color = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)
        graphics_file.write(f"0x{gba_color:04X}, ")
        if (i//3 + 1) % 8 == 0: graphics_file.write("\n    ")
    graphics_file.write("};\n")
    graphics_file.close()     
    end_time = time.time()
    duration = (end_time - start_time) * 1000 # ms
    
    print(f"Extraction complete in {duration:.2f}ms")

    return 






input_dir = "graphics/Screen.png"
output_dir = "graphics"
extract_tiles(input_dir, output_dir, 8, 8)


print("Done! Screen.h created.")


