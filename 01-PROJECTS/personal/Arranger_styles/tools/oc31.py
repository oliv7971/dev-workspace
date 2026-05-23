"""
OC31 — variante LZSS propriétaire KORG
Porté depuis KORG-Tools (C++, GPL v3 — Amir Czwink)

Format d'un bloc OC31 dans un fichier binaire KORG :
  4 bytes  "OC31"               (little-endian fourcc)
  4 bytes  uncompressed_size    (little-endian uint32)
  ...      blocs compressés
  3 bytes  sentinel   01 00 00  (bloc littéral de longueur 0)
  1 byte   check_value          (XOR de tous les octets décompressés)

Chaque bloc commence par un flag byte suivi éventuellement d'octets
supplémentaires qui encodent soit une back-référence LZSS, soit une
séquence littérale.

Distances (back-référence) : 0-based dans le fichier
  dist_stored = 0  →  dernier octet écrit
  dist_1based  = dist_stored + 1
  position_source = len(output) - dist_stored - 1

Usage rapide :
  from tools.oc31 import oc31_decompress, oc31_compress
  raw   = oc31_decompress(compressed_bytes)
  again = oc31_compress(raw)
  assert oc31_decompress(again) == raw
"""

import struct
from typing import Tuple


# ─────────────────────────────────────────────────────────────────────────────
# DÉCOMPRESSEUR
# ─────────────────────────────────────────────────────────────────────────────

def oc31_decompress(data: bytes, *, verify_check: bool = True) -> bytes:
    """
    Décompresse des données OC31.
    ``data`` doit commencer par le magic b'OC31'.
    Lève ValueError si le magic ou le checksum est incorrect.
    """
    if len(data) < 8:
        raise ValueError("Données trop courtes pour être du OC31")
    if data[0:4] != b'OC31':
        raise ValueError(f"Magic OC31 absent (reçu {data[0:4]!r})")

    uncompressed_size: int = struct.unpack_from('<I', data, 4)[0]

    out    = bytearray()
    check  = 0
    pos    = 8          # après magic + size

    def read_be_u16(p: int) -> Tuple[int, int]:
        """Retourne (valeur, nouveau_pos)."""
        return struct.unpack_from('>H', data, p)[0], p + 2

    while len(out) < uncompressed_size:
        flag = data[pos];  pos += 1

        # ── Back-référence ──────────────────────────────────────────────────
        if flag >= 0x10:

            if flag & 0xC0:                          # flag >= 0x40  (2 bytes)
                packed = data[pos];  pos += 1
                length  = (flag >> 5) + 1
                d_stored = ((flag & 0x1F) << 6) | (packed >> 2)
                n_extra  = packed & 3

            elif flag & 0x20:                        # 0x20 ≤ flag < 0x40
                indicator = flag & 0x1F
                if indicator == 0:
                    length = data[pos] + 0x22;  pos += 1
                elif indicator == 1:
                    length, pos = read_be_u16(pos)
                else:
                    length = indicator + 2
                tmp, pos = read_be_u16(pos)
                d_stored = tmp >> 2
                n_extra  = tmp & 3

            else:                                    # 0x10 ≤ flag < 0x20
                indicator = flag & 7
                if indicator == 0:
                    length = data[pos] + 0xA;  pos += 1
                elif indicator == 1:
                    length, pos = read_be_u16(pos)
                else:
                    length = indicator + 2
                tmp, pos = read_be_u16(pos)
                d_stored = (tmp >> 2) + 0x4000
                n_extra  = tmp & 3
                if flag & 8:
                    d_stored += 0x4000

            # Copie depuis le buffer de sortie (LZSS)
            src = len(out) - d_stored - 1
            for _ in range(length):
                b = out[src];  src += 1
                out.append(b);  check ^= b

            # Octets littéraux collés à la back-référence
            for _ in range(n_extra):
                b = data[pos];  pos += 1
                out.append(b);  check ^= b

        # ── Littéral ────────────────────────────────────────────────────────
        else:
            if flag == 0:
                length = data[pos] + 0x12;  pos += 1
            elif flag == 1:
                length, pos = read_be_u16(pos)
            else:
                length = flag + 2

            chunk = data[pos : pos + length]
            for b in chunk:
                check ^= b
            out.extend(chunk)
            pos += length

    # ── Sentinel + checksum ─────────────────────────────────────────────────
    # Le compresseur écrit toujours « 01 00 00 » (bloc littéral vide) puis
    # le check byte.  On saute le sentinel si présent.
    if (pos + 3 < len(data)
            and data[pos] == 0x01
            and data[pos + 1] == 0x00
            and data[pos + 2] == 0x00):
        pos += 3

    if verify_check and pos < len(data):
        stored = data[pos]
        if stored != check:
            raise ValueError(
                f"OC31 checksum invalide : attendu {check:#04x}, lu {stored:#04x}"
            )

    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# COMPRESSEUR  (LZSS glouton, table de hachage 3 bytes)
