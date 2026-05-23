"""
style_writer.py — Encodeur pour la structure interne d'un style KORG (StyleData)

Produit des bytes compatibles avec bank.objects[i] pour un ObjectType.Style.
Utilise les mêmes structures que style_reader.py (KorgStyle, MidiTrack, etc.)

Hiérarchie encodée :
  type=0x01 v=5.0  flags=Container   → wrapper StyleData
    type=0x01 v=0.3  flags=Leaf      → StyleInfoData
    type=0x02 v=0.0  flags=Container → MIDITrackList
      type=0x01 v=0.0  flags=Leaf    → TrackMapping
      type=0x02 v=0.0  flags=Leaf    → DrumOrPerc track(s)
      type=0x03 v=0.0  flags=Leaf    → Bass track(s)
      type=0x04 v=0.0  flags=Leaf    → Accompaniment track(s)
      type=0x05 v=1.0  flags=Leaf    → Guitar track(s)
    type=0x03 v=0.0  flags=Container → StyleElement × N
      type=0x01 v=1.2  flags=Leaf    → StyleElementInfoData
      type=0x02 v=0.3  flags=Leaf    → StyleTrackData (8 canaux)
      type=0x03 v=0.0  flags=Leaf    → MasterMIDITrack × M
"""

import struct
from typing import List, Tuple

from tools.korf import encode_leaf, encode_container
from tools.style_reader import (
    KorgStyle, StyleInfo, StyleTrackEntry, ElementInfo, ChordTable,
    MidiTrack, MasterMidiTrack, ChordVariationTrackMapping,
    TrackMapping, StyleElement, KorgMidiEvent,
)


# ─────────────────────────────────────────────────────────────────────────────
# KORG MIDI encoding
# ─────────────────────────────────────────────────────────────────────────────

def encode_korg_delta(delta: int) -> bytes:
    """
    Encode un delta time KORG : MSB en premier, chaque byte avec bit7=1.
    delta=0 → b'' (aucun byte)
    """
    if delta == 0:
        return b''
    groups: List[int] = []
    while delta > 0:
        groups.append(delta & 0x7F)
        delta >>= 7
    groups.reverse()  # MSB first
    return bytes(0x80 | g for g in groups)


def encode_korg_events(events: List[KorgMidiEvent]) -> bytes:
    """
    Encode une liste de KorgMidiEvent en bytes bruts KORG MIDI.
    Les deltas sont émis juste avant l'événement suivant.
    """
    out = bytearray()
    for ev in events:
        if ev.type == 'delta':
            out += encode_korg_delta(ev.delta)
            continue

        if ev.unknown_additional is not None:
            # Pas produit par le converter mais on préserve lors du round-trip
            pass

        if ev.type in ('note_off', 'note_on', 'cc', 'rxnoise_off', 'rxnoise_on'):
            codes = {'note_off': 0, 'note_on': 1, 'cc': 3,
                     'rxnoise_off': 12, 'rxnoise_on': 13}
            code = codes[ev.type]
            # In KORG MIDI, the v2 byte (velocity for notes, value for CC) has
            # bit 7 set in the original format. The reader strips it, so we
            # restore it here for round-trip byte-identity and proper playback.
            v2_byte = (ev.value2 & 0x7F) | 0x80
            if ev.unknown_additional is not None:
                code |= 0x40
                out += bytes([code, ev.unknown_additional, ev.value1, v2_byte])
            else:
                out += bytes([code, ev.value1, v2_byte])

        elif ev.type == 'aftertouch':
            code = 5
            v1_byte = (ev.value1 & 0x7F) | 0x80
            if ev.unknown_additional is not None:
                code |= 0x40
                out += bytes([code, ev.unknown_additional, v1_byte])
            else:
                out += bytes([code, v1_byte])

        elif ev.type == 'bend':
            code = 6
            combined = ev.value1 + 8192  # value1 is the signed bend value
            b1 = combined & 0x7F
            b2 = ((combined >> 7) & 0x7F) | 0x80
            if ev.unknown_additional is not None:
                code |= 0x40
                out += bytes([code, ev.unknown_additional, b1, b2])
            else:
                out += bytes([code, b1, b2])

        elif ev.type == 'meta':
            lb1 = (len(ev.meta_data) >> 7) & 0x7F
            lb2 = len(ev.meta_data) & 0x7F
            out += bytes([9, ev.meta_type, lb1, lb2]) + ev.meta_data

        else:
            raise ValueError(f"KORG MIDI: type inconnu '{ev.type}'")

    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# MasterMidiTrack binary
