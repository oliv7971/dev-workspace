#!/usr/bin/env python3
"""
Korg PA4x Style (.STY) Analyzer
Analyse la structure MIDI et les chunks propriétaires d'un fichier style Korg
"""

import struct
import sys
from pathlib import Path
from typing import BinaryIO


class STYAnalyzer:
    """Analyseur de fichiers .STY Korg PA"""
    
    # Marqueurs de sections connus
    SECTION_MARKERS = {
        'V1': 'Variation 1',
        'V2': 'Variation 2', 
        'V3': 'Variation 3',
        'V4': 'Variation 4',
        'CV1': 'Chord Variation 1',
        'CV2': 'Chord Variation 2',
        'CV3': 'Chord Variation 3',
        'CV4': 'Chord Variation 4',
        'I1': 'Intro 1',
        'I2': 'Intro 2',
        'I3': 'Intro 3',
        'I4': 'Intro 4',
        'E1': 'Ending 1',
        'E2': 'Ending 2',
        'E3': 'Ending 3',
        'E4': 'Ending 4',
        'F1': 'Fill 1',
        'F2': 'Fill 2',
        'F3': 'Fill 3',
        'F4': 'Fill 4',
        'Brk': 'Break',
        'B1': 'Break 1',
    }
    
    # Noms des canaux standard
    CHANNEL_NAMES = {
        9: 'Drums/Acc5',
        10: 'Drums',
        11: 'Percussion',
        12: 'Bass',
        13: 'Acc1',
        14: 'Acc2',
        15: 'Acc3',
        16: 'Acc4',
    }

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.chunks = []
        self.markers = []
        self.tracks = []
        self.midi_data = None
        
    def read_variable_length(self, data: bytes, offset: int) -> tuple[int, int]:
        """Lit une valeur de longueur variable MIDI"""
        value = 0
        length = 0
        while True:
            byte = data[offset + length]
            value = (value << 7) | (byte & 0x7F)
            length += 1
            if not (byte & 0x80):
                break
        return value, length

    def analyze(self) -> dict:
        """Analyse complète du fichier STY"""
        print(f"\n{'='*60}")
        print(f"Analyse de: {self.filepath.name}")
        print(f"{'='*60}")
        
        with open(self.filepath, 'rb') as f:
            data = f.read()
        
        print(f"\nTaille du fichier: {len(data)} octets")
        
        # Afficher les premiers octets pour identifier le format
        print(f"\nPremiers octets (hex): {data[:32].hex(' ')}")
        print(f"Premiers octets (ascii): {data[:32]}")
        
        result = {
            'filename': self.filepath.name,
            'size': len(data),
            'chunks': [],
            'markers': [],
            'tracks': [],
        }
        
        # Chercher les chunks MIDI standard et Korg
        offset = 0
        while offset < len(data) - 8:
            chunk_id = data[offset:offset+4]
            
            # Vérifier si c'est un chunk connu
            if chunk_id in [b'MThd', b'MTrk', b'KORG', b'Korg']:
                chunk_size = struct.unpack('>I', data[offset+4:offset+8])[0]
                chunk_info = {
                    'type': chunk_id.decode('ascii', errors='replace'),
                    'offset': offset,
                    'size': chunk_size,
                }
                
                print(f"\n[CHUNK] {chunk_info['type']} à offset {offset}, taille: {chunk_size}")
                
                if chunk_id == b'MThd':
                    self._parse_header(data[offset+8:offset+8+chunk_size], chunk_info)
                elif chunk_id == b'MTrk':
                    self._parse_track(data[offset+8:offset+8+chunk_size], chunk_info, len(result['tracks']))
                    result['tracks'].append(chunk_info)
                
                result['chunks'].append(chunk_info)
                offset += 8 + chunk_size
            else:
                offset += 1
        
        # Rechercher tous les marqueurs texte dans le fichier
        self._find_markers(data, result)
        
        # Rechercher les SysEx Korg
        self._find_sysex(data, result)
        
        return result
    
    def _parse_header(self, data: bytes, chunk_info: dict):
        """Parse le header MIDI"""
        if len(data) >= 6:
            format_type = struct.unpack('>H', data[0:2])[0]
            num_tracks = struct.unpack('>H', data[2:4])[0]
            division = struct.unpack('>H', data[4:6])[0]
            
            chunk_info['format'] = format_type
            chunk_info['num_tracks'] = num_tracks
            chunk_info['division'] = division
            
            print(f"  Format: {format_type}")
            print(f"  Nombre de pistes: {num_tracks}")
            print(f"  Division: {division} ticks/noire")
    
    def _parse_track(self, data: bytes, chunk_info: dict, track_num: int):
        """Parse une piste MIDI pour extraire les événements importants"""
        events = []
        offset = 0
        running_status = 0
        channels_used = set()
        
        print(f"  --- Piste {track_num} ---")
        
        while offset < len(data):
            # Lire le delta time
            delta, delta_len = self.read_variable_length(data, offset)
            offset += delta_len
            
            if offset >= len(data):
                break
                
            status = data[offset]
            
            # Meta event
            if status == 0xFF:
                if offset + 2 >= len(data):
                    break
                meta_type = data[offset + 1]
                length, len_bytes = self.read_variable_length(data, offset + 2)
                meta_data = data[offset + 2 + len_bytes:offset + 2 + len_bytes + length]
                
                # Marqueur (type 0x06)
                if meta_type == 0x06:
                    marker_text = meta_data.decode('ascii', errors='replace').strip()
                    marker_desc = self.SECTION_MARKERS.get(marker_text, 'Unknown')
                    events.append({
                        'type': 'marker',
                        'delta': delta,
                        'text': marker_text,
                        'description': marker_desc
                    })
                    print(f"    [MARKER] '{marker_text}' -> {marker_desc}")
                
                # Nom de piste (type 0x03)
                elif meta_type == 0x03:
                    track_name = meta_data.decode('ascii', errors='replace').strip()
                    chunk_info['name'] = track_name
                    print(f"    [TRACK NAME] '{track_name}'")
                
                # Texte (type 0x01)
                elif meta_type == 0x01:
                    text = meta_data.decode('ascii', errors='replace').strip()
                    if text:
                        print(f"    [TEXT] '{text}'")
                
                # Tempo (type 0x51)
                elif meta_type == 0x51 and length == 3:
                    tempo = (meta_data[0] << 16) | (meta_data[1] << 8) | meta_data[2]
                    bpm = 60000000 / tempo
                    print(f"    [TEMPO] {bpm:.1f} BPM")
                
                # Time signature (type 0x58)
                elif meta_type == 0x58 and length >= 2:
                    numerator = meta_data[0]
                    denominator = 2 ** meta_data[1]
                    print(f"    [TIME SIG] {numerator}/{denominator}")
                
                offset += 2 + len_bytes + length
                
            # SysEx
            elif status == 0xF0:
                # Trouver la fin du SysEx (0xF7)
                end = data.find(b'\xF7', offset)
                if end == -1:
                    break
                sysex_data = data[offset:end+1]
                
                # Vérifier si c'est un SysEx Korg (manufacturer ID = 0x42)
                if len(sysex_data) > 2 and sysex_data[1] == 0x42:
                    print(f"    [SYSEX KORG] {sysex_data[:20].hex(' ')}...")
                
                offset = end + 1
                
            # Note On/Off et autres messages de canal
            elif status >= 0x80:
                running_status = status
                channel = (status & 0x0F) + 1
                channels_used.add(channel)
                
                msg_type = status & 0xF0
                if msg_type in [0x80, 0x90, 0xA0, 0xB0, 0xE0]:
                    offset += 3  # 2 data bytes + status
                elif msg_type in [0xC0, 0xD0]:
                    offset += 2  # 1 data byte + status
                else:
                    offset += 1
            else:
                # Running status
                if running_status:
                    channel = (running_status & 0x0F) + 1
                    channels_used.add(channel)
                    msg_type = running_status & 0xF0
                    if msg_type in [0x80, 0x90, 0xA0, 0xB0, 0xE0]:
                        offset += 2
                    elif msg_type in [0xC0, 0xD0]:
                        offset += 1
                else:
                    offset += 1
        
        chunk_info['events'] = events
        chunk_info['channels'] = list(channels_used)
        
        if channels_used:
            ch_names = [f"{ch}({self.CHANNEL_NAMES.get(ch, '?')})" for ch in sorted(channels_used)]
            print(f"    [CHANNELS] {', '.join(ch_names)}")
    
    def _find_markers(self, data: bytes, result: dict):
        """Recherche tous les marqueurs texte dans le fichier"""
        print(f"\n--- Recherche de marqueurs de section ---")
        
        for marker, desc in self.SECTION_MARKERS.items():
            # Chercher le marqueur comme meta event ou en texte brut
            marker_bytes = marker.encode('ascii')
            idx = 0
            while True:
                idx = data.find(marker_bytes, idx)
                if idx == -1:
                    break
                # Vérifier le contexte (précédé par un meta event marker 0xFF 0x06)
                if idx >= 2 and data[idx-2:idx] == bytes([0xFF, 0x06]):
                    print(f"  Trouvé: '{marker}' ({desc}) à offset {idx}")
                    result['markers'].append({
                        'text': marker,
                        'description': desc,
                        'offset': idx
                    })
                idx += 1
    
    def _find_sysex(self, data: bytes, result: dict):
        """Recherche les messages SysEx Korg"""
        print(f"\n--- Recherche de SysEx Korg ---")
        
        korg_sysex = []
        idx = 0
        while True:
            # Chercher le début d'un SysEx Korg (F0 42)
            idx = data.find(b'\xF0\x42', idx)
            if idx == -1:
                break
            
            # Trouver la fin
            end = data.find(b'\xF7', idx)
            if end == -1:
                break
            
            sysex = data[idx:end+1]
            korg_sysex.append({
                'offset': idx,
                'length': len(sysex),
                'data': sysex[:32].hex(' ')  # Premiers 32 octets
            })
            
            print(f"  SysEx Korg à offset {idx}, longueur: {len(sysex)}")
            idx = end + 1
        
        result['sysex'] = korg_sysex
        print(f"  Total: {len(korg_sysex)} SysEx Korg trouvés")


def main():
    if len(sys.argv) < 2:
        # Chercher automatiquement des fichiers .STY dans le répertoire courant
        sty_files = list(Path('.').glob('*.STY')) + list(Path('.').glob('*.sty'))
        
        if not sty_files:
            print("Usage: python sty_analyzer.py <fichier.sty>")
            print("\nAucun fichier .STY trouvé dans le répertoire courant.")
            print("Placez un fichier .STY du PA4x dans ce dossier et relancez le script.")
            return
        
        print(f"Fichiers .STY trouvés: {[f.name for f in sty_files]}")
        filepath = sty_files[0]
    else:
        filepath = sys.argv[1]
    
    analyzer = STYAnalyzer(filepath)
    result = analyzer.analyze()
    
    print(f"\n{'='*60}")
    print("RÉSUMÉ")
    print(f"{'='*60}")
    print(f"Chunks trouvés: {len(result['chunks'])}")
    print(f"Pistes MIDI: {len(result['tracks'])}")
    print(f"Marqueurs de section: {len(result['markers'])}")
    if 'sysex' in result:
        print(f"SysEx Korg: {len(result['sysex'])}")


if __name__ == '__main__':
    main()
