"""Hash uniquement les fichiers qui n'ont pas encore de hash dans la DB."""
import os
import sys
import hashlib
import sqlite3
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

DB = "./reports/inventory_strasbourg.db"
console = Console()

def compute_hash(filepath, block_size=65536):
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                h.update(data)
        return h.hexdigest()
    except (PermissionError, OSError):
        return None

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Fichiers sans hash
rows = cur.execute(
    "SELECT rowid, path, size FROM files WHERE hash_md5 IS NULL AND size >= 1024"
).fetchall()

total = len(rows)
if total == 0:
    console.print("[green]Tous les fichiers sont déjà hashés ![/green]")
    sys.exit(0)

# Stats
total_hashed = cur.execute("SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL").fetchone()[0]
total_files = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
console.print(f"Fichiers dans la DB: {total_files:,}")
console.print(f"Déjà hashés: {total_hashed:,}")
console.print(f"À hasher: {total:,}")

total_size = sum(r[2] for r in rows)
console.print(f"Taille à hasher: {total_size / (1024**3):.1f} Go\n")

done = 0
errors = 0
batch = []

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TextColumn("{task.completed}/{task.total}"),
    TimeElapsedColumn(),
    console=console,
) as progress:
    task = progress.add_task("Hash", total=total)
    
    for rowid, path, size in rows:
        h = compute_hash(path)
        if h:
            batch.append((h, rowid))
            done += 1
        else:
            errors += 1
        
        if len(batch) >= 100:
            cur.executemany("UPDATE files SET hash_md5 = ? WHERE rowid = ?", batch)
            conn.commit()
            batch.clear()
        
        progress.advance(task)
    
    if batch:
        cur.executemany("UPDATE files SET hash_md5 = ? WHERE rowid = ?", batch)
        conn.commit()

console.print(f"\n[bold green]✅ Hash terminé ![/bold green]")
console.print(f"  Hashés: {done:,}")
console.print(f"  Erreurs: {errors:,}")
conn.close()
