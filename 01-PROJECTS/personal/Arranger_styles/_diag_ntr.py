"""
Quick NTR diagnostic: check what ntr values are in the source Yamaha file.
"""
from tools.sff2_reader import parse_sff2, NTR_NAMES
from collections import Counter

src = r"données etude\YAMAHA (TYROS5)\Ballad\8BeatBallad1.T160.prs"
yamaha = parse_sff2(src)

print(f"Source: {src}")
print(f"Sections: {len(yamaha.sections)}")
print(f"CASM entries (CSEGs): {len(yamaha.casm)}")
print()

all_ntr = []
for cseg in yamaha.casm:
    for ch in cseg.channels:
        all_ntr.append(ch.ntr)

ntr_counts = Counter(all_ntr)
print(f"NTR value distribution across all CSEGs:")
for ntr_val, count in sorted(ntr_counts.items()):
    name = NTR_NAMES.get(ntr_val, f"Unknown({ntr_val})")
    print(f"  ntr={ntr_val} ({name}): {count} channels")

print()
print("First CSEG details:")
if yamaha.casm:
    cseg = yamaha.casm[0]
    print(f"  name={cseg.name!r}")
    for i, ch in enumerate(cseg.channels[:10]):
        print(f"  ch[{i}]: src_ch={ch.src_ch} ntr={ch.ntr}({NTR_NAMES.get(ch.ntr, '?')})")
