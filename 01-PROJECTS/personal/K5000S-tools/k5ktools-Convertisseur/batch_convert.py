"""
Batch conversion of Kawai K5000 native files (.ka1, .kaa, .kc1, .kca)
to MIDI System Exclusive (.syx) format.

Recursively scans a source directory and converts all found Kawai files,
placing the .syx output into a mirror of the directory structure under
a specified output folder.

Usage:
    python batch_convert.py [--src DIR] [--dst DIR] [--channel N] [--bank LETTER] [--dry-run]
"""

import sys
import os
import argparse
import traceback

# Add the script directory to path so we can import the converter modules
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import bank
import multi
import helpers

# --- Conversion functions (extracted from the individual scripts) ---

BANK_IDS = {'A': 0x00, 'B': 0x01, 'D': 0x02, 'E': 0x03, 'F': 0x04}


def convert_ka1(filepath, bank_letter='A', tone_number=1, channel=1):
    """Convert a .ka1 single tone file to SysEx bytes."""
    data = helpers.read_file_data(filepath)
    if not bank.check_single_size(len(data)):
        raise ValueError(f"Invalid KA1 file size: {len(data)} bytes")

    header = bytearray([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x00, 0x00, 0x00])
    header[2] = channel - 1
    header[7] = BANK_IDS[bank_letter]
    header[8] = tone_number - 1

    message = bytearray()
    message += header
    message += data
    message += bytes([0xF7])
    return bytes(message)


def get_tone_map(patches):
    """Build the 19-byte tone bitmap for a bank SysEx message."""
    tone_bits = ['0'] * 128
    for patch in patches:
        tone_bits[patch['index']] = '1'

    groups = [tone_bits[i:i + 7] for i in range(0, len(tone_bits), 7)]
    buf = bytearray()
    for group in groups:
        bits = ''
        for b in reversed(group):
            bits += b
        buf += bytes([int(bits, 2)])
    return bytes(buf)


def convert_kaa(filepath, bank_letter='A', channel=1):
    """Convert a .kaa tone bank file to SysEx bytes."""
    data = helpers.read_file_data(filepath)
    bank_data = bank.get_bank(data)
    final_patches = sorted(bank_data['patches'], key=lambda x: x['index'])

    patch_data = bytearray()
    for patch in final_patches:
        patch_data += patch['data']

    header = bytearray([0xF0, 0x40, 0x00, 0x21, 0x00, 0x0A, 0x00, 0x00])
    header[2] = channel - 1
    header[7] = BANK_IDS[bank_letter]

    message = bytearray()
    message += header
    message += get_tone_map(final_patches)
    message += patch_data
    message += bytes([0xF7])
    return bytes(message)


def convert_kc1(filepath, number=1, channel=1):
    """Convert a .kc1 single multi/combi file to SysEx bytes."""
    data = helpers.read_file_data(filepath)
    if not multi.check_size(len(data)):
        raise ValueError(f"Invalid KC1 file size: {len(data)} bytes (expected {multi.MULTI_DATA_SIZE})")

    header = bytearray([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x20, 0x00])
    header[2] = channel - 1
    header[7] = number - 1

    message = bytearray()
    message += header
    message += data
    message += bytes([0xF7])
    return bytes(message)


def convert_kca(filepath, channel=1):
    """Convert a .kca multi/combi bank file to SysEx bytes."""
    data = helpers.read_file_data(filepath)
    if not multi.check_size(int(len(data) / multi.MULTI_COUNT)):
        raise ValueError(f"Invalid KCA file size: {len(data)} bytes (expected multiple of {multi.MULTI_DATA_SIZE})")

    header = bytearray([0xF0, 0x40, 0x00, 0x21, 0x00, 0x0A, 0x20])
    header[2] = channel - 1

    message = bytearray()
    message += header
    message += data
    message += bytes([0xF7])
    return bytes(message)


# --- Batch logic ---

EXTENSIONS = {'.ka1', '.kaa', '.kc1', '.kca'}


