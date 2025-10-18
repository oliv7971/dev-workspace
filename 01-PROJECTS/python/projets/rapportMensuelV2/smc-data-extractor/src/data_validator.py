#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC Data Validator - Module de contrôle de l'intégrité des données
Vérifie que les données extraites dans les CSV correspondent aux fichiers Excel sources
"""

import pandas as pd
import openpyxl
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import os

class SMCDataValidator:
    """Validateur de l'intégrité des données SMC extraites"""
    
    def __init__(self, csv_folder: str, source_folder: str, month: str):
        self.csv_folder = Path(csv_folder)
        self.source_folder = Path(source_folder)
        self.month = month
        self.logger = logging.getLogger(__name__)
        
        # Résultats de validation
        self.validation_results = {
            'convergences': {'total_checks': 0, 'passed': 0, 'failed': 0, 'errors': []},
            'deplacements': {'total_checks': 0, 'passed': 0, 'failed': 0, 'errors': []},
            'calculation_log': [],  # Log détaillé des calculs
            'summary': {}
        }
    
    def find_convergence_table_end(self, worksheet) -> int:
        """
        Trouve la dernière colonne du tableau de convergences en détectant 
        les cellules fusionnées ou les en-têtes de vitesse
        COPIE de la fonction identique dans smc_evolutions.py
        """
        try:
            # Chercher dans la ligne des en-têtes (ligne 8 ou 9)
            for row_num in [8, 9]:
                for col_idx in range(1, worksheet.max_column + 1):
                    cell_value = worksheet.cell(row_num, col_idx).value
                    if cell_value and isinstance(cell_value, str):
                        cell_text = cell_value.lower()
                        # Si on trouve des mots-clés de vitesse, on s'arrête à la colonne précédente
                        if any(keyword in cell_text for keyword in ['vitesse', 'évolution', 'evolution', 'velocit']):
                            return col_idx - 1
            
            # Méthode alternative: chercher les cellules fusionnées
            for merged_range in worksheet.merged_cells.ranges:
                # Examiner le contenu des cellules fusionnées
                start_cell = worksheet.cell(merged_range.min_row, merged_range.min_col)
                if start_cell.value and isinstance(start_cell.value, str):
                    cell_text = start_cell.value.lower()
                    if any(keyword in cell_text for keyword in ['vitesse', 'évolution', 'evolution']):
                        # La fin du tableau de convergences est juste avant cette zone fusionnée
                        return merged_range.min_col - 1
            
            # Si aucune détection automatique, on utilise une valeur par défaut sécurisée
            # En cherchant la dernière colonne avec un en-tête de métrique valide
            last_metric_col = 1
            excluded_headers = ['Date', 'Temps (j)', 'jours écoulés', 'Distance au front']
            
            for col_idx in range(1, min(20, worksheet.max_column + 1)):  # Limite raisonnable
                header_cell = worksheet.cell(9, col_idx).value
                if header_cell:
                    header_text = str(header_cell).strip()
                    # Si c'est une métrique valide (pas dans les exclusions)
                    if (not any(excl.lower() in header_text.lower() for excl in excluded_headers) 
                        and len(header_text) <= 4  # Les métriques sont courtes: BG, LH, etc.
                        and header_text.upper() == header_text):  # Les métriques sont en majuscules
                        last_metric_col = col_idx
            
            return last_metric_col
            
        except Exception as e:
            self.logger.warning(f"Erreur détection fin tableau convergences: {e}")
            return 12  # Valeur par défaut sécurisée
    
    def validate_all_data(self) -> Dict[str, Any]:
        """Lance la validation complète des données"""
        print("🔍 VALIDATION DES DONNÉES SMC")
        print("=" * 50)
        
        # Charger les données CSV
        csv_data = self.load_csv_data()
        if not csv_data:
            return self.validation_results
        
        # Trouver les fichiers Excel sources
        excel_files = self.find_excel_files()
        if not excel_files:
            print("❌ Aucun fichier Excel trouvé")
            return self.validation_results
        
        print(f"📊 {len(excel_files)} fichiers Excel à valider")
        print(f"📋 {len(csv_data['convergences'])} convergences CSV")
        print(f"📋 {len(csv_data['deplacements'])} déplacements CSV")
        print()
        
        # Valider chaque fichier Excel
        for i, excel_file in enumerate(excel_files, 1):
            print(f"🔍 Validation {i}/{len(excel_files)}: {excel_file.name}")
            self.validate_excel_file(excel_file, csv_data)
        
        # Générer le rapport final
        self.generate_validation_report()
        
        return self.validation_results
    
    def load_csv_data(self) -> Dict[str, pd.DataFrame]:
        """Charge les données CSV extraites"""
        csv_data = {'convergences': pd.DataFrame(), 'deplacements': pd.DataFrame()}
        
        try:
            # Convergences
            conv_file = self.csv_folder / "Convergences_SMC.csv"
            if conv_file.exists():
                csv_data['convergences'] = pd.read_csv(conv_file, encoding='utf-8-sig')
                print(f"✅ Chargé: {conv_file.name} ({len(csv_data['convergences'])} lignes)")
            
            # Déplacements
            depl_file = self.csv_folder / "Deplacements_SMC.csv"
            if depl_file.exists():
                csv_data['deplacements'] = pd.read_csv(depl_file, encoding='utf-8-sig')
                print(f"✅ Chargé: {depl_file.name} ({len(csv_data['deplacements'])} lignes)")
            
        except Exception as e:
            print(f"❌ Erreur chargement CSV: {e}")
            
        return csv_data
    
    def find_excel_files(self) -> List[Path]:
        """Trouve tous les fichiers Excel SMC dans le dossier source"""
        excel_files = []
        
        for pattern in ['**/*SMC*.xlsm', '**/*SMC*.xlsx']:
            excel_files.extend(self.source_folder.glob(pattern))
        
        return sorted(excel_files)
    
    def validate_excel_file(self, excel_file: Path, csv_data: Dict[str, pd.DataFrame]):
        """Valide un fichier Excel contre les données CSV"""
        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            
            # Extraire les informations du fichier
            file_info = self.extract_file_info(excel_file)
            
            # Valider les convergences
            if 'Convergences' in wb.sheetnames:
                self.validate_convergences_sheet(wb['Convergences'], file_info, csv_data['convergences'])
            
            # Valider les déplacements
            if 'Déplacements' in wb.sheetnames:
                self.validate_deplacements_sheet(wb['Déplacements'], file_info, csv_data['deplacements'])
                
        except Exception as e:
            error_msg = f"Erreur validation {excel_file.name}: {e}"
            print(f"  ❌ {error_msg}")
            self.validation_results['convergences']['errors'].append(error_msg)
            self.validation_results['deplacements']['errors'].append(error_msg)
    
    def extract_file_info(self, excel_file: Path) -> Dict[str, str]:
        """Extrait les informations du fichier (galerie, section, etc.)"""
        file_name = excel_file.stem
        
        # Parser le nom de fichier pour extraire galerie et section
        # Format typique: 03_104-GGS_SMC_C003_PM001_25_08-25.xlsm
        parts = file_name.split('_')
        
        galerie = "Unknown"
        section = "Unknown"
        
        try:
            if 'GGS' in file_name:
                galerie = 'GGS'
            elif 'GHA' in file_name:
                galerie = 'GHA'
            elif 'GVA' in file_name:
                galerie = 'GVA'
            
            # Chercher la section (format Cxxx ou Txxx)
            for part in parts:
                if part.startswith(('C', 'T')) and len(part) >= 3:
                    section = part[:4] if len(part) >= 4 else part
                    break
        except:
            pass
        
        return {
            'galerie': galerie,
            'section': section,
            'source_file': str(excel_file)
        }
    
    def validate_convergences_sheet(self, worksheet, file_info: Dict[str, str], csv_convergences: pd.DataFrame):
        """Valide la feuille Convergences contre les données CSV"""
        try:
            # Extraire les données Excel
            excel_data = self.extract_excel_convergences(worksheet)
            
            # Filtrer les données CSV pour ce fichier
            csv_filtered = csv_convergences[
                (csv_convergences['galerie'] == file_info['galerie']) &
                (csv_convergences['section'] == file_info['section']) &
                (csv_convergences['source_file'] == file_info['source_file'])
            ]
            
            # Comparer chaque métrique
            for metric, excel_values in excel_data.items():
                csv_metric = csv_filtered[csv_filtered['metric'] == metric]
                
                self.validation_results['convergences']['total_checks'] += 1
                
                if csv_metric.empty:
                    error_msg = f"{file_info['galerie']} {file_info['section']}: Métrique {metric} manquante dans CSV"
                    print(f"    ❌ {error_msg}")
                    self.validation_results['convergences']['errors'].append(error_msg)
                    self.validation_results['convergences']['failed'] += 1
                else:
                    # Vérifier les valeurs
                    csv_periodic = csv_metric.iloc[0]['periodic_mm']
                    csv_cumulative = csv_metric.iloc[0]['cumulative_mm']
                    
                    if self.values_match(excel_values['periodic'], csv_periodic) and \
                       self.values_match(excel_values['cumulative'], csv_cumulative):
                        self.validation_results['convergences']['passed'] += 1
                        print(f"    ✅ {metric}: OK")
                    else:
                        error_msg = f"{file_info['galerie']} {file_info['section']}: {metric} - Excel: P={excel_values['periodic']}, C={excel_values['cumulative']} vs CSV: P={csv_periodic}, C={csv_cumulative}"
                        print(f"    ❌ {error_msg}")
                        self.validation_results['convergences']['errors'].append(error_msg)
                        self.validation_results['convergences']['failed'] += 1
                        
        except Exception as e:
            error_msg = f"Erreur validation convergences {file_info['galerie']} {file_info['section']}: {e}"
            print(f"    ❌ {error_msg}")
            self.validation_results['convergences']['errors'].append(error_msg)
    
    def validate_deplacements_sheet(self, worksheet, file_info: Dict[str, str], csv_deplacements: pd.DataFrame):
        """Valide la feuille Déplacements contre les données CSV"""
        try:
            # Extraire les données Excel
            excel_data = self.extract_excel_deplacements(worksheet)
            
            # Filtrer les données CSV pour ce fichier
            csv_filtered = csv_deplacements[
                (csv_deplacements['galerie'] == file_info['galerie']) &
                (csv_deplacements['section'] == file_info['section']) &
                (csv_deplacements['source_file'] == file_info['source_file'])
            ]
            
            # Comparer chaque métrique
            for metric, excel_values in excel_data.items():
                csv_metric = csv_filtered[csv_filtered['metric'] == metric]
                
                self.validation_results['deplacements']['total_checks'] += 1
                
                if csv_metric.empty:
                    error_msg = f"{file_info['galerie']} {file_info['section']}: Métrique {metric} manquante dans CSV"
                    print(f"    ❌ {error_msg}")
                    self.validation_results['deplacements']['errors'].append(error_msg)
                    self.validation_results['deplacements']['failed'] += 1
                else:
                    # Vérifier les valeurs
                    csv_periodic = csv_metric.iloc[0]['periodic_mm']
                    csv_cumulative = csv_metric.iloc[0]['cumulative_mm']
                    
                    if self.values_match(excel_values['periodic'], csv_periodic) and \
                       self.values_match(excel_values['cumulative'], csv_cumulative):
                        self.validation_results['deplacements']['passed'] += 1
                        print(f"    ✅ {metric}: OK")
                    else:
                        error_msg = f"{file_info['galerie']} {file_info['section']}: {metric} - Excel: P={excel_values['periodic']}, C={excel_values['cumulative']} vs CSV: P={csv_periodic}, C={csv_cumulative}"
                        print(f"    ❌ {error_msg}")
                        self.validation_results['deplacements']['errors'].append(error_msg)
                        self.validation_results['deplacements']['failed'] += 1
                        
        except Exception as e:
            error_msg = f"Erreur validation déplacements {file_info['galerie']} {file_info['section']}: {e}"
            print(f"    ❌ {error_msg}")
            self.validation_results['deplacements']['errors'].append(error_msg)
    
    def extract_excel_convergences(self, worksheet) -> Dict[str, Dict[str, float]]:
        """Extrait les données de convergences directement d'Excel avec log détaillé"""
        data = {}
        
        # Trouver la fin du tableau de convergences (même logique que l'extracteur)
        end_col = self.find_convergence_table_end(worksheet)
        
        # En-têtes ligne 9
        headers = {}
        excluded_headers = ['Date', 'Temps (j)', 'jours écoulés', 'Distance au front']
        
        for col_idx in range(1, end_col + 1):
            header_cell = worksheet.cell(9, col_idx).value
            if header_cell:
                header_text = str(header_cell).strip()
                if not any(excl.lower() in header_text.lower() for excl in excluded_headers):
                    headers[col_idx] = header_text
        
        # Extraire les données avec log détaillé
        last_row = self.find_last_data_row(worksheet)
        if last_row:
            # Trouver les dates correspondantes
            last_date = self.get_date_from_row(worksheet, last_row)
            
            for col_idx, metric in headers.items():
                calculation_detail = {
                    'type': 'convergence',
                    'metric': metric,
                    'file': worksheet.parent.filename if hasattr(worksheet.parent, 'filename') else 'Unknown',
                    'calculations': []
                }
                
                # Valeur cumulative (dernière ligne)
                cumulative_cell = worksheet.cell(last_row, col_idx)
                cumulative_raw = cumulative_cell.value
                cumulative = self.clean_numeric_value(cumulative_raw)
                
                calculation_detail['calculations'].append({
                    'step': 'Valeur cumulative',
                    'description': f"Cellule {cumulative_cell.coordinate} à la date {last_date}",
                    'raw_value': cumulative_raw,
                    'cleaned_value': cumulative,
                    'formula': f"= Valeur finale dans {cumulative_cell.coordinate}"
                })
                
                # Chercher la valeur précédente pour le calcul périodique
                periodic = None
                prev_value = None
                prev_date = None
                prev_row = None
                
                for row in range(last_row - 1, 9, -1):
                    prev_cell = worksheet.cell(row, col_idx)
                    prev_cell_value = prev_cell.value
                    if prev_cell_value is not None:
                        prev_value = self.clean_numeric_value(prev_cell_value)
                        prev_date = self.get_date_from_row(worksheet, row)
                        prev_row = row
                        
                        calculation_detail['calculations'].append({
                            'step': 'Valeur précédente',
                            'description': f"Cellule {prev_cell.coordinate} à la date {prev_date}",
                            'raw_value': prev_cell_value,
                            'cleaned_value': prev_value,
                            'formula': f"= Valeur antérieure dans {prev_cell.coordinate}"
                        })
                        break
                
                # Calcul périodique
                if cumulative is not None and prev_value is not None:
                    periodic = cumulative - prev_value
                    calculation_detail['calculations'].append({
                        'step': 'Calcul périodique',
                        'description': f"Différence entre {last_date} et {prev_date}",
                        'raw_value': f"{cumulative} - {prev_value}",
                        'cleaned_value': periodic,
                        'formula': f"= {cumulative} - {prev_value} = {periodic}"
                    })
                elif cumulative is not None:
                    calculation_detail['calculations'].append({
                        'step': 'Calcul périodique impossible',
                        'description': "Pas de valeur précédente trouvée",
                        'raw_value': None,
                        'cleaned_value': None,
                        'formula': "Impossible de calculer (pas de référence)"
                    })
                
                # Résumé final
                calculation_detail['final_values'] = {
                    'periodic': periodic,
                    'cumulative': cumulative
                }
                
                self.validation_results['calculation_log'].append(calculation_detail)
                
                if metric:
                    data[metric] = {
                        'periodic': periodic,
                        'cumulative': cumulative
                    }
        
        return data
    
    def extract_excel_deplacements(self, worksheet) -> Dict[str, Dict[str, float]]:
        """Extrait les données de déplacements directement d'Excel avec log détaillé"""
        data = {}
        
        # En-têtes ligne 9 (toutes les colonnes pour déplacements)
        headers = {}
        excluded_headers = ['Date', 'Temps (j)', 'jours écoulés', 'Distance au front']
        
        for col_idx in range(1, worksheet.max_column + 1):
            header_cell = worksheet.cell(9, col_idx).value
            if header_cell:
                header_text = str(header_cell).strip()
                if not any(excl.lower() in header_text.lower() for excl in excluded_headers):
                    headers[col_idx] = header_text
        
        # Extraire les données avec log détaillé
        last_row = self.find_last_data_row(worksheet)
        if last_row:
            # Trouver les dates correspondantes
            last_date = self.get_date_from_row(worksheet, last_row)
            
            for col_idx, metric in headers.items():
                calculation_detail = {
                    'type': 'deplacement',
                    'metric': metric,
                    'file': worksheet.parent.filename if hasattr(worksheet.parent, 'filename') else 'Unknown',
                    'calculations': []
                }
                
                # Valeur cumulative (dernière ligne)
                cumulative_cell = worksheet.cell(last_row, col_idx)
                cumulative_raw = cumulative_cell.value
                cumulative = self.clean_numeric_value(cumulative_raw)
                
                calculation_detail['calculations'].append({
                    'step': 'Valeur cumulative',
                    'description': f"Cellule {cumulative_cell.coordinate} à la date {last_date}",
                    'raw_value': cumulative_raw,
                    'cleaned_value': cumulative,
                    'formula': f"= Valeur finale dans {cumulative_cell.coordinate}"
                })
                
                # Chercher la valeur précédente pour le calcul périodique
                periodic = None
                prev_value = None
                prev_date = None
                
                for row in range(last_row - 1, 9, -1):
                    prev_cell = worksheet.cell(row, col_idx)
                    prev_cell_value = prev_cell.value
                    if prev_cell_value is not None:
                        prev_value = self.clean_numeric_value(prev_cell_value)
                        prev_date = self.get_date_from_row(worksheet, row)
                        
                        calculation_detail['calculations'].append({
                            'step': 'Valeur précédente',
                            'description': f"Cellule {prev_cell.coordinate} à la date {prev_date}",
                            'raw_value': prev_cell_value,
                            'cleaned_value': prev_value,
                            'formula': f"= Valeur antérieure dans {prev_cell.coordinate}"
                        })
                        break
                
                # Calcul périodique
                if cumulative is not None and prev_value is not None:
                    periodic = cumulative - prev_value
                    calculation_detail['calculations'].append({
                        'step': 'Calcul périodique',
                        'description': f"Différence entre {last_date} et {prev_date}",
                        'raw_value': f"{cumulative} - {prev_value}",
                        'cleaned_value': periodic,
                        'formula': f"= {cumulative} - {prev_value} = {periodic}"
                    })
                elif cumulative is not None:
                    calculation_detail['calculations'].append({
                        'step': 'Calcul périodique impossible',
                        'description': "Pas de valeur précédente trouvée",
                        'raw_value': None,
                        'cleaned_value': None,
                        'formula': "Impossible de calculer (pas de référence)"
                    })
                
                # Résumé final
                calculation_detail['final_values'] = {
                    'periodic': periodic,
                    'cumulative': cumulative
                }
                
                self.validation_results['calculation_log'].append(calculation_detail)
                
                if metric:
                    data[metric] = {
                        'periodic': periodic,
                        'cumulative': cumulative
                    }
        
        return data
    
    def find_convergence_table_end(self, worksheet) -> int:
        """Trouve la fin du tableau de convergences (même logique que l'extracteur)"""
        try:
            # Chercher dans les en-têtes
            for row_num in [8, 9]:
                for col_idx in range(1, worksheet.max_column + 1):
                    cell_value = worksheet.cell(row_num, col_idx).value
                    if cell_value and isinstance(cell_value, str):
                        cell_text = cell_value.lower()
                        if any(keyword in cell_text for keyword in ['vitesse', 'évolution', 'evolution']):
                            return col_idx - 1
            
            # Chercher les cellules fusionnées
            for merged_range in worksheet.merged_cells.ranges:
                start_cell = worksheet.cell(merged_range.min_row, merged_range.min_col)
                if start_cell.value and isinstance(start_cell.value, str):
                    cell_text = start_cell.value.lower()
                    if any(keyword in cell_text for keyword in ['vitesse', 'évolution']):
                        return merged_range.min_col - 1
            
            # Valeur par défaut
            return 15
            
        except Exception:
            return 15
    
    def get_date_from_row(self, worksheet, row: int) -> str:
        """Extrait la date d'une ligne donnée"""
        date_col = 2  # Colonne des dates
        try:
            date_cell = worksheet.cell(row, date_col).value
            if date_cell:
                if isinstance(date_cell, datetime):
                    return date_cell.strftime('%Y-%m-%d')
                else:
                    return str(date_cell)
            return f"Ligne {row}"
        except:
            return f"Ligne {row}"
    
    def find_last_data_row(self, worksheet) -> Optional[int]:
        """Trouve la dernière ligne contenant des données"""
        date_col = 2  # Colonne des dates
        
        for row_idx in range(worksheet.max_row, 9, -1):
            date_cell = worksheet.cell(row_idx, date_col).value
            if date_cell is not None:
                return row_idx
        
        return None
    
    def clean_numeric_value(self, value) -> Optional[float]:
        """Nettoie et convertit une valeur numérique (même logique que l'extracteur)"""
        if pd.isna(value) or value is None:
            return None
            
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            clean_value = value.replace(',', '.').replace(' ', '').replace('\u2212', '-')
            if clean_value.upper() in ['ND', 'NR', '-', '']:
                return None
            try:
                return float(clean_value)
            except:
                return None
        
        return None
    
    def values_match(self, val1, val2, tolerance: float = 0.01) -> bool:
        """Vérifie si deux valeurs sont équivalentes (avec tolérance)"""
        # Cas où les deux sont None/NaN
        if pd.isna(val1) and pd.isna(val2):
            return True
        if val1 is None and val2 is None:
            return True
        
        # Cas où une seule est None/NaN
        if (pd.isna(val1) or val1 is None) != (pd.isna(val2) or val2 is None):
            return False
        
        # Comparaison numérique avec tolérance
        try:
            return abs(float(val1) - float(val2)) <= tolerance
        except:
            return False
    
    def generate_validation_report(self):
        """Génère le rapport de validation final"""
        print("\n" + "=" * 50)
        print("📊 RAPPORT DE VALIDATION")
        print("=" * 50)
        
        # Convergences
        conv = self.validation_results['convergences']
        print(f"🔹 CONVERGENCES:")
        print(f"   Total vérifications: {conv['total_checks']}")
        print(f"   ✅ Réussies: {conv['passed']}")
        print(f"   ❌ Échouées: {conv['failed']}")
        if conv['total_checks'] > 0:
            success_rate = (conv['passed'] / conv['total_checks']) * 100
            print(f"   📈 Taux de réussite: {success_rate:.1f}%")
        
        # Déplacements
        depl = self.validation_results['deplacements']
        print(f"\n🔹 DÉPLACEMENTS:")
        print(f"   Total vérifications: {depl['total_checks']}")
        print(f"   ✅ Réussies: {depl['passed']}")
        print(f"   ❌ Échouées: {depl['failed']}")
        if depl['total_checks'] > 0:
            success_rate = (depl['passed'] / depl['total_checks']) * 100
            print(f"   📈 Taux de réussite: {success_rate:.1f}%")
        
        # Résumé global
        total_checks = conv['total_checks'] + depl['total_checks']
        total_passed = conv['passed'] + depl['passed']
        total_failed = conv['failed'] + depl['failed']
        
        print(f"\n🎯 RÉSUMÉ GLOBAL:")
        print(f"   Total vérifications: {total_checks}")
        print(f"   ✅ Réussies: {total_passed}")
        print(f"   ❌ Échouées: {total_failed}")
        if total_checks > 0:
            global_success_rate = (total_passed / total_checks) * 100
            print(f"   📈 Taux de réussite global: {global_success_rate:.1f}%")
        
        # Sauvegarder le rapport
        self.save_validation_report()
        
        print("\n" + "=" * 50)
        if total_failed == 0:
            print("🎉 VALIDATION RÉUSSIE - Toutes les données sont conformes!")
        else:
            print(f"⚠️  VALIDATION AVEC ERREURS - {total_failed} problèmes détectés")
        print("=" * 50)
    
    def save_validation_report(self):
        """Sauvegarde le rapport de validation dans un fichier"""
        try:
            report_file = self.csv_folder / f"Rapport_Validation_SMC_{self.month.replace('-', '_')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"RAPPORT DE VALIDATION SMC - {self.month}\n")
                f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                # Résultats convergences
                conv = self.validation_results['convergences']
                f.write("CONVERGENCES:\n")
                f.write(f"  Total vérifications: {conv['total_checks']}\n")
                f.write(f"  Réussies: {conv['passed']}\n")
                f.write(f"  Échouées: {conv['failed']}\n")
                if conv['total_checks'] > 0:
                    rate = (conv['passed'] / conv['total_checks']) * 100
                    f.write(f"  Taux de réussite: {rate:.1f}%\n")
                f.write("\n")
                
                # Erreurs convergences
                if conv['errors']:
                    f.write("ERREURS CONVERGENCES:\n")
                    for error in conv['errors']:
                        f.write(f"  - {error}\n")
                    f.write("\n")
                
                # Résultats déplacements
                depl = self.validation_results['deplacements']
                f.write("DÉPLACEMENTS:\n")
                f.write(f"  Total vérifications: {depl['total_checks']}\n")
                f.write(f"  Réussies: {depl['passed']}\n")
                f.write(f"  Échouées: {depl['failed']}\n")
                if depl['total_checks'] > 0:
                    rate = (depl['passed'] / depl['total_checks']) * 100
                    f.write(f"  Taux de réussite: {rate:.1f}%\n")
                f.write("\n")
                
                # Erreurs déplacements
                if depl['errors']:
                    f.write("ERREURS DÉPLACEMENTS:\n")
                    for error in depl['errors']:
                        f.write(f"  - {error}\n")
                    f.write("\n")
            
            print(f"📄 Rapport sauvegardé: {report_file}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde rapport: {e}")


def main():
    """Test du validateur"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python data_validator.py <csv_folder> <source_folder> <month>")
        sys.exit(1)
    
    csv_folder = sys.argv[1]
    source_folder = sys.argv[2]
    month = sys.argv[3]
    
    validator = SMCDataValidator(csv_folder, source_folder, month)
    results = validator.validate_all_data()


if __name__ == "__main__":
    main()
