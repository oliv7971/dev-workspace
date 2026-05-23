"""
Scanner d'inventaire - Parcourt le NAS et catalogue tous les fichiers dans une base SQLite.
"""
import hashlib
import os
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from .config import load_config

console = Console()

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    extension TEXT,
    size INTEGER NOT NULL,
    modified_time REAL,
    created_time REAL,
    hash_md5 TEXT,
    scan_date REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_hash ON files(hash_md5);
CREATE INDEX IF NOT EXISTS idx_size ON files(size);
CREATE INDEX IF NOT EXISTS idx_extension ON files(extension);
CREATE INDEX IF NOT EXISTS idx_filename ON files(filename);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def _compute_hash_worker(filepath: str, chunk_size: int = 65536) -> str | None:
    """Worker interne pour le calcul du hash MD5."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def compute_hash(filepath: str, chunk_size: int = 65536, timeout: int = 300) -> str | None:
    """Calcule le hash MD5 d'un fichier avec timeout (défaut: 5 min). Retourne None en cas d'erreur."""
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_compute_hash_worker, filepath, chunk_size)
            return future.result(timeout=timeout)
    except FuturesTimeoutError:
        console.print(f"  [yellow]⚠ Hash timeout ({timeout}s): {filepath}[/yellow]")
        return None
    except (PermissionError, OSError) as e:
        console.print(f"  [yellow]⚠ Hash impossible: {filepath} ({e})[/yellow]")
        return None


def scan_directory(nas_path: str, config: dict, db_conn: sqlite3.Connection, compute_hashes: bool = False):
    """Scanne le répertoire NAS et insère les fichiers dans la base."""
    exclude_dirs = set(config.get("scan", {}).get("exclude_dirs", []))
    exclude_ext = set(ext.lower() for ext in config.get("scan", {}).get("exclude_extensions", []))
    min_size = config.get("scan", {}).get("min_size_for_duplicates", 1024)
    scan_time = time.time()

    # Phase 1 : Comptage rapide des fichiers
    console.print(f"\n[bold blue]📁 Scan de : {nas_path}[/bold blue]")
    console.print("[dim]Phase 1 : Comptage des fichiers...[/dim]")

    total_files = 0
    for root, dirs, files in os.walk(nas_path):
        # Exclure les dossiers système Synology
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        total_files += len(files)

    console.print(f"[green]  Trouvé : {total_files:,} fichiers[/green]")

    # Phase 2 : Scan détaillé
    console.print("[dim]Phase 2 : Catalogage...[/dim]")
    scanned = 0
    errors = 0
    total_size = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scan", total=total_files)

        batch = []
        for root, dirs, files in os.walk(nas_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for filename in files:
                filepath = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()

                if ext in exclude_ext:
                    progress.advance(task)
                    continue

                try:
                    stat = os.stat(filepath)
                    size = stat.st_size
                    mtime = stat.st_mtime
                    ctime = stat.st_ctime
                except (PermissionError, OSError):
                    errors += 1
                    progress.advance(task)
                    continue

                file_hash = None
                if compute_hashes and size >= min_size:
                    file_hash = compute_hash(filepath)

                batch.append((
                    filepath,
                    filename,
                    ext if ext else None,
                    size,
                    mtime,
                    ctime,
                    file_hash,
                    scan_time,
                ))

                total_size += size
                scanned += 1

                # Insertion par lots de 500
                if len(batch) >= 500:
                    _insert_batch(db_conn, batch)
                    batch.clear()

                progress.advance(task)

        # Insérer le reste
        if batch:
            _insert_batch(db_conn, batch)

    console.print(f"\n[bold green]✅ Scan terminé ![/bold green]")
    console.print(f"  Fichiers scannés : {scanned:,}")
    console.print(f"  Erreurs d'accès  : {errors:,}")
    console.print(f"  Taille totale    : {_format_size(total_size)}")


def _insert_batch(conn: sqlite3.Connection, batch: list):
    conn.executemany(
        """INSERT OR REPLACE INTO files
           (path, filename, extension, size, modified_time, created_time, hash_md5, scan_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        batch,
    )
    conn.commit()


def print_summary(db_conn: sqlite3.Connection):
    """Affiche un résumé de l'inventaire."""
    console.print("\n[bold]═══ RÉSUMÉ DE L'INVENTAIRE ═══[/bold]\n")

    # Stats globales
    row = db_conn.execute("SELECT COUNT(*), SUM(size) FROM files").fetchone()
    total_files, total_size = row[0], row[1] or 0
    console.print(f"  Total fichiers : {total_files:,}")
    console.print(f"  Taille totale  : {_format_size(total_size)}")

    # Top extensions par nombre
    console.print("\n[bold]Top 15 extensions (par nombre) :[/bold]")
    table = Table(show_header=True)
    table.add_column("Extension", style="cyan")
    table.add_column("Nombre", justify="right")
    table.add_column("Taille", justify="right")

    rows = db_conn.execute(
        """SELECT COALESCE(extension, '(aucune)'), COUNT(*), SUM(size)
           FROM files GROUP BY extension ORDER BY COUNT(*) DESC LIMIT 15"""
    ).fetchall()
    for ext, count, size in rows:
        table.add_row(ext, f"{count:,}", _format_size(size or 0))
    console.print(table)

    # Top extensions par taille
    console.print("\n[bold]Top 15 extensions (par taille) :[/bold]")
    table2 = Table(show_header=True)
    table2.add_column("Extension", style="cyan")
    table2.add_column("Taille", justify="right")
    table2.add_column("Nombre", justify="right")

    rows2 = db_conn.execute(
        """SELECT COALESCE(extension, '(aucune)'), SUM(size), COUNT(*)
           FROM files GROUP BY extension ORDER BY SUM(size) DESC LIMIT 15"""
    ).fetchall()
    for ext, size, count in rows2:
        table2.add_row(ext, _format_size(size or 0), f"{count:,}")
    console.print(table2)

    # Dossiers les plus volumineux (niveau 1 et 2)
    console.print("\n[bold]Top 20 dossiers les plus volumineux :[/bold]")
    # On va extraire le dossier parent
    rows3 = db_conn.execute(
        """SELECT path, size FROM files"""
    ).fetchall()

    from collections import defaultdict
    dir_sizes = defaultdict(lambda: [0, 0])  # [size, count]
    for path, size in rows3:
        parts = Path(path).parts
        # Prendre les 3 premiers niveaux après la racine
        if len(parts) >= 3:
            key = str(Path(*parts[:3]))
        elif len(parts) >= 2:
            key = str(Path(*parts[:2]))
        else:
            key = str(Path(*parts[:1]))
        dir_sizes[key][0] += size
        dir_sizes[key][1] += 1

    table3 = Table(show_header=True)
    table3.add_column("Dossier", style="cyan", max_width=80)
    table3.add_column("Taille", justify="right")
    table3.add_column("Fichiers", justify="right")

    sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1][0], reverse=True)[:20]
    for dirname, (size, count) in sorted_dirs:
        table3.add_row(dirname, _format_size(size), f"{count:,}")
    console.print(table3)


def _format_size(size_bytes: int) -> str:
    for unit in ["o", "Ko", "Mo", "Go", "To"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} Po"
