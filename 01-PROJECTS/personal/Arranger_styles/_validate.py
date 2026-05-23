import struct
from tools.korf import read_bank, iter_chunks

BANK01 = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"

def hexdump(data, offset=0, n=64):
    for i in range(0, min(n, len(data)), 16):
        raw = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in raw)
        asc_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw)
        print(f'  {offset+i:06x}: {hex_part:<48}  {asc_part}')

def parse_style_chunks(data, label):
    """Parse the top-level chunk hierarchy inside a style object."""
    print(f'\n=== {label} : chunk hierarchy ===')
    # The data starts with the outer Container
    r_data = data
    # outer container header
    outer_raw_id, outer_size = struct.unpack_from('>II', r_data, 0)
    print(f'  Outer Container raw_id={outer_raw_id:#010x} size={outer_size}')
    inner = r_data[8: 8 + outer_size]
    off = 0
    while off + 8 <= len(inner):
        raw_id, sz = struct.unpack_from('>II', inner, off)
        chunk_type = (raw_id >> 24) & 0xFF
        v_major = (raw_id >> 16) & 0xFF
        v_minor = (raw_id >>  8) & 0xFF
        flags   = raw_id & 0xFF
        print(f'  [{off:06x}] type={chunk_type:#04x} v{v_major}.{v_minor} flags={flags:#04x} size={sz}  raw_id={raw_id:#010x}')
        if chunk_type == 1 and v_minor == 3:  # StyleInfoData
            payload = inner[off+8: off+8+sz]
            name_len = payload[0]
            name = payload[1:1+name_len].decode('ascii', errors='replace')
            enabled = struct.unpack_from('>H', payload, 1+name_len+3)[0]
            ewdata_offset = 1 + name_len + 2 + 1 + 2 + 9 + 1 + 1
            ewdata = struct.unpack_from('>H', payload, ewdata_offset)[0]
            print(f'    name="{name}" enabled={enabled:#06x} with_data={ewdata:#06x}')
            hexdump(payload, offset=0, n=len(payload))
        off += 8 + sz

# --- bank structure ---
b = read_bank('test_out.STY')
data = open('test_out.STY', 'rb').read()
r = lambda o: struct.unpack_from('>I', data, o)[0]
c = r(0)
print(f'Container raw_id={c:#010x}  v{(c>>16)&0xff}.{(c>>8)&0xff}  (doit etre 0x01000114)')
t = r(28)
print(f'TOC       raw_id={t:#010x}  v{(t>>16)&0xff}.{(t>>8)&0xff}  (doit etre 0x05010018)')
print('XRef[0] doit etre 28:', b.xref[0] if b.xref else 'absent')

# --- Style inner chunk analysis ---
parse_style_chunks(b.objects[0], 'test_out.STY')

b2 = read_bank(BANK01)
parse_style_chunks(b2.objects[0], 'BANK01.STY obj0')

