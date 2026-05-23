"""
style_reader.py — Parser pour la structure interne d'un style KORF (StyleData)
Porté depuis KORG-Tools (C++, GPL v3 — Amir Czwink)

Hiérarchie dans bank.objects[i] pour un Style :

  type=0x01 v=5.x  flags=Container   → wrapper StyleData
    type=0x01 v=0.x  flags=Leaf      → StyleInfoData       (1 seul)
    type=0x02 v=0.0  flags=Container → MIDITrackList        (1 seul)
      type=0x01 v=0.0  flags=Leaf    → TrackMapping
      type=0x02 v=0.0  flags=Leaf    → DrumOrPerc track(s)
      type=0x03 v=0.0  flags=Leaf    → Bass track(s)
      type=0x04 v=0.0  flags=Leaf    → Accompaniment track(s)
      type=0x05 v=x.x  flags=Leaf    → Guitar track(s)
    type=0x03 v=0.0  flags=Container → StyleElement × N
      type=0x01 v=1.x  flags=Leaf    → StyleElementInfoData
      type=0x02 v=0.x  flags=Leaf    → StyleTrackData (8 canaux)
      type=0x03 v=0.0  flags=Leaf    → MasterMIDITrack × M (chord variations)

KORG MIDI Events :
  Si byte & 0x80 → delta time variable-length (accumulé jusqu'à byte sans bit7)
  Ensuite event type byte :
    bit 6 = unknownAdditional (lire 1 byte supplémentaire avant les data)
    0 = NoteOff   (note, vel avec bit7 → masquer)
    1 = NoteOn    (note, vel avec bit7 → masquer)
    3 = CC        (ctrl, val avec bit7 → masquer)
    5 = Aftertouch (pressure avec bit7 → masquer)
    6 = PitchBend  (2 bytes → combined = (b2<<7)|b1, valeur = -8192+combined)
    9 = MetaEvent  (type:1 + length:2 + data)
        type 0x2F = EndOfTrack, type 0x7E = UnknownMaster
   12 = RXnoiseOff
   13 = RXnoiseOn
"""

import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from tools.korf import iter_chunks


# =============================================================================
# KORG MIDI Events
# =============================================================================

@dataclass
class KorgMidiEvent:
    """Un événement KORG MIDI décodé."""
    type: str               # 'delta','note_off','note_on','cc','aftertouch','bend','meta',
                            # 'rxnoise_off','rxnoise_on'
    delta: int = 0          # pour 'delta'
    value1: int = 0
    value2: int = 0
    unknown_additional: Optional[int] = None
    meta_type: int = 0      # pour 'meta'
    meta_data: bytes = b''  # pour 'meta'

    def __repr__(self) -> str:
        if self.type == 'delta':
            return f"Delta({self.delta})"
        if self.type in ('note_on', 'note_off'):
            return f"{self.type}(note={self.value1}, vel={self.value2})"
        if self.type == 'cc':
            return f"CC(ctrl={self.value1}, val={self.value2})"
        if self.type == 'bend':
            return f"Bend({self.value1})"
        if self.type == 'meta':
            return f"Meta(type=0x{self.meta_type:02X}, len={len(self.meta_data)})"
        return f"{self.type}(v1={self.value1}, v2={self.value2})"


