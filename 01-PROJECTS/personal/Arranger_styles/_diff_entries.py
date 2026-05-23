import struct
from tools.korf import read_bank
from tools.korf_writer import _encode_toc

REF = r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY'
raw = open(REF,'rb').read()
korf_off = 8
korf_sz = struct.unpack_from('>I', raw, korf_off+4)[0]
toc_off = korf_off + 8 + korf_sz
toc_sz = struct.unpack_from('>I', raw, toc_off+4)[0]
toc_ref = raw[toc_off+8 : toc_off+8+toc_sz]

b = read_bank(REF)
names = [b.toc[i].name for i in range(0, len(b.toc), 2)]
ours_full = _encode_toc(names)
ours = ours_full[8:]

def walk(payload):
    pos = 0
    out = []
    while pos < len(payload):
        sz = struct.unpack_from('>H', payload, pos)[0]
        out.append(payload[pos:pos+2+sz])
        pos += 2 + sz
    return out

ref_entries = walk(toc_ref)
our_entries = walk(ours)
print(f'REF entries: {len(ref_entries)}, OURS entries: {len(our_entries)}')

mismatches = 0
size_diff = 0
for i, (r, o) in enumerate(zip(ref_entries, our_entries)):
    if len(r) != len(o):
        size_diff += 1
        continue
    if r != o:
        mismatches += 1
        if mismatches <= 3:
            print(f'Entry {i} mismatch:')
            print(' REF :', r.hex(' '))
            print(' OURS:', o.hex(' '))
print(f'Same-size mismatches: {mismatches}')
print(f'Different-size: {size_diff}')
