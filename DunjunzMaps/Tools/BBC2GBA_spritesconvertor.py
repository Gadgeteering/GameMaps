#!/usr/bin/env python
from PIL import Image
import time
import os, sys
import numpy as np
import UEFfile
import dunjunz
import PIL.Image
sys.modules['PIL.PyAccess'] = PIL.Image
import matplotlib.pyplot as plt
import hqx


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
    "H_DOOR":      0x06,
    "V_DOOR":      0x04,
    "WALL":        0x02,
    "BLANK":       0x00,
    "ARMOUR":      0x18,
    "CRUCIFIX":    0x34,
    "KEY":         0x30,
    "FOOD":        0x32,
    "DAGGER":      0x1E,
    "WEAPONS":     0x22,
    "HELMET":      0x36,
    "EXIT":        0x38,
    "TRAPDOOR":    0x1A,
    "TREASURE":    0x08,
    "BOOTS":       0x48,
    "TELEPORT":    0x40,
    "POTION":      0x4A
}

img_seq = {
   "BLANK",
    "WALL",
    "V_DOOR",
    "H_DOOR",
    "TREASURE",
    "TREASURE",
    "TRAPDOOR",
    "DRAINER",
    "DRAINER",
    "SWORD",
    "SWORD",
    "WEAPONS",
    "KEYS",
    "FOOD",
    "CRUCIFIX",
    "ARMOUR",
    "EXIT",
    




}



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
    
        sys.stderr.write("Usage: %s <file.euf> \n" % sys.argv[0])
        sys.exit(1)
    u = UEFfile.UEFfile(sys.argv[1])
    tile_size = (16, 16)
    input_dir = sys.argv[1]
    output_dir = os.path.join(os.path.dirname(sys.argv[2]), "levels")
    output_file = os.path.join(output_dir, "palette_tile.h")
    if not os.path.exists(output_dir):
            os.mkdir(output_dir)
    for details in u.contents:
        details["name"] = details["name"].decode('utf-8').capitalize()
        if details["name"] == "Dunjunz":
            sprites = dunjunz.Sprites(details["data"].decode('latin-1'))
            break
    tiles = 81
    sprite_tiles= Image.new("RGB", (tile_size[0]*6,tile_size[1]*4) , 0)
    num = 1
    
    # Create a reverse lookup for the loop
    id_to_name = {v: k for k, v in gba_tile_type.items()}

    max_id = max(gba_tile_type.values()) # 0x4A (74)

    for i in range(0, max_id + 2): # Stepping by 2 if your tiles are 16-bit aligned
        if i in id_to_name:
            image_name = id_to_name[i]

        else:
            image_name ="exp3"

        
        image_name = image_name.lower()
        im = sprites.sprites[image_name].image(size =(8,12))
        im = im.resize(tile_size, resample=Image.Resampling.NEAREST)
        sprite_tiles.paste(im, (0, num * tile_size[1]))
        num += 1

    
    
    
    sprite_tiles = sprite_tiles.convert("P")
    palette = sprite_tiles.getpalette()[:768]
    pixels = np.array(sprite_tiles)
    plt.imshow(pixels, cmap='gray') 
    plt.colorbar() # Shows which index corresponds to which color
    plt.show()
    pixels_test = np.zeros(shape=(8,8))
    height, width  = pixels.shape
    print(height,width)
    addr = 0
    with open(output_file, 'w') as f:
        f.write("#ifndef TILES_H\n#define TILES_H\n\n")
        f.write(f"// Total Unique Tiles: {height // 8}\n")
        
        # 1. Write Tiles (8x8 blocks)
        f.write("const unsigned char exptilesData[] = {\n")
        for ty in range(0, height, 8):
            f.write(f"    // Tile {ty//8:02X}\n    ")
            for tx in range(0,width,8):
                for y in range(8):
                    for x in range(8):
                        # We use [ty + y] for the vertical pixel row 
                        # and [x] for the horizontal pixel column
                        pixel_idx = pixels[ty + y][x + tx]
                        pixels_test [y][x] = pixels[y][x]
                        f.write(f"0x{pixel_idx:04X}, ")
                        addr += 1
                        
                        if addr == 0x30:    
                            plt.imshow(pixels_test, cmap='gray') 
                            plt.colorbar() # Shows which index corresponds to which color
                            plt.show()
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

    
    print("Saved %s." % os.path.join(output_dir, f"levelmaps.h"))
    
    sys.exit()

