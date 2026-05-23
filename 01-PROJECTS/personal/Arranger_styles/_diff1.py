"""Diff bytes-level entre raw original et write_style sur 1 style."""
import sys
from tools.korf import read_bank, ObjectType
from tools.style_reader import parse_style
from tools.style_writer import encode_style

PATH = sys.argv[1] if len(sys.argv) > 1 else r"données etude\KORG (PA4x international )\KPM_planetKeyboard.SET\STYLE\FAVORITE01.STY"

bank = read_bank(PATH)
for i, e in enumerate(bank.toc):
    if e.object_type == ObjectType.Style:
        raw = bank.objects[i]
        st = parse_style(raw)
        re = encode_style(st)
        print(f"orig={len(raw)} re={len(re)} delta={len(re)-len(raw)}")
        # find first diff after offset 16 (skip outer header sizes)
        n = min(len(raw), len(re))
        for k in range(16, n):
            if raw[k] != re[k]:
                print(f"first content diff @ 0x{k:x}")
                lo = max(0, k-32); hi = min(n, k+64)
                print("ORIG:", raw[lo:hi].hex())
                print("OURS:", re[lo:hi].hex())
                break
        else:
            if len(raw) != len(re):
                print(f"size diff at end")
        break
