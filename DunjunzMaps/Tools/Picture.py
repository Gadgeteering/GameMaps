#!/usr/bin/env python3
import sys,os
import UEFfile
import dunjunz
#import PIL.Image
from PIL import Image
#sys.modules['PIL.PyAccess'] = PIL.Image


def beeb_mode5_to_image(raw_data):
    #Acorn Electron Version: MODE 5
    # MODE 5 is 160x256 pixels. It uses 10KB (10240 bytes).
    width, height = 160, 256
    img = Image.new('RGB', (width, height))
    pixels = img.load() 

    # Default MODE 5 Palette (Logical 0-3)
    palette = {
        0: (0, 0, 0),       # Black
        1: (255, 0, 0),     # Red
        2: (255, 255, 0),   # Yellow
        3: (255, 255, 255)    # White
    }

    # Memory is organized in 8x8 character cells
    # Each cell is 8 bytes. One byte = 4 pixels (2 bits each).
    # MODE 5 is 20 cells wide (20 * 8 pixels = 160)
    for cell_y in range(32):       # 256 / 8 = 32 cells high
        for cell_x in range(20):   # 160 / 8 = 20 bytes wide (4px each * 2)
            for row in range(8):   # 8 rows per cell
                
                # Calculate memory offset for this specific 4-pixel row
                addr = (cell_y * 20 * 8) + (cell_x * 8) + row
                if addr >= len(raw_data): break

                byte_val = raw_data[addr]
                
                # Extract 4 pixels from the byte using bit-interleaving
                for p in range(4):

                    low = (byte_val >> p) & 1
                    high = (byte_val >> (p + 4)) & 1
                    color_idx = low | (high << 1)
                    
                    # Map to X, Y coordinates
                    x = (cell_x * 4) + p  # 4 pixels per byte in Mode 5
                    y = (cell_y * 8) + row
                    pixels[x, y] = palette[color_idx]

    return img 



def decode_beeb_mode2_image(raw_data):


    # 160x248 pixels (31 rows of 8x8 cells = 248 pixels high)
    width, height = 160, 248
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    palette = {
        0:(0,0,0), 1:(255,0,0), 2:(0,255,0), 3:(255,255,0),
        4:(0,0,255), 5:(255,0,255), 6:(0,255,255), 7:(255,255,255),
        8:(0,0,0), 9:(255,0,0), 10:(0,255,0), 11:(255,255,0),
        12:(0,0,255), 13:(255,0,255), 14:(0,255,255), 15:(255,255,255)
    }
    f = open("mode2_dump.txt", "w")
    # 20 cells across, 31 cells down
    for cell_y in range(31):
        for cell_x in range(20):
            # Each 8x8 cell is 32 bytes
            for row in range(8):
                # Each 8-pixel row within a cell is 4 bytes
                for b in range(4):
                    addr = (cell_y * 20 * 32) + (cell_x * 32) + (row * 4) + b
                    if addr >= len(raw_data): continue
                    
                    byte_val = raw_data[addr]
                    
                    # Extract 2 pixels: P0 (bits 0,2,4,6) and P1 (bits 1,3,5,7)
                    for p in range(2):
                        c0 = (byte_val >> (0 + p)) & 1
                        c1 = (byte_val >> (2 + p)) & 1
                        c2 = (byte_val >> (4 + p)) & 1
                        c3 = (byte_val >> (6 + p)) & 1
                        color_idx = c0 | (c1 << 1) | (c2 << 2) | (c3 << 3)
                        x = (cell_x * 4) + (row *2)+p
                        y = (cell_y * 8) + (b )

                        f.write(f"address {addr:04x} byte {byte_val:02x} p{p} b{b} Bits for pixel at ({x},{y}): {c3} {c2} {c1} {c0} -> Color Index {color_idx}\n")
                           
                        pixels[x, y] = palette[color_idx]
                        
    f.close()
    return img



if __name__ == "__main__":
    if len(sys.argv) != 3:
    
        sys.stderr.write("Usage: %s <Dunjunz UEF file> <output directory>\n" % sys.argv[0])
        sys.exit(1)
    
   
    output_dir = sys.argv[2]
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if sys.argv[1].endswith(".uef"):
        u = UEFfile.UEFfile(sys.argv[1])
        for details in u.contents:
            name = (details["name"].decode('utf-8'))
            
            if name == "DUNK":
                data =(details["data"])
                beeb_mode5_to_image(data).show()
                exit(1)
    elif sys.argv[1].endswith(".bin"):
        
        with open(sys.argv[1], "rb") as f:
            data = f.read()
            decode_beeb_mode2_image(data).show()
            exit(1)
        

    else:
        sys.stderr.write("Failed to find a suitable data file.\n")
        sys.exit(1)
    level = dunjunz.Level(details["data"],level_number)
    
    # Usage: Load your .dat or .bin screen dump
    with open("screen_dump.bin", "rb") as f:
        data = f.read()
        image = decode_beeb_mode5(data)
        image.save("output.png")
    sys.exit(1)
