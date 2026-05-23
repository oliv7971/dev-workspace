"""
KORF — parseur/écriveur de chunks pour fichiers banque KORG (.STY)
Porté depuis KORG-Tools (C++, GPL v3 — Amir Czwink)

Structure d'un fichier .STY :
  Container chunk
    KorgFile chunk   → magic KORF
    TOC chunk        → liste des objets (styles, sons…)
    N × Object chunks (StyleData, SoundData, …)
    XRef chunk       → table d'offsets KBEG…KEND

Chaque chunk = 8 bytes d'header + données :
  [0..3]  id  = type(8) | version.major(8) | version.minor(8) | flags(8)  big-endian
  [4..7]  size = taille des données (big-endian uint32)
  [8..]   données ou sous-chunks

Flags (octet bas de l'id) :
  0x04  Unknown4          — 1er chunk du fichier uniquement
  0x08  Leaf              — contient des données (pas des sous-chunks)
  0x10  InBankFile        — présent sur tous les chunks d'une banque
  0x20  OC31Compressed    — données compressées avec OC31
  0x40  Encrypted

Types de chunks (octet haut de l'id) :
  0x00  Container
  0x01  KorgFile          → contient le magic KORF
  0x02  ObjectTOC
  0x04  StyleData
  0x05  SoundData
  0x06  MultiSampleData
  0x07  PCMData
  0x09  PerformancesData
  0x0C  PadData
  0x3F  (grand Container outer)
"""

import struct
import io
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from tools.oc31 import oc31_decompress, oc31_compress


# ─────────────────────────────────────────────────────────────────────────────
# FLAGS & TYPES
# ─────────────────────────────────────────────────────────────────────────────

class ChunkFlags:
    Unknown4       = 0x04
    Leaf           = 0x08
    InBankFile     = 0x10
    OC31Compressed = 0x20
    Encrypted      = 0x40


class ChunkType:
    # valeurs issues de BankFormat.hpp (KORG-Tools)
    Container             = 1
    KorgFile              = 2
    ObjectTOC             = 5
    StyleData             = 6
    LegacySoundData       = 7
    SongBookListData      = 8
    PerformancesData      = 9
    PadData               = 12
    SoundData             = 16
    MultiSampleData       = 17
    PCMData               = 18
    CrossReferenceTable   = 0xFE


class ObjectType:
    # valeurs issues de BankFormat.hpp (KORG-Tools)
    Performance       = 1
    Style             = 2
    Sound             = 4
    MultiSample       = 5
    PCM               = 6
    StylePerformances = 7
    Pad               = 9
    SongBookEntry     = 11
    SongBook          = 12

    _NAMES = {1:'Performance',2:'Style',4:'Sound',5:'MultiSample',6:'PCM',
              7:'StylePerformances',9:'Pad',11:'SongBookEntry',12:'SongBook'}

    @classmethod
    def name(cls, v: int) -> str:
        return cls._NAMES.get(v, f'Unknown({v})')


# ─────────────────────────────────────────────────────────────────────────────
# STRUCTURES DE BASE
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ChunkHeader:
    raw_id:         int   = 0    # uint32 big-endian complet
    chunk_type:     int   = 0    # octet haut
    version_major:  int   = 0
    version_minor:  int   = 0
    flags:          int   = 0    # octet bas
    size:           int   = 0

    @property
    def is_leaf(self) -> bool:
        return bool(self.flags & ChunkFlags.Leaf)

    @property
    def is_compressed(self) -> bool:
        return bool(self.flags & ChunkFlags.OC31Compressed)

    @property
    def is_encrypted(self) -> bool:
        return bool(self.flags & ChunkFlags.Encrypted)

    def __repr__(self) -> str:
        return (f"ChunkHeader(type={self.chunk_type:#04x}, "
                f"v={self.version_major}.{self.version_minor}, "
                f"flags={self.flags:#04x}, size={self.size})")


@dataclass
class EncryptionInfo:
    serial_number_type:   int = 0   # 1=Machine, 2=FMDriver
    encryption_algorithm: int = 0   # 0=Normal,1=DES,2=Mixed,3=Blowfish
    vendor_id:            int = 0
    feature_id:           int = 0