# ─────────────────────────────────────────────────────────────────────────────

def encode_master_midi_track(track: MasterMidiTrack) -> bytes:
    """
    Encode un MasterMidiTrack en bytes.
    Format :
      [u16be=0] [timescale:u8] [unk2:u8] [unk3:u8] [u8=0] [data_len:u16be]
      [MIDI data]
      [n_entries:u8] [(type:u8, track_number:u8) × n]
    """
    midi_bytes = encode_korg_events(track.events)
    data_len = len(midi_bytes)

    header = struct.pack('>H', 0)                          # u16be = 0
    header += bytes([track.time_scale, track.unknown2, track.unknown3, 0])
    header += struct.pack('>H', data_len)

    footer = bytes([len(track.cv_track_mappings)])
    for m in track.cv_track_mappings:
        footer += bytes([m.type, m.track_number])

    return header + midi_bytes + footer


# ─────────────────────────────────────────────────────────────────────────────
# MidiTrack (global MIDI track) binary
# ─────────────────────────────────────────────────────────────────────────────

def encode_midi_track(track: MidiTrack) -> Tuple[bytes, int]:
    """
    Encode une piste globale MIDI en bytes + son chunk_type int.
    Returns (data_bytes, chunk_type_int) where chunk_type_int is used for
    the chunk header (0x02=drum, 0x03=bass, 0x04=acc, 0x05=guitar).
    """
    midi_bytes = encode_korg_events(track.events)
    data_len = len(midi_bytes)

    chunk_types = {'drum': 0x02, 'bass': 0x03, 'accompaniment': 0x04, 'guitar': 0x05}
    ct = chunk_types[track.chunk_type]

    buf = struct.pack('>H', 0)             # uint16 = 0
    buf += bytes([track.time_scale])

    unk = track.unknowns

    if ct == 0x02:  # DrumOrPerc: [ts][unk2][u16=0][data_len:u16be][midi]
        unk2 = unk[0] if len(unk) >= 1 else 0
        buf += bytes([unk2])
        buf += struct.pack('>H', 0)
        buf += struct.pack('>H', data_len)
        buf += midi_bytes

    elif ct == 0x03:  # Bass: [ts][unk2][unk3][u8=0][data_len:u16be][midi][unk4][unk5]
        unk2 = unk[0] if len(unk) >= 1 else 0
        unk3 = unk[1] if len(unk) >= 2 else 0
        unk4 = unk[2] if len(unk) >= 3 else 0
        unk5 = unk[3] if len(unk) >= 4 else 0
        buf += bytes([unk2, unk3, 0])
        buf += struct.pack('>H', data_len)
        buf += midi_bytes
        buf += bytes([unk4, unk5])

    elif ct == 0x04:  # Accompaniment: [ts][unk2][u8=0][u8=0][data_len:u16be][midi][unk3][unk4]
        unk2 = unk[0] if len(unk) >= 1 else 0
        unk3 = unk[1] if len(unk) >= 2 else 0
        unk4 = unk[2] if len(unk) >= 3 else 0
        buf += bytes([unk2, 0, 0])
        buf += struct.pack('>H', data_len)
        buf += midi_bytes
        buf += bytes([unk3, unk4])

    elif ct == 0x05:  # Guitar: [ts][unk2][u8=0][u8=0][data_len:u16be][midi][unk3][unk4]
        unk2 = unk[0] if len(unk) >= 1 else 0
        unk3 = unk[1] if len(unk) >= 2 else 0
        unk4 = unk[2] if len(unk) >= 3 else 0
        buf += bytes([unk2, 0, 0])
        buf += struct.pack('>H', data_len)
        buf += midi_bytes
        buf += bytes([unk3, unk4])

    return bytes(buf), ct


