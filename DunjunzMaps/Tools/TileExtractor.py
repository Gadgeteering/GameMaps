#!/usr/bin/env python
from PIL import Image
import time
import os, sys
import numpy as np


def extract_tiles(image_path, output_dir,tile_width,tile_height, tolerance=0):
    print("Extracting start...")
    start_time = time.time()
    if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    # Load image and convert to RGB (or RGBA)
    tiles = []  # Stores unique PIL Image objects
    num_cols = 64
    num_rows = 96
    num_levels = 3
    map_data_file = open(os.path.join(output_dir, f"levelmaps.h"), "w")
    map_data_file.write("// Auto-generated level maps\n")   
    map_data_file.write(f"#define  tiles_WIDTH   {num_cols}\n")
    map_data_file.write(f"#define  tiles_HEIGHT  {num_rows}\n")
    map_data_file.write(f"const u8 level[NUMBERLEVELS][ {num_cols} * {num_rows} ] = {{\n")
    map_data_file.write(f"{{\n")
    for level in range(1, num_levels + 1):
        tile_map = [] # Stores the index of the tile for each grid position
        
        image_path = "levels/Level_"+str(level)+".png"
        img = Image.open(image_path).convert('RGBA')
        print(f"Processing level {level}")
        for y in range(num_rows):
            for x in range(num_cols):
                # Define the box for the current tile
                left = x * tile_width
                top = y * tile_height
                right = left + tile_width
                bottom = top + tile_height
                # Crop the tile from the source
                current_tile = img.crop((left, top, right, bottom))
                current_tile_bytes = current_tile.tobytes()
                # Check if this tile already exists in our collection
                tile_index = -1
                for i, saved_tile in enumerate(tiles):
                    # Using tobytes() for a fast, exact comparison
                    if saved_tile.tobytes() == current_tile_bytes:
                        tile_index = i
                        break
                
                # If it's a new unique tile, save it
                if tile_index == -1:
                    tiles.append(current_tile)
                    tile_index = len(tiles) - 1
                
                tile_map.append(tile_index)

                # Optional progress print
                total_tiles = num_cols * num_rows
                current_count = len(tile_map)
                if current_count % 32 == 0:
                    print(f"Progress: {int((current_count / total_tiles) * 100)}%")
        for i in range(0, len(tile_map), 32):
                line = ", ".join(f"0x{index:02x}" for index in tile_map[i:i+32])
                map_data_file.write(f"  {line},\n")
        if level < num_levels:
                map_data_file.write("}, {\n")  
    map_data_file.write("}};\n")
    map_data_file.write("// shows which key fits in which door... ie. 1st door is key 5, 2nd key 2 etc\n")
    map_data_file.write("const int key_to_door_map_level [NUMBERLEVELS][MAX_KEYS_PER_LEVELS] = {\n")
    map_data_file.write("  {5, 2, 6, 8, 1, 7, 3, 4},\n")
    map_data_file.write("  {4, 3, 2, 1, 7, 6, 5, 8, 9, 20, 18, 12, 14, 15, 11, 19, 10, 13, 16, 17},\n")
    map_data_file.write("  {} // no doors for level 3\n")
    map_data_file.write("};\n")
    map_data_file.close()     
    end_time = time.time()
    duration = (end_time - start_time) * 1000 # ms
    
    print(f"Extraction complete in {duration:.2f}ms")
    print(f"Unique tiles found: {len(tiles)}")
    return tiles, tile_map



def convert_to_gba_header(img, output_file):
    # Ensure it's 8-bpp (Indexed Palette)
    img = img.convert('P')
    width, height = img.size
    pixels = np.array(img)
    palette = img.getpalette()[:768]
    
    with open(output_file, 'w') as f:
        f.write("#ifndef TILES_H\n#define TILES_H\n\n")
        f.write(f"// Total Unique Tiles: {height // 8}\n")
        
        # 1. Write Tiles (8x8 blocks)
        f.write("const unsigned char exptilesData[] = {\n")
        for ty in range(0, height, 8):
            f.write(f"    // Tile {ty//8}\n    ")
            for y in range(8):
                for x in range(8):
                    # We use [ty + y] for the vertical pixel row 
                    # and [x] for the horizontal pixel column
                    pixel_idx = pixels[ty + y][x]
                    f.write(f"0x{pixel_idx:02X}, ")
                f.write("\n    ")
        f.write("\n};\n\n")

        # If the palette is shorter than 768 bytes (256 * 3), fill the rest with black (0)
        if len(palette) < 768:
            palette.extend([0] * (768 - len(palette)))
        # 2. Write Palette (16-bit BGR555 for GBA)
        f.write("const unsigned short tilesPalette[256] = {\n    ")
        for i in range(0, 768, 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            # GBA Color format: 0RRRRRGGGGGBBBBB (but stored as BGR)
            gba_color = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)
            f.write(f"0x{gba_color:04X}, ")
            if (i//3 + 1) % 8 == 0: f.write("\n    ")
        f.write("\n};\n\n#endif")


input_dir = "levels"
output_dir = "extracted_tiles"

unique_tiles, map_data = extract_tiles(input_dir, output_dir, 8, 8)
num_tiles = len(unique_tiles)
print(f"Number of unique tiles: {num_tiles}")
tiles_temp = Image.new("RGBA", (8, 8 * num_tiles))
for i, tile in enumerate(unique_tiles):
    # Paste directly - tile is already 8x8
    tiles_temp.paste(tile, (0, 8 * i))
# 2. NOW generate the optimized 256-color palette from the combined image
tiles_indexed = tiles_temp.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
# Convert to P mode ONCE at the very end to generate the master palette
tiles_indexed.save("extracted_tiles/tiles.png")

# Pass the INDEXED image to the GBA converter
convert_to_gba_header(tiles_indexed, output_dir + "/palette_tile.h")
print("Done! map_data.h created.")


