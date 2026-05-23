"""Analyse détaillée des dossiers suspects dans 21-CERENE."""
import sqlite3
from collections import defaultdict

DB = "./reports/inventory_cerene.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\21-CERENE\\"

def fmt(size):
    if size >= 1e9: return f"{size/1e9:.1f} Go"
    if size >= 1e6: return f"{size/1e6:.1f} Mo"
    return f"{size/1e3:.1f} Ko"

def rel(path):
    return path[len(BASE):] if path.startswith(BASE) else path

def main():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    
    # Charger tous les fichiers
    cur.execute("SELECT path, filename, extension, size, modified_time FROM files")
    all_files = cur.fetchall()
    
    # ============================================================
    # 1. Dossiers "Nouveau dossier"
    # ============================================================
    print("=" * 80)
    print("1. DOSSIERS 'Nouveau dossier'")
    print("=" * 80)
    nd_files = [(rel(p), fn, ext, sz) for p, fn, ext, sz, mt in all_files 
                if "nouveau dossier" in rel(p).lower() or "new folder" in rel(p).lower()]
    
    # Grouper par dossier parent
    nd_groups = defaultdict(list)
    for r, fn, ext, sz in nd_files:
        segs = r.split("\\")
        for i, seg in enumerate(segs):
            if "nouveau dossier" in seg.lower() or "new folder" in seg.lower():
                parent = "\\".join(segs[:i])
                nd_groups[parent].append((fn, ext, sz))
                break
    
    for parent in sorted(nd_groups):
        files = nd_groups[parent]
        total = sum(s for _, _, s in files)
        print(f"\n  📁 {parent}\\Nouveau dossier/")
        print(f"     {len(files)} fichiers, {fmt(total)}")
        # Lister les fichiers
        for fn, ext, sz in sorted(files, key=lambda x: x[2], reverse=True)[:10]:
            print(f"       {fn:50s}  {fmt(sz)}")
        if len(files) > 10:
            print(f"       ... et {len(files)-10} autres")
    
    # ============================================================
    # 2. Dossiers "tmp" / "temp"
    # ============================================================
    print("\n" + "=" * 80)
    print("2. DOSSIERS 'tmp' / 'temp'")
    print("=" * 80)
    
    tmp_groups = defaultdict(list)
    for p, fn, ext, sz, mt in all_files:
        r = rel(p)
        segs = r.split("\\")
        for i, seg in enumerate(segs):
            if seg.lower() in ("tmp", "temp"):
                parent = "\\".join(segs[:i+1])
                tmp_groups[parent].append((fn, ext, sz))
                break
    
    for parent in sorted(tmp_groups, key=lambda x: sum(s for _, _, s in tmp_groups[x]), reverse=True):
        files = tmp_groups[parent]
        total = sum(s for _, _, s in files)
        print(f"\n  📁 {parent}/")
        print(f"     {len(files)} fichiers, {fmt(total)}")
        # Extensions
        ext_count = defaultdict(lambda: [0, 0])
        for fn, ext, sz in files:
            e = ext or "(sans ext)"
            ext_count[e][0] += 1
            ext_count[e][1] += sz
        top = sorted(ext_count.items(), key=lambda x: x[1][1], reverse=True)[:5]
        print(f"     Types: {', '.join(f'{e} ({n} fich, {fmt(s)})' for e, (n, s) in top)}")
    
    # ============================================================
    # 3. Dossiers "Backup" / "bak" / "sauvegarde"
    # ============================================================
    print("\n" + "=" * 80)
    print("3. DOSSIERS 'Backup' / 'bak' / 'sauvegarde'")
    print("=" * 80)
    
    bak_groups = defaultdict(list)
    for p, fn, ext, sz, mt in all_files:
        r = rel(p)
        segs = r.split("\\")
        for i, seg in enumerate(segs):
            if seg.lower() in ("backup", "bak", "sauvegarde", "save") or "sauvegarde" in seg.lower():
                parent = "\\".join(segs[:i+1])
                bak_groups[parent].append((fn, ext, sz))
                break
    
    for parent in sorted(bak_groups, key=lambda x: sum(s for _, _, s in bak_groups[x]), reverse=True):
        files = bak_groups[parent]
        total = sum(s for _, _, s in files)
        print(f"\n  📁 {parent}/")
        print(f"     {len(files)} fichiers, {fmt(total)}")
        for fn, ext, sz in sorted(files, key=lambda x: x[2], reverse=True)[:5]:
            print(f"       {fn:50s}  {fmt(sz)}")
        if len(files) > 5:
            print(f"       ... et {len(files)-5} autres")
    
    # ============================================================
    # 4. Dossiers "old" / "ancien"
    # ============================================================
    print("\n" + "=" * 80)
    print("4. DOSSIERS 'old' / 'ancien'")
    print("=" * 80)
    
    old_groups = defaultdict(list)
    for p, fn, ext, sz, mt in all_files:
        r = rel(p)
        segs = r.split("\\")
        for i, seg in enumerate(segs):
            if seg.lower() in ("old", "ancien", "anciens"):
                parent = "\\".join(segs[:i+1])
                old_groups[parent].append((fn, ext, sz))
                break
    
    for parent in sorted(old_groups, key=lambda x: sum(s for _, _, s in old_groups[x]), reverse=True):
        files = old_groups[parent]
        total = sum(s for _, _, s in files)
        print(f"\n  📁 {parent}/")
        print(f"     {len(files)} fichiers, {fmt(total)}")
        for fn, ext, sz in sorted(files, key=lambda x: x[2], reverse=True)[:5]:
            print(f"       {fn:50s}  {fmt(sz)}")
    
    # ============================================================
    # 5. Fichiers .bak isolés (hors dossiers backup)
    # ============================================================
    print("\n" + "=" * 80)
    print("5. FICHIERS .bak ISOLÉS")
    print("=" * 80)
    
    bak_files = [(rel(p), fn, sz) for p, fn, ext, sz, mt in all_files 
                 if ext and ext.lower() == ".bak"]
    total_bak = sum(s for _, _, s in bak_files)
    print(f"  {len(bak_files)} fichiers .bak, total {fmt(total_bak)}")
    for r, fn, sz in sorted(bak_files, key=lambda x: x[2], reverse=True)[:10]:
        # Premier dossier
        l1 = r.split("\\")[0]
        print(f"    [{l1}] {fn:50s}  {fmt(sz)}")
    
    # ============================================================
    # 6. Fichiers .iso / gros installeurs dans SERVEURS
    # ============================================================
    print("\n" + "=" * 80)
    print("6. FICHIERS .iso ET INSTALLEURS DANS 10-SERVEURS")
    print("=" * 80)
    
    installers = [(rel(p), fn, sz) for p, fn, ext, sz, mt in all_files 
                  if rel(p).startswith("10-SERVEURS") 
                  and ext and ext.lower() in (".iso", ".exe", ".msi")
                  and sz > 5_000_000]
    total_inst = sum(s for _, _, s in installers)
    print(f"  {len(installers)} installeurs > 5 Mo, total {fmt(total_inst)}")
    for r, fn, sz in sorted(installers, key=lambda x: x[2], reverse=True)[:15]:
        print(f"    {fn:60s}  {fmt(sz)}")
    
    # ============================================================
    # 7. 21-DONNEES\work — qu'est-ce que c'est ?
    # ============================================================
    print("\n" + "=" * 80)
    print("7. 21-DONNEES\\work — sous-dossiers")
    print("=" * 80)
    
    work_groups = defaultdict(lambda: [0, 0])
    for p, fn, ext, sz, mt in all_files:
        r = rel(p)
        segs = r.split("\\")
        if len(segs) >= 3 and segs[0] == "21-DONNEES" and segs[1] == "work":
            k = segs[2]
            work_groups[k][0] += 1
            work_groups[k][1] += sz
    
    for k in sorted(work_groups, key=lambda x: work_groups[x][1], reverse=True):
        nb, sz = work_groups[k]
        print(f"  {k:60s}  {nb:>6,} fich  {fmt(sz):>10s}")
    
    # ============================================================
    # RÉSUMÉ
    # ============================================================
    print("\n" + "=" * 80)
    print("RÉSUMÉ — POTENTIEL DE NETTOYAGE")
    print("=" * 80)
    
    all_nd = sum(sz for grp in nd_groups.values() for _, _, sz in grp)
    all_tmp = sum(sz for grp in tmp_groups.values() for _, _, sz in grp)
    all_bak_d = sum(sz for grp in bak_groups.values() for _, _, sz in grp)
    all_old = sum(sz for grp in old_groups.values() for _, _, sz in grp)
    
    nd_n = sum(len(v) for v in nd_groups.values())
    tmp_n = sum(len(v) for v in tmp_groups.values())
    bak_d_n = sum(len(v) for v in bak_groups.values())
    old_n = sum(len(v) for v in old_groups.values())
    
    print(f"  Nouveau dossier   : {nd_n:>6,} fichiers  {fmt(all_nd):>10s}")
    print(f"  tmp/temp          : {tmp_n:>6,} fichiers  {fmt(all_tmp):>10s}")
    print(f"  Backup/sauvegarde : {bak_d_n:>6,} fichiers  {fmt(all_bak_d):>10s}")
    print(f"  old/ancien        : {old_n:>6,} fichiers  {fmt(all_old):>10s}")
    print(f"  .bak isolés       : {len(bak_files):>6,} fichiers  {fmt(total_bak):>10s}")
    print(f"  Installeurs SERV  : {len(installers):>6,} fichiers  {fmt(total_inst):>10s}")
    grand = all_nd + all_tmp + all_bak_d + all_old + total_bak + total_inst
    grand_n = nd_n + tmp_n + bak_d_n + old_n + len(bak_files) + len(installers)
    print(f"  {'─'*50}")
    print(f"  TOTAL potentiel   : {grand_n:>6,} fichiers  {fmt(grand):>10s}")
    
    db.close()

if __name__ == "__main__":
    main()
