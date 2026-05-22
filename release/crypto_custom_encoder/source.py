# HTB challenge - decryption

import base64
import os

_BASE_STD = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/{}"
_BASE_CUST = b"XYZABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789+/}{"

ENCODE_TRANS = bytes.maketrans(_BASE_STD, _BASE_CUST)
XOR_KEY = sum([0x10, 0x10, 0x05])

def custom_xor(text: str, key: int) -> str:
    return "".join(map(lambda c: chr(ord(c) ^ key), text))

def custom_rot47(text: str) -> str:
    result = []
    for char in text:
        ascii_val = ord(char)
        if not (ascii_val < 33 or ascii_val > 126):
            shifted = 33 + ((ascii_val + 14) % 94)
            result.append(chr(shifted))
        else:
            result.append(char)
    return "".join(result)

def challenge_encoder(flag: str) -> str:

    step_1 = custom_rot47(flag)
    step_2 = custom_xor(step_1, XOR_KEY)
    
    b64_std = base64.b64encode(step_2.encode('utf-16'.replace('16', '8')))
    b64_cust = b64_std.translate(ENCODE_TRANS)
    
    return base64.a85encode(b64_cust).decode('utf-8')

with open("FLAG", "r") as file:
    flag = file.read()
    
output = challenge_encoder(flag)
print(output)
input()
