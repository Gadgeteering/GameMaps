#!/usr/bin/env python

"""
htmlmap.py - Save a representation of a Dunjunz level to an HTML file.

Copyright (C) 2016 David Boddie <david@boddie.org.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os, sys
import UEFfile
import dunjunz
import PIL.Image
from PIL import Image
sys.modules['PIL.PyAccess'] = PIL.Image
import hqx

type_map_gba ={
    0x00: "",
    0x06: "H_DOOR", 
    0x04: "V_DOOR",
    0x02: "WALL",
    0x18: "GENERATOR",
    0x34: "CROSS",
    0x30: "KEY",
    0x32: "FOOD",
    0x1E: "SWORD",
    0x22: "WEAPONS",
    0x36: "HELMET",
    0x38: "EXIT",
    0x1A: "KILL_SQUARE",
    0x08: "TREASURE",
    0x48: "BOOTS",
    0x40: "TELEPORTER",
    0x4A: "POTION"
}




type_map = {
    0x28: "treasure",
    0x29: "food",
    0x2a: "crucifix",
    0x2b: "teleport",
    0x51: "exit",
    0x53: "drainer",
    0x5f: "boots",
    0x60: "armour",
    0x61: "potion",
    0x62: "weapons",
    0x63: "dagger"
    }

def get_image_name(level, level_number, row, column):

    """ if (row, column) == (11, 11):
        return "ranger_up1", "Ranger"
    elif (row, column) == (12, 11):
        return "wizard_right1", "Wizard"
    elif (row, column) == (11, 12):
        return "barbarian_down1", "Barbarian"
    elif (row, column) == (12, 12):
        return "fighter_left1", "Fighter" """
    
    if (column, row) in level.keys:
        keys = level.keys[(column, row)]
        return "key", keys
    
    elif (column, row) in level.trapdoors:
        return "trapdoor", "trapdoor"
    
    elif level.is_solid(row, column):
        if (column, row) in level.doors:
            doors = level.doors[(column, row)]
            # Just use the appropriate sprite for the first door found.
            n, o = doors[0]
            if o == 0x1d:
                return "v_door", map(lambda x: x[0], doors)


            else:
                return "h_door", map(lambda x: x[0], doors)
        else:
            return "%02i" % level_number, None
    
    elif level.is_collectable(row, column) and (column, row) in level.lookup:
    
        name = type_map[level.lookup[(column, row)]]
        
        if name == "teleport":
            return name, [level.teleporters.index((column, row))]
        else:
            return name, None
    
    else:
        return "blank", None


if __name__ == "__main__":

    if len(sys.argv) != 4:
    
        sys.stderr.write("Usage: %s <Dunjunz UEF file> <level> <output directory>\n" % sys.argv[0])
        sys.exit(1)
    
    level_number = int(sys.argv[2])
    if not 1 <= level_number <= 25:
    
        sys.stderr.write("Please specify a level from 1 to 25.\n")
        sys.exit(1)
    
    u = UEFfile.UEFfile(sys.argv[1])
    output_dir = sys.argv[3]
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    for details in u.contents:
        details["name"] = details["name"].decode('utf-8').capitalize()
        if details["name"] == "Dunjunz":
            sprites = dunjunz.Sprites(details["data"])
        
        elif details["name"] == "Level%i" % level_number:
            break
    else:
        sys.stderr.write("Failed to find a suitable data file.\n")
        sys.exit(1)
    print(details["data"])
    f = open(os.path.join(output_dir, "levelmap.h"), "w")
    f.write("<//Created by GBAmap.py\n")
    f.write("const u8 level[NUMBERLEVELS][ 32 * 48 ] = {\n")
    total_levels = 2
    for level_number in range(1, 2):
        level = dunjunz.Level(details["data"],level_number)         
    
    
        for row in range(48):
            for column in range(32):
                image_name, extra = get_image_name(level, level_number, row, column)
                for hex_code,name in type_map_gba.items():
                    print(name)
                    if image_name.isdigit():
                        idx = int(image_name)
                        f.write("0x%02X" % idx)
                        break
                    elif name == image_name.upper():
                        idx = hex_code
                        f.write("0x%02X" % idx)
                        break 
                if not (row == 47 and column == 31):
                    f.write(",")
        
                if column == 31:
                    f.write("\n")
        if level_number != total_levels-1:    
            f.write("},{\n")
        else:
            f.write("};\n")
        f.close()
tile_size = (8, 8)
large_tile_size = ( tile_size[0] * 4, tile_size[1] * 4)
tile_images = Image.new("P", ( tile_size[0],32 *   tile_size[1]), 0)
tile_images.putpalette((0,0,0, 255,0,0, 0,255,0, 255,255,255))
row = 0

for sprite_name, sprite in sprites.sprites.items():

            img = sprite.image(size = tile_size)
            print(img.size)
            #upscaled = hqx.hq4x(img)
            upscaled = img
            img.show()
            tile_images.paste(img, (tile_size[0], row * tile_size[1]))
            tile_images.show()
            exit(1)
            row += 1
tile_images.save(os.path.join(output_dir, name + ".png"))
tile_images.show()
exit(1)
row = 0
sprite_images = Image.new("P", ( large_tile_size[0],  large_tile_size[1]  * large_tile_size[1]), 0)
sprite_images.putpalette((0,0,0, 255,0,0, 0,255,0, 255,255,255))
for sprite_name, sprite in sprites.sprites.items():
    sprite_image = sprite.image().convert("RGB")
    if sprite_name.isdigit():
        im = level.wall_sprite.image(size = tile_size)
    else:
        im = sprites.sprites[sprite_name].image(size = tile_size)
    im = hqx.hq4x(im)
    sprite_images.paste(im, (0, row * large_tile_size[1]))
    row += 1
    print(sprite_name)
sprite_images.save(os.path.join(output_dir, "sprites.png"))
sprite_images.show()

    
sys.exit()