@dataclass
class TOCEntry:
    object_type:  int = 0
    bank_number:  int = 0
    pos:          int = 0
    version_major: int = 0
    version_minor: int = 0
    name:         str = ""
    entry_id:     Optional[int] = None
    encryption:   Optional[EncryptionInfo] = None
    # Offset de l'objet dans le fichier (rempli via XRef)
    file_offset:  int = 0

    def __repr__(self) -> str:
        enc = " [ENC]" if self.encryption else ""
        return (f"TOCEntry({ObjectType.name(self.object_type)} "
                f"bank={self.bank_number} pos={self.pos} "
                f"v{self.version_major}.{self.version_minor} "
                f"'{self.name}'{enc})")


# ─────────────────────────────────────────────────────────────────────────────
# PARSEUR BAS NIVEAU
# ─────────────────────────────────────────────────────────────────────────────

class _Reader:
    """Lecteur binaire avec position."""
    def __init__(self, data: bytes, pos: int = 0):
        self._data = data
        self._pos  = pos

    @property
    def pos(self) -> int:
        return self._pos

    @pos.setter
    def pos(self, v: int):
        self._pos = v

    def remaining(self) -> int:
        return len(self._data) - self._pos

    def read(self, n: int) -> bytes:
        chunk = self._data[self._pos : self._pos + n]
        if len(chunk) < n:
            raise EOFError(f"Besoin de {n} bytes, seulement {len(chunk)} dispo à {self._pos:#x}")
        self._pos += n
        return chunk

    def u8(self) -> int:
        v = self._data[self._pos]; self._pos += 1; return v
    def u16be(self) -> int:
        v = struct.unpack_from('>H', self._data, self._pos)[0]; self._pos += 2; return v
    def u16le(self) -> int:
        v = struct.unpack_from('<H', self._data, self._pos)[0]; self._pos += 2; return v
    def u32be(self) -> int:
        v = struct.unpack_from('>I', self._data, self._pos)[0]; self._pos += 4; return v
    def u32le(self) -> int:
        v = struct.unpack_from('<I', self._data, self._pos)[0]; self._pos += 4; return v
    def u64le(self) -> int:
        v = struct.unpack_from('<Q', self._data, self._pos)[0]; self._pos += 8; return v
    def i16be(self) -> int:
        v = struct.unpack_from('>h', self._data, self._pos)[0]; self._pos += 2; return v
    def fourcc_le(self) -> bytes:
        b = self._data[self._pos : self._pos + 4]; self._pos += 4; return b
    def string(self, n: int) -> str:
        b = self._data[self._pos : self._pos + n]; self._pos += n
        return b.decode('latin-1').rstrip('\x00')

    # ─── méthodes "non-avançantes" ───────────────────────────────────────────
    def peek_u8(self, offset: int = 0) -> int:
        return self._data[self._pos + offset]


def _read_chunk_header(r: _Reader) -> ChunkHeader:
    """Lit les 8 bytes d'un header de chunk."""
    hdr = ChunkHeader()
    hdr.raw_id        = r.u32be()
    hdr.size          = r.u32be()
    hdr.chunk_type    = (hdr.raw_id >> 24) & 0xFF
    hdr.version_major = (hdr.raw_id >> 16) & 0xFF
    hdr.version_minor = (hdr.raw_id >>  8) & 0xFF
    hdr.flags         = hdr.raw_id & 0xFF
    return hdr


def _read_chunk_data(r: _Reader, hdr: ChunkHeader) -> bytes:
    """
    Lit les données brutes du chunk (hdr.size bytes).
    Si OC31Compressed : décompresse automatiquement.
    Retourne les données (décompressées si applicable).
    """
    raw = r.read(hdr.size)

    if hdr.is_compressed and not hdr.is_encrypted:
        if raw[:4] not in (b'OC31', b'OC32'):
            raise ValueError(f"OC31 attendu mais reçu {raw[:4]!r} à offset {r.pos - hdr.size:#x}")
        return oc31_decompress(raw, verify_check=False)

    return raw


# ─────────────────────────────────────────────────────────────────────────────
# PARSEUR TOC
# ─────────────────────────────────────────────────────────────────────────────

# HEADERENTRY_NAME_SIZE = 18, OBJECTTOC_LINESIZE = 24  (constantes BankFormat.hpp)
_HEADERENTRY_NAME_SIZE = 18
_OBJECTTOC_LINESIZE    = 24


