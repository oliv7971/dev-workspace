"""Reconstruction byte-perfect : reuse all original style + perf payloads."""
import os, struct
from tools.korf import read_bank, ChunkType, ChunkFlags, encode_chunk
from tools.korf_writer import _encode_korf_magic, _encode_toc, _encode_xref
from tools.oc31 import oc31_compress

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
OUT = r"verif\_src\favorite04.STY"

b = read_bank(REF)

names = [b.toc[i].name for i in range(0, len(b.toc), 2)]
korf_chunk = _encode_korf_magic()
toc_chunk = _encode_toc(names)

# Build style + perf chunks reusing original decompressed payloads
flags = ChunkFlags.InBankFile | ChunkFlags.OC31Compressed
inner_objs = b''
offsets = [8 + len(korf_chunk)]  # TOC offset
pos = offsets[0] + len(toc_chunk)
for i in range(0, len(b.toc), 2):
    style_payload = b.objects[i]
    perf_payload  = b.objects[i+1]
    sc = encode_chunk(ChunkType.StyleData, 0, 0, flags, oc31_compress(style_payload))
    pc = encode_chunk(ChunkType.PerformancesData, 2, 0, flags, oc31_compress(perf_payload))
    offsets.append(pos); pos += len(sc)
    offsets.append(pos); pos += len(pc)
    inner_objs += sc + pc

xref = _encode_xref(offsets)
inner = korf_chunk + toc_chunk + inner_objs + xref
outer = encode_chunk(ChunkType.Container, 0, 1,
                     ChunkFlags.Unknown4 | ChunkFlags.InBankFile, inner)

with open(OUT, 'wb') as f:
    f.write(outer)

print('written', OUT, os.path.getsize(OUT), 'orig', os.path.getsize(REF))
