"""Dump hex des chunks Ctb2 dans un CSEG SFF2 pour analyser le format exact."""
import struct, glob

def read_chunks(d, start, end):
    p = start
    while p + 8 <= end:
        tag = d[p:p+4]
        sz  = struct.unpack_from('>I', d, p+4)[0]
        yield p, tag.decode('latin1'), sz, d[p+8:p+8+sz]
        p += 8 + sz

# Analyser plusieurs variantes
files = (
    glob.glob(r'données etude\YAMAHA (TYROS5)\**\*.prs', recursive=True) +
    glob.glob(r'données etude\YAMAHA (TYROS3)\**\*.prs', recursive=True)
)

seen = set()
for fpath in sorted(files):
    import re, os
    name = os.path.basename(fpath)
    m = re.search(r'\.(T\d+|S\d+)\.', name)
    ver = m.group(1) if m else 'unknown'
    if ver in seen:
        continue
    seen.add(ver)

    with open(fpath, 'rb') as fi:
        data = fi.read()

    casm_off = data.find(b'CASM')
    if casm_off < 0:
        continue
    casm_sz = struct.unpack_from('>I', data, casm_off+4)[0]
    pos = casm_off + 8
    end = casm_off + 8 + casm_sz

    print(f"\n{'='*60}")
    print(f"Version {ver}: {name}")
    cseg_idx = 0
    for _, tag, sz, payload in read_chunks(data, pos, end):
        if tag == 'CSEG' and cseg_idx == 0:
            print(f"  CSEG[0] size={sz}")
            for _, tag2, sz2, p2 in read_chunks(payload, 0, len(payload)):
                if tag2 == 'Sdec':
                    print(f"    Sdec: {p2.rstrip(b'\\x00').decode('ascii','replace')!r}")
                elif tag2 == 'Ctb2':
                    # Affiche hex + interprétation fixe 8 bytes
                    hex_str = p2.hex()
                    name_bytes = p2[0:8]
                    ch_name = name_bytes.rstrip(b' ').decode('ascii','replace')
                    if len(p2) >= 9:
                        print(f"    Ctb2[{sz2:2d}]: name={ch_name!r:12s} | "
                              f"bytes[8+]={p2[8:].hex()} | "
                              f"raw={p2.hex()}")
                    else:
                        print(f"    Ctb2[{sz2:2d}]: raw={hex_str}")
        elif tag == 'CSEG':
            cseg_idx += 1
