import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src = u"donn\u00e9es etude\\YAMAHA (TYROS5)\\Ballad\\8BeatBallad1.T160.prs"
print(f"Testing path: {src!r}")
print(f"Exists: {os.path.exists(src)}")

try:
    from tools.sff2_reader import read_style, NTR_NAMES
    from collections import Counter
    yamaha = read_style(src)
    print(f"OK: sections={len(yamaha.sections)} casm={len(yamaha.casm)}")
    all_ntr = []
    for cseg in yamaha.casm:
        for ch in cseg.channels:
            all_ntr.append(ch.ntr)
    ntr_counts = Counter(all_ntr)
    for ntr_val, count in sorted(ntr_counts.items()):
        name = NTR_NAMES.get(ntr_val, f"Unknown({ntr_val})")
        print(f"  ntr={ntr_val} ({name}): {count} channels")
    if yamaha.casm:
        cseg = yamaha.casm[0]
        print(f"First CSEG: {cseg.sections}")
        for ch in cseg.channels[:5]:
            print(f"  {ch}")
except Exception as ex:
    import traceback
    traceback.print_exc()
