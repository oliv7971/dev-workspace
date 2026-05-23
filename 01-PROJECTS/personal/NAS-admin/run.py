"""
NAS Admin - Point d'entrée CLI

Commandes :
  python run.py scan           → Inventaire rapide (sans hash)
  python run.py scan --hash    → Inventaire complet avec hash
  python run.py summary        → Résumé de l'inventaire existant
  python run.py duplicates     → Détection des doublons
  python run.py export-csv     → Exporter les doublons en CSV
"""
import argparse
import sys
import time

from nas_admin.config import load_config
from nas_admin.inventory import init_db, scan_directory, print_summary
from nas_admin.duplicates import find_duplicates, export_duplicates_csv

from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="NAS Admin - Inventaire et gestion de NAS Synology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python run.py scan              Scan rapide sans calcul de hash
  python run.py scan --hash       Scan complet avec hash (long sur 10 To)
  python run.py summary           Voir le résumé de l'inventaire
  python run.py duplicates        Trouver les doublons (calcule les hash si besoin)
  python run.py export-csv        Exporter les doublons dans un CSV
        """,
    )
    parser.add_argument("command", choices=["scan", "summary", "duplicates", "export-csv"],
                        help="Commande à exécuter")
    parser.add_argument("--hash", action="store_true",
                        help="Calculer les hash pendant le scan (plus lent)")
    parser.add_argument("--config", default=None,
                        help="Chemin vers le fichier de configuration")
    parser.add_argument("--rehash", action="store_true",
                        help="Recalculer tous les hash (même ceux existants)")

    args = parser.parse_args()
    config = load_config(args.config)

    nas_path = config["nas"]["path"]
    db_path = config["output"]["inventory_db"]
    reports_dir = config["output"]["reports_dir"]

    console.print(f"[bold]NAS Admin[/bold] — {config['nas']['name']}")
    console.print(f"[dim]Cible : {nas_path}[/dim]")

    start = time.time()

    if args.command == "scan":
        db_conn = init_db(db_path)
        scan_directory(nas_path, config, db_conn, compute_hashes=args.hash)
        print_summary(db_conn)
        db_conn.close()

    elif args.command == "summary":
        db_conn = init_db(db_path)
        print_summary(db_conn)
        db_conn.close()

    elif args.command == "duplicates":
        db_conn = init_db(db_path)
        # Si pas encore de scan, prévenir
        count = db_conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        if count == 0:
            console.print("[red]❌ Base vide ! Lance d'abord : python run.py scan[/red]")
            sys.exit(1)
        find_duplicates(db_conn, config, recompute_hashes=args.rehash)
        db_conn.close()

    elif args.command == "export-csv":
        db_conn = init_db(db_path)
        try:
            db_conn.execute("SELECT 1 FROM duplicate_groups LIMIT 1")
        except Exception:
            console.print("[red]❌ Pas de doublons en base ! Lance d'abord : python run.py duplicates[/red]")
            sys.exit(1)
        csv_path = f"{reports_dir}/doublons_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        export_duplicates_csv(db_conn, csv_path)
        db_conn.close()

    elapsed = time.time() - start
    console.print(f"\n[dim]Terminé en {elapsed:.1f}s[/dim]")


if __name__ == "__main__":
    main()
