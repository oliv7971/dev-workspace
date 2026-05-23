"""
Analyse d'un dossier inventorié : doublons internes, statistiques, rapport.
Usage : python analyze_dossier.py <nom_dossier>
Exemple : python analyze_dossier.py "01-SFTRF"
"""
import os
import sys
import sqlite3
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
DB_DIR = os.path.abspath("inventaires")
REPORT_DIR = os.path.abspath("reports")
os.makedirs(REPORT_DIR, exist_ok=True)


def format_size(size: int) -> str:
    for unit in ["o", "Ko", "Mo", "Go", "To"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} Po"


def list_dossiers():
    files = [f for f in os.listdir(DB_DIR) if f.startswith("inventaire_") and f.endswith(".db")]
    noms = [f[len("inventaire_"):-3] for f in files]
    return sorted(noms)


def analyse(dossier: str):
    db_path = os.path.join(DB_DIR, f"inventaire_{dossier}.db")
    if not os.path.exists(db_path):
        console.print(f"[red]Base introuvable : {db_path}[/red]")
        console.print("\nDossiers disponibles :")
        for d in list_dossiers():
            console.print(f"  - {d}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)

    # --- Statistiques générales ---
    total_files, total_size = conn.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files").fetchone()
    files_hashed = conn.execute("SELECT COUNT(*) FROM files WHERE hash_md5 IS NOT NULL").fetchone()[0]

    console.print(f"\n[bold cyan]Dossier : {dossier}[/bold cyan]")
    console.print(f"  Fichiers indexés   : [bold]{total_files:,}[/bold]")
    console.print(f"  Taille totale      : [bold]{format_size(total_size)}[/bold]")
    console.print(f"  Fichiers avec hash : [bold]{files_hashed:,}[/bold] / {total_files:,}")

    # --- Doublons par hash ---
    console.print("\n[bold yellow]Recherche des doublons (même contenu)...[/bold yellow]")
    doublons = conn.execute("""
        SELECT hash_md5, COUNT(*) as nb, size, GROUP_CONCAT(path, '|||') as chemins
        FROM files
        WHERE hash_md5 IS NOT NULL
        GROUP BY hash_md5
        HAVING nb > 1
        ORDER BY (nb - 1) * size DESC
    """).fetchall()

    if not doublons:
        console.print("[green]  Aucun doublon détecté dans ce dossier.[/green]")
    else:
        espace_perdu = sum((nb - 1) * size for _, nb, size, _ in doublons)
        console.print(f"  [red]{len(doublons):,} groupes de doublons[/red] — espace récupérable : [bold red]{format_size(espace_perdu)}[/bold red]")

        table = Table(title="Top 20 doublons", box=box.SIMPLE, show_lines=True)
        table.add_column("Copies", style="red", width=6)
        table.add_column("Taille unitaire", width=14)
        table.add_column("Espace perdu", style="bold red", width=14)
        table.add_column("Fichiers", style="dim")

        for hash_md5, nb, size, chemins in doublons[:20]:
            fichiers = chemins.split("|||")
            noms = "\n".join(os.path.basename(p) for p in fichiers)
            table.add_row(str(nb), format_size(size), format_size((nb - 1) * size), noms)

        console.print(table)

        # Export rapport texte
        report_path = os.path.join(REPORT_DIR, f"doublons_{dossier}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"RAPPORT DOUBLONS : {dossier}\n")
            f.write(f"Fichiers indexés : {total_files:,}\n")
            f.write(f"Taille totale    : {format_size(total_size)}\n")
            f.write(f"Groupes doublons : {len(doublons):,}\n")
            f.write(f"Espace perdu     : {format_size(espace_perdu)}\n\n")
            f.write("=" * 100 + "\n")
            for hash_md5, nb, size, chemins in doublons:
                f.write(f"\n[{nb} copies - {format_size(size)} chacun - perte: {format_size((nb-1)*size)}]\n")
                for chemin in chemins.split("|||"):
                    f.write(f"  {chemin}\n")
        console.print(f"\n[green]Rapport exporté : {report_path}[/green]")

    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[bold]Usage:[/bold] python analyze_dossier.py <nom_dossier>")
        console.print("\nDossiers disponibles :")
        for d in list_dossiers():
            console.print(f"  - {d}")
        sys.exit(0)

    dossier = " ".join(sys.argv[1:])
    analyse(dossier)
