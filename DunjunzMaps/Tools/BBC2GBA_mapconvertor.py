#!/usr/bin/env python
from PIL import Image
import time
import os, sys
import numpy as np
import UEFfile
import dunjunz
import matplotlib.pyplot as plt

type_map = {
    0x28: "TREASURE",
    0x29: "FOOD",
    0x2a: "CRUCIFIX",
    0x2b: "TELEPORT",
    0x51: "EXIT",
    0x53: "TRAPDOOR",
    0x5f: "BOOTS",
    0x60: "ARMOUR",
    0x61: "POTION",
    0x62: "WEAPONS",
    0x63: "DAGGER"
    }

gba_tile_type = {
    "H_DOOR":      0x04,
    "V_DOOR":      0x06,
    "WALL":        0x02,
    "BLANK":       0x00,
    "ARMOUR":   0x18,
    "CRUCIFIX":       0x34,
    "KEY":         0x30,
    "FOOD":        0x32,
    "DAGGER":       0x1E,
    "WEAPONS":     0x22,
    "HELMET":      0x36,
    "EXIT":        0x38,
    "TRAPDOOR": 0x1A,
    "TREASURE":    0x08,
    "BOOTS":       0x48,
    "TELEPORT":  0x40,
    "POTION":      0x4A
}




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

def get_image_name(level, level_number, row, column):

    """ if (row, column) == (11, 11):
        return "ranger_up1", None
    elif (row, column) == (12, 11):
        return "wizard_right1", None
    elif (row, column) == (11, 12):
        return "barbarian_down1", None
    elif (row, column) == (12, 12):
        return "fighter_left1", None """
    
    if (column, row) in level.keys:
        keys = level.keys[(column, row)]
        return "KEY", keys
    
    elif (column, row) in level.trapdoors:
        return "TRAPDOOR", None
    
    elif level.is_solid(row, column):
        if (column, row) in level.doors:
            doors = level.doors[(column, row)]
            # Just use the appropriate sprite for the first door found.
            n, o = doors[0]
            if o == 0x1d:
                return "V_DOOR", list(map(lambda x: x[0], doors))
            else:
                return "H_DOOR", list(map(lambda x: x[0], doors))
        else:
            return level_number, None
    
    elif level.is_collectable(row, column) and \
         (column, row) in level.lookup:
    
        name = type_map[level.lookup[(column, row)]]
        if name == "TELEPORT":
            return name, [level.teleporters.index((column, row)) + 1]
        else:
            return name, None
    
    else:
        return "BLANK", None


if __name__ == "__main__":

    if not 0 <= len(sys.argv) <= 52:
    
        sys.stderr.write("Usage: %s <BBC level dir> \n" % sys.argv[0])
        sys.exit(1)
    
    tile_size = (16, 16)
    input_dir = sys.argv[1]
    output_dir = os.path.join(os.path.dirname(sys.argv[2]), "levels")
    if not os.path.exists(output_dir):
            os.mkdir(output_dir)
    num_cols = 32
    num_rows = 48
    Doors = []
    Keys =[]
    Doors2Keys =[]
    max_level = 3
    map_data_file = open(os.path.join(output_dir, f"levelmaps.h"), "w")
    map_data_file.write("// Auto-generated level maps\n")   
    map_data_file.write(f"#define  tiles_WIDTH   {num_cols*2}\n")
    map_data_file.write(f"#define  tiles_HEIGHT  {num_rows*2}\n")
    map_data_file.write(f"const u8 level[NUMBERLEVELS][ {num_cols*2} * {num_rows*2} ] = {{\n")
    map_data_file.write("{\n")

    for level_number in range(1, max_level+1):
        output_file_name = os.path.join(output_dir, "Level_%i.png" % level_number)
        input_file_name = os.path.join(input_dir, "LEVEL%i_2700_2700.bin" % level_number)
        file = open(input_file_name, "rb") 
        map_data=file.read()
        file.close()
        
        level = dunjunz.Level(map_data,1)
        level_np = np.zeros((num_rows*2,num_cols*2), dtype=np.uint8)
        #Orignal Sprite were in a 6 x 4 
        for row in range(num_rows):
            for column in range(num_cols):
                image_name, extra = get_image_name(level, level_number, row, column)
                if image_name == "KEY":
                        n = extra[0]
                        Keys.append(n)
                if image_name == "V_DOOR" or image_name == "H_DOOR" :
                        n = extra[0]
                        Doors.append(n)
                if image_name == level_number:
                    gba_tile= gba_tile_type["WALL"]
                    level_np[row*2][column*2] = gba_tile
                    level_np[row*2][column*2+1] = gba_tile + 1
                    level_np[row*2+1][column*2] = gba_tile + 12
                    level_np[row*2+1][column*2+1] = gba_tile + 13

                else:             
                    im = Image.open(os.path.join("tmp", image_name + ".bmp"))
                    gba_tile= gba_tile_type[image_name]
                    level_np[row*2][column*2] = gba_tile
                    level_np[row*2][column*2+1] = gba_tile + 1
                    level_np[row*2+1][column*2] = gba_tile + 12
                    level_np[row*2+1][column*2+1] = gba_tile + 13


        Doors2Keys.append(f"//Level {level_number}\n")
        Doors2Keys.append("{")
        for K,Key in enumerate(Keys):
            Found = False
            for D,Door in enumerate(Doors):
           
                if Key == Door:
                    Doors2Keys.append(D+1)
                    Doors2Keys.append(",")
                    Found = True
                    break
            if Found == False:
                Doors2Keys.append(int(99))
                Doors2Keys.append(",")
                print("Door not found")
                exit(0)
        if len(Doors) !=0:
            Doors2Keys.pop()
        Doors2Keys.append("},\n")
        Doors.clear()
        Keys.clear()
        for row in range(num_rows*2):
            for column in range(num_cols*2):
                index= level_np[row][column]
                map_data_file.write(f"0x{index:02x},")
            map_data_file.write("\n")
        if level_number != max_level:
            map_data_file.write("},{\n")
    map_data_file.write("}\n")
    map_data_file.write("};\n")
    map_data_file.write("// shows which key fits in which door... ie. 1st door is key 5, 2nd key 2 etc\n")
    map_data_file.write("const int key_to_door_map_level [NUMBERLEVELS][MAX_KEYS_PER_LEVELS] = {\n")
    for line in Doors2Keys:
        map_data_file.write(str(line))
    map_data_file.write("};\n")
    map_data_file.close()    
    print("Saved %s." % os.path.join(output_dir, f"levelmaps.h"))
    
    sys.exit()

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


