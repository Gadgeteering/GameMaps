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


sys.modules['PIL.PyAccess'] = PIL.Image

import hqx


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

    if (row, column) == (11, 11):
        return "ranger_up1", "Ranger"
    elif (row, column) == (12, 11):
        return "wizard_right1", "Wizard"
    elif (row, column) == (11, 12):
        return "barbarian_down1", "Barbarian"
    elif (row, column) == (12, 12):
        return "fighter_left1", "Fighter"
    
    elif (column, row) in level.keys:
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
            print(name)
            return name, None
    
    else:
        return "blank", None


if __name__ == "__main__":

    if len(sys.argv) != 5:
    
        sys.stderr.write("Usage: %s <Dunjunz level binary file> <level> <sprite><output directory>\n" % sys.argv[0])
        sys.exit(1)
    
    level_number = int(sys.argv[3])
    if not 1 <= level_number <= 25:
    
        sys.stderr.write("Please specify a level from 1 to 25.\n")
        sys.exit(1)
    

   
    output_dir = sys.argv[4]
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    

    f = open(os.path.join(sys.argv[1]), "rb")
    data = f.read()
    f.close()
    level = dunjunz.Level(data,level_number)
    f = open(os.path.join(sys.argv[2]), "rb")
    data = f.read()
    f.close()
    sprites = dunjunz.Sprites(data)

    f = open(os.path.join(output_dir, "index.html"), "w")
    f.write("<html>\n<head><title>Dunjunz Level %i</title></head>\n" % level_number)
    f.write("<body>\n<h1>Dunjunz Level %i</h1>\n" % level_number)
    f.write('<table cellpadding="0" cellspacing="0">\n')
    
    for row in range(48):
    
        f.write("<tr>\n")
        
        for column in range(32):
            if extra != None:
                f.write('<td><img src="%s.bmp" alt="%s" /></td>\n' % (image_name, ",".join(map(str, extra))))
            else:
                f.write('<td><img src="%s.bmp" /></td>\n' % image_name)
        
        f.write("</tr>\n")
    
    f.write("</table>\n<body>\n<html>\n")
    
    for name, sprite in sprites.sprites.items():
        img = sprite.image().convert("RGB")
        upscaled = hqx.hq4x(img)
        upscaled.show()
        exit(1)
        upscaled.save(os.path.join(output_dir, name + ".bmp"))
    img = level.wall_sprite.image().convert("RGB")
    upscaled = hqx.hq4x(img)
    upscaled.save(os.path.join(output_dir, "%02i.bmp" % level_number))
    sys.exit()