def _parse_toc_v0(data: bytes) -> List[TOCEntry]:
    """
    TOC version 0.0 : entrées de taille fixe (OBJECTTOC_LINESIZE = 24 bytes).
    Layout : name(18) + type(1) + bank(1) + pos(1) + major(1) + minor(1) + zero(1)
    """
    n_entries = len(data) // _OBJECTTOC_LINESIZE
    entries: List[TOCEntry] = []
    r = _Reader(data)

    for _ in range(n_entries):
        e = TOCEntry()
        e.name          = r.read(_HEADERENTRY_NAME_SIZE).rstrip(b'\x00').decode('latin-1')
        e.object_type   = r.u8()
        e.bank_number   = r.u8()
        e.pos           = r.u8()
        e.version_major = r.u8()
        e.version_minor = r.u8()
        _zero           = r.u8()   # padding
        entries.append(e)

    return entries


def _toc_crc32_update(crc: int, data: bytes) -> int:
    """
    CRC utilisé pour les entrées TOC v1 (TOCEntryChecksumFunction.hpp).
    Polynôme 0xEDB88320 (variante big-endian de CRC-32).
    """
    # Table pré-calculée à la volée
    if not hasattr(_toc_crc32_update, '_table'):
        table = []
        for i in range(256):
            s = i << 24
            for _ in range(8):
                high = s >> 31
                s = (s << 1) & 0xFFFFFFFF
                if high:
                    s ^= 0xEDB88320
            table.append(s)
        _toc_crc32_update._table = table
    table = _toc_crc32_update._table

    for b in data:
        idx = (crc >> 24) ^ b
        crc = ((crc << 8) & 0xFFFFFFFF) ^ table[idx]
    return crc


def _parse_toc_v1(data: bytes, minor: int) -> List[TOCEntry]:
    """
    TOC version 1.x : entrées variable-length avec propriétés et checksum.
    Chaque entrée :
      uint16 headerEntrySize   (taille de nProps+props+checksum)
      uint16 nProperties
      [nProperties × (uint16 type + uint16 size + bytes[size])]
      uint32 checksum CRC-like (big-endian)
    """
    r = _Reader(data)
    entries: List[TOCEntry] = []
    left = len(data)

    while left >= 6:    # au moins headerEntrySize(2) + nProps(2) + checksum(4)
        entry_size_pos = r.pos
        header_entry_size = r.u16be()
        left -= 2
        if header_entry_size == 0:
            break

        # Tout lire d'un coup pour calculer le CRC
        entry_raw = r.read(header_entry_size)
        left -= header_entry_size

        er = _Reader(entry_raw)
        n_props = struct.unpack_from('>H', entry_raw, 0)[0]
        er.pos = 2

        e = TOCEntry()
        props_end = header_entry_size - 4   # 4 = taille du checksum

        for _ in range(n_props):
            if er.pos >= props_end:
                break
            prop_type = er.u16be()
            prop_size = er.u16be()
            prop_start = er.pos

            if prop_type == 0:      # position
                e.object_type = er.u8()
                er.u8()             # bank_number (on ignore)
                e.pos         = er.u8()
            elif prop_type == 1:    # version
                e.version_major = er.u8()
                e.version_minor = er.u8()
            elif prop_type == 2:    # nom
                raw = er.read(prop_size)
                e.name = raw.rstrip(b'\x00').decode('latin-1', errors='replace')
            elif prop_type == 3:    # chiffrement
                enc = EncryptionInfo()
                enc.serial_number_type   = er.u8()
                enc.encryption_algorithm = er.u8()
                enc.vendor_id            = er.u16be()
                enc.feature_id           = er.u16be()
                e.encryption = enc
            elif prop_type == 4:    # id uint64 LE
                e.entry_id = er.u64le()
            else:
                er.read(prop_size)  # champs inconnus

            # Aligner sur prop_size
            consumed = er.pos - prop_start
            if consumed < prop_size:
                er.read(prop_size - consumed)

        # Checksum (on lit mais on ne valide pas)
        _crc = struct.unpack_from('>I', entry_raw, props_end)[0]
        entries.append(e)

    return entries


def _parse_toc(hdr: ChunkHeader, data: bytes) -> List[TOCEntry]:
    if hdr.version_major == 0:
        return _parse_toc_v0(data)
    elif hdr.version_major == 1:
        return _parse_toc_v1(data, hdr.version_minor)
    else:
        raise ValueError(f"Version TOC inconnue : {hdr.version_major}.{hdr.version_minor}")