# ─────────────────────────────────────────────────────────────────────────────

_MAX_DIST  = 0xBFFF   # distance max stockée (0-based) → 1-based = 0xC000
_MAX_LEN   = 0xFFFF
_MIN_LEN   = 3        # longueur minimale d'une back-référence


def _backref_encoded_size(d_stored: int, length: int) -> int:
    """
    Nombre d'octets nécessaires pour encoder la back-référence
    (header seulement, sans les éventuels extra bytes).
    d_stored : distance 0-based telle que stockée dans le fichier.
    """
    if length <= 8 and d_stored <= 0x7FF:
        return 2
    if d_stored < 0x4000:
        if length <= 0x1F + 2:   return 3   # 1 flag + 2 dist
        if length <= 0xFF + 0x22: return 4  # 1 flag + 1 len + 2 dist
        return 5                             # 1 flag + 2 len + 2 dist
    else:
        if length <= 7 + 2:      return 3
        if length <= 0xFF + 0xA: return 4
        return 5


def _encode_backref(buf: bytearray, d_stored: int, length: int) -> None:
    """Encode une back-référence (sans extra bytes, n_extra=0)."""
    if length <= 8 and d_stored <= 0x7FF:
        buf.append(((length - 1) << 5) | (d_stored >> 6))
        buf.append((d_stored & 0x3F) << 2)             # n_extra = 0

    elif d_stored < 0x4000:
        if length <= 0x1F + 2:
            buf.append((length - 2) | 0x20)
        elif length <= 0xFF + 0x22:
            buf.append(0x20)
            buf.append(length - 0x22)
        else:
            buf.append(0x21)
            buf.extend(struct.pack('>H', length))
        buf.extend(struct.pack('>H', d_stored << 2))   # n_extra = 0

    else:
        large = d_stored >= 0x8000
        flag  = 0x10 | (8 if large else 0)
        d_rel = d_stored - 0x4000 - (0x4000 if large else 0)
        if length <= 7 + 2:
            buf.append(flag | (length - 2))
        elif length <= 0xFF + 0xA:
            buf.append(flag)
            buf.append(length - 0xA)
        else:
            buf.append(flag | 1)
            buf.extend(struct.pack('>H', length))
        buf.extend(struct.pack('>H', d_rel << 2))      # n_extra = 0


def _encode_literal(buf: bytearray, chunk: bytes) -> None:
    """Encode un bloc littéral de longueur quelconque."""
    ln = len(chunk)
    if ln == 0:
        return
    if 4 <= ln <= 17:
        buf.append(ln - 2)
    elif 0x12 <= ln <= 0x12 + 0xFF:
        buf.append(0)
        buf.append(ln - 0x12)
    else:
        # Forme universelle (fonctionne pour ln = 1, 2, 3 et ln > 273)
        buf.append(1)
        buf.extend(struct.pack('>H', ln))
    buf.extend(chunk)


