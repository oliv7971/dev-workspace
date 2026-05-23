"""
Parser for Yamaha SFF2 arranger style files (.prs, .sst).

Supports all variants:
  Tyros3   : T108
  Tyros5   : T150-T166
  PSR-S    : S74x, S94x
  Expansion: .sst files (same binary format as .prs)

Usage:
    from tools.sff2_reader import read_style, dump_style
    style = read_style("MyStyle.T160.prs")
    dump_style(style)
"""

import os
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ─── VLQ helpers ──────────────────────────────────────────────────────────────

def _read_vlq(data: bytes, pos: int) -> Tuple[int, int]:
    """Read a MIDI Variable Length Quantity. Returns (value, new_pos)."""
    val = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        val = (val << 7) | (b & 0x7F)
        if not (b & 0x80):
            break
    return val, pos


def _encode_vlq(value: int) -> bytes:
    """Encode an integer as a MIDI Variable Length Quantity."""
    assert value >= 0
    result = [value & 0x7F]
    value >>= 7
    while value:
        result.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(result)


# ─── Data structures ──────────────────────────────────────────────────────────

# Note Transposition Rule constants (SFF2 spec)
NTR_NONE   = 0   # No transposition (percussion)
NTR_BASS   = 1   # Transpose to chord root (bass lines)
NTR_GUITAR = 2   # Guitar mode (single key chord voicing)
NTR_ALL    = 3   # Transpose all chord tones

NTR_NAMES = {0: "None", 1: "Bass", 2: "Guitar", 3: "All"}

# Standard SFF2 section names in display order
SECTION_ORDER = [
    "Main A", "Main B", "Main C", "Main D",
    "Fill In AA", "Fill In AB", "Fill In BA", "Fill In BB",
    "Fill In CC", "Fill In DD",
    "Intro A", "Intro B", "Intro C",
    "Ending A", "Ending B", "Ending C",
    "Fill In BA",
]


@dataclass
class Ctb2Entry:
    """One channel entry in a SFF2 Ctb2 channel table (47 bytes).

    Ctb2 binary layout:
      [0]    src_ch  — source MIDI channel, 0-based
      [1:9]  name    — 8 bytes, ASCII, space-padded
      [9]    src_ch  — repeated (confirmed by hex analysis)
      [10]   ntr     — Note Transposition Rule
      [11]   ntt     — Note Transposition Table
      [12:]  extra   — 35 bytes (OTS / variation chord data)
    """
    src_ch: int    # Source MIDI channel, 0-based (0=Ch1 … 15=Ch16)
    name: str      # Instrument name (8 chars, trailing spaces stripped)
    ntr: int       # Note Transposition Rule
    ntt: int       # Note Transposition Table
    raw: bytes     # Full raw payload (47 bytes typically)

    @property
    def midi_channel(self) -> int:
        """1-based MIDI channel number."""
        return self.src_ch + 1

    def is_drum(self) -> bool:
        """Heuristic: channel 8 or 9 (0-based) → percussion."""
        return self.src_ch in (8, 9) or self.ntr == NTR_NONE

    def __repr__(self) -> str:
        ntr = NTR_NAMES.get(self.ntr, str(self.ntr))
        return (f"Ctb2(ch={self.src_ch+1:2d}, name={self.name!r:12s}, "
                f"ntr={ntr}, ntt=0x{self.ntt:02X})")


@dataclass
class CSEGEntry:
    """A CSEG block groups sections that share the same channel configuration."""
    sections: List[str]        # e.g. ['Main A', 'Main B', 'Fill In AA']
    channels: List[Ctb2Entry]  # channel assignments for this group

    def channel_for(self, src_ch_0based: int) -> Optional[Ctb2Entry]:
        """Return the Ctb2 entry for a given 0-based MIDI channel, or None."""
        return next((c for c in self.channels if c.src_ch == src_ch_0based), None)

    def channel_by_name(self, name: str) -> Optional[Ctb2Entry]:
        """Return the Ctb2 entry whose name matches (case-insensitive, partial)."""
        name_lo = name.lower()
        return next((c for c in self.channels if name_lo in c.name.lower()), None)