def decode_korg_midi(data: bytes) -> List[KorgMidiEvent]:
    """Décode une séquence d'événements KORG MIDI depuis des bytes bruts."""
    events: List[KorgMidiEvent] = []
    pos = 0
    n = len(data)

    while pos < n:
        b = data[pos]; pos += 1

        # Delta time variable-length (bit7 = continuation)
        if b & 0x80:
            total = 0
            while b & 0x80:
                total = (total << 7) | (b & 0x7F)
                b = data[pos]; pos += 1
            events.append(KorgMidiEvent(type='delta', delta=total))

        # unknownAdditional si bit6 mis
        unk_add: Optional[int] = None
        if b & 0x40:
            b &= ~0x40
            unk_add = data[pos]; pos += 1

        # Dispatch sur le type d'événement
        if b in (0, 1, 3, 12, 13):
            v1 = data[pos]; pos += 1
            v2 = data[pos] & 0x7F; pos += 1
            names = {0: 'note_off', 1: 'note_on', 3: 'cc',
                     12: 'rxnoise_off', 13: 'rxnoise_on'}
            events.append(KorgMidiEvent(
                type=names[b], value1=v1, value2=v2,
                unknown_additional=unk_add))

        elif b == 5:  # Aftertouch
            v1 = data[pos] & 0x7F; pos += 1
            events.append(KorgMidiEvent(type='aftertouch', value1=v1,
                                        unknown_additional=unk_add))

        elif b == 6:  # PitchBend
            b1 = data[pos]; pos += 1
            b2 = data[pos] & 0x7F; pos += 1
            combined = (b2 << 7) | b1
            value = -8192 + combined
            events.append(KorgMidiEvent(type='bend', value1=value,
                                        unknown_additional=unk_add))

        elif b == 9:  # MetaEvent
            meta_type = data[pos]; pos += 1
            lb1 = data[pos]; pos += 1
            lb2 = data[pos]; pos += 1
            meta_len = (lb1 << 7) | (lb2 & 0x7F)
            meta_data = data[pos:pos + meta_len]; pos += meta_len
            events.append(KorgMidiEvent(type='meta', meta_type=meta_type,
                                        meta_data=meta_data))
            if meta_type == 0x2F:  # EndOfTrack
                break

        else:
            raise ValueError(
                f"KORG MIDI: type inconnu 0x{b:02X} à pos {pos - 1}")

    return events


# =============================================================================
# Structures de données
# =============================================================================

@dataclass
class StyleInfo:
    name: str
    enabled_style_elements: int    # bitmask
    style_elements_with_data: int  # bitmask
    unknowns: bytes


@dataclass
class ProgramChangeSeq:
    msb: int
    lsb: int
    program: int

    def __str__(self) -> str:
        return f"MSB={self.msb} LSB={self.lsb} PC={self.program}"


@dataclass
class StyleTrackEntry:
    expression: int
    sound: ProgramChangeSeq
    range_bottom: int
    range_top: int
    ntt: int
    unknown1: bytes
    unknown3: int = 4
    unknown4: int = 0


@dataclass
class ChordTable:
    entries: List[int]   # 22 ou 24 indices de chord variation


@dataclass
class ElementInfo:
    chord_variations_with_data: int   # bitmask des CV disponibles
    time_sig_numerator: int
    time_sig_denominator: int
    chord_table: ChordTable
    cue_mode: int = 0
    unknown4: bytes = b''
    unknown5: bytes = b''


@dataclass
class ChordVariationTrackMapping:
    type: int
    track_number: int


@dataclass
class MasterMidiTrack:
    time_scale: int
    unknown2: int
    unknown3: int
    events: List[KorgMidiEvent]
    cv_track_mappings: List[ChordVariationTrackMapping]


@dataclass
class StyleElement:
    info: ElementInfo
    track_data: List[StyleTrackEntry]           # toujours 8 entrées
    master_tracks: List[Tuple[int, MasterMidiTrack]]  # (cv_index, track)


@dataclass
class MidiTrack:
    chunk_type: str    # 'drum', 'bass', 'accompaniment', 'guitar'
    time_scale: int
    events: List[KorgMidiEvent]
    unknowns: bytes    # bytes divers selon le type


@dataclass
class TrackMapping:
    n_midi_tracks: int
    indices: List[int]


@dataclass
class KorgStyle:
    info: StyleInfo
    track_mapping: Optional[TrackMapping]
    midi_tracks: List[MidiTrack]
    style_elements: List[StyleElement]   # dans l'ordre du fichier


# =============================================================================
# Lecteur binaire interne
# =============================================================================

class _R:
    """Lecteur binaire positionnel."""

    def __init__(self, data: bytes):
        self._d = data
        self.pos = 0

    def read(self, n: int) -> bytes:
        v = self._d[self.pos:self.pos + n]
        self.pos += n
        return v

    def u8(self) -> int:
        v = self._d[self.pos]
        self.pos += 1
        return v

    def u16be(self) -> int:
        v = struct.unpack_from('>H', self._d, self.pos)[0]
        self.pos += 2
        return v

    def i16be(self) -> int:
        v = struct.unpack_from('>h', self._d, self.pos)[0]
        self.pos += 2
        return v

    def remaining(self) -> int:
        return len(self._d) - self.pos


