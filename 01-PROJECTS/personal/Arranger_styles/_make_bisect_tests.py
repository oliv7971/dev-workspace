"""Bisection : create test variants that progressively rebuild parts of BANK01."""
import os, struct, shutil
from tools.korf import read_bank, ChunkType, ChunkFlags, encode_chunk
from tools.korf_writer import _encode_korf_magic, _encode_toc, _encode_xref
from tools.oc31 import oc31_compress, oc31_decompress

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
OUT_DIR = r"verif"

# Read raw bytes
with open(REF, 'rb') as f:
    raw = f.read()

# Read parsed bank
b = read_bank(REF)

def mk_set(set_name: str, data: bytes):
    d = os.path.join(OUT_DIR, f"{set_name}.SET", "STYLE")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "FAVORITE01.STY"), 'wb') as f:
        f.write(data)

# Locate raw chunks in REF: outer at 0, korf at 8, toc at 0x1c, then objects.
outer_cid, outer_sz = struct.unpack_from('>II', raw, 0)
korf_off = 8
korf_cid, korf_sz = struct.unpack_from('>II', raw, korf_off)
korf_total = 8 + korf_sz
toc_off = korf_off + korf_total
toc_cid, toc_sz = struct.unpack_from('>II', raw, toc_off)
toc_total = 8 + toc_sz
objs_off = toc_off + toc_total

# Walk objects + xref
chunk_blocks = []  # list of (offset, total_size) for each inner chunk after TOC
pos = objs_off
while pos < 8 + outer_sz:
    cid, sz = struct.unpack_from('>II', raw, pos)
    chunk_blocks.append((pos, 8 + sz, cid))
    pos += 8 + sz

# XRef is the last
xref_off, xref_total, xref_cid = chunk_blocks[-1]
obj_blocks = chunk_blocks[:-1]
print(f"Found {len(obj_blocks)} object chunks + 1 xref")

# Helper: rebuild file with given parts (each is a `bytes` representing the inner chunk including header)
def assemble(korf_b, toc_b, objs_b_list, xref_b):
    inner = korf_b + toc_b + b''.join(objs_b_list) + xref_b
    return encode_chunk(ChunkType.Container, 0, 1,
                        ChunkFlags.Unknown4 | ChunkFlags.InBankFile, inner)

# Source verbatim parts
korf_v = raw[korf_off : korf_off + korf_total]
toc_v  = raw[toc_off  : toc_off  + toc_total]
xref_v = raw[xref_off : xref_off + xref_total]
objs_v = [raw[o : o+sz] for o,sz,_ in obj_blocks]

# === BASELINE: TEST_A_VERBATIM ===
mk_set("TEST_A_VERBATIM", raw)

# === TEST_B_OUTER: rebuild only outer container ===
inner = raw[8 : 8 + outer_sz]
data = encode_chunk(ChunkType.Container, 0, 1,
                    ChunkFlags.Unknown4 | ChunkFlags.InBankFile, inner)
mk_set("TEST_B_OUTER", data)

# === TEST_C_KORF: rebuild outer + KORF chunk ===
korf_new = _encode_korf_magic()
data = assemble(korf_new, toc_v, objs_v, xref_v)
mk_set("TEST_C_KORF", data)

# === TEST_D_TOC: rebuild outer + KORF + TOC (XRef must be recomputed
# because our TOC has different size than verbatim) ===
names = [b.toc[i].name for i in range(0, len(b.toc), 2)]
toc_new = _encode_toc(names)
toc_offset_new = 8 + len(korf_new)
offsets_new = [toc_offset_new]
pos = toc_offset_new + len(toc_new)
for ob in objs_v:
    offsets_new.append(pos)
    pos += len(ob)
xref_new = _encode_xref(offsets_new)
data = assemble(korf_new, toc_new, objs_v, xref_new)
mk_set("TEST_D_TOC", data)

# === TEST_D2_REFTOC_NEWXREF: REF toc bytes + recomputed XRef ===
# Isolates: is the issue TOC encoding, or XRef recomputation?
toc_offset_new = 8 + len(korf_new)
offsets_new = [toc_offset_new]
pos = toc_offset_new + len(toc_v)
for ob in objs_v:
    offsets_new.append(pos)
    pos += len(ob)
xref_new2 = _encode_xref(offsets_new)
data = assemble(korf_new, toc_v, objs_v, xref_new2)
mk_set("TEST_D2_REFTOC_NEWXREF", data)

# === TEST_E_XREF: rebuild XRef (recomputed offsets to match verbatim chunks) ===
# Compute XRef offsets matching verbatim positions
toc_offset_new = 8 + len(korf_new)
offsets_new = [toc_offset_new]
pos = toc_offset_new + len(toc_v)
for ob in objs_v:
    offsets_new.append(pos)
    pos += len(ob)
xref_new = _encode_xref(offsets_new)
data = assemble(korf_new, toc_v, objs_v, xref_new)
mk_set("TEST_E_XREF", data)

# === TEST_F_RECOMPRESS_ONE: rebuild only chunk[0] (Style) with our OC31 ===
# obj_blocks[0] is StyleData (type 6). Decompress, recompress, replace.
flags = ChunkFlags.InBankFile | ChunkFlags.OC31Compressed
new_obj0 = encode_chunk(ChunkType.StyleData, 0, 0, flags,
                        oc31_compress(b.objects[0]))
objs_modified = [new_obj0] + objs_v[1:]
# XRef must be recomputed because chunk[0] size changed
toc_offset_new = 8 + len(korf_new)
offsets_new = [toc_offset_new]
pos = toc_offset_new + len(toc_v)
for ob in objs_modified:
    offsets_new.append(pos)
    pos += len(ob)
xref_new = _encode_xref(offsets_new)
data = assemble(korf_new, toc_v, objs_modified, xref_new)
mk_set("TEST_F_RECOMPRESS1", data)

# === TEST_G_RECOMPRESS_ALL_STYLES: only Style chunks (type 6), keep PERF verbatim ===
objs_g = []
for i, (off, sz, cid) in enumerate(obj_blocks):
    ct = (cid >> 24) & 0xFF
    if ct == 6:  # StyleData
        objs_g.append(encode_chunk(ChunkType.StyleData, 0, 0, flags,
                                   oc31_compress(b.objects[i])))
    else:
        objs_g.append(objs_v[i])
toc_offset_new = 8 + len(korf_new)
offsets_new = [toc_offset_new]
pos = toc_offset_new + len(toc_v)
for ob in objs_g:
    offsets_new.append(pos)
    pos += len(ob)
xref_new = _encode_xref(offsets_new)
data = assemble(korf_new, toc_v, objs_g, xref_new)
mk_set("TEST_G_RECOMPRESS_STYLES", data)

print("Created sets:")
for n in os.listdir(OUT_DIR):
    if n.startswith("TEST_") and n.endswith(".SET"):
        f = os.path.join(OUT_DIR, n, "STYLE", "FAVORITE01.STY")
        if os.path.exists(f):
            print(f"  {n}  ({os.path.getsize(f):,} bytes)")
