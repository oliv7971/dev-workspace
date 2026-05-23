"""
Diagnostic : compare la structure binaire de BANK01.STY et test_out.STY
pour trouver ce qui fait planter PA Manager.
"""
import struct, sys

def hexdump(data, offset=0, n=64):
    for i in range(0, min(n, len(data)), 16):
        hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
        asc_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"  {offset+i:06x}: {hex_part:<48}  {asc_part}")

def read_chunk_header(data, pos):
    raw_id, size = struct.unpack_from('>II', data, pos)
    chunk_type    = (raw_id >> 24) & 0xFF
    version_major = (raw_id >> 16) & 0xFF
    version_minor = (raw_id >>  8) & 0xFF
    flags         = raw_id & 0xFF
    return chunk_type, version_major, version_minor, flags, size, raw_id

def describe_chunk(chunk_type, version_major, version_minor, flags, size, pos):
    names = {1:'Container',2:'KorgFile',5:'ObjectTOC',6:'StyleData',
             9:'PerformancesData',0xFE:'XRef'}
    name = names.get(chunk_type, f'Unknown({chunk_type:#04x})')
    return (f"@{pos:#08x}  type={chunk_type:#04x}({name}) "
            f"v{version_major}.{version_minor} flags={flags:#04x} size={size}")

def dump_file(path, label):
    with open(path, 'rb') as f:
        data = f.read()
    print(f"\n{'='*70}")
    print(f"  {label}: {path}")
    print(f"  Total file size: {len(data)} bytes")
    print(f"{'='*70}")

    print("\n--- First 32 bytes (raw) ---")
    hexdump(data, 0, 32)

    pos = 0
    # Outer container
    ct, vmaj, vmin, fl, sz, rid = read_chunk_header(data, pos)
    print(f"\n[1] {describe_chunk(ct, vmaj, vmin, fl, sz, pos)}")
    print(f"    raw_id = {rid:#010x}")
    pos += 8  # skip outer header (inner content starts here)

    # KorgFile chunk
    ct, vmaj, vmin, fl, sz, rid = read_chunk_header(data, pos)
    print(f"\n[2] {describe_chunk(ct, vmaj, vmin, fl, sz, pos)}")
    print(f"    raw_id = {rid:#010x}")
    print(f"    payload ({sz} bytes):")
    hexdump(data, pos+8, sz)
    pos += 8 + sz

    # TOC chunk
    ct, vmaj, vmin, fl, sz, rid = read_chunk_header(data, pos)
    print(f"\n[3] {describe_chunk(ct, vmaj, vmin, fl, sz, pos)}")
    print(f"    raw_id = {rid:#010x}")
    print(f"    first 32 bytes of TOC:")
    hexdump(data, pos+8, min(sz, 32))
    toc_pos = pos
    toc_size = sz
    pos += 8 + sz

    # Object chunks
    obj_idx = 0
    xref_offsets = None
    while pos < len(data) - 8:
        ct, vmaj, vmin, fl, sz, rid = read_chunk_header(data, pos)
        if ct == 0xFE:  # XRef
            print(f"\n[XRef] {describe_chunk(ct, vmaj, vmin, fl, sz, pos)}")
            print(f"    raw_id = {rid:#010x}")
            xref_data = data[pos+8:pos+8+sz]
            if xref_data[:4] == b'KBEG':
                n = (sz - 8 - 4) // 4  # subtract KBEG(4) + KEND(4) + nEntries(4)
                offsets = struct.unpack_from(f'>{n}I', xref_data, 4)
                print(f"    XRef entries ({n}): {list(offsets)}")
                xref_offsets = offsets
            break
        else:
            print(f"\n[obj {obj_idx}] {describe_chunk(ct, vmaj, vmin, fl, sz, pos)}")
            print(f"    raw_id = {rid:#010x}")
        pos += 8 + sz
        obj_idx += 1

    # Verify XRef offsets point to correct chunk headers
    if xref_offsets:
        print(f"\n--- XRef offset verification ---")
        for i, off in enumerate(xref_offsets):
            if off + 8 <= len(data):
                ct2, vmaj2, vmin2, fl2, sz2, rid2 = read_chunk_header(data, off)
                names = {6:'StyleData',9:'PerformancesData',0xFE:'XRef'}
                name2 = names.get(ct2, f'Unknown({ct2:#04x})')
                print(f"    offset[{i}]={off:#010x} → type={ct2:#04x}({name2}) size={sz2}")
            else:
                print(f"    offset[{i}]={off:#010x} → HORS FICHIER!")

BANK01 = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
TEST   = r"test_out.STY"

dump_file(BANK01, "BANK01.STY (référence)")
dump_file(TEST,   "test_out.STY (généré)")
