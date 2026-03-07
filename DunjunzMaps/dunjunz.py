#!/usr/bin/env python

"""
dunjunz.py - Classes and functions for extracting data from Dunjunz.

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

import sys
from PIL import Image


def unscramble_data(data):
    new_data = []
    for i in range(len(data)):
        new_data += bytes([(data[i]) ^ (i % 256)])

    return new_data


checksums = [0x62, 0xcd, 0x0c, 0x44, 0x4d, 0x22, 0xf6, 0x42,
             0x21, 0x7d, 0x5d, 0xd8, 0xa0, 0xf1, 0x0f, 0xcc,
             0xd3, 0x53, 0x3b, 0x83, 0x71, 0xb2, 0x6f, 0xf3,
             0xf1]

def add_checksum(level_number, data):

    """Accepts a complete set of level data and calculates the appropriate
    value to replace the last byte with in order to make the calculated
    checksum for the data match the one stored in the game itself. The data
    must be scrambled after this value has been added."""
    
    total = 0

    for i in range(len(data) - 1):
        
        total += data[i]
    
    total = total & 0xff
    
    c = checksums[level_number - 1]
    if c < total:
        v = 0x100 + c - total
    else:
        v = c - total
    return v


def read_bits(byte):

    bits = []
    i = 128
    while i > 0:
    
        if byte & i == i:

            bits.append(1)
        else:
            bits.append(0)
        
        i = i >> 1
    return bits

from PIL import Image

def decode_mode5_sprite(data, width_px, height_px):
    """
    Decodes raw BBC Micro MODE 5 sprite data into a Pillow Image.
    MODE 5: 4 colors (2 bits/pixel), stored in 8x8 character cell blocks.
    """
    # Create an RGB image
    img = Image.new('RGB', (width_px, height_px))
    pixels = img.load()

    # Standard MODE 5 Palette (Logical 0-3)
    palette = {
        0: (0, 0, 0),       # Black
        1: (255, 0, 0),     # Red
        2: (255, 255, 0),   # Yellow
        3: (255, 255, 255)  # White
    }

    # Iterate through character cells (8x8 pixels)
    # In Mode 5, a cell is 8 bytes. One byte = 4 pixels.
    cells_across = width_px // 4
    cells_down = height_px // 8  
    ptr = 0
    for cy in range(cells_down):
        for cx in range(cells_across):
            # Process one 8x8 cell (8 bytes)
            for row in range(8):
                if ptr >= len(data): break
                byte_val = data[ptr]
                ptr += 1
                
                # Extract 4 pixels from the byte (Bit-interleaved)
                for p in range(4):
                    # Bit p = low, Bit p+4 = high
                    low = (byte_val >> p) & 1
                    high = (byte_val >> (p + 4)) & 1
                    color_idx = low | (high << 1)
                    
                    # Calculate target coordinates
                    x = (cx * 4) + p
                    y = (cy * 8) + row
                    pixels[x, y] = palette[color_idx]

    return img



class Level:

    def __init__(self, data, level_number, scrambled = True):
    
        if scrambled:
            data = unscramble_data(data)
            #if add_checksum(level_number, data) != 0:
                #print("Data unscrambled unsuccessfully.")
                #exit(1)
         
        self.read_data(data)
    
    def read_data(self, data):
    
        self.lookup = {}
        self.teleporters = []
        
        for i in range(1, 0x20):
        
            x = data[i]
            y = data[0x20 + i]
            t = data[0x40 + i]
            if t != 0xff:
                self.lookup[(x, y)] = t
                if t == 0x2b:
                    self.teleporters.append((x, y))
        
        self.doors = {}
        
        for i in range(1, 21):
        
            x = data[0x60 + i]
            y = data[0x75 + i]
            o = data[0x8a + i]
            if x != 0xff and y != 0xff and o != 0xff:
                self.doors.setdefault((x, y), []).append((i, o))
        
        self.keys = {}
        
        for i in range(1, 21):
        
            x = data[0xa0 + i]
            y = data[0xb5 + i]
            if x != 0xff and y != 0xff:
                self.keys.setdefault((x, y), []).append(i)
        
        self.trapdoors = set()
        
        for i in range(8):
        
            x = data[0xd0 + i]
            y = data[0xd8 + i]
            self.trapdoors.add((x, y))
        
        self.solid = []
        self.collectables = []
       
        for row in range(48):     

            r = ((row//8) * 0x20) + (row % 8)
            solid_row = []
            collectables_row = []
            
            for column in range(0, 32, 8):
                solid_row += read_bits(data[0xe0 + r + column])
                
                collectables_row += read_bits(data[0x1b0 + r + column])
            self.solid.append(solid_row)
            self.collectables.append(collectables_row)
        
        # Read the wall tile for the level.
        self.wall_sprite = Sprite(data[-48:-24])
        
        self.exit_x = data[0x1e]
        self.exit_y = data[0x3e]
    
    def is_solid(self, row, column):
        return self.solid[row][column] != 0
    
    def is_collectable(self, row, column):
        return self.collectables[row][column] == 0


class Sprite:

    def __init__(self, data):
    
        self.data = self.read_sprite(data)
    
    def read_columns(self, byte):
    
        columns = []
        byte = ord(byte) if isinstance(byte, str) else byte
        for i in range(4):

            v = (byte & 0x01) | ((byte & 0x10) >> 3)
            byte = byte >> 1
            columns.append(v)

    
        columns.reverse()
        return "".join(map(chr, columns))
    
    def read_sprite(self, tile):
    
        sprite = ""
        
        i = 0
        while i < 24:
            sprite += self.read_columns(tile[i]) + self.read_columns(tile[i + 1])
            i += 2
        
        return sprite
    
    def image(self, size = None):
    
        im = Image.frombytes("P", (8, 12), self.data.encode('latin-1'))
        im.putpalette((0,0,0, 255,0,0, 0,255,0, 255,255,255))
        if size != None:
            im = im.resize(size, Image.NEAREST)
        return im


class Sprites:

    sprite_names = {
        0x0140: ("boots", "armour", "potion", "dagger", "weapons", "crucifix"),
        0x0e40: ("sword_up", "sword_right", "sword_down", "sword_left"),
        0x1100: ("ranger_left1", "skull0", "skull1", "skull2", "skull3", "skull4"),
        0x1910: ("drainer",),
        0x19e0: ("exit",),
        0x1a40: ("wizard_up0", "wizard_up1", "wizard_right0", "wizard_right1",
                 "wizard_down0", "wizard_down1", "wizard_left0", "wizard_left1",
                 "barbarian_up0", "barbarian_up1", "barbarian_right0", "barbarian_right1",
                 "barbarian_down0", "barbarian_down1", "barbarian_left0", "barbarian_left1",
                 "fighter_up0", "fighter_up1", "fighter_right0", "fighter_right1",
                 "fighter_down0", "fighter_down1", "fighter_left0", "fighter_left1",
                 "fireball_up", "fireball_right", "fireball_down", "fireball_left",
                 "axe_up", "axe_right", "axe_down", "axe_left",
                 "key", "treasure", "food"),
        0x2100: ("teleport",),
        0x2208: ("v_door",),
        0x2240: ("exp0", "exp1", "exp2", "exp3", "trapdoor"),
        0x2340: ("arrow_up", "arrow_right", "arrow_down", "arrow_left", "h_door"),
        0x2440: ("block", "ranger_up0", "ranger_up1", "ranger_right0", "ranger_right1",
                 "ranger_down0", "ranger_down1", "ranger_left0",
                 "enemy_up0", "enemy_up1", "enemy_right0", "enemy_right1",
                 "enemy_down0", "enemy_down1", "enemy_left0", "enemy_left1"),
        }
    
    def __init__(self, data):
    
        self.data = data
        self.sprites = {}
        self.read_all(data)
        self.sprites["blank"] = Sprite("\x00" * 8 * 12)
    
    def read_all(self, data):
    
        for base, names in self.sprite_names.items():
            print("Reading sprites at offset %04x..." % base)
            print("Sprites: %s" % ", ".join(names))
            for s in range(len(names)):
            
                offset = base + (s * 48)
                sprite = Sprite(data[offset:offset + 0x18])
                self.sprites[names[s]] = sprite
