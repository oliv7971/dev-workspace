"""Dump raw TOC bytes from BANK01 to compare with test_out."""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
GEN = "test_out.STY"

def u32be(d, off): return struct.unpack_from('>I', d, off)[0]
def u16be(d, off): return struct.unpack_from('>H', d, off)[0]

def get_toc_raw(path):
    with open(path, 'rb') as f:
        d = f.read()
    # Container skip 8 bytes
    # KorgFile is at offset 8
    kf_raw = u32be(d, 8)
    kf_size = u32be(d, 12)
    # TOC starts after KorgFile
    toc_off = 8 + 8 + kf_size
    toc_raw = u32be(d, toc_off)
    toc_size = u32be(d, toc_off+4)
    return d[toc_off : toc_off + 8 + toc_size], toc_off

for label, path in [("BANK01", REF), ("test_out", GEN)]:
    raw, off = get_toc_raw(path)
    raw_id = u32be(raw, 0)
    size = u32be(raw, 4)
    print(f"\n{label}: TOC at {off:#x}, raw_id={raw_id:#010x}, size={size}")
    payload = raw[8:]
    print(f"  payload bytes (first 120): {payload[:120].hex()}")
    print()
    # Parse entries manually
    pos = 0
    entry_num = 0
    while pos < len(payload) and entry_num < 4:
        if pos + 2 > len(payload): break
        header_entry_size = u16be(payload, pos)
        if header_entry_size == 0:
            break
        entry_end = pos + 2 + header_entry_size
        content = payload[pos+2 : entry_end]
        print(f"  entry[{entry_num}]: pos={pos}, headerEntrySize={header_entry_size}")
        print(f"    content hex: {content.hex()}")
        # Parse props
        if len(content) < 2: 
            pos = entry_end
            entry_num += 1
            continue
        n_props = u16be(content, 0)
        print(f"    n_props = {n_props}")
        prop_pos = 2
        for pi in range(n_props):
            if prop_pos + 4 > len(content): break
            ptype = u16be(content, prop_pos)
            psize = u16be(content, prop_pos+2)
            pdata = content[prop_pos+4 : prop_pos+4+psize]
            print(f"    prop[{pi}]: type={ptype}, size={psize}, data={pdata.hex()}  ({pdata!r})")
            prop_pos += 4 + psize
        # CRC is last 4 bytes
        crc = u32be(content, len(content)-4)
        print(f"    CRC = {crc:#010x}")
        pos = entry_end
        entry_num += 1
