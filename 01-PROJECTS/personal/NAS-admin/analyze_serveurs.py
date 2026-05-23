"""Analyse détaillée de 10-SERVEURS et recouvrements."""
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
    
    # Charger tous les fichiers en mémoire
    cur.execute("SELECT path, filename, extension, size FROM files")
    all_files = cur.fetchall()
    
    # === MOZART02 niveau 3 ===
    print("=== MOZART02 : sous-dossiers niveau 3 ===")
    folders = defaultdict(lambda: [0, 0])
    for path, fn, ext, size in all_files:
        r = rel(path)
        segs = r.split("\\")
        if len(segs) >= 4 and "MOZART02" in segs[1]:
            k = "\\".join(segs[:4])
            folders[k][0] += 1
            folders[k][1] += size
    
    for k in sorted(folders, key=lambda x: folders[x][1], reverse=True):
        nb, sz = folders[k]
        print(f"  {k:75s}  {nb:>8,} fich  {fmt(sz):>10s}")
    
    # === MOZART02 niveau 4 pour les gros ===
    print("\n=== MOZART02\\travail : sous-dossiers niveau 4 ===")
    folders4 = defaultdict(lambda: [0, 0])
    for path, fn, ext, size in all_files:
        r = rel(path)
        segs = r.split("\\")
        if len(segs) >= 5 and "MOZART02" in segs[1] and segs[3] == "travail":
            k = "\\".join(segs[:5])
            folders4[k][0] += 1
            folders4[k][1] += size
    
    for k in sorted(folders4, key=lambda x: folders4[x][1], reverse=True)[:20]:
        nb, sz = folders4[k]
        print(f"  {k:80s}  {nb:>8,} fich  {fmt(sz):>10s}")
    
    # === Recouvrement nom+taille (pas hash) ===
    print("\n=== RECOUVREMENT 10-SERVEURS vs 03-PROJETS (nom+taille identiques) ===")
    serveurs_by_key = defaultdict(list)
    projets_by_key = defaultdict(list)
    
    for path, fn, ext, size in all_files:
        r = rel(path)
        key = (fn, size)
        if r.startswith("10-SERVEURS"):
            serveurs_by_key[key].append(r)
        elif r.startswith("03-PROJETS"):
            projets_by_key[key].append(r)
    
    overlap_count = 0
    overlap_size = 0
    for key in serveurs_by_key:
        if key in projets_by_key:
            fn, sz = key
            overlap_count += len(serveurs_by_key[key])
            overlap_size += sz * len(serveurs_by_key[key])
    
    print(f"  Fichiers SERVEURS avec homonyme dans PROJETS: {overlap_count:,}")
    print(f"  Taille potentiellement récupérable: {fmt(overlap_size)}")
    
    # === Contenu unique de 10-SERVEURS (pas dans PROJETS) ===
    unique_serveurs = defaultdict(lambda: [0, 0])
    for path, fn, ext, size in all_files:
        r = rel(path)
        if r.startswith("10-SERVEURS"):
            key = (fn, size)
            if key not in projets_by_key:
                segs = r.split("\\")
                k = segs[1] if len(segs) >= 2 else "(racine)"
                unique_serveurs[k][0] += 1
                unique_serveurs[k][1] += size
    
    print(f"\n=== CONTENU UNIQUE DE 10-SERVEURS (absent de PROJETS) ===")
    for k in sorted(unique_serveurs, key=lambda x: unique_serveurs[x][1], reverse=True):
        nb, sz = unique_serveurs[k]
        print(f"  {k:55s}  {nb:>8,} fich  {fmt(sz):>10s}")
    
    # === Que contient MSys ? ===
    print("\n=== MSys : sous-dossiers ===")
    msys = defaultdict(lambda: [0, 0])
    for path, fn, ext, size in all_files:
        r = rel(path)
        segs = r.split("\\")
        if len(segs) >= 3 and segs[0] == "10-SERVEURS" and segs[1] == "MSys":
            k = segs[2]
            msys[k][0] += 1
            msys[k][1] += size
    
    for k in sorted(msys, key=lambda x: msys[x][1], reverse=True)[:15]:
        nb, sz = msys[k]
        print(f"  {k:55s}  {nb:>8,} fich  {fmt(sz):>10s}")
    
    # === Copie de cvsroot - c'est quoi ? ===
    print("\n=== Copie de cvsroot : contenu ===")
    cvs = defaultdict(lambda: [0, 0])
    for path, fn, ext, size in all_files:
        r = rel(path)
        segs = r.split("\\")
        if len(segs) >= 3 and "cvsroot" in segs[1].lower():
            k = segs[2] if len(segs) >= 3 else "(racine)"
            cvs[k][0] += 1
            cvs[k][1] += size
    
    for k in sorted(cvs, key=lambda x: cvs[x][1], reverse=True)[:15]:
        nb, sz = cvs[k]
        print(f"  {k:55s}  {nb:>8,} fich  {fmt(sz):>10s}")
    
    db.close()

if __name__ == "__main__":
    main()