def oc31_compress(data: bytes) -> bytes:
    """
    Compresse ``data`` en OC31.
    Retourne des bytes commençant par b'OC31'.
    Compression gloutonne par table de hachage sur 3 bytes.
    """
    n = len(data)
    body = bytearray()

    # Table de hachage : h → liste de positions (les plus récentes d'abord)
    hash_table: dict[int, list[int]] = {}

    def h3(p: int) -> int:
        return (data[p] << 16) | (data[p + 1] << 8) | data[p + 2]

    def add_pos(p: int) -> None:
        if p + _MIN_LEN > n:
            return
        key = h3(p)
        lst = hash_table.setdefault(key, [])
        lst.append(p)
        # Élagage des entrées hors de portée ou en excès (max 64 entries)
        while lst and (p - lst[0]) > _MAX_DIST:
            lst.pop(0)
        if len(lst) > 64:
            del lst[:-64]

    def find_match(pos: int) -> Tuple[int, int]:
        """Retourne (d_stored, length) du meilleur match, ou (0, 0)."""
        if pos + _MIN_LEN > n:
            return 0, 0
        key = h3(pos)
        candidates = hash_table.get(key, [])
        best_len   = 0
        best_d     = 0
        lim        = min(_MAX_LEN, n - pos)
        # Limit to last 32 candidates to avoid O(n²) on repetitive data
        for cp in reversed(candidates[-32:]):
            d = pos - cp
            if d > _MAX_DIST:
                break
            ml = 0
            while ml < lim and data[cp + ml] == data[pos + ml]:
                ml += 1
            if ml >= _MIN_LEN and ml > best_len:
                best_len = ml
                best_d   = d - 1   # 0-based (d_stored)
                if best_len == lim:
                    break
        return best_d, best_len

    pending = bytearray()   # littéraux en attente

    def flush() -> None:
        if pending:
            _encode_literal(body, bytes(pending))
            pending.clear()

    pos = 0
    while pos < n:
        # Chercher d'abord (contre positions < pos), puis ajouter pos au hash
        d_stored, length = find_match(pos)
        add_pos(pos)

        if length >= _MIN_LEN and _backref_encoded_size(d_stored, length) < length:
            flush()
            _encode_backref(body, d_stored, length)
            # Ajouter les positions intermédiaires à la table
            for i in range(1, length):
                add_pos(pos + i)
            pos += length
        else:
            pending.append(data[pos])
            pos += 1

    flush()

    # Checksum
    check = 0
    for b in data:
        check ^= b

    # Sentinel + check byte
    body.append(0x01)
    body.extend(b'\x00\x00')
    body.append(check)

    # Assemblage final
    out = bytearray()
    out.extend(b'OC31')
    out.extend(struct.pack('<I', n))
    out.extend(body)
    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

