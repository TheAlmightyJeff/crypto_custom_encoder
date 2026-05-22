![img](assets/banner.png)

<img src='assets/htb.png' style='zoom: 80%;' align=left /> <font size='10'>Custom Encoder</font>

22<sup>nd</sup> May 2026

Prepared By: `Tobias`

Challenge Author(s): `Tobias`

Difficulty: <font color='green'>Very Easy</font>

<br><br>

# Synopsis (!)

To solve this challenge, the user must write a reverse-engineering script in Python that undoes a series of deterministic encoding layers applied to a target flag string. The layers must be decoded in the exact reverse order of their application: standard Ascii85 decoding, custom Base64 alphabet translation, standard Base64 decoding, symmetric bitwise XOR, and symmetric ROT47 rotation (using the slightly optimized offset logic).

## Description (!)

An operator managed to capture an encoded string along with the Python routine used to mask it. The encoding pipeline seems to apply standard algorithms but with non-standard configurations. Can you reverse the flow and recover the flag?

## Skills Required (!)

- Basic Python programming
- Understanding of encoding types (Base64, Ascii85)
- Familiarity with symmetric data transformations (XOR, ROT47)

## Skills Learned (!)

- Learn how to map and invert a custom substitution alphabet in Python using translation tables.
- Learn how to identify and match modified execution parameters (such as collapsed ROT47 mathematical offsets) in a reverse engineering pipeline.
- Understand the symmetric property of XOR and ROT47 algorithms where encryption and decryption logic are identical.

# Enumeration (!)

## Analyzing the source code (*)

When you unzip the challenge zip file, you are provided with two primary files inside the release directory:
- `source.py`: The Python script containing the configuration arrays, obfuscated logic routines, and execution handles.
- `output.txt`: A single-line text file containing the final encoded flag string payload.

If we look at `source.py`, we can see that our goal is:
- Understand the sequential layout of the transformation pipeline.
- Extract the configuration arrays (`_BASE_STD` and `_BASE_CUST`) and resolve the obfuscated `XOR_KEY` mask value.
- Re-implement the symmetric functions natively to process the cipher text backwards.

The basic workflow of the script is as follows:
1. The script reads cleartext characters from a private asset file named `FLAG`.
2. The flag string undergoes a visual structural shift via the modified `custom_rot47()` mechanism using an optimized `+ 14` math shortcut.
3. The rotated text is obfuscated using lambda mappings against a bitwise mask value calculated dynamic via `sum([0x10, 0x10, 0x05])` (resolving to `0x25`).
4. The output is processed through standard Base64 encoding (utilizing a dynamic string replacement trick to define `'utf-8'`) and immediately translated into a customized alphabet mapping sequence via `bytes.maketrans()`.
5. The scrambled string is packed into its final format using the standard `base64.a85encode()` function and printed.

A little summary of all the interesting things we have found out so far:
1. The pipeline relies completely on deterministic steps with no randomized initialization vectors (IVs) or dynamic keys.
2. The `custom_rot47` mechanism loops cleanly over standard printable ASCII blocks (range 33 to 126), making it its own mathematical inverse even with the visually shifted conditional bounds (`if not (ascii_val < 33 or ascii_val > 126)`).
3. The bitwise `XOR` operation with key `0x25` is completely symmetric; running the output bytes back through the same block flips the bits back to their precise initial state.

# Solution (!)

## Finding the vulnerability (*)

This challenge does not contain an exploitation vulnerability. Instead, it is a cryptography/reverse-engineering puzzle. The security weakness is the use of static, symmetric encoding operations without strong cryptographic primitives or private keys. Because the entire generation routine along with the unique alphabet substitution map is provided directly in `source.py`, the cipher text can be perfectly parsed backward step-by-step to expose the hidden plaintext flag.

## Exploitation (!)

### Connecting to the server (*)

This challenge does not require an active runtime docker instance. It is a static downloadable challenge.

Let us consider our attack scenario.
1. Read the raw cipher text string from the distributed `output.txt` asset file.
2. Undo the outer container format by applying a standard Ascii85 decoding loop.
3. Align the jumbled character structure back to traditional compliance by building an inverse mapping array via `bytes.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)`.
4. Run a standard Base64 parse loop against the aligned bytes.
5. Re-apply bitwise XOR processing against the `0x25` constant mask value.
6. Re-apply the exact matching `custom_rot47` loop block from the source file to restore the original ASCII coordinates.

The attack explained above can be implemented with the following code:

```python
def custom_xor(text: str, key: int) -> str:
    return "".join(chr(ord(char) ^ key) for char in text)

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
```

### Getting the flag (!)

A final summary of all that was said above:
1. Read the input payload sequence from the `output.txt` file descriptor.
2. Step backward dynamically through the structural layers using our custom solution setup.

This recap can be represented by code using `pwn()` function:

```python
def pwn():
    import base64

    CUSTOM_ALPHABET = b"XYZABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789+/}{"
    STANDARD_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/{}"
    DECODE_TRANS = bytes.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)
    XOR_KEY = 0x00000025

    with open("output.txt", "r") as file:
        encrypted = file.read().strip()

    layer_4 = base64.a85decode(encrypted.encode('utf-8'))
    layer_3 = layer_4.translate(DECODE_TRANS)
    layer_2 = base64.b64decode(layer_3).decode('utf-8')
    layer_1 = custom_xor(layer_2, XOR_KEY)
    flag = custom_rot47(layer_1)

    print(f"[+] Final flag: {flag}")

if __name__ == "__main__":
    pwn()
```

## Flag
`HTB{m1nim4l_0bfusc4ti0n_is_n0t_3n0ugh}`
