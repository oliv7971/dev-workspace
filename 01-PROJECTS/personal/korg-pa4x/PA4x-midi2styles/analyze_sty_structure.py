#!/usr/bin/env python3
"""
Analyse détaillée de la structure des fichiers .STY PA4x
"""

import struct
import sys
from pathlib import Path


def analyze_sty(filepath: str):
    """Analyse la structure d'un fichier STY PA4x"""
    
    data = Path(filepath).read_bytes()
    
    print(f"=== Analyse de {filepath} ===")
    print(f"Taille: {len(data)} octets")
    print()
    
    # Header analysis
    print("=== HEADER (premiers 32 bytes) ===")
    for i in range(0, 32, 16):
        hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{i:04x}: {hex_part}  {ascii_part}')
    
    # Trouver KORF
    korf_pos = data.find(b'KORF')
    print(f"\nKORF signature at offset: {korf_pos}")
    if korf_pos != -1:
        # Après KORF: version et taille probable
        after_korf = data[korf_pos+4:korf_pos+12]
        print(f"Après KORF: {after_korf.hex(' ')}")
    
    # Rechercher les noms de styles
    print("\n=== NOMS DE STYLES DETECTES ===")
    import re
    # Pattern: suite de caractères alphanumériques suivie de null
    names_found = []
    for match in re.finditer(rb'([A-Z][A-Za-z0-9 \-\.]{2,25})\x00', data[:10000]):
        name = match.group(1).decode('latin-1')
        offset = match.start()
        if name not in ['KORF', 'KORG', 'STARTUP', 'ALL']:
            names_found.append((offset, name))
            print(f"  [{offset:04x}] {name}")
    
    # Rechercher les marqueurs de section
    print("\n=== MARQUEURS DE SECTION ===")
    section_markers = {
        'V1': [], 'V2': [], 'V3': [], 'V4': [],
        'CV1': [], 'CV2': [], 'CV3': [], 'CV4': [],
        'I1': [], 'I2': [], 'I3': [], 'I4': [],
        'E1': [], 'E2': [], 'E3': [], 'E4': [],
        'F1': [], 'F2': [], 'F3': [], 'F4': [],
        'Brk': [], 'GS': [], 'XG': [],
    }
    
    for marker in section_markers.keys():
        marker_bytes = marker.encode('ascii')
        idx = 0
        while True:
            idx = data.find(marker_bytes, idx)
            if idx == -1:
                break
            section_markers[marker].append(idx)
            idx += 1
    
    for marker, positions in section_markers.items():
        if positions:
            print(f"  {marker}: {len(positions)} occurrence(s)")
            # Afficher contexte du premier
            pos = positions[0]
            ctx_before = data[max(0,pos-8):pos]
            ctx_after = data[pos:pos+len(marker)+8]
            print(f"      Premier: offset {pos}, contexte: {ctx_before.hex()} | {marker} | {ctx_after[len(marker):].hex()}")
    
    # Chercher les signatures KORG
    print("\n=== SIGNATURES KORG/MIDI ===")
    for sig in [b'KORG', b'MIDI', b'MThd', b'MTrk', b'SFF1', b'SFF2', b'CASM', b'CSEG', b'Sdec', b'Ctab', b'Cntt']:
        pos = data.find(sig)
        if pos != -1:
            print(f"  {sig.decode('latin-1')}: offset {pos}")
            # Afficher contexte
            ctx = data[pos:pos+40]
            print(f"      {ctx[:20].hex(' ')}")
    
    # Chercher les SysEx Korg
    print("\n=== SYSEX KORG ===")
    sysex_count = 0
    idx = 0
    while sysex_count < 10:
        idx = data.find(b'\xF0\x42', idx)
        if idx == -1:
            break
        # Trouver la fin
        end = data.find(b'\xF7', idx)
        if end != -1:
            length = end - idx + 1
            print(f"  SysEx Korg à {idx}, longueur {length}: {data[idx:idx+min(20,length)].hex(' ')}...")
            sysex_count += 1
        idx += 1
    
    # Analyser la structure probable de l'index des styles
    print("\n=== STRUCTURE D'INDEX (hypothèse) ===")
    # Le fichier semble avoir un header, puis des entrées de 52 bytes environ
    # Chaque entrée contient un offset vers les données du style
    
    # Essayons de lire les offsets potentiels
    print("Analyse des 4-bytes potentiels offsets dans le header:")
    for i in range(0, 200, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if 1000 < val < len(data):
            # Pourrait être un offset valide
            target = data[val:val+20] if val < len(data) - 20 else b''
            if any(32 <= b < 127 for b in target[:10]):
                print(f"  Offset {i}: valeur {val} -> {target[:20]}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        analyze_sty(sys.argv[1])
    else:
        # Chercher un fichier STY
        for sty in Path('.').rglob('*.STY'):
            analyze_sty(str(sty))
            break