# =============================================================================
# Parseurs des structures individuelles
# =============================================================================

def _parse_style_info(data: bytes, version_minor: int) -> StyleInfo:
    r = _R(data)
    name_len = r.u8()
    name = r.read(name_len).decode('ascii', errors='replace')
    unknown111 = r.i16be()
    unknown3 = r.u8()
    enabled = r.u16be()
    unk_bytes = r.read(9)
    unk15 = r.u8()
    unk16 = r.u8()
    if version_minor > 2:
        style_elements_with_data = r.u16be()
    else:
        style_elements_with_data = enabled
    return StyleInfo(
        name=name,
        enabled_style_elements=enabled,
        style_elements_with_data=style_elements_with_data,
        unknowns=(struct.pack('>h', unknown111) +
                  bytes([unknown3]) + unk_bytes +
                  bytes([unk15, unk16])),
    )


def _parse_chord_table(r: _R) -> ChordTable:
    n = r.u8()
    entries = [r.u8() for _ in range(n)]
    return ChordTable(entries=entries)


def _parse_element_info(data: bytes, major: int, minor: int) -> ElementInfo:
    r = _R(data)
    cv_flags = r.u8()

    # major=0 : ntt global (déprécié, on le lit puis on l'ignore)
    if major == 0:
        _ntt_global = r.u8()

    time_sig_encoded = r.u8()
    numerator = time_sig_encoded >> 3
    denominator = 1 << (time_sig_encoded & 7)

    chord_table = _parse_chord_table(r)

    cue_mode = 0
    unknown4 = b''
    unknown5 = b''

    # cueMode présent si version > 0.0
    if (major, minor) > (0, 0):
        cue_mode = r.u8()

    if major >= 1:
        if minor >= 2:
            unknown4 = r.read(3)
            unknown5 = r.read(12)
        if minor >= 3:
            _unk6 = r.u8()

    return ElementInfo(
        chord_variations_with_data=cv_flags,
        time_sig_numerator=numerator,
        time_sig_denominator=denominator,
        chord_table=chord_table,
        cue_mode=cue_mode,
        unknown4=unknown4,
        unknown5=unknown5,
    )


def _parse_style_track_data(data: bytes, minor: int) -> List[StyleTrackEntry]:
    r = _R(data)

    # v0.0 : expression + son + plages de clavier
    base = []
    for _ in range(8):
        expr = r.u8()
        msb = r.u8(); lsb = r.u8(); pc = r.u8()
        rb = r.u8(); rt = r.u8()
        base.append({'expr': expr,
                     'sound': ProgramChangeSeq(msb, lsb, pc),
                     'rb': rb, 'rt': rt})

    # v0.1 : unknown1[3] par piste
    unk1_list = [b'\x00\x00\x00'] * 8
    if minor >= 1:
        for i in range(8):
            unk1_list[i] = r.read(3)

    # v0.2 : ntt par piste
    ntts = [0] * 8
    if minor >= 2:
        for i in range(8):
            ntts[i] = r.u8()

    # v0.3 : unknown3 par piste
    unk3s = [4] * 8
    if minor >= 3:
        for i in range(8):
            unk3s[i] = r.u8()

    # v0.4 : unknown4 par piste
    unk4s = [0] * 8
    if minor >= 4:
        for i in range(8):
            unk4s[i] = r.u8()

    return [
        StyleTrackEntry(
            expression=base[i]['expr'],
            sound=base[i]['sound'],
            range_bottom=base[i]['rb'],
            range_top=base[i]['rt'],
            ntt=ntts[i],
            unknown1=unk1_list[i],
            unknown3=unk3s[i],
            unknown4=unk4s[i],
        )
        for i in range(8)
    ]