@dataclass
class MidiEvent:
    """A MIDI event at a relative tick within its style section."""
    tick: int    # Ticks from the start of the section (relative)
    data: bytes  # Raw event bytes: [status, data1, data2?] — no delta time

    @property
    def status(self) -> int:
        return self.data[0] if self.data else 0

    @property
    def channel(self) -> int:
        """0-based MIDI channel (only valid for channel events)."""
        return (self.status & 0x0F)

    @property
    def event_type(self) -> int:
        """Event type nibble (0x80=NoteOff, 0x90=NoteOn, 0xB0=CC, etc.)."""
        return (self.status & 0xF0)


@dataclass
class StyleSection:
    """One arranger style section (Main A, Intro B, Ending C, …)."""
    name: str
    events: List[MidiEvent] = field(default_factory=list)

    @property
    def duration_ticks(self) -> int:
        """Tick of the last event (approximate section duration)."""
        return max((e.tick for e in self.events), default=0)

    def events_on_channel(self, ch_0based: int) -> List[MidiEvent]:
        """All events on a specific 0-based MIDI channel."""
        return [e for e in self.events
                if (e.status & 0x80) and (e.channel == ch_0based)]

    def note_events(self) -> List[MidiEvent]:
        """Note On and Note Off events only."""
        return [e for e in self.events if e.event_type in (0x80, 0x90)]

    def cc_events(self, cc_num: Optional[int] = None) -> List[MidiEvent]:
        """Control Change events, optionally filtered by CC number."""
        evs = [e for e in self.events if e.event_type == 0xB0]
        if cc_num is not None:
            evs = [e for e in evs if len(e.data) >= 2 and e.data[1] == cc_num]
        return evs


@dataclass
class YamahaStyle:
    """A fully parsed Yamaha SFF2 arranger style."""
    path: str
    sff_version: str           # 'SFF2' (or 'SFF1' for very old files)
    style_name: str            # Human-readable style name
    ticks_per_beat: int        # Typically 1920
    tempo: int                 # Initial tempo in µs/beat (at tick 0)
    time_sig: Tuple[int, int]  # (numerator, denominator)
    sections: List[StyleSection]
    casm: List[CSEGEntry]
    has_fnrc: bool             # True if FNRc chunk present

    @property
    def bpm(self) -> float:
        return 60_000_000 / self.tempo if self.tempo else 0.0

    def section(self, name: str) -> Optional[StyleSection]:
        """Return the section with the given name, or None."""
        return next((s for s in self.sections if s.name == name), None)

    def cseg_for_section(self, section_name: str) -> Optional[CSEGEntry]:
        """Return the CSEG that contains the given section name, or None."""
        for cseg in self.casm:
            if section_name in cseg.sections:
                return cseg
        return None

    def sections_by_order(self) -> List[StyleSection]:
        """Return sections sorted by standard SFF2 display order."""
        order = {name: i for i, name in enumerate(SECTION_ORDER)}
        return sorted(self.sections,
                      key=lambda s: order.get(s.name, len(SECTION_ORDER)))


# ─── Internal parsers ─────────────────────────────────────────────────────────

def _parse_ctb2(payload: bytes) -> Ctb2Entry:
    """Parse a Ctb2 channel-table entry (always 47 bytes in SFF2).

    Format confirmed by binary analysis of T108/T151/T160/T162/T406 files:
      byte [0]    = src_ch  (0-based MIDI channel)
      bytes [1:9] = name    (8 ASCII bytes, space-padded)
      byte [9]    = src_ch  (repeated)
      byte [10]   = NTR     (Note Transposition Rule)
      byte [11]   = NTT     (Note Transposition Table)
      bytes [12:] = extra   (35 bytes: OTS/chord variation data)
    """
    if len(payload) < 12:
        raise ValueError(f"Ctb2 too short: {len(payload)} bytes")
    src_ch = payload[0]
    name   = payload[1:9].rstrip(b' ').decode('ascii', 'replace')
    ntr    = payload[10]
    ntt    = payload[11]
    return Ctb2Entry(src_ch=src_ch, name=name, ntr=ntr, ntt=ntt, raw=bytes(payload))


