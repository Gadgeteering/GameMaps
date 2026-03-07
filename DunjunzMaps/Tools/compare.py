def hex_cmp(file1_path, file2_path, output_path):
    with open(file1_path, 'rb') as f1, \
         open(file2_path, 'rb') as f2, \
         open(output_path, 'w') as out:
        
        offset = 0
        while True:
            # Read one byte at a time
            b1 = f1.read(1)
            b2 = f2.read(1)
            
            # Stop if both files end
            if not b1 and not b2:
                break
            
            # Handle files of different lengths
            if b1 != b2:
                val1 = b1.hex().upper() if b1 else "--"
                val2 = b2.hex().upper() if b2 else "--"
                
                # Format: Offset (Hex): File1_Byte File2_Byte
                line = f"{offset:08X}: {val1} {val2}\n"
                out.write(line)
                print(line, end="") # Also print to console
            
            offset += 1

# Execute the comparison
hex_cmp('DUN1_2000_2000.bin', 'tmp/DUNJUNZ.bin', 'note.txt')
