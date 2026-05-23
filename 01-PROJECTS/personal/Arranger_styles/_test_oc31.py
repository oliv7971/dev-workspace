from tools.oc31 import oc31_compress, oc31_decompress
import time

# Test 1: repetitive data (worst case for old code)
data = b'\x00\x01\x02' * 17392  # ~52KB
t = time.time()
c = oc31_compress(data)
elapsed = time.time() - t
print(f'Test 1: {len(data)}→{len(c)} bytes in {elapsed:.2f}s')
d = oc31_decompress(c)
print('  roundtrip:', d == data)

# Test 2: random-ish data
import struct
data2 = bytes(range(256)) * 204 + bytes(range(48))  # ~52KB
t = time.time()
c2 = oc31_compress(data2)
elapsed2 = time.time() - t
print(f'Test 2: {len(data2)}→{len(c2)} bytes in {elapsed2:.2f}s')
d2 = oc31_decompress(c2)
print('  roundtrip:', d2 == data2)
