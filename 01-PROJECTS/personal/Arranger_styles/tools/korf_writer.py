"""
korf_writer.py — KORF .STY bank file writer

Produces a valid KORG .STY bank file from a list of (name, style_bytes) pairs.

Bank file structure:
  Container chunk (type=0x01 v=0.0 flags=0x14)  ← outer wrapper
    KorgFile chunk (type=0x02 v=0.0 flags=0x18)  ← KORF magic
    ObjectTOC chunk (type=0x05 v=0.0 flags=0x18) ← style index
    N × StyleData chunks (type=0x06 v=0.0 flags=0x30) ← compressed styles
    XRef chunk (type=0xFE v=0.0 flags=0x18)       ← offset table

Flags used at bank level:
  InBankFile(0x10) + Unknown4(0x04) = 0x14  → first outer Container
  Leaf(0x08) + InBankFile(0x10) = 0x18      → KorgFile, TOC, XRef leaves
  InBankFile(0x10) + OC31Compressed(0x20) = 0x30 → StyleData objects
"""

import os
import struct
from typing import List, Tuple

from tools.korf import (
    encode_chunk,
    ChunkType, ChunkFlags, ObjectType,
    _toc_crc32_update,
)
from tools.oc31 import oc31_compress

_PERF_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'perf_template.bin')


def _load_perf_template() -> bytes:
    """Charge le template StylePerformances depuis tools/perf_template.bin."""
    if not os.path.exists(_PERF_TEMPLATE_PATH):
        raise FileNotFoundError(
            f"Fichier template PERF manquant : {_PERF_TEMPLATE_PATH}\n"
            "Veuillez d'abord exécuter : python _extract_perf_template.py"
        )
    with open(_PERF_TEMPLATE_PATH, 'rb') as f:
        return f.read()


# ─────────────────────────────────────────────────────────────────────────────
# KorgFile chunk (KORF magic)
# ─────────────────────────────────────────────────────────────────────────────

