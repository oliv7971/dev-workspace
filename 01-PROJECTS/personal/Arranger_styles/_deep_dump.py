"""Deep dump of decompressed inner StyleData structure."""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from tools.korf import read_bank
from tools.oc31 import oc31_decompress

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
GEN = "test_out.STY"

def u32be(d, off): return struct.unpack_from('>I', d, off)[0]
def u16be(d, off): return struct.unpack_from('>H', d, off)[0]

def walk(data, off, end, indent=0, max_depth=6, depth=0):
    end = min(end, len(data))
    pfx = "  " * indent
    while off + 8 <= end:
        raw_id = u32be(data, off)
        size   = u32be(data, off+4)
        ctype  = (raw_id >> 24) & 0xFF
        vmaj   = (raw_id >> 16) & 0xFF
        vmin   = (raw_id >>  8) & 0xFF
        flags  = raw_id & 0xFF
        is_leaf = bool(flags & 0x08)
        chunk_end = min(off+8+size, len(data))
        # Show first 16 bytes of payload
        pay_preview = data[off+8 : min(off+8+16, chunk_end)].hex()
        print(f"{pfx}[{off:06x}] type={ctype:02x} v{vmaj}.{vmin} fl={flags:02x} sz={size:5d}  "
              f"{'LEAF' if is_leaf else 'CONT'}  {pay_preview}")
        if not is_leaf and depth < max_depth and size > 0:
            walk(data, off+8, chunk_end, indent+1, max_depth, depth+1)
        off = off + 8 + size

def get_style_bytes(path):
    b = read_bank(path)
    return b.objects[0]  # already decompressed

print("=" * 70)
print("BANK01 inner StyleData (obj 0) decompressed")
print("=" * 70)
ref_style = get_style_bytes(REF)
print(f"  size: {len(ref_style)} bytes")
walk(ref_style, 0, len(ref_style), max_depth=3)

print()
print("=" * 70)
print("test_out inner StyleData (obj 0) decompressed")
print("=" * 70)
gen_style = get_style_bytes(GEN)
print(f"  size: {len(gen_style)} bytes")
walk(gen_style, 0, len(gen_style), max_depth=3)

# Now compare TrackMapping payload
print()
print("=" * 70)
print("TrackMapping raw bytes (first 64 bytes each)")
print("=" * 70)

def find_track_mapping(style_data):
    """Walk into Container > MIDITrackList > TrackMapping."""
    # Container (top level)
    c_off = 0
    c_size = u32be(style_data, 4)
    off = 8  # inside Container
    end = 8 + c_size
    while off + 8 < end:
        raw_id = u32be(style_data, off)
        size   = u32be(style_data, off+4)
        ctype  = (raw_id >> 24) & 0xFF
        flags  = raw_id & 0xFF
        is_leaf = bool(flags & 0x08)
        # MIDITrackList = type 0x02, not leaf
        if ctype == 0x02 and not is_leaf:
            # inside MIDITrackList, find TrackMapping = type 0x01
            inner_off = off + 8
            inner_end = off + 8 + size
            while inner_off + 8 < inner_end:
                r2 = u32be(style_data, inner_off)
                s2 = u32be(style_data, inner_off+4)
                t2 = (r2 >> 24) & 0xFF
                if t2 == 0x01:
                    return inner_off, s2
                inner_off += 8 + s2
        off += 8 + size
    return None, None

for label, sdata in [("BANK01", ref_style), ("test_out", gen_style)]:
    tm_off, tm_size = find_track_mapping(sdata)
    if tm_off is None:
        print(f"{label}: TrackMapping NOT FOUND")
        continue
    payload = sdata[tm_off+8 : tm_off+8+tm_size]
    n_tracks = u16be(payload, 0)
    n_indices = u16be(payload, 2)
    print(f"{label}: TrackMapping at {tm_off:#x}, size={tm_size}")
    print(f"  n_tracks={n_tracks}, n_indices={n_indices}")
    print(f"  indices (first 16): {[u16be(payload, 4+i*2) for i in range(min(16,n_indices))]}")
    print(f"  raw hex (first 32 bytes): {payload[:32].hex()}")