def _parse_sdec(payload: bytes) -> List[str]:
    """Parse a Sdec section-description payload.

    The payload is a comma+space separated list of section names,
    e.g. b'Main A,Main B,Fill In AA,Fill In BB'.
    """
    text = payload.rstrip(b'\x00').decode('ascii', 'replace')
    return [s.strip() for s in text.split(',') if s.strip()]


def _iter_chunks(data: bytes, start: int, end: int):
    """Iterate RIFF-style chunks: tag(4) + size(4 BE) + payload(size)."""
    pos = start
    while pos + 8 <= end:
        tag = data[pos:pos+4].decode('latin1')
        sz  = struct.unpack_from('>I', data, pos+4)[0]
        if pos + 8 + sz > end:
            break
        yield tag, sz, data[pos+8 : pos+8+sz]
        pos += 8 + sz


def _parse_casm(data: bytes, casm_off: int) -> List[CSEGEntry]:
    """Parse the CASM block and return a list of CSEGEntry."""
    casm_sz = struct.unpack_from('>I', data, casm_off + 4)[0]
    csegs: List[CSEGEntry] = []

    for tag, sz, payload in _iter_chunks(data, casm_off + 8, casm_off + 8 + casm_sz):
        if tag != 'CSEG':
            continue
        sections: List[str] = []
        channels: List[Ctb2Entry] = []
        for tag2, sz2, p2 in _iter_chunks(payload, 0, len(payload)):
            if tag2 == 'Sdec':
                sections = _parse_sdec(p2)
            elif tag2 == 'Ctb2':
                try:
                    channels.append(_parse_ctb2(p2))
                except ValueError:
                    pass  # skip malformed entries silently
        csegs.append(CSEGEntry(sections=sections, channels=channels))

    return csegs