# ─────────────────────────────────────────────────────────────────────────────
# TrackMapping binary
# ─────────────────────────────────────────────────────────────────────────────

def encode_track_mapping(tm: TrackMapping) -> bytes:
    """
    Encode un TrackMapping.
    Format : [n_tracks:u16be] [n_entries:u16be] [indices:u16be × n_entries]
    """
    buf = struct.pack('>HH', tm.n_midi_tracks, len(tm.indices))
    for idx in tm.indices:
        buf += struct.pack('>H', idx)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# StyleInfoData binary (v0.3)
# ─────────────────────────────────────────────────────────────────────────────

def encode_style_info(info: StyleInfo) -> bytes:
    """
    Encode un StyleInfo en bytes (version 0.3).
    Format :
      [name_len:u8] [name_bytes] [unknown111:i16be] [unknown3:u8]
      [enabled:u16be] [unk_bytes:9] [unk15:u8] [unk16:u8]
      [style_elements_with_data:u16be]   (present because minor=3 > 2)
    """
    name_bytes = info.name.encode('ascii', errors='replace')
    unk = info.unknowns  # 2(i16be) + 1 + 9 + 1 + 1 = 14 bytes

    buf = bytes([len(name_bytes)]) + name_bytes
    buf += unk[:2]                              # unknown111 (i16be)
    buf += unk[2:3]                             # unknown3
    buf += struct.pack('>H', info.enabled_style_elements)
    buf += unk[3:12]                            # unk_bytes (9 bytes)
    buf += unk[12:13]                           # unk15
    buf += unk[13:14]                           # unk16
    buf += struct.pack('>H', info.style_elements_with_data)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# ElementInfo binary (v1.2)
# ─────────────────────────────────────────────────────────────────────────────

def encode_element_info(ei: ElementInfo) -> bytes:
    """
    Encode un ElementInfo en bytes (version 1.2).
    Format :
      [cv_flags:u8] [time_sig_encoded:u8] [n_chord_entries:u8]
      [chord_entries:n×u8] [cue_mode:u8]
      [unknown4:3 bytes] [unknown5:12 bytes]
    """
    import math
    denom_log2 = int(math.log2(ei.time_sig_denominator)) if ei.time_sig_denominator >= 1 else 2
    time_sig_encoded = (ei.time_sig_numerator << 3) | (denom_log2 & 0x7)

    entries = ei.chord_table.entries
    buf = bytes([
        ei.chord_variations_with_data,
        time_sig_encoded,
        len(entries),
    ])
    buf += bytes(entries)
    buf += bytes([ei.cue_mode])

    # unknown4 (3 bytes) and unknown5 (12 bytes) — present in v1.2
    unk4 = (ei.unknown4 + b'\x00' * 3)[:3]
    unk5 = (ei.unknown5 + b'\x00' * 12)[:12]
    buf += unk4
    buf += unk5

    return buf


# ─────────────────────────────────────────────────────────────────────────────
# StyleTrackData binary (v0.3)
# ─────────────────────────────────────────────────────────────────────────────

