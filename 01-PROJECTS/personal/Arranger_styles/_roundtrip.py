"""
Round-trip validation: read test_out.STY, parse inner style, check consistency.
Also compares key metrics with BANK01.STY obj0.
"""
import struct
import sys
from tools.korf import read_bank, iter_chunks
from tools.style_reader import parse_style

BANK01 = r"donnees etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
BANK01_REAL = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"

def check_bank01_path():
    import os
    if os.path.exists(BANK01_REAL):
        return BANK01_REAL
    return BANK01

def report(label, ok, detail=""):
    status = "OK" if ok else "FAIL"
    line = f"  [{status}] {label}"
    if detail:
        line += f"  ({detail})"
    print(line)

print("=== Round-trip validation: test_out.STY ===\n")

# 1. Read bank
b = read_bank('test_out.STY')
print(f"XRef: {b.xref}")
print(f"TOC entries: {len(b.toc)}")
for i, e in enumerate(b.toc):
    print(f"  [{i}] {e}")
print()

# 2. Parse inner style
obj = b.objects[0]
print(f"Style object size: {len(obj)} bytes")
try:
    style = parse_style(obj)
    print("parse_style: OK")
except Exception as ex:
    print(f"parse_style: FAILED  -> {ex}")
    sys.exit(1)

print()
print("=== Style content ===")
print(f"  Name       : '{style.info.name}'")
print(f"  Enabled    : {style.info.enabled_style_elements:#06x}")
print(f"  WithData   : {style.info.style_elements_with_data:#06x}")
print(f"  n_midi_tracks (TrackMapping.n_midi_tracks): {style.track_mapping.n_midi_tracks}")
print(f"  indices len (TrackMapping.indices): {len(style.track_mapping.indices)}")
print(f"  global tracks (midi_tracks): {len(style.midi_tracks)}")
print(f"  style_elements: {len(style.style_elements)}")

# 3. TrackMapping consistency
tm = style.track_mapping
report("n_midi_tracks == len(midi_tracks)",
       tm.n_midi_tracks == len(style.midi_tracks),
       f"{tm.n_midi_tracks} vs {len(style.midi_tracks)}")
report("n_midi_tracks == len(indices)",
       tm.n_midi_tracks == len(tm.indices),
       f"{tm.n_midi_tracks} vs {len(tm.indices)}")
# indices should be 1-based and < n_midi_tracks+1
bad_indices = [i for i in tm.indices if i < 1 or i > tm.n_midi_tracks]
report("all indices valid (1..n_midi_tracks)",
       len(bad_indices) == 0,
       f"bad: {bad_indices[:5]}..." if bad_indices else "")

# 4. StyleElement / MasterMidiTrack cv_track_mappings
print()
print("=== StyleElement check ===")
for ei, elem in enumerate(style.style_elements):
    # Check each MasterMidiTrack's cv_track_mappings
    for mi, (_cv, mt) in enumerate(elem.master_tracks):
        for ci, cm in enumerate(mt.cv_track_mappings):
            # track_number should be < n_midi_tracks
            ok = cm.track_number < tm.n_midi_tracks
            if not ok:
                print(f"  FAIL elem[{ei}] master[{mi}] cv[{ci}]: track_number={cm.track_number} >= n={tm.n_midi_tracks}")
            # type should be 0-3
            if cm.type > 3:
                print(f"  FAIL elem[{ei}] master[{mi}] cv[{ci}]: type={cm.type} out of range")

# Summary for elements
n_with_mt = sum(1 for e in style.style_elements if e.master_tracks)
n_empty = sum(1 for e in style.style_elements if not e.master_tracks)
print(f"  Elements with MasterMidiTrack: {n_with_mt}")
print(f"  Empty elements: {n_empty}")

# 5. Compare with BANK01
print()
print("=== Comparison with BANK01.STY obj0 ===")
try:
    b2 = read_bank(BANK01_REAL)
    obj2 = b2.objects[0]
    style2 = parse_style(obj2)
    print(f"  BANK01 '{style2.info.name}': n_tracks={style2.track_mapping.n_midi_tracks}, "
          f"indices={len(style2.track_mapping.indices)}, "
          f"midi_tracks={len(style2.midi_tracks)}, "
          f"elements={len(style2.style_elements)}")
    # Compare track type distributions
    test_types = {}
    for t in style.midi_tracks:
        test_types[t.chunk_type] = test_types.get(t.chunk_type, 0) + 1
    b1_types = {}
    for t in style2.midi_tracks:
        b1_types[t.chunk_type] = b1_types.get(t.chunk_type, 0) + 1
    print(f"  test_out track types: {test_types}")
    print(f"  BANK01   track types: {b1_types}")
except Exception as ex:
    print(f"  BANK01 parse failed: {ex}")

# 6. Inner chunk hierarchy of MIDITrackList (deep parse)
print()
print("=== MIDITrackList inner structure (test_out) ===")
# Re-parse the inner MIDITrackList chunk manually
outer_hdr_id, outer_sz = struct.unpack_from('>II', obj, 0)
inner = obj[8: 8+outer_sz]
off = 0
n_style_info = 0
n_midi_list = 0
n_elem = 0
while off + 8 <= len(inner):
    raw_id, sz = struct.unpack_from('>II', inner, off)
    ct = (raw_id >> 24) & 0xFF
    vm = (raw_id >> 16) & 0xFF
    vn = (raw_id >> 8)  & 0xFF
    fl = raw_id & 0xFF
    if ct == 0x02:  # MIDITrackList
        n_midi_list += 1
        midi_list_data = inner[off+8: off+8+sz]
        # Parse sub-chunks
        sub_off = 0
        n_tm = 0; n_drum = 0; n_bass = 0; n_acc = 0; n_gtr = 0
        while sub_off + 8 <= len(midi_list_data):
            sub_id, sub_sz = struct.unpack_from('>II', midi_list_data, sub_off)
            sub_ct = (sub_id >> 24) & 0xFF
            if sub_ct == 0x01: n_tm += 1
            elif sub_ct == 0x02: n_drum += 1
            elif sub_ct == 0x03: n_bass += 1
            elif sub_ct == 0x04: n_acc += 1
            elif sub_ct == 0x05: n_gtr += 1
            sub_off += 8 + sub_sz
        print(f"  MIDITrackList sub-chunks: TrackMapping={n_tm} Drum={n_drum} Bass={n_bass} Acc={n_acc} Guitar={n_gtr}")
        print(f"    total sub-chunks: {n_tm+n_drum+n_bass+n_acc+n_gtr}")
        report("TrackMapping present (exactly 1)", n_tm == 1)
        report("total tracks match n_midi_tracks",
               n_drum+n_bass+n_acc+n_gtr == tm.n_midi_tracks,
               f"{n_drum+n_bass+n_acc+n_gtr} vs {tm.n_midi_tracks}")
    elif ct == 0x03:
        n_elem += 1
    off += 8 + sz

report("Exactly 1 MIDITrackList", n_midi_list == 1)
report(f"15 StyleElements", n_elem == 15, f"got {n_elem}")
