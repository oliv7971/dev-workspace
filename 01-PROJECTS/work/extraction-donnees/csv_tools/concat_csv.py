#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programme de concaténation de fichiers CSV

Fonctionnalités :
- Concaténation simple : empiler plusieurs CSV
- Gestion des en-têtes (conserver, ignorer, harmoniser)
- Filtrage par motif de nom de fichier
- Support de différents encodages et séparateurs
- Options de tri et de dédoublonnage

Exemples d'usage :
    py concat_csv.py --input "*.csv" --output combined.csv
    py concat_csv.py --input "data/*.csv" --output result.csv --no-header
    py concat_csv.py --input "export_*.csv" --output merged.csv --encoding utf-8
    py concat_csv.py --input "*.csv" --output final.csv --sort-by "Date" --dedupe
"""

import argparse
import pandas as pd
import glob
import os
from pathlib import Path
import logging
import sys
from typing import List, Optional

# Configuration du logging
LOG_FORMAT = "%(levelname)s - %(message)s"

class CSVConcatenator:
    """Classe pour gérer la concaténation de fichiers CSV"""
    
    def __init__(self, encoding='utf-8', separator=',', verbose=False):
        self.encoding = encoding
        self.separator = separator
        self.verbose = verbose
        
        # Configuration du logging
        level = logging.INFO if verbose else logging.WARNING
        logging.basicConfig(level=level, format=LOG_FORMAT)
        
    def find_csv_files(self, pattern: str, workdir: Optional[str] = None) -> List[Path]:
        """Trouve tous les fichiers CSV correspondant au motif"""
        # Changer de répertoire si spécifié
        original_dir = None
        if workdir:
            original_dir = os.getcwd()
            workdir_path = Path(workdir)
            if not workdir_path.exists():
                logging.error(f"Le répertoire de travail n'existe pas : {workdir}")
                return []
            os.chdir(workdir_path)
            logging.info(f"Répertoire de travail : {workdir_path.absolute()}")
        
        try:
            files = glob.glob(pattern)
            csv_files = [Path(f) for f in files if f.lower().endswith('.csv')]
            
            # Convertir en chemins absolus si on a changé de répertoire
            if workdir:
                csv_files = [f.absolute() for f in csv_files]
            
            if not csv_files:
                current_dir = workdir if workdir else "répertoire courant"
                logging.warning(f"Aucun fichier CSV trouvé avec le motif '{pattern}' dans {current_dir}")
                return []
                
            logging.info(f"Fichiers trouvés : {len(csv_files)}")
            for f in sorted(csv_files):
                logging.info(f"  - {f}")
                
            return sorted(csv_files)
        
        finally:
            # Revenir au répertoire original
            if original_dir:
                os.chdir(original_dir)
    
    def read_csv_file(self, file_path: Path, has_header: bool = True) -> Optional[pd.DataFrame]:
        """Lit un fichier CSV avec gestion d'erreurs"""
        try:
            if has_header:
                df = pd.read_csv(file_path, encoding=self.encoding, sep=self.separator)
            else:
                df = pd.read_csv(file_path, encoding=self.encoding, sep=self.separator, header=None)
            
            logging.info(f"Lu {file_path.name} : {len(df)} lignes, {len(df.columns)} colonnes")
            return df
            
        except Exception as e:
            logging.error(f"Erreur lors de la lecture de {file_path} : {e}")
            return None
    
    def concatenate_files(self, file_pattern: str, output_file: str, 
                         has_header: bool = True, sort_by: Optional[str] = None,
                         dedupe: bool = False, add_source_column: bool = False,
                         workdir: Optional[str] = None) -> bool:
        """Concatène les fichiers CSV"""
        
        # Trouver les fichiers
        csv_files = self.find_csv_files(file_pattern, workdir)
        if not csv_files:
            return False
        
        dataframes = []
        
        # Lire chaque fichier
        for file_path in csv_files:
            df = self.read_csv_file(file_path, has_header)
            if df is not None:
                # Ajouter une colonne source si demandé
                if add_source_column:
                    df['source_file'] = file_path.name
                dataframes.append(df)
        
        if not dataframes:
            logging.error("Aucun fichier n'a pu être lu")
            return False
        
        # Concaténation
        try:
            logging.info("Concaténation en cours...")
            combined_df = pd.concat(dataframes, ignore_index=True, sort=False)
            logging.info(f"Résultat : {len(combined_df)} lignes, {len(combined_df.columns)} colonnes")
            
            # Tri si demandé
            if sort_by and sort_by in combined_df.columns:
                logging.info(f"Tri par la colonne '{sort_by}'")
                combined_df = combined_df.sort_values(by=sort_by)
            
            # Dédoublonnage si demandé
            if dedupe:
                before_count = len(combined_df)
                combined_df = combined_df.drop_duplicates()
                after_count = len(combined_df)
                logging.info(f"Dédoublonnage : {before_count - after_count} lignes supprimées")
            
            # Sauvegarde
            output_path = Path(output_file)
            combined_df.to_csv(output_path, index=False, encoding=self.encoding, sep=self.separator)
            logging.info(f"Fichier sauvegardé : {output_path}")
            logging.info(f"Taille finale : {len(combined_df)} lignes")
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors de la concaténation : {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Concaténation de fichiers CSV")
    
    # Arguments obligatoires
    parser.add_argument("--input", "-i", required=True,
                       help="Motif des fichiers d'entrée (ex: '*.csv', 'data/*.csv')")
    parser.add_argument("--output", "-o", required=True,
                       help="Fichier de sortie")
    
    # Répertoire de travail
    parser.add_argument("--workdir", "-w",
                       help="Répertoire où chercher les fichiers (défaut: répertoire courant)")
    
    # Options de lecture
    parser.add_argument("--encoding", default="utf-8",
                       help="Encodage des fichiers (défaut: utf-8)")
    parser.add_argument("--separator", "-s", default=",",
                       help="Séparateur CSV (défaut: virgule)")
    parser.add_argument("--no-header", action="store_true",
                       help="Les fichiers n'ont pas d'en-tête")
    
    # Options de traitement
    parser.add_argument("--sort-by", 
                       help="Nom de la colonne pour trier le résultat")
    parser.add_argument("--dedupe", action="store_true",
                       help="Supprimer les lignes dupliquées")
    parser.add_argument("--add-source", action="store_true",
                       help="Ajouter une colonne avec le nom du fichier source")
    
    # Options d'affichage
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Mode verbeux")
    
    args = parser.parse_args()
    
    # Vérification du motif d'entrée
    if not any(c in args.input for c in ['*', '?', '[']):
        # Si pas de caractères génériques, vérifier que le fichier existe
        if not Path(args.input).exists():
            print(f"Erreur : Le fichier {args.input} n'existe pas")
            sys.exit(1)
    
    # Création du concatenateur
    concatenator = CSVConcatenator(
        encoding=args.encoding,
        separator=args.separator,
        verbose=args.verbose
    )
    
    # Concaténation
    success = concatenator.concatenate_files(
        file_pattern=args.input,
        output_file=args.output,
        has_header=not args.no_header,
        sort_by=args.sort_by,
        dedupe=args.dedupe,
        add_source_column=args.add_source,
        workdir=args.workdir
    )
    
    if success:
        print(f"✓ Concaténation réussie : {args.output}")
    else:
        print("✗ Échec de la concaténation")
        sys.exit(1)

if __name__ == "__main__":
    main()