def _encode_korf_magic() -> bytes:
    """
    KorgFile chunk payload: [0x0B000000 u32be][0x0000 u16be][0x00 u8][KORF fourcc-le]
    """
    payload = struct.pack('>I', 0x0B000000)
    payload += struct.pack('>H', 0)
    payload += b'\x00'
    payload += b'KORF'
    payload += b'\x00'   # trailing null → size=12 comme BANK01.STY
    return encode_chunk(
        ChunkType.KorgFile, 0, 0,
        ChunkFlags.Leaf | ChunkFlags.InBankFile,
        payload,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TOC chunk (v1.0)
# ─────────────────────────────────────────────────────────────────────────────

# Fixed name field width in TOC entries, matching PA4x BANK01.STY format.
_TOC_NAME_SIZE = 28

def _encode_toc(names: List[str]) -> bytes:
    """
    Build TOC v1.0 payload matching PA4x BANK01.STY format exactly.
    Entry layout:
      uint16 headerEntrySize
      uint16 nProperties
      [nProperties x (uint16 type + uint16 size + bytes[size])]
      uint32 CRC
    Property ORDER (must match PA Manager expectation):
      [0] type=2  name:     28 bytes fixed, null-padded
      [1] type=0  position: object_type(1) + bank_number(1) + pos(1)
      [2] type=1  version:  major(1) + minor(1)
    For each style slot: Style entry then StylePerformances entry.
    """
    def _entry(object_type: int, pos: int, name: str,
               version_major: int = 0, version_minor: int = 0) -> bytes:
        # name: fixed 28 bytes, null-padded (truncate if longer)
        name_enc = name.encode('ascii', errors='replace')
        name_field = (name_enc + b'\x00' * _TOC_NAME_SIZE)[:_TOC_NAME_SIZE]
        props = b''
        props += struct.pack('>HH', 2, _TOC_NAME_SIZE) + name_field
        props += struct.pack('>HH', 0, 3) + bytes([object_type, 0, pos])
        props += struct.pack('>HH', 1, 2) + bytes([version_major, version_minor])
        n_props_field = struct.pack('>H', 3)
        content_before_crc = n_props_field + props
        # Entry size field = length of (content_before_crc + 4-byte CRC)
        size_field = struct.pack('>H', len(content_before_crc) + 4)
        # CRC is computed over the FULL entry including the size prefix.
        crc = _toc_crc32_update(0, size_field + content_before_crc)
        return size_field + content_before_crc + struct.pack('>I', crc)

    payload = b''
    for i, name in enumerate(names):
        payload += _entry(ObjectType.Style, i, name, version_major=0, version_minor=0)
        # StylePerformances chunk is v2.0 — TOC version must match.
        # PERF entry name field is empty (Style entry holds the name).
        payload += _entry(ObjectType.StylePerformances, i, '', version_major=2, version_minor=0)

    return encode_chunk(
        ChunkType.ObjectTOC, 1, 0,
        ChunkFlags.Leaf | ChunkFlags.InBankFile,
        payload,
    )


# ─────────────────────────────────────────────────────────────────────────────
# StyleData object chunks (type=0x06, compressed)
# ─────────────────────────────────────────────────────────────────────────────

def _encode_style_object(style_bytes: bytes) -> bytes:
    """
    Encode one StyleData object chunk.
    flags = InBankFile(0x10) | OC31Compressed(0x20) = 0x30
    The style bytes are compressed with OC31.
    """
    compressed = oc31_compress(style_bytes)
    flags = ChunkFlags.InBankFile | ChunkFlags.OC31Compressed
    return encode_chunk(ChunkType.StyleData, 0, 0, flags, compressed)


def _encode_perf_object(perf_bytes: bytes) -> bytes:
    """
    Encode one StylePerformances (PerformancesData) object chunk.
    flags = InBankFile(0x10) | OC31Compressed(0x20) = 0x30
    """
    compressed = oc31_compress(perf_bytes)
    flags = ChunkFlags.InBankFile | ChunkFlags.OC31Compressed
    return encode_chunk(ChunkType.PerformancesData, 2, 0, flags, compressed)


# ─────────────────────────────────────────────────────────────────────────────
# XRef chunk
# ─────────────────────────────────────────────────────────────────────────────

def _encode_xref(offsets: List[int]) -> bytes:
    """
    XRef payload: "KBEG" + N × uint32_BE offsets + "KEND" + uint32_LE nEntries
    """
    payload = b'KBEG'
    for off in offsets:
        payload += struct.pack('>I', off)
    payload += b'KEND'
    payload += struct.pack('>I', len(offsets))

    return encode_chunk(
        ChunkType.CrossReferenceTable, 0, 0,
        ChunkFlags.Leaf | ChunkFlags.InBankFile,
        payload,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Full bank assembly
# ─────────────────────────────────────────────────────────────────────────────

def write_bank(styles: List[Tuple[str, bytes]], output_path: str) -> None:
    """
    Write a KORG .STY bank file.

    Args:
        styles: list of (style_name, style_bytes) where style_bytes is the
                output of style_writer.encode_style()
        output_path: path to write the .STY file
    """
    names = [name for name, _ in styles]

    # Load the StylePerformances template (required by KORG PA Manager)
    perf_template = _load_perf_template()

    # Build KorgFile + TOC chunks (TOC now has 2 entries per style)
    korf_chunk = _encode_korf_magic()
    toc_chunk = _encode_toc(names)

    # Build StyleData chunks and the shared PerformancesData chunk
    style_chunks = [_encode_style_object(b) for _, b in styles]
    perf_chunk = _encode_perf_object(perf_template)

    # Compute offsets (absolute from file start).
    # Layout: outer_header(8) + korf_chunk + toc_chunk + [style_i + perf_i] × N + xref
    # XRef entry[0] = TOC chunk offset, then 2 entries per style (Style, PERF)
    OUTER_HEADER_SIZE = 8
    toc_offset = OUTER_HEADER_SIZE + len(korf_chunk)
    pos = toc_offset + len(toc_chunk)
    offsets = [toc_offset]  # first XRef entry always points to TOC
    for sc in style_chunks:
        offsets.append(pos)        # offset of Style chunk
        pos += len(sc)
        offsets.append(pos)        # offset of PERF chunk
        pos += len(perf_chunk)

    xref_chunk = _encode_xref(offsets)

    # Build full inner content: korf + toc + [style + perf]×N + xref
    inner = korf_chunk + toc_chunk
    for sc in style_chunks:
        inner += sc
        inner += perf_chunk
    inner += xref_chunk

    # Build outer container v0.1  flags: Unknown4(0x04) | InBankFile(0x10) = 0x14
    outer_flags = ChunkFlags.Unknown4 | ChunkFlags.InBankFile
    outer = encode_chunk(ChunkType.Container, 0, 1, outer_flags, inner)

    with open(output_path, 'wb') as f:
        f.write(outer)
