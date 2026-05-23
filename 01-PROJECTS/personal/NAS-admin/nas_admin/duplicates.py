"""
Détection de doublons - Trouve les fichiers identiques sur le NAS.

Stratégie en 2 passes pour la performance sur 10 To :
  1. Grouper par taille (instantané, élimine ~90% des fichiers)
  2. Calculer les hash MD5 uniquement sur les candidats (même taille)
"""
import hashlib
import os
import sqlite3
import time

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from .inventory import _format_size, compute_hash

console = Console()


def find_duplicates(db_conn: sqlite3.Connection, config: dict, recompute_hashes: bool = False):
    """Détecte les doublons dans la base d'inventaire."""

    min_size = config.get("scan", {}).get("min_size_for_duplicates", 1024)

    console.print("\n[bold blue]🔍 Détection des doublons[/bold blue]\n")

    # Étape 1 : Trouver les tailles qui apparaissent plus d'une fois
    console.print("[dim]Étape 1 : Groupement par taille...[/dim]")
    size_groups = db_conn.execute(
        """SELECT size, COUNT(*) as cnt
           FROM files
           WHERE size >= ?
           GROUP BY size
           HAVING cnt > 1
           ORDER BY size DESC""",
        (min_size,),
    ).fetchall()

    total_candidates = sum(cnt for _, cnt in size_groups)
    console.print(f"  {len(size_groups):,} groupes de taille identique ({total_candidates:,} fichiers candidats)")

    if not size_groups:
        console.print("[green]  Aucun doublon potentiel trouvé ![/green]")
        return

    # Étape 2 : Calculer les hash pour les candidats
    console.print("[dim]Étape 2 : Calcul des hash (uniquement sur les candidats)...[/dim]")

    hashed_count = 0
    error_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Hashing", total=total_candidates)

        for size, _ in size_groups:
            files = db_conn.execute(
                "SELECT id, path, hash_md5 FROM files WHERE size = ?", (size,)
            ).fetchall()

            for file_id, filepath, existing_hash in files:
                if existing_hash and not recompute_hashes:
                    progress.advance(task)
                    continue

                file_hash = compute_hash(filepath)
                if file_hash:
                    db_conn.execute(
                        "UPDATE files SET hash_md5 = ? WHERE id = ?", (file_hash, file_id)
                    )
                    hashed_count += 1
                else:
                    error_count += 1

                progress.advance(task)

            db_conn.commit()

    console.print(f"  Hash calculés : {hashed_count:,}")
    if error_count:
        console.print(f"  [yellow]Erreurs : {error_count:,}[/yellow]")

    # Étape 3 : Identifier les groupes de doublons
    console.print("[dim]Étape 3 : Identification des doublons...[/dim]")

    _create_duplicates_table(db_conn)
    _generate_duplicates_report(db_conn)


def _create_duplicates_table(db_conn: sqlite3.Connection):
    """Crée une vue/table des doublons dans la base."""
    db_conn.executescript("""
        DROP TABLE IF EXISTS duplicate_groups;
        CREATE TABLE duplicate_groups AS
        SELECT
            hash_md5,
            size,
            COUNT(*) as file_count,
            COUNT(*) * size - size as wasted_space
        FROM files
        WHERE hash_md5 IS NOT NULL
        GROUP BY hash_md5
        HAVING COUNT(*) > 1
        ORDER BY wasted_space DESC;

        CREATE INDEX IF NOT EXISTS idx_dup_hash ON duplicate_groups(hash_md5);
    """)
    db_conn.commit()


def _generate_duplicates_report(db_conn: sqlite3.Connection):
    """Affiche le rapport de doublons."""
    stats = db_conn.execute(
        """SELECT COUNT(*), SUM(file_count), SUM(wasted_space)
           FROM duplicate_groups"""
    ).fetchone()

    group_count, total_dup_files, total_wasted = stats[0] or 0, stats[1] or 0, stats[2] or 0

    console.print(f"\n[bold]═══ RAPPORT DE DOUBLONS ═══[/bold]\n")
    console.print(f"  Groupes de doublons : {group_count:,}")
    console.print(f"  Fichiers concernés  : {total_dup_files:,}")
    console.print(f"  [bold red]Espace gaspillé       : {_format_size(total_wasted)}[/bold red]")

    if group_count == 0:
        console.print("\n[green]🎉 Aucun doublon trouvé ![/green]")
        return

    # Top 30 groupes par espace gaspillé
    console.print(f"\n[bold]Top 30 groupes de doublons (par espace gaspillé) :[/bold]")
    table = Table(show_header=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Taille fichier", justify="right")
    table.add_column("Copies", justify="right")
    table.add_column("Espace gaspillé", justify="right", style="red")
    table.add_column("Exemple de fichier", max_width=90)

    top_groups = db_conn.execute(
        """SELECT dg.hash_md5, dg.size, dg.file_count, dg.wasted_space
           FROM duplicate_groups dg
           ORDER BY dg.wasted_space DESC
           LIMIT 30"""
    ).fetchall()

    for i, (hash_md5, size, count, wasted) in enumerate(top_groups, 1):
        example = db_conn.execute(
            "SELECT path FROM files WHERE hash_md5 = ? LIMIT 1", (hash_md5,)
        ).fetchone()
        example_path = example[0] if example else "?"
        # Tronquer le chemin si trop long
        if len(example_path) > 90:
            example_path = "..." + example_path[-87:]
        table.add_row(
            str(i),
            _format_size(size),
            str(count),
            _format_size(wasted),
            example_path,
        )

    console.print(table)


def export_duplicates_csv(db_conn: sqlite3.Connection, output_path: str):
    """Exporte tous les doublons dans un fichier CSV pour analyse dans Excel."""
    import csv

    groups = db_conn.execute(
        "SELECT hash_md5, size, file_count, wasted_space FROM duplicate_groups ORDER BY wasted_space DESC"
    ).fetchall()

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Groupe", "Hash MD5", "Taille (octets)", "Taille (lisible)",
            "Nb copies", "Espace gaspillé", "Chemin du fichier"
        ])

        for group_num, (hash_md5, size, count, wasted) in enumerate(groups, 1):
            files = db_conn.execute(
                "SELECT path FROM files WHERE hash_md5 = ? ORDER BY path", (hash_md5,)
            ).fetchall()
            for filepath, in files:
                writer.writerow([
                    group_num, hash_md5, size, _format_size(size),
                    count, _format_size(wasted), filepath
                ])

    console.print(f"\n[green]📄 Export CSV : {output_path}[/green]")
    console.print(f"  ({len(groups):,} groupes de doublons exportés)")
