"""Extraction de toutes les archives de 34-controle voussoirs SMP4.
Extrait chaque archive dans _extracted/<nom_archive>/ pour pouvoir ensuite
consolider le contenu avec SESSIONS CONTROLES.

Usage:
  python extract_smp4_archives.py          # dry-run
  python extract_smp4_archives.py --apply  # extraction reelle
"""
import subprocess
import sqlite3
import os
import sys
import time

DB = r'inventaires/inventaire_34-controle voussoirs SMP4.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\34-controle voussoirs SMP4'
EXTRACT_DIR = os.path.join(BASE, '_extracted')
SEVENZ = r'C:\Program Files\7-Zip\7z.exe'

APPLY = '--apply' in sys.argv
FORCE = '--force' in sys.argv

conn = sqlite3.connect(DB)
c = conn.cursor()

# Lister toutes les archives
archives = []

# Archives dans ZIP/
c.execute("""SELECT filename, size FROM files 
WHERE path LIKE ? AND extension IN ('.7z', '.zip', '.rar')
ORDER BY size DESC""", (BASE + r'\USINE-VOUSSOIRS-SMLP\ZIP\%',))
for fn, sz in c.fetchall():
    full = os.path.join(BASE, 'USINE-VOUSSOIRS-SMLP', 'ZIP', fn)
    archives.append((full, fn, sz))

# 11-SMP4.zip dans _a_classer
c.execute("SELECT path, filename, size FROM files WHERE filename = '11-SMP4.zip'")
for p, fn, sz in c.fetchall():
    # path dans l'inventaire inclut le filename pour ce cas
    parent = os.path.dirname(p) if p.endswith(fn) else p
    full = os.path.join(parent, fn)
    archives.append((full, fn, sz))

conn.close()

print(f"{'=' * 100}")
print(f"EXTRACTION DES ARCHIVES - 34-controle voussoirs SMP4")
print(f"{'=' * 100}")
print(f"Mode: {'APPLY' if APPLY else 'DRY-RUN'}{' (FORCE)' if FORCE else ''}")
print(f"Destination: {EXTRACT_DIR}")
print(f"Archives: {len(archives)}")

total_sz = sum(sz for _, _, sz in archives)
print(f"Taille totale archives: {total_sz/1073741824:.1f} Go")
print()

if APPLY and not os.path.exists(EXTRACT_DIR):
    os.makedirs(EXTRACT_DIR)
    print(f"Cree: {EXTRACT_DIR}")

success = 0
errors = []

for i, (full_path, archive_name, archive_sz) in enumerate(archives, 1):
    # Nom du dossier de destination = nom archive sans extension
    dest_name = os.path.splitext(archive_name)[0]
    dest_dir = os.path.join(EXTRACT_DIR, dest_name)
    
    sz_str = f"{archive_sz/1073741824:.2f} Go" if archive_sz > 1073741824 else f"{archive_sz/1048576:.0f} Mo"
    print(f"[{i}/{len(archives)}] {archive_name} ({sz_str})")
    print(f"  -> {dest_dir}")
    
    if not os.path.exists(full_path):
        print(f"  ERREUR: fichier introuvable!")
        errors.append((archive_name, "fichier introuvable"))
        continue
    
    if APPLY:
        if os.path.exists(dest_dir) and not FORCE:
            # Verifier si deja extrait
            existing = sum(len(files) for _, _, files in os.walk(dest_dir))
            if existing > 0:
                print(f"  SKIP: deja extrait ({existing} fichiers)")
                success += 1
                continue
        
        os.makedirs(dest_dir, exist_ok=True)
        
        t0 = time.time()
        try:
            result = subprocess.run(
                [SEVENZ, 'x', '-y', f'-o{dest_dir}', full_path],
                capture_output=True, text=True, timeout=21600,
                encoding='utf-8', errors='replace'
            )
            elapsed = time.time() - t0
            
            if result.returncode == 0:
                # Compter les fichiers extraits
                extracted = sum(len(files) for _, _, files in os.walk(dest_dir))
                print(f"  OK: {extracted} fichiers extraits en {elapsed:.0f}s")
                success += 1
            else:
                # 7z retourne 1 pour warnings (pas forcement une erreur)
                if result.returncode == 1:
                    extracted = sum(len(files) for _, _, files in os.walk(dest_dir))
                    print(f"  WARNING (code 1): {extracted} fichiers extraits en {elapsed:.0f}s")
                    if result.stderr:
                        print(f"  stderr: {result.stderr[:200]}")
                    success += 1
                else:
                    print(f"  ERREUR (code {result.returncode})")
                    if result.stderr:
                        print(f"  stderr: {result.stderr[:300]}")
                    errors.append((archive_name, f"code {result.returncode}"))
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT (>1h)")
            errors.append((archive_name, "timeout"))
        except Exception as e:
            print(f"  ERREUR: {e}")
            errors.append((archive_name, str(e)))
    else:
        print(f"  (dry-run)")

print(f"\n{'=' * 100}")
print(f"RESUME")
print(f"{'=' * 100}")
if APPLY:
    print(f"Extraites avec succes: {success}/{len(archives)}")
    if errors:
        print(f"Erreurs: {len(errors)}")
        for name, err in errors:
            print(f"  {name}: {err}")
else:
    print(f"{len(archives)} archives a extraire")
    print(f"Taille compressees: {total_sz/1073741824:.1f} Go")
    print(f"\nRelancer avec --apply pour executer")
