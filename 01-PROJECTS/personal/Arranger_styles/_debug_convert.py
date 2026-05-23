import traceback, sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    print("Step 1: import sff2_reader")
    from tools.sff2_reader import read_style
    print("Step 2: import converter")
    from tools.converter import convert_style
    print("Step 3: import style_writer")
    from tools.style_writer import encode_style
    print("Step 4: import korf_writer")
    from tools.korf_writer import write_bank
    print("Step 5: read yamaha")
    yamaha = read_style(r'données etude\YAMAHA (TYROS5)\Ballad\8BeatBallad1.T160.prs')
    print(f"  OK: {yamaha.style_name!r}, {len(yamaha.sections)} sections")
    for s in yamaha.sections:
        print(f"    section: {s.name!r}")
    print("Step 6: convert")
    korg = convert_style(yamaha)
    print(f"  OK: {len(korg.midi_tracks)} tracks, {len(korg.style_elements)} elements")
    print("Step 7: encode")
    data = encode_style(korg)
    print(f"  OK: {len(data)} bytes")
except Exception as e:
    traceback.print_exc()
