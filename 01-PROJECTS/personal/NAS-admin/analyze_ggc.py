"""Analyse structurelle de 32-GGC-BUREAU."""
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_ggc.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\32-GGC-BUREAU\\"

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    if size >= 1e3: return f"{size/1e3:.1f} Ko"
    return f"{size} o"

def rel(path):
    return path[len(BASE):] if path.startswith(BASE) else path

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute("SELECT path, filename, extension, size FROM files")
    all_files = cur.fetchall()
    
    # === Niveau 1 ===
    print("=" * 80)
    print("32-GGC-BUREAU — STRUCTURE NIVEAU 1")
    print("=" * 80)
    
    total_size = sum(sz for _, _, _, sz in all_files)
    lvl1 = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path)
        segs = r.split("\\")
        lvl1[segs[0]][0] += 1
        lvl1[segs[0]][1] += sz
    
    for k in sorted(lvl1, key=lambda x: lvl1[x][1], reverse=True):
        nb, sz = lvl1[k]
        pct = sz / total_size * 100
        print(f"  {k:40s}  {nb:>8,} fich  {fmt(sz):>10s}  ({pct:.1f}%)")
    print(f"\n  TOTAL: {len(all_files):,} fichiers, {fmt(total_size)}")
    
    # === Niveau 2 top 30 ===
    print(f"\n{'='*80}")
    print("NIVEAU 2 (top 30)")
    print("=" * 80)
    lvl2 = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path)
        segs = r.split("\\")
        k = "\\".join(segs[:2]) if len(segs) >= 2 else segs[0]
        lvl2[k][0] += 1
        lvl2[k][1] += sz
    
    for k, (nb, sz) in sorted(lvl2.items(), key=lambda x: x[1][1], reverse=True)[:30]:
        pct = sz / total_size * 100
        print(f"  {k:55s}  {nb:>6,} fich  {fmt(sz):>10s}  ({pct:.1f}%)")
    
    # === Doublons — où sont-ils ? ===
    print(f"\n{'='*80}")
    print("DOUBLONS — LOCALISATION")
    print("=" * 80)
    
    # Charger les groupes de doublons
    cur.execute("SELECT group_id, path, size FROM duplicate_groups ORDER BY size DESC")
    dup_rows = cur.fetchall()
    
    # Grouper par group_id
    groups = defaultdict(list)
    for gid, path, size in dup_rows:
        groups[gid].append((path, size))
    
    # Analyser par paire de dossiers niveau 1
    pair_stats = defaultdict(lambda: [0, 0])  # (folder1, folder2) -> [count, size]
    for gid, members in groups.items():
        size = members[0][1]
        folders = set()
        for path, _ in members:
            r = rel(path)
            folders.add(r.split("\\")[0])
        
        folders = sorted(folders)
        wasted = size * (len(members) - 1)
        
        if len(folders) == 1:
            key = f"{folders[0]} (interne)"
        else:
            key = " ↔ ".join(folders)
        pair_stats[key][0] += len(members) - 1
        pair_stats[key][1] += wasted
    
    for key in sorted(pair_stats, key=lambda x: pair_stats[x][1], reverse=True):
        nb, sz = pair_stats[key]
        print(f"  {key:55s}  {nb:>6,} doub  {fmt(sz):>10s}")
    
    # === Top 10 groupes détaillés ===
    print(f"\n{'='*80}")
    print("TOP 10 GROUPES DE DOUBLONS (détail)")
    print("=" * 80)
    
    # Trier par taille gaspillée
    sorted_groups = sorted(groups.items(), key=lambda x: x[1][0][1] * (len(x[1])-1), reverse=True)
    for gid, members in sorted_groups[:10]:
        size = members[0][1]
        wasted = size * (len(members) - 1)
        fn = os.path.basename(members[0][0]) if '\\' in members[0][0] else members[0][0]
        print(f"\n  Groupe {gid} — {fn} ({fmt(size)} x {len(members)} copies = {fmt(wasted)} gaspillé)")
        for path, _ in members:
            r = rel(path)
            # Tronquer à 90 chars
            if len(r) > 90:
                r = "..." + r[-87:]
            print(f"    • {r}")
    
    # === Dossiers suspects ===
    print(f"\n{'='*80}")
    print("DOSSIERS SUSPECTS")
    print("=" * 80)
    
    suspects = ["a classer", "divers", "temp", "tmp", "old", "ancien",
                "backup", "bak", "copie", "copy", "nouveau dossier",
                "brouillon", "a trier", "doublon", "poubelle", "trash"]
    
    suspect_folders = defaultdict(lambda: [0, 0])
    for path, fn, ext, sz in all_files:
        r = rel(path).lower()
        for suspect in suspects:
            if suspect in r:
                segs = rel(path).split("\\")
                for i, seg in enumerate(segs):
                    if suspect in seg.lower():
                        folder = "\\".join(segs[:i+1])
                        suspect_folders[folder][0] += 1
                        suspect_folders[folder][1] += sz
                        break
                break
    
    if suspect_folders:
        for folder in sorted(suspect_folders, key=lambda x: suspect_folders[x][1], reverse=True)[:15]:
            nb, sz = suspect_folders[folder]
            print(f"  {folder:60s}  {nb:>5,} fich  {fmt(sz):>10s}")
    else:
        print("  (aucun)")
    
    # === .bak et Thumbs.db ===
    print(f"\n{'='*80}")
    print("FICHIERS NETTOYABLES (.bak, Thumbs.db)")
    print("=" * 80)
    
    bak_count = 0
    bak_size = 0
    thumbs_count = 0
    thumbs_size = 0
    
    for path, fn, ext, sz in all_files:
        if ext and ext.lower() == ".bak":
            bak_count += 1
            bak_size += sz
        if fn.lower() == "thumbs.db":
            thumbs_count += 1
            thumbs_size += sz
    
    print(f"  .bak       : {bak_count:>5,} fichiers  {fmt(bak_size):>10s}")
    print(f"  Thumbs.db  : {thumbs_count:>5,} fichiers  {fmt(thumbs_size):>10s}")
    
    db.close()

import os
if __name__ == "__main__":
    main()
