def hex_cmp(file1_path,):
    with open(file1_path, 'rb') as f1:
        
        offset = 0
        while True:
            # Read one byte at a time
            b1 = f1.read(1)  
            
            # Stop if both files end
            if not b1:
                break
            b2=0
            # Handle files of different lengths
            if b1 != b2:
                val1 = b1.hex().upper() if b1 else "--"

                
                # Format: Offset (Hex): File1_Byte File2_Byte
                line = f"{offset:08X}: {val1}\n"

                print(line, end="") # Also print to console
            
            offset += 1

# Execute the comparison
hex_cmp('SCREEN_3280_3280.bin')
