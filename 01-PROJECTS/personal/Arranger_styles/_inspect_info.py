from tools.korf import read_bank, iter_chunks
import struct

b2 = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')

def get_info(buf):
    for h,p in iter_chunks(buf):
        for h2,p2 in iter_chunks(p):
            if h2.chunk_type == 0x01 and h2.version_minor == 3:
                return p2
    return None

results = []
for i in range(0, len(b2.objects), 2):
    name = b2.toc[i].name
    info = get_info(b2.objects[i])
    if info is None: continue
    nl = info[0]
    p = 1+nl
    u111 = struct.unpack_from('>h', info, p)[0]; p+=2
    u3 = info[p]; p+=1
    enabled = struct.unpack_from('>H', info, p)[0]; p+=2
    unk = info[p:p+9]; p+=9
    u15 = info[p]; p+=1
    u16 = info[p]; p+=1
    wdata = struct.unpack_from('>H', info, p)[0]
    results.append((name, u111, u3, enabled, unk, u15, u16, wdata))

print('u3 unique:', sorted(set(r[2] for r in results)))
print('u15 unique:', sorted(set(r[5] for r in results)))
print('u16 unique:', sorted(set(r[6] for r in results)))
print('wdata unique:', sorted(set(r[7] for r in results)))
print('unk[0] unique:', sorted(set(r[4][0] for r in results)))
print('unk[1] unique:', sorted(set(r[4][1] for r in results)))
print('unk full unique count:', len(set(r[4] for r in results)))
print()
print('u111 distribution (first 20):', sorted(set(r[1] for r in results))[:20])
print()
for r in results[:8]:
    print(f'  {r[0]!r:25} u111={r[1]:6} u3={r[2]:#04x} enabled={r[3]:#06x} unk={r[4].hex()} u15={r[5]} u16={r[6]} wdata={r[7]:#06x}')
