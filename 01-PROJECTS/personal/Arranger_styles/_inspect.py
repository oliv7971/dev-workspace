"""Inspect notre USER01 vs un style 'planet' qui marche."""
import sys
from tools.korf import read_bank, ObjectType
from tools.style_reader import parse_style

def show(path, label):
    bank = read_bank(path)
    print(f"\n=== {label}: {path} ===")
    for i, e in enumerate(bank.toc):
        if e.object_type != ObjectType.Style:
            continue
        st = parse_style(bank.objects[i])
        print(f"\nStyle: {st.info.name}")
        print(f"  midi_tracks ({len(st.midi_tracks)}):")
        for j, t in enumerate(st.midi_tracks):
            n_ev = sum(1 for ev in t.events if ev.type != 'delta')
            print(f"    [{j}] {t.chunk_type:15s} ts={t.time_scale}  events={n_ev}  unknowns={t.unknowns.hex()}")
        print(f"  track_mapping: n={st.track_mapping.n_midi_tracks}  indices={st.track_mapping.indices}")
        print(f"  style_elements ({len(st.style_elements)}):")
        for j, el in enumerate(st.style_elements[:3]):
            print(f"    elem[{j}]: cv_flags=0x{el.info.chord_variations_with_data:02x} cue_mode={el.info.cue_mode}")
            for k, te in enumerate(el.track_data):
                print(f"      track[{k}]: expr={te.expression} sound=({te.sound.msb},{te.sound.lsb},{te.sound.program}) ntt={te.ntt} unk1={te.unknown1.hex()} unk3={te.unknown3}")
            print(f"      master_tracks ({len(el.master_tracks)}):")
            for cv_idx, mt in el.master_tracks[:4]:
                n_ev = sum(1 for ev in mt.events if ev.type != 'delta')
                cvm = [(m.type, m.track_number) for m in mt.cv_track_mappings]
                print(f"        cv={cv_idx} ts={mt.time_scale} unk2={mt.unknown2} unk3={mt.unknown3} ev={n_ev} cvm={cvm}")
        return st

a = show(r"verif\TEST.SET\STYLE\USER01.STY", "OURS")
b = show(r"données etude\KORG (PA4x international )\KPM_planetKeyboard.SET\STYLE\FAVORITE01.STY", "REF")
