"""Vérifie les types des chunks d'objets au niveau banque."""
import struct
from tools.korf import _Reader, _read_chunk_header, ChunkType

with open(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY', 'rb') as f:
    data = f.read()

r = _Reader(data)
outer_hdr = _read_chunk_header(r)
print(f"Outer: type=0x{outer_hdr.chunk_type:02X} v={outer_hdr.version_major}.{outer_hdr.version_minor} flags=0x{outer_hdr.flags:02X} size={outer_hdr.size}")

korf_hdr = _read_chunk_header(r)
r.read(korf_hdr.size)
print(f"KorgFile: type=0x{korf_hdr.chunk_type:02X} v={korf_hdr.version_major}.{korf_hdr.version_minor} flags=0x{korf_hdr.flags:02X} size={korf_hdr.size}")

toc_hdr = _read_chunk_header(r)
r.read(toc_hdr.size)
print(f"TOC: type=0x{toc_hdr.chunk_type:02X} v={toc_hdr.version_major}.{toc_hdr.version_minor} flags=0x{toc_hdr.flags:02X} size={toc_hdr.size}")

# Read first 5 object headers
for i in range(5):
    if r.remaining() < 8:
        break
    obj_hdr = _read_chunk_header(r)
    print(f"Object[{i}]: type=0x{obj_hdr.chunk_type:02X} v={obj_hdr.version_major}.{obj_hdr.version_minor} flags=0x{obj_hdr.flags:02X} size={obj_hdr.size}")
    if obj_hdr.chunk_type == 0xFE:
        break
    r.read(obj_hdr.size)
