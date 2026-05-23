"""
converter.py — Yamaha SFF2 → KORG PA4x style converter

Converts a YamahaStyle (from sff2_reader) into a KorgStyle (for style_writer).

Key mappings:
  - Yamaha sections → KORG StyleElements (by name mapping)
  - Yamaha channels → KORG global MidiTracks (by NTR type)
  - Yamaha ticks (1920/beat) → KORG ticks (timescale × 32 / beat)
  - Yamaha MIDI events → KORG MidiEvent format

NTR → KORG track type:
  NTR 0 (None/drum)  → drum        (chunk 0x02)
  NTR 1 (Bass)       → bass        (chunk 0x03)
  NTR 2 (Guitar)     → guitar      (chunk 0x05)
  NTR 3 (All/chord)  → accompaniment (chunk 0x04)

Section name mapping Yamaha → KORG StyleElement index:
  'Main A'      → 11 (Variation1)
  'Main B'      → 12 (Variation2)
  'Main C'      → 13 (Variation3)
  'Main D'      → 14 (Variation4)
  'Fill In AA'  → 2  (Fill1)
  'Fill In BB'  → 3  (Fill2)
  'Fill In CC'  → 9  (Fill3)
  'Fill In DD'  → 10 (Fill4)
  'Fill In BA'  → 6  (Break)
  'Intro A'     → 0  (Intro1)
  'Intro B'     → 1  (Intro2)
  'Intro C'     → 7  (Intro3)
  'Ending A'    → 4  (Ending1)
  'Ending B'    → 5  (Ending2)
  'Ending C'    → 8  (Ending3)
"""

import math
import os
import struct
from typing import Dict, List, Optional, Set, Tuple

