"""Detailed binary comparison of test_out.STY vs BANK01.STY header/TOC/XRef."""
import sys
import struct
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REF  = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
GEN  = "test_out.STY"

def u32be(data, off):
    return struct.unpack_from('>I', data, off)[0]

def u16be(data, off):
    return struct.unpack_from('>H', data, off)[0]

def dump_chunk_header(data, off, label=""):
    raw_id = u32be(data, off)
    size   = u32be(data, off+4)
    ctype  = (raw_id >> 24) & 0xFF
    vmaj   = (raw_id >> 16) & 0xFF
    vmin   = (raw_id >>  8) & 0xFF
    flags  = (raw_id      ) & 0xFF
    print(f"  {label:30s}  off={off:#08x}  raw_id={raw_id:#010x}  "
          f"type={ctype:#04x} v{vmaj}.{vmin} flags={flags:#04x}  size={size}")
    return off + 8, size

def walk_chunks(data, off, end, indent=0, max_depth=4, depth=0):
    """Walk container chunks recursively."""
    if depth > max_depth:
        return
    end = min(end, len(data))
    prefix = "  " * indent
    while off < end:
        if off + 8 > end:
            print(f"{prefix}  [truncated at {off:#x}]")
            break
        raw_id = u32be(data, off)
        size   = u32be(data, off+4)
        ctype  = (raw_id >> 24) & 0xFF
        vmaj   = (raw_id >> 16) & 0xFF
        vmin   = (raw_id >>  8) & 0xFF
        flags  = (raw_id      ) & 0xFF
        is_leaf = bool(flags & 0x08)
        chunk_end = min(off + 8 + size, len(data))
        print(f"{prefix}  [{off:#08x}] raw={raw_id:#010x} type={ctype:#04x} v{vmaj}.{vmin} "
              f"flags={flags:#04x} size={size}  {'LEAF' if is_leaf else 'CONTAINER'}")
        if not is_leaf and size > 0 and depth < max_depth:
            walk_chunks(data, off+8, chunk_end, indent+1, max_depth, depth+1)
        off = off + 8 + size

print("=" * 70)
print("REFERENCE: BANK01.STY")
print("=" * 70)
with open(REF, 'rb') as f:
    ref = f.read()

print(f"File size: {len(ref)} bytes")
print(f"First 8 bytes: {ref[:8].hex()}")
walk_chunks(ref, 0, len(ref), max_depth=2)

print()
print("=" * 70)
print("GENERATED: test_out.STY")
print("=" * 70)
with open(GEN, 'rb') as f:
    gen = f.read()

print(f"File size: {len(gen)} bytes")
print(f"First 8 bytes: {gen[:8].hex()}")
walk_chunks(gen, 0, len(gen), max_depth=2)

# ── XRef comparison ─────────────────────────────────────────────────────────
print()
print("=" * 70)
print("XREF comparison")
print("=" * 70)

def find_xref(data):
    """Find XRef chunk (type=0xFE)."""
    off = 0
    while off < len(data) - 8:
        raw_id = u32be(data, off)
        size   = u32be(data, off+4)
        ctype  = (raw_id >> 24) & 0xFF
        if ctype == 0xFE:
            return off
        # skip to next chunk (only works at top level Container)
        # Actually walk into Container
        flags = raw_id & 0xFF
        is_leaf = bool(flags & 0x08)
        if not is_leaf:
            off += 8  # go into container
        else:
            off += 8 + size
    return None

def find_xref_at_end(data):
    """XRef is usually the last chunk inside the Container. Walk from end."""
    # Container is chunk 0: size = u32be(data, 4)
    container_size = u32be(data, 4)
    # last 8 bytes of container = XRef header?
    # Actually walk Container body looking for type=0xFE
    off = 8  # skip container header
    end = 8 + container_size
    # walk at depth 1
    while off < end - 8:
        raw_id = u32be(data, off)
        size   = u32be(data, off+4)
        ctype  = (raw_id >> 24) & 0xFF
        flags  = raw_id & 0xFF
        if ctype == 0xFE:
            return off
        is_leaf = bool(flags & 0x08)
        if is_leaf:
            off += 8 + size
        else:
            off += 8 + size  # skip over (don't recurse at top level)
    return None

for label, data in [("BANK01", ref), ("test_out", gen)]:
    xref_off = find_xref_at_end(data)
    if xref_off is None:
        print(f"{label}: XRef NOT FOUND")
        continue
    raw_id = u32be(data, xref_off)
    size   = u32be(data, xref_off+4)
    payload = data[xref_off+8 : xref_off+8+size]
    n_entries = u32be(payload, 0)
    print(f"{label}: XRef at {xref_off:#x}, size={size}, payload_len={len(payload)}, n_entries={n_entries}")
    for i in range(min(n_entries, 10)):
        eoff = 4 + i*4
        if eoff + 4 > len(payload): break
        val = u32be(payload, eoff)
        print(f"  xref[{i}] = {val}  ({val:#010x})")

# ── TOC comparison ────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("TOC (ObjectTOC) raw bytes comparison")
print("=" * 70)

def find_toc(data):
    """Find ObjectTOC chunk (type=0x05) inside KorgFile (type=0x02)."""
    off = 8  # skip Container header
    # KorgFile
    raw_id = u32be(data, off)
    ctype = (raw_id >> 24) & 0xFF
    if ctype != 0x02:
        print(f"  Expected KorgFile at {off:#x}, got type={ctype:#x}")
        return None, None
    kf_size = u32be(data, off+4)
    # skip KorgFile payload
    off2 = off + 8 + kf_size
    # ObjectTOC
    raw_id2 = u32be(data, off2)
    ctype2 = (raw_id2 >> 24) & 0xFF
    if ctype2 != 0x05:
        print(f"  Expected ObjectTOC at {off2:#x}, got type={ctype2:#x}")
        return None, None
    toc_size = u32be(data, off2+4)
    return off2, toc_size

for label, data in [("BANK01", ref), ("test_out", gen)]:
    toc_off, toc_size = find_toc(data)
    if toc_off is None:
        continue
    toc_raw = data[toc_off : toc_off+8+toc_size]
    print(f"{label}: TOC at {toc_off:#x}, size={toc_size}")
    print(f"  header hex: {toc_raw[:8].hex()}")
    print(f"  payload hex: {toc_raw[8:8+min(toc_size,80)].hex()}")
    # decode TOC payload
    pay = data[toc_off+8 : toc_off+8+toc_size]
    if len(pay) >= 12:
        n_entries = u32be(pay, 0)
        crc       = u32be(pay, 4)
        unk       = u32be(pay, 8)
        print(f"  n_entries={n_entries}, crc={crc:#010x}, unk={unk}")
        entry_off = 12
        for i in range(min(n_entries, 5)):
            if entry_off + 12 > len(pay): break
            pos  = u32be(pay, entry_off)
            t    = u16be(pay, entry_off+4)
            bank = u16be(pay, entry_off+6)
            unk2 = u32be(pay, entry_off+8)
            print(f"    toc[{i}]: pos={pos}, type={t}, bank={bank}, unk={unk2:#010x}")
            entry_off += 12
            # name (null-terminated after 12-byte fixed part?)
            # read until null
            name = bytearray()
            while entry_off < len(pay) and pay[entry_off] != 0:
                name.append(pay[entry_off])
                entry_off += 1
            entry_off += 1  # skip null
            print(f"    toc[{i}]: name={name.decode('ascii', errors='replace')!r}")

print()
print("Done.")
