"""Dump BANK01 first MasterMidiTrack footer and all track_numbers."""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from tools.korf import read_bank
from tools.style_reader import parse_style

REF = r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY"
GEN = "test_out.STY"

def u32be(d, off): return struct.unpack_from('>I', d, off)[0]
def u16be(d, off): return struct.unpack_from('>H', d, off)[0]

for label, path in [("BANK01", REF), ("test_out", GEN)]:
    print(f"\n{'='*60}")
    print(f"{label}")
    print('='*60)
    bk = read_bank(path)
    sdata = bk.objects[0]
    parsed = parse_style(sdata)

    n_indices = len(parsed.track_mapping.indices)
    n_tracks  = parsed.track_mapping.n_midi_tracks
    print(f"  n_tracks={n_tracks}, n_indices={n_indices}")
    print(f"  first 10 indices: {parsed.track_mapping.indices[:10]}")

    all_tn = []
    for ei, elem in enumerate(parsed.style_elements):
        for ci, (cv_idx, mt) in enumerate(elem.master_tracks):
            for mi, m in enumerate(mt.cv_track_mappings):
                all_tn.append(m.track_number)

    if all_tn:
        print(f"  track_numbers range: [{min(all_tn)}, {max(all_tn)}]")
        print(f"  first 20 track_numbers: {all_tn[:20]}")
        # Check 0-based validity  
        invalid_0 = [tn for tn in all_tn if tn < 0 or tn >= n_indices]
        # Check 1-based validity
        invalid_1 = [tn for tn in all_tn if tn < 1 or tn > n_indices]
        print(f"  0-based check (0..{n_indices-1}): {'OK' if not invalid_0 else f'INVALID: {invalid_0[:5]}'}")
        print(f"  1-based check (1..{n_indices}): {'OK' if not invalid_1 else f'INVALID: {invalid_1[:5]}'}")
    
    # Check what indices[track_number] actually points to  
    print(f"\n  First element, CV 0 mappings:")
    for ci, (cv_idx, mt) in enumerate(parsed.style_elements[0].master_tracks):
        for mi, m in enumerate(mt.cv_track_mappings):
            tn = m.track_number
            idx_val = parsed.track_mapping.indices[tn] if 0 <= tn < n_indices else "INVALID"
            print(f"    mapping[{mi}]: type={m.type}  track_number={tn}  -> indices[{tn}]={idx_val}")

print("\nDone.")