def _parse_mtrk(mtrk_data: bytes) -> Tuple:
    """Parse the main style MTrk.

    Handles both section-delimiter strategies used in SFF2:
      - 0xFF 0x06 Marker events with section names (all versions)
      - 0xFF 0x01 Text  events with "fn:<section>" prefix (Tyros5 T16x)

    When both appear at the same tick for the same section, the Marker takes
    priority and the Text event is ignored (it's redundant).

    Returns:
        (tempo, time_sig, sff_version, style_name, sections)
    """
    pos = 0
    abs_tick = 0
    running_status = 0

    tempo      = 500000       # default 120 BPM
    time_sig   = (4, 4)
    sff_version = 'SFF2'
    style_name  = ''
    tempo_set   = False

    # Section accumulation
    current_name: Optional[str] = None
    current_start: int = 0
    sections_raw: Dict[str, List[MidiEvent]] = {}
    section_order: List[str] = []   # preserve insertion order

    def _begin_section(name: str) -> None:
        nonlocal current_name, current_start
        current_name  = name
        current_start = abs_tick
        if name not in sections_raw:
            sections_raw[name] = []
            section_order.append(name)

    def _store_event(evt_bytes: bytes) -> None:
        if current_name is not None:
            rel_tick = abs_tick - current_start
            sections_raw[current_name].append(MidiEvent(tick=rel_tick, data=evt_bytes))

    while pos < len(mtrk_data):
        # ── Delta time ────────────────────────────────────────────────────────
        delta, pos = _read_vlq(mtrk_data, pos)
        abs_tick += delta

        if pos >= len(mtrk_data):
            break

        status = mtrk_data[pos]

        # ── Meta event ────────────────────────────────────────────────────────
        if status == 0xFF:
            pos += 1
            if pos >= len(mtrk_data):
                break
            meta_type = mtrk_data[pos]; pos += 1
            meta_len, pos = _read_vlq(mtrk_data, pos)
            meta_data = mtrk_data[pos : pos + meta_len]; pos += meta_len

            if meta_type == 0x51:                          # Set Tempo
                if not tempo_set:
                    b = b'\x00' + meta_data[:3]
                    tempo = struct.unpack_from('>I', b)[0]
                    tempo_set = True

            elif meta_type == 0x58:                        # Time Signature
                if len(meta_data) >= 2:
                    time_sig = (meta_data[0], 1 << meta_data[1])

            elif meta_type == 0x03:                        # Track Name
                raw_name = meta_data.rstrip(b'\x00').decode('ascii', 'replace')
                # Track name is typically the filename; extract base name
                style_name = os.path.splitext(os.path.basename(raw_name))[0]
                # Strip version suffix (.T160, .T108, …)
                import re
                style_name = re.sub(r'\.(T|S)\d+$', '', style_name)

            elif meta_type == 0x06:                        # Marker
                name = meta_data.rstrip(b'\x00').decode('ascii', 'replace')
                if name == 'SFF2':
                    sff_version = 'SFF2'
                elif name == 'SFF1':
                    sff_version = 'SFF1'
                elif name not in ('SInt',):               # skip control markers
                    _begin_section(name)

            elif meta_type == 0x01:                        # Text
                text = meta_data.rstrip(b'\x00').decode('ascii', 'replace')
                if text.startswith('fn:'):
                    # Tyros5-style section delimiter — only start if not already
                    # started by a Marker event at the same tick
                    fn_name = text[3:]
                    if current_name != fn_name:
                        _begin_section(fn_name)

            elif meta_type == 0x2F:                        # End of Track
                break

        # ── SysEx ─────────────────────────────────────────────────────────────
        elif status in (0xF0, 0xF7):
            pos += 1
            sx_len, pos = _read_vlq(mtrk_data, pos)
            sx_data = mtrk_data[pos : pos + sx_len]; pos += sx_len
            # Store SysEx only inside sections (skip global setup at tick 0)
            if current_name is not None:
                # Reconstruct F0 + length + data (self-contained)
                evt = bytes([status]) + _encode_vlq(sx_len) + sx_data
                _store_event(evt)

        # ── Channel event with explicit status byte ───────────────────────────
        elif status & 0x80:
            running_status = status
            ch_type = status & 0xF0
            pos += 1  # consume status byte

            if ch_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):  # 2 data bytes
                if pos + 2 > len(mtrk_data):
                    break
                d1, d2 = mtrk_data[pos], mtrk_data[pos + 1]; pos += 2
                _store_event(bytes([status, d1, d2]))

            elif ch_type in (0xC0, 0xD0):                   # 1 data byte
                if pos >= len(mtrk_data):
                    break
                d1 = mtrk_data[pos]; pos += 1
                _store_event(bytes([status, d1]))
            # 0xF0..0xFE already handled above; 0xFF handled above

        # ── Running status ────────────────────────────────────────────────────
        elif running_status & 0x80:
            ch_type = running_status & 0xF0

            if ch_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):  # 2 data bytes
                if pos + 2 > len(mtrk_data):
                    break
                d1, d2 = mtrk_data[pos], mtrk_data[pos + 1]; pos += 2
                _store_event(bytes([running_status, d1, d2]))

            elif ch_type in (0xC0, 0xD0):                   # 1 data byte
                if pos >= len(mtrk_data):
                    break
                d1 = mtrk_data[pos]; pos += 1
                _store_event(bytes([running_status, d1]))

        else:
            # Unknown byte — skip to avoid infinite loop
            pos += 1

    # Build ordered StyleSection list
    sections = [
        StyleSection(name=name, events=sections_raw[name])
        for name in section_order
    ]
    return tempo, time_sig, sff_version, style_name, sections


# ─── Public API ───────────────────────────────────────────────────────────────

