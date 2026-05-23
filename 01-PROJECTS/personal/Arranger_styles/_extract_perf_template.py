"""
Extrait le premier objet StylePerformances (index 1) de BANK01.STY
et le sauvegarde dans tools/perf_template.bin.

Stratégie : lecture bas niveau sans décompresser l'objet 0 (Style).
"""
import struct, os, sys

BANK = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"

with open(BANK, 'rb') as f:
    data = f.read()

pos = 0

def u32be():
    global pos
    v = struct.unpack_from('>I', data, pos)[0]
    pos += 4
    return v

def read_bytes(n):
    global pos
    v = data[pos:pos+n]
    pos += n
    return v

def skip(n):
    global pos
    pos += n

# 1. Outer container chunk (type=1 Container)
raw_id = u32be(); size = u32be()
print(f"Outer container: type={raw_id>>24:#04x}, size={size}")

# 2. KorgFile chunk header (type=2) + data  → contains 'KORF' magic
raw_id = u32be(); korf_size = u32be()
print(f"KorgFile chunk: type={raw_id>>24:#04x}, size={korf_size}")
skip(korf_size)  # skip KorgFile data

# 3. TOC chunk header (type=5) + data
raw_id = u32be(); toc_size = u32be()
print(f"TOC chunk: type={raw_id>>24:#04x}, size={toc_size}")
skip(toc_size)  # skip TOC data

# 4. Objects: skip object 0 (Style), read object 1 (PERF)
# Object 0 (Style):
raw_id = u32be(); size0 = u32be()
chunk_type0 = raw_id >> 24
flags0 = raw_id & 0xFF
print(f"Object 0: type={chunk_type0:#04x}, size={size0}, flags={flags0:#04x}")
skip(size0)  # skip without decompressing

# Object 1 (PERF):
raw_id = u32be(); size1 = u32be()
chunk_type1 = raw_id >> 24
flags1 = raw_id & 0xFF
print(f"Object 1: type={chunk_type1:#04x}, size={size1}, flags={flags1:#04x}")
compressed_perf = read_bytes(size1)
print(f"  Compressed PERF bytes: {len(compressed_perf)}")

# Decompress
sys.path.insert(0, '.')
from tools.oc31 import oc31_decompress
perf_data = oc31_decompress(compressed_perf, verify_check=False)
print(f"  Decompressed PERF: {len(perf_data)} bytes")

# Save
os.makedirs('tools', exist_ok=True)
with open('tools/perf_template.bin', 'wb') as f:
    f.write(perf_data)
print(f"Saved to tools/perf_template.bin ({len(perf_data)} bytes)")
