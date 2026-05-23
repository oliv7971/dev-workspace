"""
MD5 échantillon : compare quelques .zfs de TMS CHAMBON vs 02-PHASE 02
Prend les 3 premiers fichiers (petit, moyen, grand) pour vérifier.
"""
import sqlite3
import hashlib
import os

DB_PATH = "./reports/inventory_chambon37.db"
BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"

SAMPLE = [
    "AMTP5003_20150420174334_101_0.zfs",   # 76 Mo
    "AMTP5003_20150420181239_106_0.zfs",   # 304 Mo
    "AMTP5003_20150421113619_142_0.zfs",   # 76 Mo
]

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print(f"{'Fichier':<50} {'Source':<12} {'MD5'}")
print("-" * 100)

for fname in SAMPLE:
    cur.execute("SELECT path FROM files WHERE filename = ?", (fname,))
    rows = [r[0] for r in cur.fetchall()]
    tms   = [p for p in rows if "TMS CHAMBON" in p]
    p02   = [p for p in rows if "02-PHASE 02" in p]

    hashes = {}
    for label, paths in [("TMS", tms), ("P02", p02)]:
        path = paths[0] if paths else None
        if not path or not os.path.exists(path):
            hashes[label] = "INTROUVABLE"
            print(f"  {fname:<50} {label:<12} INTROUVABLE")
            continue
        print(f"  {fname:<50} {label:<12} calcul...", end="\r", flush=True)
        h = md5(path)
        hashes[label] = h
        print(f"  {fname:<50} {label:<12} {h}")

    if "TMS" in hashes and "P02" in hashes and hashes["TMS"] != "INTROUVABLE":
        if hashes["TMS"] == hashes["P02"]:
            print(f"  {'':50} {'':12} >>> IDENTIQUES ✓")
        else:
            print(f"  {'':50} {'':12} >>> DIFFERENTS !!!")
    print()

conn.close()
