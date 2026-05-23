"""Dump les headers de chunks de bank.objects[0] pour comprendre les flags/versions."""
from tools.korf import read_bank, iter_chunks, _Reader, _read_chunk_header

bank = read_bank(r'données etude\KORG (PA4x musikant)\PA4X (KORG).SET\STYLE\BANK01.STY')

# Aussi: dump le header du premier objet dans le fichier brut
# On doit retrouver le raw_id utilisé pour l'objet style dans la banque
data = bank.raw_data

# Afficher les 10 premiers chunks de bank.objects[0]
style_data = bank.objects[0]
print("=== Chunks de bank.objects[0] (layer 1) ===")
for hdr, payload in iter_chunks(style_data):
    print(f"  type=0x{hdr.chunk_type:02X}  v={hdr.version_major}.{hdr.version_minor}  flags=0x{hdr.flags:02X}  size={hdr.size}")
    if hdr.chunk_type == 0x01 and hdr.version_major == 5:
        print("  === Outer wrapper - inner chunks (layer 2) ===")
        for hdr2, payload2 in iter_chunks(payload):
            print(f"    type=0x{hdr2.chunk_type:02X}  v={hdr2.version_major}.{hdr2.version_minor}  flags=0x{hdr2.flags:02X}  size={hdr2.size}")
            if hdr2.chunk_type == 0x02:  # MIDITrackList
                for hdr3, payload3 in iter_chunks(payload2):
                    print(f"      MIDI type=0x{hdr3.chunk_type:02X}  v={hdr3.version_major}.{hdr3.version_minor}  flags=0x{hdr3.flags:02X}  size={hdr3.size}")
            if hdr2.chunk_type == 0x03:  # StyleElement (first one)
                for hdr3, payload3 in iter_chunks(payload2):
                    print(f"      Elem type=0x{hdr3.chunk_type:02X}  v={hdr3.version_major}.{hdr3.version_minor}  flags=0x{hdr3.flags:02X}  size={hdr3.size}")
                break  # just first element