def _parse_master_midi_track(data: bytes) -> MasterMidiTrack:
    r = _R(data)
    zero = r.u16be()
    if zero != 0:
        raise ValueError(f"MasterMIDITrack: uint16=0 attendu, reçu {zero}")
    time_scale = r.u8()
    unk2 = r.u8()
    unk3 = r.u8()
    r.u8()   # assert == 0
    data_len = r.u16be()
    midi_data = r.read(data_len)
    events = decode_korg_midi(midi_data)

    n_entries = r.u8()
    cv_mappings = [
        ChordVariationTrackMapping(type=r.u8(), track_number=r.u8())
        for _ in range(n_entries)
    ]
    return MasterMidiTrack(time_scale=time_scale, unknown2=unk2,
                           unknown3=unk3, events=events,
                           cv_track_mappings=cv_mappings)


def _parse_midi_track(chunk_type: int, major: int, minor: int,
                      data: bytes) -> MidiTrack:
    """Parse une piste du MIDITrackList en fonction de son type."""
    r = _R(data)
    r.u16be()   # assert == 0
    time_scale = r.u8()

    if chunk_type == 0x02:          # DrumOrPerc
        unk2 = r.u8()
        r.u16be()                   # assert == 0
        data_len = r.u16be()
        events = decode_korg_midi(r.read(data_len))
        return MidiTrack('drum', time_scale, events, bytes([unk2]))

    elif chunk_type == 0x03:        # Bass
        unk2 = r.u8(); unk3 = r.u8()
        r.u8()                      # assert == 0
        data_len = r.u16be()
        events = decode_korg_midi(r.read(data_len))
        unk4 = r.u8(); unk5 = r.u8()
        return MidiTrack('bass', time_scale, events,
                         bytes([unk2, unk3, unk4, unk5]))

    elif chunk_type == 0x04:        # Accompaniment
        unk2 = r.u8()
        r.u8()                      # assert == 0
        r.u8()                      # assert == 0
        data_len = r.u16be()
        events = decode_korg_midi(r.read(data_len))
        unk3 = r.u8(); unk4 = r.u8()
        return MidiTrack('accompaniment', time_scale, events,
                         bytes([unk2, unk3, unk4]))

    elif chunk_type == 0x05:        # Guitar (v1.x ou v0.1)
        unk2 = r.u8()
        r.u8()                      # assert == 0
        r.u8()                      # assert == 0
        data_len = r.u16be()
        events = decode_korg_midi(r.read(data_len))
        unk3 = r.u8(); unk4 = r.u8()
        return MidiTrack('guitar', time_scale, events, bytes([unk2, unk3, unk4]))

    else:
        raise ValueError(f"MIDITrackList: type inconnu 0x{chunk_type:02X}")


def _parse_track_mapping(data: bytes) -> TrackMapping:
    r = _R(data)
    n_tracks = r.u16be()
    n_entries = r.u16be()
    indices = [r.u16be() for _ in range(n_entries)]
    return TrackMapping(n_midi_tracks=n_tracks, indices=indices)


# =============================================================================
# Parseur principal
# =============================================================================

