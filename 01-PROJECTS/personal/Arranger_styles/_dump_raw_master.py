"""Dump binaire brut des MasterMidiTrack pour comprendre l'encodage exact."""
import sys, struct
sys.path.insert(0, '.')
from tools.korf import read_bank, iter_chunks

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')
style_data = bank.objects[0]

# Naviguer manuellement dans la hiérarchie pour extraire les MasterMidiTracks bruts
from tools.korf import iter_chunks

chunks_l1 = list(iter_chunks(style_data))
outer_hdr, outer_data = chunks_l1[0]

elem_raws = []
for hdr, data in iter_chunks(outer_data):
    if hdr.chunk_type == 0x03:  # StyleElement
        for sub_hdr, sub_data in iter_chunks(data):
            if sub_hdr.chunk_type == 0x03:  # MasterMidiTrack
                elem_raws.append(sub_data)

print(f"MasterMidiTrack raw blocs: {len(elem_raws)}")
print()

# Les 3 premiers raw blocs de l'element 0
print("=== Intro1 - MasterMidiTrack bruts ===")
for i, raw in enumerate(elem_raws[:6]):
    print(f"\n  Track {i} ({len(raw)} bytes): {raw.hex()}")
    # Décoder manuellement
    # Format: u16be=0, timescale:u8, unk2:u8, unk3:u8, u8=0, data_len:u16be, data[data_len], n_entries:u8, entries[n_entries]
    pos = 0
    zero = struct.unpack_from('>H', raw, pos)[0]; pos += 2
    ts   = raw[pos]; pos += 1
    u2   = raw[pos]; pos += 1
    u3   = raw[pos]; pos += 1
    z2   = raw[pos]; pos += 1
    dlen = struct.unpack_from('>H', raw, pos)[0]; pos += 2
    midi = raw[pos:pos+dlen]; pos += dlen
    n    = raw[pos]; pos += 1
    entries = [(raw[pos+j*2], raw[pos+j*2+1]) for j in range(n)]
    print(f"    zero={zero} ts={ts} u2={u2} u3={u3} z2={z2} dlen={dlen}")
    print(f"    midi_hex: {midi.hex()}")
    print(f"    n_entries={n} entries={entries}")

    # Décoder le MIDI
    from tools.style_reader import decode_korg_midi
    events = decode_korg_midi(midi)
    print(f"    events: {events}")
