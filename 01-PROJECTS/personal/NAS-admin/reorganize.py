"""
Script de réorganisation de 11-TSGT\_A CLASSER

Mode DRY-RUN par défaut : affiche ce qui sera fait sans rien toucher.
Lancer avec --execute pour réellement déplacer les fichiers.

Usage:
  python reorganize.py              → Affiche le plan (dry-run)
  python reorganize.py --execute    → Exécute les déplacements
"""
import os
import shutil
import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

BASE = r"\\Nas_travail\01-ds414-data\11-TSGT"
AC = os.path.join(BASE, "_A CLASSER")

# ─── PLAN DE REORGANISATION ─────────────────────────────────────────
# Chaque entrée : (source relative dans _A CLASSER, destination relative dans 11-TSGT)
# Si la source est un dossier, tout le contenu est déplacé.

MOVES = [
    # ── 12-TP : Travaux Pratiques ──
    ("exercices",           r"12-TP\exercices"),
    ("TSGT-2011-2012",      r"12-TP\TSGT-2011-2012"),
    ("releves_batiment",    r"12-TP\releves-batiment"),
    ("routier-covadis",     r"12-TP\routier-covadis"),
    ("route",               r"12-TP\routier-covadis\route"),
    ("sig",                 r"12-TP\sig"),
    ("GPStestcalcul2012",   r"12-TP\GPS-calcul-2012"),
    ("stages",              r"12-TP\stages"),

    # ── 13-DONNEES-COURS : contenu pédagogique (dumps clé USB, data) ──
    ("cle_20120412",        r"13-DONNEES-COURS\cle_20120412"),
    ("cle_20120606",        r"13-DONNEES-COURS\cle_20120606"),
    ("data_tsgt_2011-2012", r"13-DONNEES-COURS\data_tsgt_2011-2012"),
    ("tsgt",                r"13-DONNEES-COURS\tsgt"),
    ("exam",                r"13-DONNEES-COURS\exam"),

    # ── 11-COURS : formations ──
    ("afpa017",             r"11-COURS\formations\afpa017"),
    ("revisions_cnfpt",     r"11-COURS\formations\revisions_cnfpt"),

    # ── 21-DOCS : documentation ──
    ("DOCS",                r"21-DOCS\divers\DOCS"),
    ("docs2",               r"21-DOCS\divers\docs2"),
    ("docs7",               r"21-DOCS\divers\docs7"),
    ("MESDOCS",             r"21-DOCS\divers\MESDOCS"),
    ("images",              r"21-DOCS\divers\images"),
    ("fiches",              r"21-DOCS\modeles\fiches"),
    ("exemples_plans",      r"21-DOCS\modeles\exemples_plans"),
    ("gabarits",            r"21-DOCS\modeles\gabarits"),
    ("modeles-fichiers",    r"21-DOCS\modeles\modeles-fichiers"),
    ("Profils Types",       r"21-DOCS\modeles\Profils Types"),
    ("leve_code",           r"21-DOCS\codes-leve"),
    ("ressources",          r"21-DOCS\ressources"),

    # ── 31-SOFTS : logiciels ──
    ("leica",               r"31-SOFTS\leica"),
    ("data",                r"31-SOFTS\data-cyclone"),
    ("install",             r"31-SOFTS\install-aclasser"),

    # ── 41-CAPTURES : captures d'écran et photos ──
    ("PrintScreen Files",   r"41-CAPTURES\PrintScreen Files"),
    ("100OLYMP",            r"41-CAPTURES\100OLYMP"),

    # ── 01-ADMINISTRATIF ──
    ("rapports",            r"01-ADMINISTRATIF\rapports"),

    # ── Fichiers en vrac à la racine de _A CLASSER ──
    # TP / exercices
    ("TP7-CHEMINEMENT_OB.dwg",         r"12-TP\divers\TP7-CHEMINEMENT_OB.dwg"),
    ("PLAN8APPART.dwg",                r"12-TP\divers\PLAN8APPART.dwg"),
    ("new block.dwg",                  r"12-TP\divers\new block.dwg"),
    ("plan_cite_sotenot_isle_les_villenoy.dwg",  r"12-TP\divers\plan_cite_sotenot_isle_les_villenoy.dwg"),
    ("plan_cite_sotenot_isle_les_villenoy2.dwg", r"12-TP\divers\plan_cite_sotenot_isle_les_villenoy2.dwg"),
    ("ruedelaglaisiere.dwg",           r"12-TP\divers\ruedelaglaisiere.dwg"),
    ("rapport_tp22.doc",               r"12-TP\divers\rapport_tp22.doc"),
    ("tp19-2.pdf",                     r"12-TP\divers\tp19-2.pdf"),
    ("feuille_calcul_polygo-20111108-pour-tp-corps_de_rue.ods", r"12-TP\divers\feuille_calcul_polygo-20111108-pour-tp-corps_de_rue.ods"),
    ("releve_cave_herons_20111210.ods", r"12-TP\divers\releve_cave_herons_20111210.ods"),
    ("releve_cave_herons_20111210-2.ods", r"12-TP\divers\releve_cave_herons_20111210-2.ods"),
    ("correction niveau apparent sur les distances.xls", r"12-TP\divers\correction niveau apparent sur les distances.xls"),
    ("Carnet de levé.xls",             r"12-TP\divers\Carnet de levé.xls"),

    # Cours / docs techniques
    ("ITSEOA - Fas4-TOPOMETRIE - SETRA - FR.pdf", r"21-DOCS\divers\ITSEOA - Fas4-TOPOMETRIE - SETRA - FR.pdf"),
    ("corrige-bts-batiment-2007-topographie.pdf",  r"15-Annales BTS GT\corrige-bts-batiment-2007-topographie.pdf"),
    ("Tasa Fiche 002 - Les blocs AutoCAD.pdf",    r"21-DOCS\divers\Tasa Fiche 002 - Les blocs AutoCAD.pdf"),
    ("guide_assainissement.pdf",       r"21-DOCS\divers\guide_assainissement.pdf"),
    ("notes_autocad.txt",              r"21-DOCS\divers\notes_autocad.txt"),
    ("ChemiseVerte.pdf",               r"21-DOCS\modeles\ChemiseVerte.pdf"),
    ("ChemiseVerteSimple.PDF",         r"21-DOCS\modeles\ChemiseVerteSimple.PDF"),
    ("sauvegarde_données_terrain.pdf", r"21-DOCS\divers\sauvegarde_données_terrain.pdf"),

    # SIG
    ("Initiation_ArcGis9.pdf",        r"12-TP\sig\Initiation_ArcGis9.pdf"),
    ("TD_arcgis_etudiants.pdf",        r"12-TP\sig\TD_arcgis_etudiants.pdf"),
    ("SIG definition.pdf",             r"12-TP\sig\SIG definition.pdf"),
    ("sig.pdf",                        r"12-TP\sig\sig.pdf"),
    ("sig1.pdf",                       r"12-TP\sig\sig1.pdf"),
    ("qgis-1.6.0_user_guide_fr.pdf",  r"12-TP\sig\qgis-1.6.0_user_guide_fr.pdf"),

    # Stages
    ("lettre_stage_tsgt_hyparc.pdf",   r"12-TP\stages\lettre_stage_tsgt_hyparc.pdf"),

    # Photos
    ("c-vandroux.JPG",                 r"41-CAPTURES\photos\c-vandroux.JPG"),
    ("d-gaudillere.JPG",               r"41-CAPTURES\photos\d-gaudillere.JPG"),
    ("d-soulage.JPG",                  r"41-CAPTURES\photos\d-soulage.JPG"),
    ("im012.jpg",                      r"41-CAPTURES\photos\im012.jpg"),

    # Softs / installeurs
    ("CycloneSetup561.exe",            r"31-SOFTS\data-cyclone\CycloneSetup561.exe"),
    ("SetupDWGTrueView2013_32bit.exe", r"31-SOFTS\SetupDWGTrueView2013_32bit.exe"),

    # Archive données
    ("data_tsgt_2011-2012.zip",        r"13-DONNEES-COURS\data_tsgt_2011-2012.zip"),

    # Poubelle (Thumbs.db)
    # ("Thumbs.db",                    → à supprimer manuellement)
]