def read_style(path: str) -> YamahaStyle:
    """Parse a Yamaha SFF2 style file (.prs or .sst).

    Args:
        path: Absolute or relative path to the file.

    Returns:
        YamahaStyle containing all parsed sections and CASM data.

    Raises:
        ValueError: If the file is not a valid SFF2/SFF1 style.
        FileNotFoundError: If the file does not exist.
    """
    with open(path, 'rb') as fh:
        data = fh.read()

    if data[:4] != b'MThd':
        raise ValueError(f"Not a MIDI file: {path}")

    # ── MThd ──────────────────────────────────────────────────────────────────
    mthd_sz        = struct.unpack_from('>I', data, 4)[0]
    ticks_per_beat = struct.unpack_from('>H', data, 12)[0]

    # ── MTrk ──────────────────────────────────────────────────────────────────
    mtrk_off = 8 + mthd_sz
    if data[mtrk_off : mtrk_off + 4] != b'MTrk':
        raise ValueError(f"Expected MTrk immediately after MThd in {path}")
    mtrk_sz   = struct.unpack_from('>I', data, mtrk_off + 4)[0]
    mtrk_data = data[mtrk_off + 8 : mtrk_off + 8 + mtrk_sz]

    if b'SFF2' not in mtrk_data and b'SFF1' not in mtrk_data:
        raise ValueError(f"No SFF2/SFF1 marker found in MTrk of {path}")

    tempo, time_sig, sff_version, style_name, sections = _parse_mtrk(mtrk_data)

    # Fall back to filename if style_name not extracted from track name meta
    if not style_name:
        import re
        base = os.path.splitext(os.path.basename(path))[0]
        style_name = re.sub(r'\.(T|S)\d+$', '', base)

    # ── CASM ──────────────────────────────────────────────────────────────────
    after_mtrk = mtrk_off + 8 + mtrk_sz
    casm_off   = data.find(b'CASM', after_mtrk)
    if casm_off < 0:
        casm_off = data.find(b'CASM')   # fallback: search from beginning
    casm = _parse_casm(data, casm_off) if casm_off >= 0 else []

    has_fnrc = b'FNRc' in data[after_mtrk:]

    return YamahaStyle(
        path           = path,
        sff_version    = sff_version,
        style_name     = style_name,
        ticks_per_beat = ticks_per_beat,
        tempo          = tempo,
        time_sig       = time_sig,
        sections       = sections,
        casm           = casm,
        has_fnrc       = has_fnrc,
    )


# ─── Pretty-printer ───────────────────────────────────────────────────────────

def dump_style(style: YamahaStyle, show_events: int = 0) -> None:
    """Print a human-readable summary of a parsed YamahaStyle.

    Args:
        style:       Parsed style object.
        show_events: If > 0, show the first N events per section.
    """
    print(f"Style : {style.style_name!r}")
    print(f"  Format  : {style.sff_version}, {style.ticks_per_beat} ticks/beat")
    print(f"  Tempo   : {style.tempo} µs/beat ({style.bpm:.1f} BPM)")
    print(f"  TimeSig : {style.time_sig[0]}/{style.time_sig[1]}")
    print(f"  FNRc    : {style.has_fnrc}")
    print(f"  Sections ({len(style.sections)}):")
    for sec in style.sections_by_order():
        print(f"    [{sec.name:16s}] {len(sec.events):5d} events, "
              f"last_tick={sec.duration_ticks}")
        if show_events:
            for ev in sec.events[:show_events]:
                type_name = {
                    0x80: 'NoteOff', 0x90: 'NoteOn', 0xA0: 'Aftertouch',
                    0xB0: 'CC', 0xC0: 'PC', 0xD0: 'ChanPres', 0xE0: 'Bend',
                }.get(ev.event_type, f'0x{ev.status:02X}')
                print(f"      tick={ev.tick:6d}  ch={ev.channel+1:2d}  "
                      f"{type_name:10s}  {ev.data[1:].hex()}")
    print(f"  CASM ({len(style.casm)} CSEGs):")
    for i, cseg in enumerate(style.casm):
        print(f"    CSEG[{i}] -> {cseg.sections}")
        for ch in cseg.channels:
            print(f"      {ch}")
