"""Round-trip + sound usage check sur la SET 'KORG (PA4x international )'."""
import os, sys, glob
from collections import Counter
from tools.korf import read_bank, ObjectType
from tools.style_reader import parse_style
from tools.style_writer import encode_style as write_style

ROOT = sys.argv[1] if len(sys.argv) > 1 else r"données etude\KORG (PA4x international )\KPM_planetKeyboard.SET\STYLE"

styles = sorted(glob.glob(os.path.join(ROOT, "*.STY")))
print(f"{len(styles)} fichiers .STY")

global_sounds = Counter()
for path in styles:
    with open(path, "rb") as f:
        raw = f.read()
    try:
        bank = read_bank(path)
    except Exception as e:
        print(f"  PARSE FAIL {os.path.basename(path)}: {e}")
        continue
    style_pairs = [(e, bank.objects[i]) for i, e in enumerate(bank.toc)
                   if e.object_type == ObjectType.Style and i < len(bank.objects)]
    print(f"\n{os.path.basename(path)}: {len(style_pairs)} style(s)")
    for entry, raw in style_pairs:
        try:
            st = parse_style(raw)
        except Exception as e:
            print(f"  parse_style fail: {e}")
            continue
        # round-trip
        re_bytes = write_style(st)
        ok = re_bytes == raw
        # collect sounds used
        sounds_local = []
        for elem in st.style_elements:
            for entry in elem.track_data:
                pc = entry.sound
                if pc:
                    sounds_local.append((pc.msb, pc.lsb, pc.program))
        c = Counter(sounds_local)
        global_sounds.update(c)
        print(f"  {st.info.name:20s}  RT={'OK' if ok else 'DIFF'}  sounds={len(c)} uniques")

print("\n=== Top 30 sons utilisés ===")
for snd, n in global_sounds.most_common(30):
    print(f"  msb={snd[0]:3d} lsb={snd[1]:3d} pc={snd[2]:3d}  ×{n}")
