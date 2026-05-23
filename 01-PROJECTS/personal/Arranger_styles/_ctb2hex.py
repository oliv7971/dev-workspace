"""
Hexdump the raw Ctb2 entries from 8BeatBallad1 to verify the byte layout.
"""
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src = "donn\u00e9es etude\\YAMAHA (TYROS5)\\Ballad\\8BeatBallad1.T160.prs"

with open(src, 'rb') as f:
    data = f.read()

def find_tag(data, tag, start=0):
    tag_b = tag.encode('ascii')
    pos = data.find(tag_b, start)
    if pos < 0:
        return None
    sz = struct.unpack_from('>I', data, pos+4)[0]
    return pos, sz, data[pos+8:pos+8+sz]

def iter_chunks(data, start, end):
    pos = start
    while pos + 8 <= end:
        tag = data[pos:pos+4].decode('latin1', errors='replace')
        sz = struct.unpack_from('>I', data, pos+4)[0]
        if pos + 8 + sz > end:
            break
        yield pos, tag, sz, data[pos+8:pos+8+sz]
        pos += 8 + sz

def hexdump(data, label=""):
    if label:
        print(f"  {label}:")
    for i in range(0, min(len(data), 64), 16):
        raw = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in raw)
        asc_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw)
        print(f"    [{i:02x}] {hex_part:<48}  {asc_part}")

# Find CASM
casm = find_tag(data, 'CASM')
if not casm:
    print("No CASM found!")
    sys.exit(1)

casm_pos, casm_sz, casm_data = casm
print(f"CASM at {casm_pos:#x}, size={casm_sz}")

# Parse first CSEG's Ctb2 entries
n_ctb2 = 0
for cseg_off, tag, sz, cseg_data in iter_chunks(data, casm_pos+8, casm_pos+8+casm_sz):
    if tag != 'CSEG':
        continue
    print(f"\nCSEG at {cseg_off:#x}:")
    for inner_off, tag2, sz2, payload in iter_chunks(cseg_data, 0, len(cseg_data)):
        if tag2 == 'Sdec':
            print(f"  Sdec: {payload.rstrip(b'chr(0)').decode('ascii', 'replace')}")
        elif tag2 == 'Ctb2':
            n_ctb2 += 1
            if n_ctb2 <= 6:
                src_ch = payload[0]
                name = payload[1:9].rstrip(b' ').decode('ascii', 'replace')
                print(f"  Ctb2 #{n_ctb2}: src_ch={src_ch} name={name!r}")
                hexdump(payload[:20], f"  payload[0:20]")
    break  # only first CSEG
