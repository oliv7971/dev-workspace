import struct
from tools.korf import read_bank

REF = r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY'
raw = open(REF,'rb').read()
korf_off = 8
korf_sz = struct.unpack_from('>I', raw, korf_off+4)[0]
toc_off = korf_off + 8 + korf_sz
toc_sz = struct.unpack_from('>I', raw, toc_off+4)[0]
toc = raw[toc_off+8 : toc_off+8+toc_sz]

b = read_bank(REF)
all_names = [t.name for t in b.toc]

pos = 0; idx = 0
while pos < len(toc):
    sz = struct.unpack_from('>H', toc, pos)[0]
    entry = toc[pos+2:pos+2+sz]
    if sz == 62:
        print(f'Entry #{idx} (name={all_names[idx]!r}) size=62:')
        nprops = struct.unpack_from('>H', entry, 0)[0]
        p = 2
        for k in range(nprops):
            t,s = struct.unpack_from('>HH', entry, p); p += 4
            d = entry[p:p+s]; p += s
            print(f'  prop type={t} size={s}: hex={d.hex(" ")}')
            print(f'                          ascii={d!r}')
        print(f'  CRC: {entry[p:p+4].hex()}')
        print()
    pos += 2 + sz
    idx += 1

# Show one normal entry near them
print('---')
print('Normal entry 0:')
sz = struct.unpack_from('>H', toc, 0)[0]
entry = toc[2:2+sz]
nprops = struct.unpack_from('>H', entry, 0)[0]
p=2
for k in range(nprops):
    t,s = struct.unpack_from('>HH', entry, p); p += 4
    d = entry[p:p+s]; p += s
    print(f'  prop type={t} size={s}: hex={d.hex(" ")}')