def find_kawai_files(src_dir, dst_dir=None):
    """Recursively find all Kawai K5000 native files."""
    results = []
    for root, dirs, files in os.walk(src_dir):
        # Skip macOS resource fork directories
        if '__MACOSX' in root:
            continue
        # Skip the output destination directory
        if dst_dir and os.path.abspath(root).startswith(os.path.abspath(dst_dir)):
            continue
        for fname in files:
            # Skip macOS resource forks (._xxx files)
            if fname.startswith('._'):
                continue
            if os.path.splitext(fname)[1].lower() in EXTENSIONS:
                results.append(os.path.join(root, fname))
    return sorted(results)


def convert_file(filepath, bank_letter, channel):
    """Convert a single Kawai file to SysEx bytes. Returns (syx_bytes, info_str)."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.ka1':
        syx = convert_ka1(filepath, bank_letter=bank_letter, tone_number=1, channel=channel)
        return syx, f"KA1 single tone -> bank {bank_letter}, tone 1"

    elif ext == '.kaa':
        syx = convert_kaa(filepath, bank_letter=bank_letter, channel=channel)
        return syx, f"KAA tone bank -> bank {bank_letter}"

    elif ext == '.kc1':
        syx = convert_kc1(filepath, number=1, channel=channel)
        return syx, "KC1 single multi -> slot 1"

    elif ext == '.kca':
        syx = convert_kca(filepath, channel=channel)
        return syx, "KCA multi bank"

    else:
        raise ValueError(f"Unknown extension: {ext}")


def main():
    parser = argparse.ArgumentParser(
        description='Batch convert Kawai K5000 native files to SysEx (.syx)')
    parser.add_argument('--src', default=r'D:\01-MUSIQUE\03-KAWAI',
                        help='Source directory to scan recursively (default: D:\\01-MUSIQUE\\03-KAWAI)')
    parser.add_argument('--dst', default=None,
                        help='Destination directory for .syx files (default: <src>\\SYX)')
    parser.add_argument('--channel', type=int, default=1,
                        help='MIDI channel 1-16 (default: 1)')
    parser.add_argument('--bank', default='A',
                        help='Default bank letter for KA1/KAA files: A, B, D, E, F (default: A)')
    parser.add_argument('--dry-run', action='store_true',
                        help='List files that would be converted without actually converting')

    args = parser.parse_args()

    src_dir = os.path.abspath(args.src)
    dst_dir = os.path.abspath(args.dst) if args.dst else os.path.join(src_dir, 'SYX')
    channel = args.channel
    bank_letter = args.bank.upper()

    if channel < 1 or channel > 16:
        print(f"ERROR: MIDI channel must be 1-16 (got {channel})")
        sys.exit(1)

    if bank_letter not in BANK_IDS:
        print(f"ERROR: Bank must be A, B, D, E, or F (got {bank_letter})")
        sys.exit(1)

    if not os.path.isdir(src_dir):
        print(f"ERROR: Source directory not found: {src_dir}")
        sys.exit(1)

    print(f"Source:      {src_dir}")
    print(f"Destination: {dst_dir}")
    print(f"MIDI channel: {channel}")
    print(f"Default bank: {bank_letter}")
    print()

    kawai_files = find_kawai_files(src_dir, dst_dir)
    print(f"Found {len(kawai_files)} Kawai files to convert")

    # Count by extension
    from collections import Counter
    ext_counts = Counter(os.path.splitext(f)[1].lower() for f in kawai_files)
    for ext in sorted(ext_counts.keys()):
        print(f"  {ext}: {ext_counts[ext]}")
    print()

    if args.dry_run:
        print("--- DRY RUN ---")
        for f in kawai_files:
            rel = os.path.relpath(f, src_dir)
            out_rel = rel + '.syx'
            print(f"  {rel}  ->  {out_rel}")
        print(f"\nTotal: {len(kawai_files)} files would be converted")
        return

    converted = 0
    errors = 0

    for filepath in kawai_files:
        rel_path = os.path.relpath(filepath, src_dir)
        out_rel = rel_path + '.syx'
        out_path = os.path.join(dst_dir, out_rel)

        try:
            syx_data, info = convert_file(filepath, bank_letter, channel)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            with open(out_path, 'wb') as f:
                f.write(syx_data)

            converted += 1
            print(f"  OK  {rel_path}  ({info}, {len(syx_data)} bytes)")

        except Exception as e:
            errors += 1
            print(f"  ERR {rel_path}  -- {e}")

    print()
    print(f"Done: {converted} converted, {errors} errors, {len(kawai_files)} total")


if __name__ == '__main__':
    main()