# ─────────────────────────────────────────────────────────────────────────────
# PARSEUR XREF
# ─────────────────────────────────────────────────────────────────────────────

def _parse_xref(data: bytes) -> List[int]:
    """
    XRef = "KBEG" + N × uint32_BE offsets + "KEND" + uint32_LE nEntries
    Retourne la liste des offsets absolus dans le fichier.
    """
    if data[:4] != b'KBEG':
        raise ValueError(f"XRef sans KBEG : {data[:4]!r}")
    r = _Reader(data, 4)
    offsets: List[int] = []
    while r.remaining() >= 4:
        tag = r.read(4)
        if tag in (b'KEND', b'KBEG'):
            break
        r.pos -= 4
        offsets.append(r.u32be())
    return offsets


# ─────────────────────────────────────────────────────────────────────────────
# LECTURE D'UNE BANQUE COMPLÈTE
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class KorgBank:
    """Représente une banque KORG (.STY) entièrement parsée."""
    toc:        List[TOCEntry]  = field(default_factory=list)
    xref:       List[int]       = field(default_factory=list)
    # Données brutes de chaque objet (décompressées si OC31)
    objects:    List[bytes]     = field(default_factory=list)
    # Header du chunk principal pour pouvoir réécrire
    raw_data:   bytes           = b""

    def style_entries(self) -> List[TOCEntry]:
        return [e for e in self.toc if e.object_type == ObjectType.Style]


def read_bank(path: str) -> KorgBank:
    """
    Lit un fichier banque KORG (.STY) et retourne un KorgBank.
    Exemple : bank = read_bank(r'données etude\\...\\BANK01.STY')
    """
    with open(path, 'rb') as f:
        data = f.read()

    bank = KorgBank(raw_data=data)
    r    = _Reader(data)

    # ── 1. Outer container chunk (type=Container=1) ─────────────────────────
    outer_hdr = _read_chunk_header(r)
    if outer_hdr.chunk_type != ChunkType.Container:
        raise ValueError(
            f"Container attendu (type=1), reçu type={outer_hdr.chunk_type:#04x} "
            f"— le fichier est peut-être chiffré ou corrompu")

    # ── 2. KorgFile chunk (type=KorgFile=2, magic KORF) ──────────────────────
    korf_hdr  = _read_chunk_header(r)
    if korf_hdr.chunk_type != ChunkType.KorgFile:
        raise ValueError(f"KorgFile attendu (type=2), reçu type={korf_hdr.chunk_type:#04x}")
    korf_data = r.read(korf_hdr.size)
    kr = _Reader(korf_data)
    _magic1 = kr.u32be()           # 0x0B000000
    _zero2  = kr.u16be()           # 0x0000
    _zero3  = kr.u8()              # 0x00
    fourcc  = kr.fourcc_le()       # "KORF"  (LE fourcc = ASCII normal)
    if fourcc != b'KORF':
        raise ValueError(f"KORF attendu, reçu {fourcc!r}")

    # ── 3. TOC chunk (type=ObjectTOC=5) ──────────────────────────────────────
    toc_hdr  = _read_chunk_header(r)
    if toc_hdr.chunk_type != ChunkType.ObjectTOC:
        raise ValueError(f"TOC attendu (type=5), reçu type={toc_hdr.chunk_type:#04x}")
    toc_raw  = _read_chunk_data(r, toc_hdr)
    bank.toc = _parse_toc(toc_hdr, toc_raw)

    # ── 4. Objects (styles, sons, etc.) ──────────────────────────────────────
    # Les objets suivent le TOC dans l'ordre du TOC.
    # On s'arrête dès qu'on rencontre le XRef (type=0xFE) ou la fin du fichier.
    for entry in bank.toc:
        if r.remaining() < 8:
            break
        obj_start = r.pos
        obj_hdr   = _read_chunk_header(r)

        # Le XRef peut arriver avant qu'on ait lu tous les objets (styles ROM)
        if obj_hdr.chunk_type == ChunkType.CrossReferenceTable:
            # On l'a déjà avancé — lire sa data et parser le XRef
            xref_raw = _read_chunk_data(r, obj_hdr)
            try:
                bank.xref = _parse_xref(xref_raw)
            except ValueError:
                pass
            break

        raw = _read_chunk_data(r, obj_hdr)
        bank.objects.append(raw)
        entry.file_offset = obj_start

    # ── 5. XRef chunk (si pas encore lu) ─────────────────────────────────────
    if not bank.xref and r.remaining() >= 8:
        xref_hdr = _read_chunk_header(r)
        if xref_hdr.chunk_type == ChunkType.CrossReferenceTable:
            xref_raw = _read_chunk_data(r, xref_hdr)
            try:
                bank.xref = _parse_xref(xref_raw)
            except ValueError:
                pass

    return bank