from tools.sff2_reader import (
    YamahaStyle, StyleSection, MidiEvent, Ctb2Entry, CSEGEntry,
    NTR_NONE, NTR_BASS, NTR_GUITAR, NTR_ALL,
)
from tools.style_reader import (
    KorgStyle, StyleInfo, StyleElement, ElementInfo, ChordTable,
    StyleTrackEntry, ProgramChangeSeq, MidiTrack, MasterMidiTrack,
    ChordVariationTrackMapping, TrackMapping, KorgMidiEvent,
    STYLE_ELEMENT_NAMES,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

KORG_TIMESCALE = 24
KORG_TICKS_PER_BEAT = KORG_TIMESCALE * 32   # 768
YAMAHA_TICKS_PER_BEAT = 1920

# Maps Yamaha section name → KORG element index (0-based in STYLE_ELEMENT_NAMES)
YAMAHA_TO_KORG_ELEM: Dict[str, int] = {
    'Intro A':     0,   # Intro1
    'Intro B':     1,   # Intro2
    'Fill In AA':  2,   # Fill1
    'Fill In BB':  3,   # Fill2
    'Ending A':    4,   # Ending1
    'Ending B':    5,   # Ending2
    'Fill In BA':  6,   # Break
    'Intro C':     7,   # Intro3
    'Ending C':    8,   # Ending3
    'Fill In CC':  9,   # Fill3
    'Fill In DD': 10,   # Fill4
    'Main A':     11,   # Variation1
    'Main B':     12,   # Variation2
    'Main C':     13,   # Variation3
    'Main D':     14,   # Variation4
}

# Maps NTR → KORG track type string
NTR_TO_KORG_TYPE: Dict[int, str] = {
    NTR_NONE:   'drum',
    NTR_BASS:   'bass',
    NTR_GUITAR: 'guitar',
    NTR_ALL:    'accompaniment',
}

# Maps NTR → KORG ChordVariationTrackMapping.type (0=drum,1=bass,2=acc,3=guitar)
NTR_TO_CV_TYPE: Dict[int, int] = {
    NTR_NONE:   0,
    NTR_BASS:   1,
    NTR_ALL:    2,
    NTR_GUITAR: 3,
}

# Number of KORG StyleElements (always 15)
N_KORG_ELEMENTS = 15


# ─────────────────────────────────────────────────────────────────────────────
# Tick conversion
# ─────────────────────────────────────────────────────────────────────────────

def yamaha_tick_to_korg(ytick: int, timescale: int = KORG_TIMESCALE) -> int:
    """Convert a Yamaha tick (1920/beat) to KORG ticks (timescale×32/beat)."""
    return round(ytick * timescale * 32 / YAMAHA_TICKS_PER_BEAT)


# ─────────────────────────────────────────────────────────────────────────────
# Section length calculation
# ─────────────────────────────────────────────────────────────────────────────

def _section_length_yamaha(section: StyleSection, time_sig: Tuple[int, int]) -> int:
    """
    Compute section length in Yamaha ticks.
    Uses the last note-off or the last event tick + quantize to bar boundary.
    """
    num, den = time_sig
    ticks_per_bar = YAMAHA_TICKS_PER_BEAT * 4 * num // den

    if not section.events:
        return ticks_per_bar  # default 1 bar

    max_tick = max(e.tick for e in section.events)

    # Round up to nearest bar boundary
    if max_tick == 0:
        return ticks_per_bar
    n_bars = math.ceil(max_tick / ticks_per_bar)
    return n_bars * ticks_per_bar


# ─────────────────────────────────────────────────────────────────────────────
# Convert Yamaha MIDI events to KORG events
# ─────────────────────────────────────────────────────────────────────────────

def _yamaha_events_to_korg(
    yamaha_events: List[MidiEvent],
    src_ch: int,
    loop_delta_korg: int,
    timescale: int = KORG_TIMESCALE,
) -> List[KorgMidiEvent]:
    """
    Convert Yamaha MidiEvents on src_ch to a list of KorgMidiEvents
    (with deltas interleaved, and final EndOfTrack).

    The events are re-sorted by tick, and a loop delta is inserted before EOT.
    """
    # Filter and sort
    filtered = sorted(
        [e for e in yamaha_events if (e.status & 0x80) and (e.channel == src_ch)],
        key=lambda e: e.tick,
    )

    korg_events: List[KorgMidiEvent] = []
    current_korg_tick = 0

    for ev in filtered:
        korg_tick = yamaha_tick_to_korg(ev.tick, timescale)
        delta = korg_tick - current_korg_tick
        if delta > 0:
            korg_events.append(KorgMidiEvent(type='delta', delta=delta))
            current_korg_tick = korg_tick

        et = ev.event_type
        d = ev.data

        if et == 0x90 and len(d) >= 3:    # NoteOn
            vel = d[2]
            if vel == 0:
                korg_events.append(KorgMidiEvent(type='note_off', value1=d[1], value2=64))
            else:
                korg_events.append(KorgMidiEvent(type='note_on', value1=d[1], value2=vel))

        elif et == 0x80 and len(d) >= 3:  # NoteOff
            korg_events.append(KorgMidiEvent(type='note_off', value1=d[1], value2=d[2]))

        elif et == 0xB0 and len(d) >= 3:  # CC
            korg_events.append(KorgMidiEvent(type='cc', value1=d[1], value2=d[2]))

        elif et == 0xE0 and len(d) >= 3:  # PitchBend
            lsb = d[1] & 0x7F
            msb = d[2] & 0x7F
            combined = (msb << 7) | lsb
            value = combined - 8192
            korg_events.append(KorgMidiEvent(type='bend', value1=value))

        elif et == 0xD0 and len(d) >= 2:  # Channel Pressure (Aftertouch)
            korg_events.append(KorgMidiEvent(type='aftertouch', value1=d[1] & 0x7F))

        # Skip SysEx and other meta events

    # Insert loop delta then EndOfTrack
    remaining_delta = loop_delta_korg - current_korg_tick
    if remaining_delta > 0:
        korg_events.append(KorgMidiEvent(type='delta', delta=remaining_delta))
    korg_events.append(KorgMidiEvent(type='meta', meta_type=0x2F, meta_data=b''))

    return korg_events


# ─────────────────────────────────────────────────────────────────────────────
# Build KORG global MidiTracks from Yamaha channels
# ─────────────────────────────────────────────────────────────────────────────

def _collect_all_channels(yamaha: YamahaStyle) -> List[Ctb2Entry]:
    """
    Collect one Ctb2Entry per unique (src_ch, ntr) pair across all CSEGs.
    Returns sorted by (ntr, src_ch) for predictable ordering.
    """
    seen: Dict[Tuple[int, int], Ctb2Entry] = {}
    for cseg in yamaha.casm:
        for ctb2 in cseg.channels:
            key = (ctb2.ntr, ctb2.src_ch)
            if key not in seen:
                seen[key] = ctb2
    return sorted(seen.values(), key=lambda c: (NTR_TO_CV_TYPE.get(c.ntr, 99), c.src_ch))


def _build_global_tracks(
    channels: List[Ctb2Entry],
    yamaha: YamahaStyle,
    yamaha_section: StyleSection,
    loop_delta_korg: int,
    timescale: int = KORG_TIMESCALE,
) -> List[MidiTrack]:
    """Build one KORG global MidiTrack per Yamaha channel, with events from the section."""
    tracks = []
    for ctb2 in channels:
        # Classify KORG track type primarily by Yamaha source channel:
        #   ch 9-10 (0-based 8-9)     → drum
        #   ch 11   (0-based 10)      → bass
        #   ch 6-7  (0-based 5-6)     → guitar
        #   anything else             → accompaniment
        # NTR is used only as a fallback for non-standard channel numbers.
        ch0 = ctb2.src_ch  # 0-based
        if ctb2.is_drum() or ch0 in (8, 9):
            korg_type = 'drum'
        elif ch0 == 10:
            korg_type = 'bass'
        elif ch0 in (5, 6):
            korg_type = 'guitar'
        elif ch0 in (11, 12, 13, 14, 15):
            korg_type = 'accompaniment'
        else:
            korg_type = NTR_TO_KORG_TYPE.get(ctb2.ntr, 'accompaniment')
        events = _yamaha_events_to_korg(
            yamaha_section.events, ctb2.src_ch, loop_delta_korg, timescale)
        # unknowns: minimal (all zeros)
        if korg_type == 'drum':
            unknowns = b'\x00'
        elif korg_type == 'bass':
            unknowns = b'\x00\x00\x00\x00'
        else:
            unknowns = b'\x00\x00\x00'
        tracks.append(MidiTrack(
            chunk_type=korg_type,
            time_scale=timescale,
            events=events,
            unknowns=unknowns,
        ))
    return tracks


# ─────────────────────────────────────────────────────────────────────────────
# Build KORG StyleElement
# ─────────────────────────────────────────────────────────────────────────────

def _default_chord_table(n_cv: int) -> ChordTable:
    """All chord variations map to CV[0] (index 0)."""
    # Standard KORG chord table has 24 entries
    return ChordTable(entries=[0] * 24)


def _make_element_info(
    time_sig: Tuple[int, int],
    n_cv: int,
    cue_mode: int = 0,
) -> ElementInfo:
    """Create an ElementInfo for a KORG StyleElement with n_cv chord variations."""
    num, den = time_sig
    # cv_flags: bits for CV[0]..CV[n_cv-1]
    cv_flags = (1 << n_cv) - 1

    chord_table = _default_chord_table(n_cv)

    return ElementInfo(
        chord_variations_with_data=cv_flags,
        time_sig_numerator=num,
        time_sig_denominator=den,
        chord_table=chord_table,
        cue_mode=cue_mode,
        unknown4=b'\x00\x00\x00',
        unknown5=b'\x00' * 12,
    )


def _make_style_track_entries(channels: List[Ctb2Entry]) -> List[StyleTrackEntry]:
    """
    Create 8 StyleTrackEntry from Yamaha channel info.
    Up to 8 channels are used; the rest get default/empty entries.

    Default sound: GM2 Grand Piano (msb=121, lsb=0, pc=0) for melodic tracks,
    GM2 Standard Kit (msb=120, lsb=0, pc=0) for drum tracks. These map to
    valid KORG PA4x factory sounds and avoid "unreferenced sound" crashes.
    """
    def _default_sound(ctb2: Ctb2Entry) -> ProgramChangeSeq:
        if ctb2.is_drum() or ctb2.src_ch in (8, 9):
            return ProgramChangeSeq(120, 0, 0)   # Standard Drum Kit (factory)
        return ProgramChangeSeq(121, 0, 0)       # Grand Piano (factory)

    entries = []
    for i in range(8):
        if i < len(channels):
            ctb2 = channels[i]
            entries.append(StyleTrackEntry(
                expression=127,
                sound=_default_sound(ctb2),
                range_bottom=0,
                range_top=127,
                ntt=1,  # Bypass (no transposition) — safe default
                unknown1=b'\x00\x00\x00',
                unknown3=4,
            ))
        else:
            # Empty slot → harmless Grand Piano default
            entries.append(StyleTrackEntry(
                expression=127,
                sound=ProgramChangeSeq(121, 0, 0),
                range_bottom=0,
                range_top=127,
                ntt=1,
                unknown1=b'\x00\x00\x00',
                unknown3=4,
            ))
    return entries


def _build_master_midi_track(
    channels: List[Ctb2Entry],
    loop_delta_korg: int,
    timescale: int = KORG_TIMESCALE,
    track_index_offset: int = 0,
) -> MasterMidiTrack:
    """
    Build a MasterMidiTrack for one chord variation.

    The MIDI data contains one UnknownMaster meta (0x7E) event per channel,
    followed by a loop delta and EndOfTrack.

    cv_track_mappings reference the absolute position in the global TrackMapping.
    """
    # Build UnknownMaster events (one per channel, slot_idx = position in channels list)
    events: List[KorgMidiEvent] = []
    for i, _ctb2 in enumerate(channels):
        slot_idx = i  # slot index within this CV's channel list
        # Meta 0x7E: data = [03, slot_idx, 00, 00]
        events.append(KorgMidiEvent(
            type='meta',
            meta_type=0x7E,
            meta_data=bytes([0x03, slot_idx, 0x00, 0x00]),
        ))

    # Loop delta + EndOfTrack
    events.append(KorgMidiEvent(type='delta', delta=loop_delta_korg))
    events.append(KorgMidiEvent(type='meta', meta_type=0x2F, meta_data=b''))

    # cv_track_mappings: index into the GLOBAL TrackMapping.indices array
    # (0-based). Each element's tracks occupy a contiguous block in that
    # array starting at `track_index_offset`. Without this offset, every
    # element would reference element 0's tracks → only element 0 plays.
    cv_mappings = []
    for i, ctb2 in enumerate(channels):
        # Use the same classification as global track types so the mapping
        # type matches the actual track type. (0=drum, 1=bass, 2=acc, 3=guitar)
        ch0 = ctb2.src_ch
        if ctb2.is_drum() or ch0 in (8, 9):
            cv_type = 0  # drum
        elif ch0 == 10:
            cv_type = 1  # bass
        elif ch0 in (5, 6):
            cv_type = 3  # guitar
        elif ch0 in (11, 12, 13, 14, 15):
            cv_type = 2  # accompaniment
        else:
            cv_type = NTR_TO_CV_TYPE.get(ctb2.ntr, 2)
        cv_mappings.append(ChordVariationTrackMapping(
            type=cv_type,
            track_number=track_index_offset + i,
        ))

    return MasterMidiTrack(
        time_scale=timescale,
        unknown2=0,
        unknown3=0,
        events=events,
        cv_track_mappings=cv_mappings,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Empty element (for elements with no Yamaha section data)
# ─────────────────────────────────────────────────────────────────────────────

def _make_empty_element(time_sig: Tuple[int, int]) -> StyleElement:
    """Create a minimal empty StyleElement (CV[0] only, no note events)."""
    timescale = KORG_TIMESCALE
    num, den = time_sig
    ticks_per_bar_korg = KORG_TICKS_PER_BEAT * 4 * num // den
    loop_delta = ticks_per_bar_korg

    ei = ElementInfo(
        chord_variations_with_data=0x01,  # CV[0] only
        time_sig_numerator=num,
        time_sig_denominator=den,
        chord_table=ChordTable(entries=[0] * 24),
        cue_mode=0,
        unknown4=b'\x00\x00\x00',
        unknown5=b'\x00' * 12,
    )

    # Minimal master track: just delta + EOT
    mt = MasterMidiTrack(
        time_scale=timescale,
        unknown2=0,
        unknown3=0,
        events=[
            KorgMidiEvent(type='delta', delta=loop_delta),
            KorgMidiEvent(type='meta', meta_type=0x2F, meta_data=b''),
        ],
        cv_track_mappings=[],
    )

    track_entries = [StyleTrackEntry(
        expression=127,
        sound=ProgramChangeSeq(121, 0, 0),   # Grand Piano (factory)
        range_bottom=0,
        range_top=127,
        ntt=1,
        unknown1=b'\x00\x00\x00',
        unknown3=4,
    ) for _ in range(8)]

    return StyleElement(info=ei, track_data=track_entries, master_tracks=[(0, mt)])


# ─────────────────────────────────────────────────────────────────────────────
# Main conversion
# ─────────────────────────────────────────────────────────────────────────────

def convert_style(yamaha: YamahaStyle, name: Optional[str] = None) -> KorgStyle:
    """
    Convert a YamahaStyle to a KorgStyle.

    Args:
        yamaha: parsed Yamaha style
        name: override style name (defaults to basename of yamaha.path)

    Returns:
        KorgStyle ready for encoding with style_writer.encode_style()
    """
    timescale = KORG_TIMESCALE
    time_sig = yamaha.time_sig

    if name is None:
        base = os.path.basename(yamaha.path)
        name = base.split('.')[0][:16]   # max 16 chars for KORG style name

    # ── Step 1: Collect all unique Yamaha channels ─────────────────────────
    all_channels = _collect_all_channels(yamaha)
    n_channels = len(all_channels)

    # ── Step 2: Build one global MidiTrack per channel per section ─────────
    # We need one set of global tracks per StyleElement (each element gets its own)
    # KORG design: each element references global tracks via TrackMapping
    # We'll build a flat list of tracks: for each element, for each channel

    # Map Yamaha section name → KORG element index
    section_map: Dict[int, StyleSection] = {}  # elem_idx → section
    for sec in yamaha.sections:
        if sec.name in YAMAHA_TO_KORG_ELEM:
            elem_idx = YAMAHA_TO_KORG_ELEM[sec.name]
            section_map[elem_idx] = sec

    # ── Step 3: Build global tracks + TrackMapping ─────────────────────────
    # For each element that has a corresponding Yamaha section,
    # we create n_channels global tracks. The TrackMapping indices list
    # tells each element/CV which global track to use.
    #
    # Layout of global tracks:
    #   elem0_ch0, elem0_ch1, ..., elem0_chN,
    #   elem1_ch0, elem1_ch1, ..., elem1_chN,
    #   ...
    # TrackMapping.indices entries are 1-based.

    global_tracks: List[MidiTrack] = []
    tm_indices: List[int] = []   # 1-based global track indices, built per-element

    style_elements: List[StyleElement] = []

    for elem_idx in range(N_KORG_ELEMENTS):
        sec = section_map.get(elem_idx)

        if sec is None or not sec.events:
            # No data for this element — create empty element
            elem = _make_empty_element(time_sig)
            style_elements.append(elem)
            # No tracks added for empty elements (master has no cv_mappings)
            continue

        # Compute loop length in Yamaha ticks, then KORG ticks
        yamaha_len = _section_length_yamaha(sec, time_sig)
        loop_delta_korg = yamaha_tick_to_korg(yamaha_len, timescale)

        # Determine which channels are used by this section
        # Find the CSEG that covers this section
        cseg = yamaha.cseg_for_section(sec.name)
        if cseg is not None:
            section_channels = cseg.channels
        else:
            section_channels = all_channels

        # KORG style format limits to 8 slots per master track (8 meta 0x7E
        # events, 8 entries in StyleTrackData). If more Yamaha channels are
        # present, keep only the first 8 to avoid overflow into non-existent
        # slots (which causes "playChunk" errors in KPM/PA4x).
        if len(section_channels) > 8:
            section_channels = section_channels[:8]

        # Build global tracks for this element
        first_global_idx = len(global_tracks) + 1  # 1-based
        tracks = _build_global_tracks(
            section_channels, yamaha, sec, loop_delta_korg, timescale)
        global_tracks.extend(tracks)

        # Build TrackMapping entries for this element's CV[0]
        indices_for_elem = list(range(first_global_idx, first_global_idx + len(tracks)))
        for idx_1based in indices_for_elem:
            tm_indices.append(idx_1based)

        # Build MasterMidiTrack — track_numbers must be GLOBAL indices
        # into TrackMapping.indices. Use `first_global_idx - 1` as offset
        # (first_global_idx is 1-based, track_number is 0-based).
        mt = _build_master_midi_track(
            section_channels,
            loop_delta_korg,
            timescale,
            track_index_offset=first_global_idx - 1,
        )

        # Build element info
        ei = _make_element_info(time_sig, 1)  # 1 chord variation
        track_entries = _make_style_track_entries(section_channels)

        style_elements.append(StyleElement(
            info=ei,
            track_data=track_entries,
            master_tracks=[(0, mt)],
        ))

        # (tm_abs_offset no longer needed; PA Manager tracks the global offset)

    # ── Step 4: Build TrackMapping ─────────────────────────────────────────
    track_mapping = TrackMapping(
        n_midi_tracks=len(global_tracks),
        indices=tm_indices,
    )

    # ── Step 5: Build StyleInfo ────────────────────────────────────────────
    # enabled_style_elements: bitmask of all 15 elements
    enabled_mask = (1 << N_KORG_ELEMENTS) - 1
    # style_elements_with_data: bitmask of elements that have data
    with_data_mask = 0
    for elem_idx, sec in section_map.items():
        if sec.events:
            with_data_mask |= (1 << elem_idx)

    # StyleInfo "unknowns" layout (14 bytes) :
    #   2 bytes : unknown111 (i16be) — varie selon le style (probablement hash/tempo)
    #   1 byte  : unknown3            — flags ; valeurs vues : 0x00, 0xc8, 0xf8
    #   9 bytes : unk_bytes           — DOIT commencer par 0x01 0x08 0x08
    #                                  (les 6 octets suivants varient par style)
    #   1 byte  : unk15 (toujours 0)
    #   1 byte  : unk16 (toujours 0)
    # Sans ces magiques (notamment unk_bytes[0]=0x01), KORG PA Manager rejette
    # la banque avec « Possibly corrupt index STYLE Chunk ».
    unknowns = (
        b'\x59\x50'                              # unknown111 (valeur arbitraire valide)
        + b'\xf8'                                # unknown3
        + b'\x01\x08\x08\x08\x08\x08\x08\x08\x08'  # unk_bytes (préfixe magique + défauts neutres)
        + b'\x00\x00'                            # unk15 + unk16
    )
    assert len(unknowns) == 14

    style_info = StyleInfo(
        name=name,
        enabled_style_elements=enabled_mask,
        style_elements_with_data=with_data_mask,
        unknowns=unknowns,
    )

    return KorgStyle(
        info=style_info,
        track_mapping=track_mapping,
        midi_tracks=global_tracks,
        style_elements=style_elements,
    )