def count_items(path):
    """Compte fichiers et taille dans un dossier."""
    if os.path.isfile(path):
        return 1, os.path.getsize(path)
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(path):
        total_files += len(files)
        for f in files:
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total_files, total_size


def format_size(size_bytes):
    for unit in ["o", "Ko", "Mo", "Go"]:
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} To"


def main():
    parser = argparse.ArgumentParser(description="Réorganisation de _A CLASSER")
    parser.add_argument("--execute", action="store_true",
                        help="Exécuter les déplacements (sinon dry-run)")
    args = parser.parse_args()

    console.print(f"\n[bold]{'🔧 EXÉCUTION' if args.execute else '📋 DRY-RUN (simulation)'}[/bold]")
    console.print(f"[dim]Source : {AC}[/dim]")
    console.print(f"[dim]Cible  : {BASE}[/dim]\n")

    table = Table(show_header=True, title="Plan de déplacement")
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Source (_A CLASSER\\...)", max_width=35)
    table.add_column("→ Destination (11-TSGT\\...)", max_width=45, style="green")
    table.add_column("Fichiers", justify="right")
    table.add_column("Taille", justify="right")
    table.add_column("Statut", justify="center")

    total_moved_files = 0
    total_moved_size = 0
    results = []

    for i, (src_rel, dst_rel) in enumerate(MOVES, 1):
        src = os.path.join(AC, src_rel)
        dst = os.path.join(BASE, dst_rel)

        if not os.path.exists(src):
            table.add_row(str(i), src_rel, dst_rel, "-", "-", "[yellow]ABSENT[/yellow]")
            results.append((src_rel, dst_rel, "absent"))
            continue

        nfiles, size = count_items(src)
        total_moved_files += nfiles
        total_moved_size += size

        if os.path.exists(dst):
            table.add_row(str(i), src_rel, dst_rel, str(nfiles), format_size(size), "[red]CONFLIT[/red]")
            results.append((src_rel, dst_rel, "conflict"))
        else:
            table.add_row(str(i), src_rel, dst_rel, str(nfiles), format_size(size), "[green]OK[/green]")
            results.append((src_rel, dst_rel, "ok"))

    console.print(table)
    console.print(f"\n  Total à déplacer : {total_moved_files:,} fichiers, {format_size(total_moved_size)}")

    # Fichiers restants à la racine de _A CLASSER (non couverts par le plan)
    planned_sources = set(src for src, _ in MOVES)
    remaining = []
    if os.path.exists(AC):
        for item in os.listdir(AC):
            if item not in planned_sources:
                remaining.append(item)

    if remaining:
        console.print(f"\n[yellow]  ⚠ {len(remaining)} éléments NON couverts par le plan :[/yellow]")
        for item in sorted(remaining):
            full = os.path.join(AC, item)
            if os.path.isdir(full):
                nf, sz = count_items(full)
                console.print(f"    📁 {item}/ ({nf} fichiers, {format_size(sz)})")
            else:
                sz = os.path.getsize(full)
                console.print(f"    📄 {item} ({format_size(sz)})")

    conflicts = [r for r in results if r[2] == "conflict"]
    if conflicts:
        console.print(f"\n[red]  ⚠ {len(conflicts)} conflits (destination existe déjà) — ils seront ignorés[/red]")

    if not args.execute:
        console.print(f"\n[bold cyan]  → Pour exécuter : python reorganize.py --execute[/bold cyan]\n")
        return

    # ─── EXÉCUTION ───
    console.print(f"\n[bold yellow]Déplacement en cours...[/bold yellow]")
    success = 0
    errors = 0

    for src_rel, dst_rel, status in results:
        if status != "ok":
            continue

        src = os.path.join(AC, src_rel)
        dst = os.path.join(BASE, dst_rel)

        try:
            # Créer le dossier parent de la destination
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            # Déplacer
            shutil.move(src, dst)
            console.print(f"  [green]✓[/green] {src_rel} → {dst_rel}")
            success += 1
        except Exception as e:
            console.print(f"  [red]✗[/red] {src_rel} : {e}")
            errors += 1

    console.print(f"\n[bold green]  ✅ {success} déplacements réussis[/bold green]")
    if errors:
        console.print(f"[bold red]  ❌ {errors} erreurs[/bold red]")

    # Vérifier si _A CLASSER est vide maintenant
    if os.path.exists(AC):
        remaining_after = os.listdir(AC)
        if not remaining_after:
            console.print(f"\n  [green]_A CLASSER est vide ! Tu peux le supprimer.[/green]")
        else:
            console.print(f"\n  [yellow]{len(remaining_after)} éléments restants dans _A CLASSER[/yellow]")


if __name__ == "__main__":
    main()
