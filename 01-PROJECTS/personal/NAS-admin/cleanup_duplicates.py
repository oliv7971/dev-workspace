"""
Suppression des doublons dans 21-CERENE.

Règles :
  - On GARDE de préférence le fichier dans 03-PROJETS
  - On SUPPRIME de préférence le fichier dans 10-SERVEURS
  - On NE TOUCHE PAS aux fichiers dans 13-DATAROOM
  - En cas d'égalité, on garde le chemin le plus court (moins profond)

Mode DRY-RUN par défaut. Lancer avec --execute pour supprimer.

Usage:
  python cleanup_duplicates.py              → Affiche ce qui serait supprimé
  python cleanup_duplicates.py --execute    → Supprime réellement
"""
import argparse
import os
import sqlite3
import time

from rich.console import Console
from rich.table import Table

console = Console()

DB_PATH = "./reports/inventory_cerene.db"

# Priorité de conservation (plus le score est bas, plus on veut garder)
KEEP_PRIORITY = {
    "03-PROJETS": 1,
    "02-AFFAIRES": 2,
    "04-ADMINISTRATIF": 3,
    "01-Fournisseurs": 4,
    "05-COMMERCIAL": 5,
    "21-DONNEES": 6,
    "07-PANORAMAS": 7,
    "22-DOCS": 8,
    "10-SERVEURS": 9,  # Supprimé en priorité
}

PROTECTED_DIRS = {"13-DATAROOM"}

BASE_PREFIX = r"\\Nas_travail\01-ds414-data\21-CERENE"


def get_top_dir(path):
    """Extrait le dossier de niveau 1 (ex: '03-PROJETS')."""
    rest = path[len(BASE_PREFIX) + 1:]
    return rest.split("\\")[0]


def pick_keeper(paths):
    """
    Parmi une liste de chemins, choisit lequel garder.
    Retourne (chemin_à_garder, [chemins_à_supprimer], [chemins_protégés])
    """
    protected = []
    candidates = []

    for p in paths:
        top = get_top_dir(p)
        if top in PROTECTED_DIRS:
            protected.append(p)
        else:
            score = KEEP_PRIORITY.get(top, 5)
            candidates.append((score, len(p), p))

    if not candidates:
        # Tous protégés, rien à faire
        return None, [], protected

    # Trier : score le plus bas = on garde, puis chemin le plus court
    candidates.sort()
    keeper = candidates[0][2]
    to_delete = [c[2] for c in candidates[1:]]

    return keeper, to_delete, protected


def main():
    parser = argparse.ArgumentParser(description="Suppression des doublons 21-CERENE")
    parser.add_argument("--execute", action="store_true", help="Supprimer réellement")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)

    groups = conn.execute(
        "SELECT hash_md5, size, file_count, wasted_space FROM duplicate_groups ORDER BY wasted_space DESC"
    ).fetchall()

    console.print(f"\n[bold]{'🗑️  SUPPRESSION' if args.execute else '📋 DRY-RUN (simulation)'}[/bold]")
    console.print(f"[dim]Groupes de doublons : {len(groups):,}[/dim]")
    console.print(f"[dim]Protégé : 13-DATAROOM (aucune suppression)[/dim]")
    console.print(f"[dim]Priorité de conservation : 03-PROJETS > autres > 10-SERVEURS[/dim]\n")

    total_deleted_files = 0
    total_deleted_size = 0
    total_kept = 0
    total_protected = 0
    errors = 0

    # Stats par dossier source
    from collections import defaultdict
    delete_by_dir = defaultdict(lambda: [0, 0])  # [count, size]

    # Détail des gros doublons
    big_actions = []

    for hash_md5, size, file_count, wasted in groups:
        files = conn.execute(
            "SELECT path FROM files WHERE hash_md5 = ? ORDER BY path", (hash_md5,)
        ).fetchall()
        paths = [p for (p,) in files]

        keeper, to_delete, protected = pick_keeper(paths)
        total_protected += len(protected)

        if not to_delete:
            total_kept += 1
            continue

        total_kept += 1  # le fichier gardé

        for filepath in to_delete:
            top = get_top_dir(filepath)
            delete_by_dir[top][0] += 1
            delete_by_dir[top][1] += size
            total_deleted_files += 1
            total_deleted_size += size

            # Logger les gros fichiers (> 100 Mo)
            if size > 100 * 1024 * 1024 and len(big_actions) < 40:
                short_keep = keeper[len(BASE_PREFIX) + 1:] if keeper else "?"
                short_del = filepath[len(BASE_PREFIX) + 1:]
                big_actions.append((size, short_del, short_keep))

            if args.execute:
                try:
                    os.remove(filepath)
                except Exception as e:
                    console.print(f"  [red]✗ {filepath}: {e}[/red]")
                    errors += 1

    # Affichage des gros fichiers
    if big_actions:
        console.print("[bold]Fichiers > 100 Mo à supprimer (top 40) :[/bold]")
        table = Table(show_header=True)
        table.add_column("Taille", justify="right")
        table.add_column("SUPPRIMÉ", style="red", max_width=80)
        table.add_column("GARDÉ", style="green", max_width=80)

        for sz, deleted, kept in sorted(big_actions, key=lambda x: -x[0]):
            size_str = f"{sz / 1024 / 1024:.0f} Mo" if sz < 1024**3 else f"{sz / 1024**3:.1f} Go"
            table.add_row(size_str, deleted, kept)
        console.print(table)

    # Résumé par dossier
    console.print(f"\n[bold]Suppressions par dossier :[/bold]")
    table2 = Table(show_header=True)
    table2.add_column("Dossier", style="cyan")
    table2.add_column("Fichiers supprimés", justify="right")
    table2.add_column("Espace libéré", justify="right", style="red")

    for d, (cnt, sz) in sorted(delete_by_dir.items(), key=lambda x: -x[1][1]):
        gb = sz / 1024**3
        table2.add_row(d, f"{cnt:,}", f"{gb:.1f} Go")
    console.print(table2)

    # Résumé global
    console.print(f"\n[bold]═══ RÉSUMÉ ═══[/bold]")
    console.print(f"  Fichiers à supprimer  : {total_deleted_files:,}")
    console.print(f"  [bold red]Espace à libérer      : {total_deleted_size / 1024**3:.1f} Go[/bold red]")
    console.print(f"  Fichiers protégés     : {total_protected:,} (DATAROOM)")
    if errors:
        console.print(f"  [red]Erreurs               : {errors}[/red]")

    if not args.execute:
        console.print(f"\n[bold cyan]  → Pour exécuter : python cleanup_duplicates.py --execute[/bold cyan]\n")
    else:
        console.print(f"\n[bold green]  ✅ Suppression terminée[/bold green]\n")

    conn.close()


if __name__ == "__main__":
    main()
