import argparse

import os

import argparse

width = 32
height = 48
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()


# Get ROM bytes
with open(args.filename, "rb") as file:
    bytes = file.read()
    print(F"Read {len(bytes)} bytes from {args.filename}")

def xor_decode(data):
    """
    Decodes data where each byte is XORed with its position (modulo 256).
    """
    decoded_bytes = []
    
    for i, byte in enumerate(data):
        # Apply the XOR operation: new_byte = byte ^ (index % 256)
        new_byte = byte ^ (i % 256)
        decoded_bytes.append(new_byte)
        
    return decoded_bytes


data = xor_decode(bytes)
i = 0
for y in range(height):
    
    for x in range(width):
            print(hex(data[i]), end=":")
            i+=1
    print()
    
  