def parse_style(style_data: bytes) -> KorgStyle:
    """
    Parse les données décompressées d'un style KORF.
    style_data = bank.objects[i] pour une entrée ObjectType.Style.

    Retourne un KorgStyle avec toutes les sous-structures peuplées.
    """
    # Couche 1 : outer wrapper (type=0x01 v=5.x)
    chunks_l1 = list(iter_chunks(style_data))
    if not chunks_l1:
        raise ValueError("StyleData vide")
    outer_hdr, outer_data = chunks_l1[0]
    if outer_hdr.chunk_type != 0x01:
        raise ValueError(
            f"StyleData: type=0x01 attendu, reçu 0x{outer_hdr.chunk_type:02X}")

    style_info: Optional[StyleInfo] = None
    track_mapping: Optional[TrackMapping] = None
    midi_tracks: List[MidiTrack] = []
    style_elements: List[StyleElement] = []

    # Couche 2 : StyleInfo | MIDITrackList | StyleElements
    for hdr, data in iter_chunks(outer_data):
        ct = hdr.chunk_type

        if ct == 0x01:
            # StyleInfoData
            style_info = _parse_style_info(data, hdr.version_minor)

        elif ct == 0x02:
            # MIDITrackList (container)
            for sub_hdr, sub_data in iter_chunks(data):
                sct = sub_hdr.chunk_type
                if sct == 0x01:
                    track_mapping = _parse_track_mapping(sub_data)
                elif sct in (0x02, 0x03, 0x04, 0x05):
                    track = _parse_midi_track(
                        sct, sub_hdr.version_major,
                        sub_hdr.version_minor, sub_data)
                    midi_tracks.append(track)

        elif ct == 0x03:
            # StyleElement (container)
            elem_info: Optional[ElementInfo] = None
            track_data: Optional[List[StyleTrackEntry]] = None
            master_tracks: List[Tuple[int, MasterMidiTrack]] = []
            remaining_cv_flags = 0
            next_cv_idx = 0

            for sub_hdr, sub_data in iter_chunks(data):
                sct = sub_hdr.chunk_type

                if sct == 0x01:
                    elem_info = _parse_element_info(
                        sub_data, sub_hdr.version_major, sub_hdr.version_minor)
                    remaining_cv_flags = elem_info.chord_variations_with_data
                    next_cv_idx = 0

                elif sct == 0x02:
                    track_data = _parse_style_track_data(
                        sub_data, sub_hdr.version_minor)

                elif sct == 0x03:
                    # Avancer au prochain bit mis dans remaining_cv_flags
                    while (remaining_cv_flags & 1) == 0 and remaining_cv_flags != 0:
                        next_cv_idx += 1
                        remaining_cv_flags >>= 1
                    cv_idx = next_cv_idx
                    next_cv_idx += 1
                    remaining_cv_flags >>= 1

                    mt = _parse_master_midi_track(sub_data)
                    master_tracks.append((cv_idx, mt))

            style_elements.append(StyleElement(
                info=elem_info,
                track_data=track_data or [],
                master_tracks=master_tracks,
            ))

    return KorgStyle(
        info=style_info,
        track_mapping=track_mapping,
        midi_tracks=midi_tracks,
        style_elements=style_elements,
    )


# =============================================================================
# Noms des éléments de style (d'après StyleElementNumber dans KORG-Tools)
# =============================================================================

# Ordre des StyleElements dans le fichier :
# les éléments non-variation d'abord (11 éléments), puis les 4 variations
STYLE_ELEMENT_NAMES = [
    'Intro1', 'Intro2', 'Fill1', 'Fill2',
    'Ending1', 'Ending2', 'Break',
    'Intro3', 'Ending3', 'Fill3', 'Fill4',
    'Variation1', 'Variation2', 'Variation3', 'Variation4',
]


# =============================================================================
# Utilitaires d'affichage
# =============================================================================

def dump_style(style: KorgStyle) -> None:
    """Affiche un résumé lisible d'un KorgStyle parsé."""
    info = style.info
    print(f"Style: {info.name!r}")
    print(f"  Enabled elements  : 0b{info.enabled_style_elements:015b}")
    print(f"  Elements with data: 0b{info.style_elements_with_data:015b}")

    if style.track_mapping:
        tm = style.track_mapping
        print(f"  TrackMapping: {tm.n_midi_tracks} pistes MIDI, "
              f"{len(tm.indices)} entrées de mapping")

    print(f"  MIDITrackList: {len(style.midi_tracks)} pistes")
    for i, t in enumerate(style.midi_tracks):
        print(f"    [{i:2d}] {t.chunk_type:15s}  "
              f"timescale={t.time_scale}  {len(t.events)} événements KORG MIDI")

    print(f"  StyleElements: {len(style.style_elements)}")
    for i, elem in enumerate(style.style_elements):
        name = STYLE_ELEMENT_NAMES[i] if i < len(STYLE_ELEMENT_NAMES) else f'Element{i}'
        ei = elem.info
        cv_count = bin(ei.chord_variations_with_data).count('1')
        print(f"    [{i:2d}] {name:<12s}  "
              f"{ei.time_sig_numerator}/{ei.time_sig_denominator}  "
              f"cv_flags=0b{ei.chord_variations_with_data:08b} ({cv_count} CVs)  "
              f"cueMode={ei.cue_mode}  "
              f"master_tracks={len(elem.master_tracks)}")
        if elem.track_data:
            for j, td in enumerate(elem.track_data):
                print(f"      ch{j}  expr={td.expression:3d}  "
                      f"{td.sound}  "
                      f"range=[{td.range_bottom}..{td.range_top}]  "
                      f"ntt=0x{td.ntt:02X}")
