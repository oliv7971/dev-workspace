"""TEST_H: parse REF style, re-encode via our style_writer, re-wrap, save."""
import os, struct
from tools.korf import read_bank, ChunkType, ChunkFlags, encode_chunk
from tools.korf_writer import _encode_korf_magic, _encode_toc, _encode_xref
from tools.oc31 import oc31_compress
from tools.style_reader import parse_style
from tools.style_writer import encode_style

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"

with open(REF, 'rb') as f:
    raw = f.read()
b = read_bank(REF)

# Re-encode each style object through our style_writer
flags = ChunkFlags.InBankFile | ChunkFlags.OC31Compressed
new_objs = []
for i, t in enumerate(b.toc):
    if t.object_type == 2:  # StyleData
        st = parse_style(b.objects[i])
        re_encoded = encode_style(st)
        # Diff sizes
        print(f'  style[{i}] {t.name!r}: orig={len(b.objects[i])} re={len(re_encoded)} '
              f'identical={re_encoded == b.objects[i]}')
        new_objs.append(encode_chunk(ChunkType.StyleData, 0, 0, flags,
                                     oc31_compress(re_encoded)))
    else:
        # Re-wrap performance data verbatim (object_type 7 → ChunkType.PerformancesData=9)
        ct = ChunkType.PerformancesData
        # Performance chunks have version 2.0
        new_objs.append(encode_chunk(ct, 2, 0, flags, oc31_compress(b.objects[i])))

names = [b.toc[i].name for i in range(0, len(b.toc), 2)]
korf_b = _encode_korf_magic()
toc_b = _encode_toc(names)
toc_off = 8 + len(korf_b)
offsets = [toc_off]
pos = toc_off + len(toc_b)
for ob in new_objs:
    offsets.append(pos)
    pos += len(ob)
xref_b = _encode_xref(offsets)

inner = korf_b + toc_b + b''.join(new_objs) + xref_b
data = encode_chunk(ChunkType.Container, 0, 1,
                    ChunkFlags.Unknown4 | ChunkFlags.InBankFile, inner)

out = r"verif\TEST_H_RESTYLE.SET\STYLE\FAVORITE01.STY"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'wb') as f:
    f.write(data)
print(f'Wrote {out} ({len(data):,} bytes)')
