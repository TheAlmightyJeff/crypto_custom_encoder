import base64
import os

# Alphabets used in the challenge
CUSTOM_ALPHABET = b"XYZABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789+/}{"
STANDARD_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/{}"

# REVERSE TRANSFORMATION: Map the custom alphabet back to the standard one
DECODE_TRANS = bytes.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)
XOR_KEY = 0x00000025

def custom_xor(text: str, key: int) -> str:
    # XOR is its own inverse
    return "".join(chr(ord(char) ^ key) for char in text)

def custom_rot47(text: str) -> str:
    # Updated to perfectly mirror the obfuscated function in source.py
    result = []
    for char in text:
        ascii_val = ord(char)
        if not (ascii_val < 33 or ascii_val > 126):
            shifted = 33 + ((ascii_val + 14) % 94)
            result.append(chr(shifted))
        else:
            result.append(char)
    return "".join(result)

def challenge_decoder(encrypted_string: str) -> str:
    # Step 1: Undo Ascii85 encoding
    custom_b64 = base64.a85decode(encrypted_string.encode('utf-8'))
    
    # Step 2: Swap the custom alphabet back to standard Base64
    standard_b64 = custom_b64.translate(DECODE_TRANS)
    
    # Step 3: Undo standard Base64 encoding
    layer_2 = base64.b64decode(standard_b64).decode('utf-8')
    
    # Step 4: Undo XOR operation
    layer_1 = custom_xor(layer_2, XOR_KEY)
    
    # Step 5: Undo ROT47 to recover the flag
    flag = custom_rot47(layer_1)
    
    return flag

# Read from the output file
with open("output.txt", "r") as file:
    encrypted = file.read().strip()
    
print(f"Final flag: {challenge_decoder(encrypted)}")
input()
