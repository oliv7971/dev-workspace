"""Dump détaillé d'un style KORG : pistes MIDI, CV mappings, events."""
import sys
sys.path.insert(0, '.')
from tools.korf import read_bank
from tools.style_reader import parse_style, STYLE_ELEMENT_NAMES

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
# Prendre le premier style (les objets Style sont aux entrées TOC de type Style)
style_entries = bank.style_entries()
print(f"Banque: {len(bank.objects)} objets, {len(style_entries)} styles")
# bank.objects contient uniquement les Style (les PerformancesData sont interlacés dans le TOC)
# On prend le premier objet
style_data = bank.objects[0]
style = parse_style(style_data)
print(f"Style: {style.info.name!r}")
print()

# MIDITrackList (pistes globales)
print(f"=== MIDITrackList ({len(style.midi_tracks)} pistes) ===")
for i, t in enumerate(style.midi_tracks):
    evts = [e for e in t.events if e.type != 'delta']
    note_on = [e for e in evts if e.type == 'note_on']
    cc_evts = [e for e in evts if e.type == 'cc']
    print(f"  [{i}] {t.chunk_type:15s}  timescale={t.time_scale}  "
          f"total={len(t.events)}  noteOn={len(note_on)}  CC={len(cc_evts)}")
    # Premiers events
    for e in evts[:3]:
        print(f"       {e}")

print()

# Mapping des pistes
if style.track_mapping:
    tm = style.track_mapping
    print(f"=== TrackMapping: {tm.n_midi_tracks} MIDI tracks, {len(tm.indices)} indices ===")
    print(f"  indices: {tm.indices}")
    print()

# Premier style element en détail
print(f"=== StyleElement[0]: {STYLE_ELEMENT_NAMES[0]} ===")
elem = style.style_elements[0]
ei = elem.info
print(f"  TimeSig: {ei.time_sig_numerator}/{ei.time_sig_denominator}")
print(f"  CV flags: 0b{ei.chord_variations_with_data:08b}")
print(f"  Chord table: {ei.chord_table.entries}")
print(f"  Track data (8 canaux):")
for j, td in enumerate(elem.track_data):
    print(f"    ch{j}: expr={td.expression}  {td.sound}  range=[{td.range_bottom}..{td.range_top}]  ntt=0x{td.ntt:02X}  unk3={td.unknown3}  unk4={td.unknown4}")
print(f"  MasterMIDITracks: {len(elem.master_tracks)}")
for cv_idx, mt in elem.master_tracks:
    note_ons = [e for e in mt.events if e.type == 'note_on']
    ccs = [e for e in mt.events if e.type == 'cc']
    metas = [e for e in mt.events if e.type == 'meta']
    print(f"    CV[{cv_idx}]: timescale={mt.time_scale}  total={len(mt.events)}  "
          f"noteOn={len(note_ons)}  CC={len(ccs)}  meta={len(metas)}")
    print(f"    cv_track_mappings: {[(m.type, m.track_number) for m in mt.cv_track_mappings]}")
    print(f"    Premiers events:")
    n = 0
    for e in mt.events:
        if e.type == 'delta':
            continue
        print(f"      {e}")
        n += 1
        if n >= 8: break

print()
# 3 premiers elements pour voir le pattern
for i in range(min(3, len(style.style_elements))):
    elem = style.style_elements[i]
    name = STYLE_ELEMENT_NAMES[i] if i < len(STYLE_ELEMENT_NAMES) else f'?{i}'
    print(f"=== StyleElement[{i}]: {name} ===")
    for cv_idx, mt in elem.master_tracks:
        note_ons = [e for e in mt.events if e.type == 'note_on']
        print(f"  CV[{cv_idx}]: {len(mt.events)} events ({len(note_ons)} noteOn), "
              f"cv_mappings={[(m.type, m.track_number) for m in mt.cv_track_mappings]}")
