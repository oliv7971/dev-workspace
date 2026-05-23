"""
Analyse des structures SFF2 Yamaha pour tous les fichiers de styles disponibles.
Compare Tyros3 (.T108), Tyros5 (.T160/.T161/.T152/.T153/.T166),
PSR-S series (.S747/.S942/.S943) et fichiers .sst
"""
import struct
import os
import glob

BASE = r"données etude"


def read_chunks(data, start, end):
    pos = start
    while pos + 8 <= end:
        tag = data[pos:pos+4]
        sz  = struct.unpack_from('>I', data, pos+4)[0]
        ascii_tag = ''.join(chr(b) if 32 <= b < 127 else '.' for b in tag)
        yield pos, ascii_tag, sz, data[pos+8:pos+8+sz]
        pos += 8 + sz


def parse_mtrk_markers(data):
    """Trouve SFF2, SInt et sections dans le MTrk."""
    mthd_sz = struct.unpack_from('>I', data, 4)[0]
    mtrk_off = 8 + mthd_sz
    mtrk_sz  = struct.unpack_from('>I', data, mtrk_off+4)[0]
    mtrk_data = data[mtrk_off+8 : mtrk_off+8+mtrk_sz]

    results = {}
    for marker in [b'SFF2', b'SFF1', b'SInt']:
        idx = mtrk_data.find(marker)
        if idx >= 0:
            results[marker.decode()] = {'offset_in_mtrk': idx}

    # Sections (0xFF 0x06 délimité par SFF2)
    results['mtrk_size'] = mtrk_sz
    results['mtrk_offset'] = mtrk_off
    return results


def parse_ctb2(data):
    """Parse un chunk Ctb2 : table de canaux SFF2."""
    # Format: name(10) + source_ch(1) + dest_ch(1) + ... (voir SFF2 spec)
    # En réalité: name (variable, null-term), puis champs fixes
    pos = 0
    # name: longueur byte + string
    name_len = data[pos]; pos += 1
    name = data[pos:pos+name_len].decode('ascii', errors='replace'); pos += name_len

    if pos >= len(data):
        return {'name': name}

    # Champs fixes : ch(1) + mode(1) + ... selon SFF2
    src_ch    = data[pos] if pos < len(data) else 0; pos += 1
    dest_ch   = data[pos] if pos < len(data) else 0; pos += 1
    editable  = data[pos] if pos < len(data) else 0; pos += 1
    mute      = data[pos] if pos < len(data) else 0; pos += 1

    rest = data[pos:]
    return {
        'name': name,
        'src_ch': src_ch,
        'dest_ch': dest_ch,
        'editable': editable,
        'mute': mute,
        'rest_len': len(rest),
    }


def parse_sdec(data):
    """Parse un chunk Sdec : description de section."""
    # Format: string ASCII null-terminated ou length-prefixed
    # En SFF2: "Main A, Main B, ..." séparé par virgule+espace
    text = data.rstrip(b'\x00').decode('ascii', errors='replace')
    return text


def parse_cseg(cseg_data, label=""):
    """Parse un CSEG complet (Sdec + Ctb2 * N)."""
    result = {'sdec': None, 'channels': []}
    for pos, tag, sz, payload in read_chunks(cseg_data, 0, len(cseg_data)):
        if tag == 'Sdec':
            result['sdec'] = parse_sdec(payload)
        elif tag == 'Ctb2':
            result['channels'].append(parse_ctb2(payload))
    return result


def analyze_file(path):
    with open(path, 'rb') as f:
        data = f.read()

    name = os.path.basename(path)
    ext  = os.path.splitext(path)[1].lower()
    sz   = len(data)

    # Chunks de premier niveau
    top_chunks = [(t, s) for _, t, s, _ in read_chunks(data, 0, sz)]

    # Markers dans MTrk
    markers = parse_mtrk_markers(data)

    # CASM
    casm_off = data.find(b'CASM')
    casm_info = {}
    if casm_off >= 0:
        casm_sz = struct.unpack_from('>I', data, casm_off+4)[0]
        csegs = []
        for _, tag, ssz, payload in read_chunks(data, casm_off+8, casm_off+8+casm_sz):
            if tag == 'CSEG':
                csegs.append(parse_cseg(payload))
        casm_info = {'n_csegs': len(csegs), 'csegs': csegs}

    return {
        'name': name, 'size': sz,
        'top_chunks': [t for t, s in top_chunks],
        'has_fnrc': any(t == 'FNRc' for t, s in top_chunks),
        'sff_version': markers.get('SFF2', markers.get('SFF1', {})) and ('SFF2' if 'SFF2' in markers else 'SFF1'),
        'casm': casm_info,
    }


# ─── Scan de tous les fichiers styles Yamaha ─────────────────────────────────

all_files = (
    glob.glob(r'données etude\YAMAHA (TYROS3)\**\*.prs', recursive=True) +
    glob.glob(r'données etude\YAMAHA (TYROS5)\**\*.prs', recursive=True) +
    glob.glob(r'données etude\YAMAHA (TYROS5)\**\*.sst', recursive=True)
)

print(f"Fichiers trouvés : {len(all_files)}\n")

# Grouper par variante de version (T108, T151, T152, T153, T154, T160, T161, T166, S747, S942...)
from collections import defaultdict
by_ver = defaultdict(list)
for f in sorted(all_files):
    name = os.path.basename(f)
    # Extraire le code de version (Txx ou Sxxx)
    import re
    m = re.search(r'\.(T\d+|S\d+)\.', name)
    ver = m.group(1) if m else 'unknown'
    by_ver[ver].append(f)

print("Versions détectées :")
for ver in sorted(by_ver.keys()):
    print(f"  {ver:8s} : {len(by_ver[ver])} fichier(s)")
print()

# Analyser un représentant de chaque version
print("="*70)
print("ANALYSE PAR VERSION")
print("="*70)

seen_ver = set()
for f in sorted(all_files):
    name = os.path.basename(f)
    import re
    m = re.search(r'\.(T\d+|S\d+)\.', name)
    ver = m.group(1) if m else 'unknown'
    if ver in seen_ver:
        continue
    seen_ver.add(ver)

    r = analyze_file(f)
    print(f"\n--- {ver} : {r['name']} ({r['size']} bytes) ---")
    print(f"  Format : {r['sff_version']}")
    print(f"  Chunks : {r['top_chunks']}")
    print(f"  FNRc   : {r['has_fnrc']}")
    casm = r['casm']
    print(f"  CASM   : {casm.get('n_csegs', 0)} CSEGs")
    for i, cseg in enumerate(casm.get('csegs', [])):
        print(f"    CSEG[{i}] sdec={cseg['sdec']!r}  {len(cseg['channels'])} canaux")
        for ch in cseg['channels']:
            print(f"      {ch['name']!r:20s}  src={ch['src_ch']:2d}  dest={ch['dest_ch']:2d}  "
                  f"edit={ch['editable']}  mute={ch['mute']}")
