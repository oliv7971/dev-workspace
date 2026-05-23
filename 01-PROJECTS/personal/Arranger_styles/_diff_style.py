import struct
from tools.korf import read_bank

ref_bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
ref_style = ref_bank.objects[0]
our_bank = read_bank(r'verif\TEST.SET\STYLE\USER01.STY')
our_style = our_bank.objects[0]

print('REF size:', len(ref_style), 'name:', ref_bank.toc[0].name)
print('OUR size:', len(our_style), 'name:', our_bank.toc[0].name)

def walk(buf, label):
    print(f'\n--- {label} top-level chunks ---')
    pos = 0
    while pos + 8 <= len(buf):
        cid, sz = struct.unpack_from('>II', buf, pos)
        ct = (cid >> 24) & 0xFF
        ver_hi = (cid >> 16) & 0xFF
        ver_lo = (cid >> 8) & 0xFF
        fl = cid & 0xFF
        print(f'  pos={pos:6} type=0x{ct:02x} v={ver_hi}.{ver_lo} fl=0x{fl:02x} sz={sz}')
        pos += 8 + sz
    if pos != len(buf):
        print(f'  WARNING: trailing {len(buf)-pos} bytes')

walk(ref_style, 'REF')
walk(our_style, 'OUR')

def walk_deep(buf, depth=0, max_depth=3, label=''):
    pos = 0
    while pos + 8 <= len(buf):
        cid, sz = struct.unpack_from('>II', buf, pos)
        ct = (cid >> 24) & 0xFF
        ver_hi = (cid >> 16) & 0xFF
        ver_lo = (cid >> 8) & 0xFF
        fl = cid & 0xFF
        print('  '*depth + f'type=0x{ct:02x} v={ver_hi}.{ver_lo} fl=0x{fl:02x} sz={sz}')
        if depth < max_depth and not (fl & 0x08) and sz > 0:
            walk_deep(buf[pos+8:pos+8+sz], depth+1, max_depth)
        pos += 8 + sz

print('\n=== REF deep ===')
walk_deep(ref_style[8:8+struct.unpack_from('>I', ref_style, 4)[0]])
print('\n=== OUR deep ===')
walk_deep(our_style[8:8+struct.unpack_from('>I', our_style, 4)[0]])