def encode_style_track_data(entries: List[StyleTrackEntry]) -> bytes:
    """
    Encode 8 StyleTrackEntry en bytes (version 0.3).
    Format :
      8 × [expr:u8][msb:u8][lsb:u8][pc:u8][range_bot:u8][range_top:u8]
      8 × unknown1[3]
      8 × ntt[1]
      8 × unknown3[1]
    """
    # Pad or truncate to exactly 8 entries
    while len(entries) < 8:
        from tools.style_reader import ProgramChangeSeq
        entries = list(entries) + [StyleTrackEntry(
            expression=127, sound=ProgramChangeSeq(0, 0, 0),
            range_bottom=0, range_top=127, ntt=0,
            unknown1=b'\x00\x00\x00', unknown3=4)]

    buf = b''
    for e in entries[:8]:
        buf += bytes([e.expression, e.sound.msb, e.sound.lsb, e.sound.program,
                      e.range_bottom, e.range_top])

    for e in entries[:8]:
        unk1 = (e.unknown1 + b'\x00\x00\x00')[:3]
        buf += unk1

    for e in entries[:8]:
        buf += bytes([e.ntt])

    for e in entries[:8]:
        buf += bytes([e.unknown3])

    return buf


# ─────────────────────────────────────────────────────────────────────────────
# StyleElement binary
# ─────────────────────────────────────────────────────────────────────────────

def encode_style_element(elem: StyleElement) -> bytes:
    """Encode un StyleElement complet (ElementInfo + TrackData + MasterTracks)."""
    ei_bytes = encode_element_info(elem.info)
    td_bytes = encode_style_track_data(elem.track_data)
    mt_bytes = b''
    for _cv_idx, mt in elem.master_tracks:
        mt_bytes += encode_master_midi_track(mt)

    # ElementInfo leaf: type=0x01 v=1.2
    ei_chunk = encode_leaf(0x01, 1, 2, ei_bytes, in_bank=False)
    # StyleTrackData leaf: type=0x02 v=0.3
    td_chunk = encode_leaf(0x02, 0, 3, td_bytes, in_bank=False)
    # MasterMidiTrack leafs: type=0x03 v=0.0 (one per CV)
    mt_chunks = b''
    for _cv_idx, mt in elem.master_tracks:
        mt_data = encode_master_midi_track(mt)
        mt_chunks += encode_leaf(0x03, 0, 0, mt_data, in_bank=False)

    children = ei_chunk + td_chunk + mt_chunks
    return encode_container(0x03, 0, 0, children, in_bank=False)


# ─────────────────────────────────────────────────────────────────────────────
# Full style binary (= bank.objects[i])
# ─────────────────────────────────────────────────────────────────────────────

def encode_style(style: KorgStyle) -> bytes:
    """
    Encode un KorgStyle complet en bytes (format bank.objects[i]).
    
    Returns bytes that can be stored as a StyleData object in a KORF bank.
    """
    # ── StyleInfoData leaf (type=0x01 v=0.3) ─────────────────────────────────
    info_bytes = encode_style_info(style.info)
    info_chunk = encode_leaf(0x01, 0, 3, info_bytes, in_bank=False)

    # ── MIDITrackList container (type=0x02 v=0.0) ─────────────────────────────
    tm_bytes = encode_track_mapping(style.track_mapping)
    tm_chunk = encode_leaf(0x01, 0, 0, tm_bytes, in_bank=False)

    track_chunks = b''
    for track in style.midi_tracks:
        track_data, ct = encode_midi_track(track)
        # version: drum/bass/acc=v0.0, guitar=v1.0
        if ct == 0x05:
            track_chunks += encode_leaf(ct, 1, 0, track_data, in_bank=False)
        else:
            track_chunks += encode_leaf(ct, 0, 0, track_data, in_bank=False)

    midi_list_children = tm_chunk + track_chunks
    midi_list_chunk = encode_container(0x02, 0, 0, midi_list_children, in_bank=False)

    # ── StyleElements containers (type=0x03 v=0.0) ──────────────────────────
    elem_chunks = b''
    for elem in style.style_elements:
        elem_chunks += encode_style_element(elem)

    # ── Outer wrapper container (type=0x01 v=5.0) ────────────────────────────
    inner = info_chunk + midi_list_chunk + elem_chunks
    return encode_container(0x01, 5, 0, inner, in_bank=False)
