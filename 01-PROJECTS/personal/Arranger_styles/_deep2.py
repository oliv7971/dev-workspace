"""Compare KorgFile payload, StyleInfo, MasterMidiTrack footer between BANK01 and test_out."""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from tools.korf import read_bank

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
GEN = "test_out.STY"

def u32be(d, off): return struct.unpack_from('>I', d, off)[0]
def u16be(d, off): return struct.unpack_from('>H', d, off)[0]

# KorgFile raw
print("=== KorgFile chunk ===")
for label, path in [("BANK01", REF), ("test_out", GEN)]:
    with open(path, 'rb') as f:
        d = f.read()
    raw = d[8:8+8+12]
    print(f"{label}: header={raw[:8].hex()}  payload={raw[8:].hex()}")
    pay = raw[8:]
    v0 = u32be(pay, 0)
    v1 = u16be(pay, 4)
    v2 = pay[6]
    v3 = pay[7:11]
    print(f"  u32be={v0:#010x}  u16be={v1:#06x}  u8={v2}  fourcc={v3.decode('ascii')!r}")

# StyleInfo
print()
print("=== StyleInfo bytes ===")
rb = read_bank(GEN)
rr = read_bank(REF)
for label, bk in [("BANK01", rr), ("test_out", rb)]:
    sdata = bk.objects[0]
    # StyleInfo: first child of outer Container
    si_size = u32be(sdata, 12)
    si_pay  = sdata[16 : 16+si_size]
    print(f"{label}: StyleInfo size={si_size}")
    print(f"  hex: {si_pay.hex()}")
    # decode
    name_len = si_pay[0]
    name = si_pay[1:1+name_len].decode('ascii', errors='replace')
    pos = 1 + name_len
    unk111 = struct.unpack_from('>h', si_pay, pos)[0]; pos += 2
    unk3   = si_pay[pos]; pos += 1
    enabled = u16be(si_pay, pos); pos += 2
    unk9   = si_pay[pos:pos+9]; pos += 9
    unk15  = si_pay[pos]; pos += 1
    unk16  = si_pay[pos]; pos += 1
    with_data = u16be(si_pay, pos)
    print(f"  name={name!r}  unk111={unk111}  unk3={unk3}  enabled={enabled:#06x}  "
          f"with_data={with_data:#06x}")
    print(f"  unk9={unk9.hex()}  unk15={unk15}  unk16={unk16}")

# MasterMidiTrack footer analysis
print()
print("=== First MasterMidiTrack footer (test_out element 0) ===")
gen_sdata = rb.objects[0]
off = 8  # skip outer Container header
# find MIDITrackList (type=0x02, not leaf)
while off < len(gen_sdata) - 8:
    raw_id = u32be(gen_sdata, off)
    size = u32be(gen_sdata, off+4)
    ctype = (raw_id >> 24) & 0xFF
    flags = raw_id & 0xFF
    if ctype == 0x02 and not (flags & 0x08):
        break
    off += 8 + size
mtl_off = off + 8
mtl_end = off + 8 + size

# find first StyleElement (type=0x03, container)
off2 = 8  # skip outer Container header
while off2 < len(gen_sdata) - 8:
    raw_id = u32be(gen_sdata, off2)
    sz2 = u32be(gen_sdata, off2+4)
    ct2 = (raw_id >> 24) & 0xFF
    fl2 = raw_id & 0xFF
    if ct2 == 0x03 and not (fl2 & 0x08):
        break
    off2 += 8 + sz2
elem_off = off2 + 8
elem_end = off2 + 8 + sz2

# inside StyleElement, find MasterMidiTrack (type=0x03, leaf)
off3 = elem_off
while off3 < elem_end - 8:
    raw_id = u32be(gen_sdata, off3)
    sz3 = u32be(gen_sdata, off3+4)
    ct3 = (raw_id >> 24) & 0xFF
    fl3 = raw_id & 0xFF
    if ct3 == 0x03 and (fl3 & 0x08):
        break
    off3 += 8 + sz3
mt_pay = gen_sdata[off3+8 : off3+8+sz3]
print(f"  MasterMidiTrack size={sz3}")
print(f"  header: {mt_pay[:8].hex()}")
data_len = u16be(mt_pay, 6)
print(f"  data_len={data_len}")
footer_start = 8 + data_len
footer = mt_pay[footer_start:]
print(f"  footer hex: {footer.hex()}")
n_entries = footer[0]
print(f"  n_cv_mappings={n_entries}")
for i in range(n_entries):
    t = footer[1 + i*2]
    tn = footer[2 + i*2]
    print(f"    mapping[{i}]: type={t}  track_number={tn}")

# Also check if indices in TrackMapping cover all referenced track_numbers
print()
print("=== TrackMapping range vs MasterMidiTrack track_numbers ===")
try:
    from tools.style_reader import parse_style
    parsed = parse_style(rb.objects[0])
    n_indices = len(parsed.track_mapping.indices)
    print(f"  n_indices={n_indices}")
    all_tn = []
    for elem in parsed.style_elements:
        for _, mt in elem.master_tracks:
            for m in mt.cv_track_mappings:
                all_tn.append(m.track_number)
    if all_tn:
        print(f"  track_numbers range: [{min(all_tn)}, {max(all_tn)}]")
        invalid = [tn for tn in all_tn if tn < 0 or tn >= n_indices]
        if invalid:
            print(f"  [INVALID] track_numbers out of range: {invalid[:10]}")
        else:
            print(f"  [OK] all track_numbers in [0, {n_indices-1}]")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()

print()
print("Done.")