# ─────────────────────────────────────────────────────────────────────────────
# ÉCRITURE BAS NIVEAU DES CHUNKS
# ─────────────────────────────────────────────────────────────────────────────

def _chunk_id(chunk_type: int, version_major: int, version_minor: int, flags: int) -> int:
    return ((chunk_type & 0xFF) << 24 | (version_major & 0xFF) << 16
            | (version_minor & 0xFF) << 8 | (flags & 0xFF))


def encode_chunk(chunk_type: int, version_major: int, version_minor: int,
                 flags: int, data: bytes, *, compress: bool = False) -> bytes:
    """
    Encode un chunk complet (header 8 bytes + données).
    Si compress=True, les données sont compressées OC31 (flag mis automatiquement).
    """
    if compress:
        payload = oc31_compress(data)
        flags |= ChunkFlags.OC31Compressed
    else:
        payload = data

    cid    = _chunk_id(chunk_type, version_major, version_minor, flags)
    header = struct.pack('>II', cid, len(payload))
    return header + payload


def encode_leaf(chunk_type: int, version_major: int, version_minor: int,
                data: bytes, in_bank: bool = True, compress: bool = False) -> bytes:
    """Chunk feuille (Leaf flag mis automatiquement)."""
    flags = ChunkFlags.Leaf
    if in_bank:
        flags |= ChunkFlags.InBankFile
    return encode_chunk(chunk_type, version_major, version_minor, flags, data, compress=compress)


def encode_container(chunk_type: int, version_major: int, version_minor: int,
                     children: bytes, in_bank: bool = True, extra_flags: int = 0) -> bytes:
    """Chunk conteneur (pas de Leaf flag)."""
    flags = ChunkFlags.InBankFile if in_bank else 0
    flags |= extra_flags
    return encode_chunk(chunk_type, version_major, version_minor, flags, children)


# ─────────────────────────────────────────────────────────────────────────────
# ITÉRATEUR DE SOUS-CHUNKS (pour les données style décompressées)
# ─────────────────────────────────────────────────────────────────────────────

def iter_chunks(data: bytes):
    """
    Générateur sur les sous-chunks d'un bloc de données.
    Yield : (ChunkHeader, payload_bytes)
    payload est déjà décompressé si OC31.
    """
    r = _Reader(data)
    while r.remaining() >= 8:
        hdr     = _read_chunk_header(r)
        payload = _read_chunk_data(r, hdr)
        yield hdr, payload


def dump_chunks(data: bytes, indent: int = 0) -> None:
    """Affiche récursivement la hiérarchie des sous-chunks."""
    prefix = "  " * indent
    for hdr, payload in iter_chunks(data):
        print(f"{prefix}{hdr}  payload={len(payload)} bytes")
        if not hdr.is_leaf and not hdr.is_encrypted:
            dump_chunks(payload, indent + 1)


# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE DE HAUT NIVEAU
# ─────────────────────────────────────────────────────────────────────────────

def dump_bank(path: str) -> None:
    """Affiche le contenu d'une banque KORG (.STY)."""
    bank = read_bank(path)
    print(f"Banque : {path}")
    print(f"  {len(bank.toc)} entrées TOC")
    print()
    for i, entry in enumerate(bank.toc):
        print(f"  [{i:2d}] {entry}")
        if i < len(bank.objects) and bank.objects[i]:
            obj = bank.objects[i]
            if entry.object_type == ObjectType.Style:
                print(f"       données : {len(obj)} bytes (décompressés)")
                try:
                    dump_chunks(obj, indent=3)
                except Exception as e:
                    print(f"       (erreur lecture sous-chunks : {e})")
        print()


if __name__ == "__main__":
    import sys
    path = (sys.argv[1] if len(sys.argv) > 1
            else r"données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY")
    dump_bank(path)
