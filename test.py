import struct

hex_data = "0f5c6bbe8bb6263d875624c10000c0bfcdcca0c133b3e3423f83be3d3a1388bcd87d2341f9ab52bc6c808a3cb7959a3d0bcb8c41e36d4141feab3e410000"
raw = bytes.fromhex(hex_data)

floats = []
for i in range(0, len(raw) - (len(raw) % 4), 4):
    chunk = raw[i:i+4]
    value = struct.unpack("<f", chunk)[0]   # little-endian float32
    floats.append(value)

for idx, value in enumerate(floats):
    print(idx, value)