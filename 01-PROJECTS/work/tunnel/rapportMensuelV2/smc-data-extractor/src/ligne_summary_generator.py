#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC Ligne Summary Generator - Générateur de récapitulatifs en ligne
Génère des récapitulatifs en ligne pour chaque élément mesuré (convergences et déplacements)
Format: périodique et cumulé sur une seule ligne par fichier/type
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import os
import sys

# Ajouter le répertoire parent pour importer le correcteur
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from metric_name_corrector import MetricNameCorrector
    CORRECTOR_AVAILABLE = True
except ImportError:
    print("⚠️ Module metric_name_corrector non trouvé, correction automatique désactivée")
    CORRECTOR_AVAILABLE = False

class LigneSummaryGenerator:
    """Générateur de récapitulatifs en ligne pour les données SMC"""
    
    def __init__(self, csv_folder: str, output_folder: str, month: str):
        self.csv_folder = Path(csv_folder)
        self.output_folder = Path(output_folder)
        self.month = month
        
        # Créer le dossier de sortie s'il n'existe pas
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
    def load_csv_data(self) -> Dict[str, pd.DataFrame]:
        """Charge les données depuis les fichiers CSV avec correction automatique des noms"""
        data = {}
        
        csv_files = {
            'convergences': 'Convergences_SMC.csv',
            'deplacements': 'Deplacements_SMC.csv'
        }
        
        # Initialiser le correcteur si disponible
        corrector = MetricNameCorrector() if CORRECTOR_AVAILABLE else None
        
        for key, filename in csv_files.items():
            file_path = self.csv_folder / filename
            if file_path.exists():
                try:
                    # Lire le fichier avec le séparateur point-virgule (par défaut pour nos fichiers)
                    df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
                    
                    # Vérifier si le séparateur est correct en regardant si on a les bonnes colonnes
                    expected_columns = ['galerie', 'section', 'metric']
                    if not all(col in df.columns for col in expected_columns):
                        # Si les colonnes attendues ne sont pas là, essayer avec la virgule
                        df = pd.read_csv(file_path, sep=',', encoding='utf-8-sig')
                    
                    # Nettoyer les lignes corrompues avant traitement
                    df = self._clean_corrupted_lines(df)
                    
                    # Appliquer la correction automatique des noms de métriques
                    if corrector and 'metric' in df.columns:
                        print(f"🔧 Correction automatique des métriques dans {filename}...")
                        df = corrector.correct_dataframe_metrics(df)
                    
                    data[key] = df
                    print(f"✅ Chargé: {filename} ({len(df)} lignes)")
                except Exception as e:
                    print(f"❌ Erreur lecture {filename}: {e}")
                    data[key] = pd.DataFrame()
            else:
                print(f"⚠️ Fichier manquant: {filename}")
                data[key] = pd.DataFrame()
        
        return data
    
    def _clean_corrupted_lines(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les lignes corrompues dans le DataFrame"""
        if df.empty or 'galerie' not in df.columns or 'section' not in df.columns or 'metric' not in df.columns:
            return df
        
        # Filtrer les lignes où galerie est un nombre (lignes corrompues)
        import re
        numeric_pattern = r'^-?\d+\.?\d*$'
        
        # Identifier les lignes corrompues
        corrupted_mask = df['galerie'].astype(str).str.match(numeric_pattern, na=False)
        
        corrupted_count = corrupted_mask.sum()
        if corrupted_count > 0:
            print(f"🧹 Suppression de {corrupted_count} lignes corrompues")
            
            # Garder seulement les lignes non corrompues
            df_clean = df[~corrupted_mask].copy()
            
            return df_clean
        
        return df
    
    def generate_ligne_summary_convergences(self, df: pd.DataFrame) -> List[str]:
        """Génère les récapitulatifs en ligne pour les convergences"""
        if df.empty:
            return ["Aucune donnée de convergences disponible"]
        
        summary_lines = []
        
        # Grouper par fichier source (galerie + section)
        grouped = df.groupby(['galerie', 'section', 'source_file'])
        
        for (galerie, section, source_file), group in grouped:
            # Identifier TOUTES les métriques disponibles pour ce groupe
            available_metrics = set(group['metric'].unique())
            
            # Ordre préféré des métriques, mais on affiche toutes celles disponibles
            preferred_order = ['BG', 'IG', 'HG', 'HD', 'ID', 'BD', 'LH', 'LI', 'LB']
            
            # Commencer par l'ordre préféré, puis ajouter les autres
            metric_order = []
            for metric in preferred_order:
                if metric in available_metrics:
                    metric_order.append(metric)
                    available_metrics.remove(metric)
            
            # Ajouter les métriques restantes (triées alphabétiquement)
            remaining_metrics = sorted([m for m in available_metrics 
                                      if not m.startswith('Distance au front')])
            metric_order.extend(remaining_metrics)
            
            # Données périodiques et cumulées
            periodic_values = []
            cumulative_values = []
            
            for metric in metric_order:
                metric_data = group[group['metric'] == metric]
                if not metric_data.empty:
                    periodic = metric_data.iloc[0]['periodic_mm']
                    cumulative = metric_data.iloc[0]['cumulative_mm']
                    
                    # Formatage des valeurs
                    if pd.isna(periodic):
                        periodic_str = "N/A"
                    else:
                        periodic_str = f"{periodic:.2f}"
                    
                    if pd.isna(cumulative):
                        cumulative_str = "N/A"
                    else:
                        cumulative_str = f"{cumulative:.2f}"
                    
                    periodic_values.append(f"{metric}:{periodic_str}")
                    cumulative_values.append(f"{metric}:{cumulative_str}")
                else:
                    periodic_values.append(f"{metric}:N/A")
                    cumulative_values.append(f"{metric}:N/A")
            
            # Construire les lignes
            base_name = f"{galerie} {section}"
            
            periodic_line = f"{base_name} (Convergences - périodique)"
            periodic_line += f"\n  {' | '.join(periodic_values)}"
            
            cumulative_line = f"{base_name} (Convergences - cumulé)"
            cumulative_line += f"\n  {' | '.join(cumulative_values)}"
            
            summary_lines.append(periodic_line)
            summary_lines.append(cumulative_line)
            summary_lines.append("")  # Ligne vide
        
        return summary_lines
    
    def generate_ligne_summary_deplacements(self, df: pd.DataFrame) -> List[str]:
        """Génère les récapitulatifs en ligne pour les déplacements"""
        if df.empty:
            return ["Aucune donnée de déplacements disponible"]
        
        summary_lines = []
        
        # Grouper par fichier source (galerie + section)
        grouped = df.groupby(['galerie', 'section', 'source_file'])
        
        for (galerie, section, source_file), group in grouped:
            # Identifier toutes les métriques disponibles pour ce groupe
            available_metrics = {}
            
            for _, row in group.iterrows():
                metric = row['metric']
                periodic = row['periodic_mm']
                cumulative = row['cumulative_mm']
                
                # Formatage des valeurs
                if pd.isna(periodic):
                    periodic_str = "N/A"
                else:
                    periodic_str = f"{periodic:.2f}"
                
                if pd.isna(cumulative):
                    cumulative_str = "N/A"
                else:
                    cumulative_str = f"{cumulative:.2f}"
                
                available_metrics[metric] = {
                    'periodic': periodic_str,
                    'cumulative': cumulative_str
                }
            
            # Ordre préféré pour les déplacements (adapté aux vraies métriques)
            displacement_order = [
                'DPM bas gauche', 'DH bas gauche', 'DZ bas gauche',
                'DPM haut gauche', 'DH haut gauche', 'DZ haut gauche',
                'DPM centre haut', 'DH centre haut', 'DZ centre haut',
                'DPM haut droit', 'DH haut droit', 'DZ haut droit',
                'DPM bas droit', 'DH bas droit', 'DZ bas droit'
            ]
            
            # Commencer par l'ordre préféré
            metric_order = []
            remaining_metrics = set(available_metrics.keys())
            
            for preferred_metric in displacement_order:
                if preferred_metric in available_metrics:
                    metric_order.append(preferred_metric)
                    remaining_metrics.remove(preferred_metric)
            
            # Ajouter les métriques restantes (triées alphabétiquement)
            metric_order.extend(sorted(remaining_metrics))
            
            periodic_values = []
            cumulative_values = []
            
            for metric in metric_order:
                if metric in available_metrics:
                    data = available_metrics[metric]
                    
                    # Simplifier le nom pour l'affichage
                    metric_short = metric.replace("bas gauche", "BG").replace("haut gauche", "HG")\
                                       .replace("haut droit", "HD").replace("bas droit", "BD")\
                                       .replace("inter gauche", "IG").replace("inter droit", "ID")\
                                       .replace("centre haut", "CH").replace("centre", "C")\
                                       .replace("centre bas", "CB")
                    
                    periodic_values.append(f"{metric_short}:{data['periodic']}")
                    cumulative_values.append(f"{metric_short}:{data['cumulative']}")
            
            # Construire les lignes
            base_name = f"{galerie} {section}"
            
            periodic_line = f"{base_name} (Déplacements - périodique)"
            periodic_line += f"\n  {' | '.join(periodic_values)}"
            
            cumulative_line = f"{base_name} (Déplacements - cumulé)"
            cumulative_line += f"\n  {' | '.join(cumulative_values)}"
            
            summary_lines.append(periodic_line)
            summary_lines.append(cumulative_line)
            summary_lines.append("")  # Ligne vide
        
        return summary_lines
    
    def generate_all_ligne_summaries(self) -> bool:
        """Génère tous les récapitulatifs en ligne"""
        try:
            print(f"🔄 Génération des récapitulatifs en ligne - Mois: {self.month}")
            
            # Charger les données
            data = self.load_csv_data()
            
            if data['convergences'].empty and data['deplacements'].empty:
                print("❌ Aucune donnée disponible")
                return False
            
            summary_lines = []
            summary_lines.append(f"RÉCAPITULATIFS EN LIGNE SMC - {self.month}")
            summary_lines.append("=" * 60)
            summary_lines.append("")
            
            # Convergences
            if not data['convergences'].empty:
                summary_lines.append("CONVERGENCES")
                summary_lines.append("-" * 40)
                conv_lines = self.generate_ligne_summary_convergences(data['convergences'])
                summary_lines.extend(conv_lines)
                summary_lines.append("")
            
            # Déplacements
            if not data['deplacements'].empty:
                summary_lines.append("DÉPLACEMENTS")
                summary_lines.append("-" * 40)
                depl_lines = self.generate_ligne_summary_deplacements(data['deplacements'])
                summary_lines.extend(depl_lines)
                summary_lines.append("")
            
            # Sauvegarder le fichier
            output_file = self.output_folder / f"Recapitulatifs_Ligne_SMC_{self.month.replace('-', '_')}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(summary_lines))
            
            print(f"✅ Récapitulatifs en ligne générés: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération récapitulatifs: {e}")
            return False
    
    def generate_csv_ligne_summaries(self) -> bool:
        """Génère des récapitulatifs en ligne au format CSV"""
        try:
            print(f"🔄 Génération des récapitulatifs CSV en ligne - Mois: {self.month}")
            
            # Charger les données
            data = self.load_csv_data()
            
            if data['convergences'].empty and data['deplacements'].empty:
                print("❌ Aucune donnée disponible")
                return False
            
            # Convergences CSV
            if not data['convergences'].empty:
                conv_summary = []
                grouped = data['convergences'].groupby(['galerie', 'section', 'source_file'])
                
                for (galerie, section, source_file), group in grouped:
                    # Identifier TOUTES les métriques disponibles pour ce groupe
                    available_metrics = set(group['metric'].unique())
                    
                    # Ordre préféré des métriques
                    preferred_order = ['BG', 'IG', 'HG', 'HD', 'ID', 'BD', 'LH', 'LI', 'LB']
                    
                    # Commencer par l'ordre préféré, puis ajouter les autres
                    metric_order = []
                    for metric in preferred_order:
                        if metric in available_metrics:
                            metric_order.append(metric)
                            available_metrics.remove(metric)
                    
                    # Ajouter les métriques restantes (triées alphabétiquement)
                    remaining_metrics = sorted([m for m in available_metrics 
                                              if not m.startswith('Distance au front')])
                    metric_order.extend(remaining_metrics)
                    
                    # Ligne périodique
                    periodic_row = {
                        'galerie': galerie,
                        'section': section,
                        'type': 'Convergences',
                        'mode': 'périodique'
                    }
                    
                    # Ligne cumulée
                    cumulative_row = {
                        'galerie': galerie,
                        'section': section,
                        'type': 'Convergences',
                        'mode': 'cumulé'
                    }
                    
                    for metric in metric_order:
                        metric_data = group[group['metric'] == metric]
                        if not metric_data.empty:
                            periodic = metric_data.iloc[0]['periodic_mm']
                            cumulative = metric_data.iloc[0]['cumulative_mm']
                        else:
                            periodic = None
                            cumulative = None
                        
                        periodic_row[metric] = periodic
                        cumulative_row[metric] = cumulative
                    
                    conv_summary.append(periodic_row)
                    conv_summary.append(cumulative_row)
                
                # Sauvegarder CSV convergences
                conv_df = pd.DataFrame(conv_summary)
                
                # Réorganiser les colonnes dans l'ordre voulu
                base_columns = ['galerie', 'section', 'type', 'mode']
                metric_columns = ['BG', 'IG', 'HG', 'HD', 'ID', 'BD', 'LH', 'LI', 'LB']
                ordered_columns = base_columns + [col for col in metric_columns if col in conv_df.columns]
                conv_df = conv_df[ordered_columns]
                
                conv_output = self.output_folder / f"Convergences_Ligne_SMC_{self.month.replace('-', '_')}.csv"
                conv_df.to_csv(conv_output, index=False, encoding='utf-8-sig')
                print(f"✅ Convergences en ligne CSV: {conv_output}")
            
            # Déplacements CSV
            if not data['deplacements'].empty:
                depl_summary = []
                grouped = data['deplacements'].groupby(['galerie', 'section', 'source_file'])
                
                for (galerie, section, source_file), group in grouped:
                    # Identifier toutes les métriques disponibles
                    metrics = []
                    metrics_data = {}
                    
                    for _, row in group.iterrows():
                        metric = row['metric']
                        # Simplifier le nom pour le CSV
                        metric_short = metric.replace("bas gauche", "BG").replace("haut gauche", "HG")\
                                           .replace("haut droit", "HD").replace("bas droit", "BD")\
                                           .replace("centre haut", "CH").replace("centre", "C")\
                                           .replace("centre bas", "CB")\
                                           .replace("inter gauche", "IG").replace("inter droit", "ID")
                        
                        if metric_short not in metrics:
                            metrics.append(metric_short)
                        
                        metrics_data[metric_short] = {
                            'periodic': row['periodic_mm'],
                            'cumulative': row['cumulative_mm']
                        }
                    
                    # Ordre voulu pour les déplacements : BG, IG, HG, HD, ID, BD pour chaque type (DPM, DH, DZ)
                    displacement_order = [
                        'DPM BG', 'DH BG', 'DZ BG', 
                        'DPM IG', 'DH IG', 'DZ IG',
                        'DPM HG', 'DH HG', 'DZ HG', 
                        'DPM CH', 'DH CH', 'DZ CH',
                        'DPM HD', 'DH HD', 'DZ HD', 
                        'DPM ID', 'DH ID', 'DZ ID',
                        'DPM BD', 'DH BD', 'DZ BD'
                    ]
                    
                    # Organiser les métriques selon l'ordre voulu
                    ordered_metrics = []
                    remaining_metrics = set(metrics)
                    
                    for preferred_metric in displacement_order:
                        if preferred_metric in remaining_metrics:
                            ordered_metrics.append(preferred_metric)
                            remaining_metrics.remove(preferred_metric)
                    
                    # Ajouter les métriques restantes à la fin
                    ordered_metrics.extend(sorted(remaining_metrics))
                    metrics = ordered_metrics
                    
                    # Ligne périodique
                    periodic_row = {
                        'galerie': galerie,
                        'section': section,
                        'type': 'Déplacements',
                        'mode': 'périodique'
                    }
                    
                    # Ligne cumulée
                    cumulative_row = {
                        'galerie': galerie,
                        'section': section,
                        'type': 'Déplacements',
                        'mode': 'cumulé'
                    }
                    
                    for metric_short in metrics:
                        data_metric = metrics_data.get(metric_short, {'periodic': None, 'cumulative': None})
                        periodic_row[metric_short] = data_metric['periodic']
                        cumulative_row[metric_short] = data_metric['cumulative']
                    
                    depl_summary.append(periodic_row)
                    depl_summary.append(cumulative_row)
                
                # Sauvegarder CSV déplacements
                depl_df = pd.DataFrame(depl_summary)
                
                # Réorganiser les colonnes dans l'ordre voulu pour les déplacements
                base_columns = ['galerie', 'section', 'type', 'mode']
                displacement_columns = [
                    'DPM BG', 'DH BG', 'DZ BG', 
                    'DPM IG', 'DH IG', 'DZ IG',
                    'DPM HG', 'DH HG', 'DZ HG', 
                    'DPM CH', 'DH CH', 'DZ CH',
                    'DPM HD', 'DH HD', 'DZ HD', 
                    'DPM ID', 'DH ID', 'DZ ID',
                    'DPM BD', 'DH BD', 'DZ BD'
                ]
                ordered_columns = base_columns + [col for col in displacement_columns if col in depl_df.columns]
                # Ajouter les colonnes restantes à la fin
                remaining_columns = [col for col in depl_df.columns if col not in ordered_columns]
                ordered_columns.extend(remaining_columns)
                depl_df = depl_df[ordered_columns]
                
                depl_output = self.output_folder / f"Deplacements_Ligne_SMC_{self.month.replace('-', '_')}.csv"
                depl_df.to_csv(depl_output, index=False, encoding='utf-8-sig')
                print(f"✅ Déplacements en ligne CSV: {depl_output}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération récapitulatifs CSV: {e}")
            return False


def generate_ligne_summaries(csv_folder: str, output_folder: str, month: str, log_callback=None) -> bool:
    """Fonction principale pour générer les récapitulatifs en ligne"""
    
    if log_callback:
        log_callback("📄 Génération des récapitulatifs en ligne...")
    
    try:
        generator = LigneSummaryGenerator(csv_folder, output_folder, month)
        
        # Générer les récapitulatifs texte
        text_success = generator.generate_all_ligne_summaries()
        
        # Générer les récapitulatifs CSV
        csv_success = generator.generate_csv_ligne_summaries()
        
        if log_callback:
            if text_success and csv_success:
                log_callback("✅ Récapitulatifs en ligne générés avec succès")
            elif text_success or csv_success:
                log_callback("⚠️ Récapitulatifs partiellement générés")
            else:
                log_callback("❌ Échec génération récapitulatifs en ligne")
        
        return text_success or csv_success
        
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Erreur récapitulatifs en ligne: {e}")
        return False


if __name__ == "__main__":
    # Test
    csv_folder = r"C:\temp\smc_output"
    output_folder = r"C:\temp\smc_output"
    month = "2025-08"
    
    generate_ligne_summaries(csv_folder, output_folder, month)
