#!/usr/bin/env python3
"""
convert.py — Convertisseur Yamaha SFF2 → KORG PA4x .STY

Usage:
    python convert.py INPUT.prs [OUTPUT.STY] [OPTIONS]

Arguments:
    INPUT.prs       Fichier style Yamaha (.prs, .sst, .T160.prs, etc.)
    OUTPUT.STY      Fichier banque KORG de sortie (.STY)
                    (défaut: verif/TEST.SET/STYLE/{nom}.STY)

Options:
    --name NAME     Nom du style dans la banque (défaut: nom du fichier d'entrée)
    --dry-run       Parse et convertit sans écrire le fichier de sortie

Exemples:
    python convert.py "données etude/YAMAHA (TYROS5)/Ballad/8BeatBallad1.T160.prs"
    python convert.py "données etude/YAMAHA (TYROS5)/Ballad/8BeatBallad1.T160.prs" output.STY
    python convert.py MyStyle.sst MyStyle.STY --name "My Style"
"""

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Convertisseur Yamaha SFF2 → KORG PA4x .STY',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('input', help='Fichier style Yamaha (.prs / .sst)')
    parser.add_argument('output', nargs='?', default=None,
                        help='Fichier banque KORG de sortie (.STY) '
                             '(défaut: verif/TEST.SET/STYLE/{nom}.STY)')
    parser.add_argument('--name', default=None,

                        help='Nom du style (défaut: nom du fichier sans extension)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Convertit sans écrire le fichier de sortie')
    args = parser.parse_args()

    # ── Validate input ────────────────────────────────────────────────────────
    if not os.path.isfile(args.input):
        print(f"Erreur: fichier introuvable: {args.input}", file=sys.stderr)
        return 1

    # ── Determine style name ───────────────────────────────────────────────────
    style_name = args.name
    if style_name is None:
        base = os.path.basename(args.input)
        # Strip all extensions (e.g. "8BeatBallad1.T160.prs" -> "8BeatBallad1")
        style_name = base.split('.')[0][:16]

    # ── Determine output path ──────────────────────────────────────────────────
    if args.output is None:
        _deploy_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'verif', 'TEST.SET', 'STYLE',
        )
        os.makedirs(_deploy_dir, exist_ok=True)
        # Nommage KORG : USER01.STY .. USER99.STY (premier slot libre)
        for _slot in range(1, 100):
            _candidate = os.path.join(_deploy_dir, f'USER{_slot:02d}.STY')
            if not os.path.exists(_candidate):
                break
        args.output = _candidate

    # ── Parse Yamaha style ────────────────────────────────────────────────────
    print(f"Lecture : {args.input}")
    try:
        from tools.sff2_reader import read_style
        yamaha = read_style(args.input)
    except Exception as e:
        print(f"Erreur de lecture du fichier Yamaha: {e}", file=sys.stderr)
        return 1

    print(f"  Style Yamaha : {yamaha.style_name!r}")
    print(f"  Tempo        : {yamaha.bpm:.1f} BPM")
    print(f"  Signature    : {yamaha.time_sig[0]}/{yamaha.time_sig[1]}")
    print(f"  Sections     : {len(yamaha.sections)}")
    print(f"  CASM         : {len(yamaha.casm)} groupes")

    # ── Convert to KORG ───────────────────────────────────────────────────────
    print(f"\nConversion -> KORG (nom: {style_name!r})")
    try:
        from tools.converter import convert_style, YAMAHA_TO_KORG_ELEM, N_KORG_ELEMENTS
        korg_style = convert_style(yamaha, name=style_name)
    except Exception as e:
        import traceback
        print(f"Erreur de conversion: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1

    n_tracks = len(korg_style.midi_tracks)
    n_elems = sum(1 for elem in korg_style.style_elements
                  if any(ev.type == 'note_on' for t in
                         [tr for tr in korg_style.midi_tracks]
                         for ev in t.events))
    print(f"  Pistes globales  : {n_tracks}")
    print(f"  StyleElements    : {len(korg_style.style_elements)}")

    # ── Encode KORG style ─────────────────────────────────────────────────────
    print("\nEncodage KORG...")
    try:
        from tools.style_writer import encode_style
        style_bytes = encode_style(korg_style)
    except Exception as e:
        import traceback
        print(f"Erreur d'encodage: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1

    print(f"  Taille style (brut): {len(style_bytes)} bytes")

    # ── Write output bank ─────────────────────────────────────────────────────
    if args.dry_run:
        print("\n[--dry-run] Fichier non écrit.")
        return 0

    try:
        from tools.korf_writer import write_bank
        write_bank([(style_name, style_bytes)], args.output)
    except Exception as e:
        import traceback
        print(f"Erreur d'écriture: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1

    size_kb = os.path.getsize(args.output) / 1024
    print(f"\nFichier écrit : {args.output} ({size_kb:.1f} Ko)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
