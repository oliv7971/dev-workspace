"""Dump détaillé du MTrk d'un fichier SFF2 : sections, SInt, tempo."""
import struct, glob, os

def read_vlq(data, pos):
    val = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        val = (val << 7) | (b & 0x7F)
        if not (b & 0x80):
            break
    return val, pos

def dump_mtrk(data):
    """Dump les events du MTrk principal (style)."""
    # Localiser MThd → MTrk
    mthd_sz = struct.unpack_from('>I', data, 4)[0]
    mtrk_off = 8 + mthd_sz
    mtrk_sz  = struct.unpack_from('>I', data, mtrk_off + 4)[0]
    mtrk_data = data[mtrk_off + 8 : mtrk_off + 8 + mtrk_sz]
    print(f"MTrk @ {mtrk_off}, taille={mtrk_sz}")
    
    pos = 0
    abs_tick = 0
    running_status = 0
    event_count = 0
    
    while pos < len(mtrk_data):
        delta, pos = read_vlq(mtrk_data, pos)
        abs_tick += delta
        
        if pos >= len(mtrk_data):
            break
        
        status = mtrk_data[pos]
        
        if status == 0xFF:  # Meta
            pos += 1
            meta_type = mtrk_data[pos]; pos += 1
            meta_len, pos = read_vlq(mtrk_data, pos)
            meta_data = mtrk_data[pos:pos+meta_len]; pos += meta_len
            
            if meta_type == 0x51:
                us = struct.unpack_from('>I', b'\x00' + meta_data)[0]
                bpm = 60_000_000 / us
                print(f"  tick={abs_tick:6d}  META Tempo: {us} µs/beat = {bpm:.1f} BPM")
            elif meta_type == 0x58:
                num = meta_data[0]; den = 1 << meta_data[1]
                print(f"  tick={abs_tick:6d}  META TimeSig: {num}/{den}  clocks={meta_data[2]}  32nds={meta_data[3]}")
            elif meta_type == 0x06:
                txt = meta_data.rstrip(b'\x00').decode('ascii', 'replace')
                print(f"  tick={abs_tick:6d}  MARKER: {txt!r}")
            elif meta_type == 0x01:
                txt = meta_data.rstrip(b'\x00').decode('ascii', 'replace')
                print(f"  tick={abs_tick:6d}  TEXT: {txt!r}")
            elif meta_type == 0x2F:
                print(f"  tick={abs_tick:6d}  END OF TRACK (pos={pos})")
                break
            else:
                print(f"  tick={abs_tick:6d}  META 0x{meta_type:02X} len={meta_len}: {meta_data[:16].hex()}...")
        
        elif status in (0xF0, 0xF7):  # SysEx
            pos += 1
            sx_len, pos = read_vlq(mtrk_data, pos)
            sx_data = mtrk_data[pos:pos+sx_len]; pos += sx_len
            marker = sx_data[:4].decode('ascii', 'replace')
            print(f"  tick={abs_tick:6d}  SYSEX 0x{status:02X} len={sx_len}: marker={marker!r}  hex={sx_data[:16].hex()}...")
        
        elif status & 0x80:  # Canal avec status byte explicite
            running_status = status
            ch_type = status & 0xF0
            ch = status & 0x0F
            
            if ch_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):  # 2 data bytes
                d1 = mtrk_data[pos]; d2 = mtrk_data[pos+1]; pos += 2
                if event_count < 5 or ch_type == 0xB0 and d1 in (0, 32, 7):
                    names = {0x80:'NoteOff',0x90:'NoteOn',0xA0:'Aftertouch',0xB0:'CC',0xE0:'PitchBend'}
                    print(f"  tick={abs_tick:6d}  {names[ch_type]} ch={ch+1} d1={d1} d2={d2}")
            elif ch_type == 0xC0:  # Program change
                d1 = mtrk_data[pos]; pos += 1
                print(f"  tick={abs_tick:6d}  PC ch={ch+1} prog={d1}")
            elif ch_type == 0xD0:  # Chan pressure
                pos += 1
            event_count += 1
        
        else:  # Running status
            ch_type = running_status & 0xF0
            ch = running_status & 0x0F
            
            if ch_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                pos += 2
            elif ch_type in (0xC0, 0xD0):
                pos += 1
            event_count += 1


# T160 reference
files_t160 = glob.glob(r'données etude\YAMAHA (TYROS5)\**\*.prs', recursive=True)
ref = next(f for f in sorted(files_t160) if 'T160' in f)
print(f"=== {os.path.basename(ref)} ===")
with open(ref, 'rb') as fi:
    d = fi.read()
dump_mtrk(d)