def extract_oc31_blocks(data: bytes) -> dict:
    """
    Analyse un flux OC31 et retourne des statistiques sur les blocs
    (utile pour le débogage et la validation).
    """
    if data[0:4] != b'OC31':
        raise ValueError("Pas du OC31")
    uncomp_size = struct.unpack_from('<I', data, 4)[0]
    pos = 8
    blocks = []
    total_out = 0

    while total_out < uncomp_size:
        blk_pos = pos
        flag = data[pos];  pos += 1

        if flag >= 0x10:
            if flag & 0xC0:
                packed = data[pos];  pos += 1
                length   = (flag >> 5) + 1
                d_stored = ((flag & 0x1F) << 6) | (packed >> 2)
                n_extra  = packed & 3
                form     = "backref-short"
            elif flag & 0x20:
                indicator = flag & 0x1F
                if indicator == 0:
                    length = data[pos] + 0x22;  pos += 1
                elif indicator == 1:
                    length = struct.unpack_from('>H', data, pos)[0];  pos += 2
                else:
                    length = indicator + 2
                tmp = struct.unpack_from('>H', data, pos)[0];  pos += 2
                d_stored = tmp >> 2
                n_extra  = tmp & 3
                form     = "backref-medium"
            else:
                indicator = flag & 7
                if indicator == 0:
                    length = data[pos] + 0xA;  pos += 1
                elif indicator == 1:
                    length = struct.unpack_from('>H', data, pos)[0];  pos += 2
                else:
                    length = indicator + 2
                tmp = struct.unpack_from('>H', data, pos)[0];  pos += 2
                d_stored = (tmp >> 2) + 0x4000
                n_extra  = tmp & 3
                if flag & 8:
                    d_stored += 0x4000
                form = "backref-large"
            pos += n_extra
            total_out += length + n_extra
            blocks.append({
                "type": "backref", "form": form, "offset": blk_pos,
                "length": length, "distance": d_stored + 1, "n_extra": n_extra
            })
        else:
            if flag == 0:
                length = data[pos] + 0x12;  pos += 1
            elif flag == 1:
                length = struct.unpack_from('>H', data, pos)[0];  pos += 2
            else:
                length = flag + 2
            pos += length
            total_out += length
            blocks.append({"type": "literal", "offset": blk_pos, "length": length})

    return {
        "uncompressed_size": uncomp_size,
        "compressed_size": len(data),
        "ratio": len(data) / uncomp_size if uncomp_size else 0,
        "n_blocks": len(blocks),
        "n_backref": sum(1 for b in blocks if b["type"] == "backref"),
        "n_literal": sum(1 for b in blocks if b["type"] == "literal"),
        "blocks": blocks,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TEST  (round-trip sur des données réelles)
# ─────────────────────────────────────────────────────────────────────────────

def _test_roundtrip_synthetic() -> None:
    """Vérifie décompression→compression→décompression sur des données synthétiques."""
    tests = [
        b"Hello, World!",
        b"ABCABCABCABCABC" * 100,
        bytes(range(256)) * 40,
        b"\x00" * 1000,
        b"La vie est belle " * 200 + b"fin.",
    ]
    for i, original in enumerate(tests):
        compressed   = oc31_compress(original)
        decompressed = oc31_decompress(compressed)
        assert decompressed == original, (
            f"Test {i} échoué : {len(original)} bytes → {len(compressed)} bytes "
            f"→ {len(decompressed)} bytes"
        )
        ratio = len(compressed) / len(original)
        print(f"Test {i:2d} OK — {len(original):6d} → {len(compressed):6d} bytes "
              f"(ratio {ratio:.3f})")


def test_decompress_real(bank_path: str, style_index: int = 0) -> None:
    """
    Tente de décompresser le premier chunk OC31 trouvé dans un fichier banque KORG.
    Exemple : test_decompress_real(r'données etude\\KORG (PA4x musikant)\\...\\BANK01.STY')
    """
    with open(bank_path, 'rb') as f:
        data = f.read()

    # Chercher les occurrences de OC31
    import re
    offsets = [m.start() for m in re.finditer(b'OC31', data)]
    print(f"Trouvé {len(offsets)} blocs OC31 dans {bank_path}")
    for i, off in enumerate(offsets[:5]):
        try:
            raw = oc31_decompress(data[off:], verify_check=False)
            print(f"  [{i}] offset={off:#010x}  →  {len(raw)} bytes décompressés")
            stats = extract_oc31_blocks(data[off:])
            print(f"       {stats['n_blocks']} blocs : "
                  f"{stats['n_backref']} backrefs + {stats['n_literal']} littéraux")
        except Exception as e:
            print(f"  [{i}] offset={off:#010x}  ERREUR : {e}")


if __name__ == "__main__":
    print("=== Tests round-trip synthétiques ===")
    _test_roundtrip_synthetic()
    print("\nTous les tests ont réussi.")
