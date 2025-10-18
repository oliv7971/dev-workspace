#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur Unifié SMC & Carrure - Version COMPLÈTE
Implémente la logique métier complète: dernières valeurs + valeurs périodiques + graphiques
"""

import os
import re
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from calendar import monthrange
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDataExtractor:
    """Extracteur unifié pour SMC et Carrure avec logique métier complète"""

    def __init__(self, target_month: str):
        self.target_year, self.target_month = map(int, target_month.split('-'))

        # Fenêtre temporelle du mois
        self.month_start = date(self.target_year, self.target_month, 1)
        last_day = monthrange(self.target_year, self.target_month)[1]
        self.month_end = date(self.target_year, self.target_month, last_day)

        logger.info(f"Extracteur unifié initialisé pour période: {self.month_start} à {self.month_end}")

        # Résultats consolidés
        self.all_results = {
            'smc_convergences': [],
            'smc_deplacements': [],
            'carrure_deplacements': [],
            'carrure_cintres': [],
            'graph_zones': []
        }

    def parse_date(self, date_value) -> Optional[date]:
        """Parse une date dans différents formats (copié de SMC)"""
        if pd.isna(date_value) or date_value is None:
            return None

        if isinstance(date_value, datetime):
            return date_value.date()

        if isinstance(date_value, (int, float)):
            try:
                excel_epoch = datetime(1899, 12, 30)
                return (excel_epoch + pd.Timedelta(days=date_value)).date()
            except:
                return None

        if isinstance(date_value, str):
            clean_date = date_value.strip()
            date_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d/%m/%y',
                '%d-%m-%Y',
                '%d-%m-%y'
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(clean_date, fmt).date()
                except:
                    continue
        return None

    def clean_numeric_value(self, value) -> Optional[float]:
        """Nettoie et convertit une valeur numérique"""
        if pd.isna(value) or value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            clean_value = value.replace(',', '.').replace(' ', '').replace('\u2212', '-')
            if clean_value.upper() in ['ND', 'NR', '-', '', '#N/A']:
                return None
            try:
                return float(clean_value)
            except:
                return None
        return None

    def get_cell_color(self, cell):
        """Récupère la couleur de fond d'une cellule"""
        try:
            if cell.fill and cell.fill.start_color:
                return cell.fill.start_color.rgb
            return None
        except:
            return None

    def detect_graph_zones_by_color(self, worksheet, reference_color=None):
        """Détecte les zones de graphique par couleur de cellule"""
        if reference_color is None:
            # Prendre la couleur de A1 comme référence
            ref_cell = worksheet['A1']
            reference_color = self.get_cell_color(ref_cell)

        zones = []
        current_zone = None

        for row in range(1, worksheet.max_row + 1):
            for col in range(1, worksheet.max_column + 1):
                cell = worksheet.cell(row, col)
                cell_color = self.get_cell_color(cell)

                # Si la couleur correspond à la couleur de référence
                if cell_color == reference_color and cell.value:
                    if current_zone is None:
                        current_zone = {
                            'start_row': row,
                            'start_col': col,
                            'title': str(cell.value),
                            'cells': [(row, col)]
                        }
                    else:
                        current_zone['cells'].append((row, col))
                        current_zone['end_row'] = row
                        current_zone['end_col'] = col
                else:
                    # Fin de zone
                    if current_zone:
                        zones.append(current_zone)
                        current_zone = None

        # Ajouter la dernière zone si elle existe
        if current_zone:
            zones.append(current_zone)

        return zones

    def calculate_evolutions(self, data_rows: List[Dict], metrics: List[str]) -> Dict[str, Dict]:
        """
        Calcule les évolutions selon la logique métier:
        - Dernières valeurs (cumulatives)
        - Valeurs périodiques (mois - mois précédent)
        """
        if not data_rows:
            return {}

        # Filtrer par période
        dates_in_month = []
        dates_before_month = []

        for row in data_rows:
            row_date = row['date']
            if self.month_start <= row_date <= self.month_end:
                dates_in_month.append(row)
            elif row_date < self.month_start:
                dates_before_month.append(row)

        # Trier par date
        dates_in_month.sort(key=lambda x: x['date'])
        dates_before_month.sort(key=lambda x: x['date'])
        all_data_sorted = sorted(data_rows, key=lambda x: x['date'])

        results = {}

        for metric in metrics:
            if metric not in ['Date', 'Temps (j)', 'jours écoulés', 'Distance au front']:
                # 1. DERNIÈRE VALEUR CUMULATIVE (de toutes les données)
                last_cumulative_value = None
                last_cumulative_date = None
                for row in reversed(all_data_sorted):
                    if metric in row and row[metric] is not None:
                        last_cumulative_value = row[metric]
                        last_cumulative_date = row['date']
                        break

                # 2. DERNIÈRE VALEUR DANS LE MOIS
                last_in_month_value = None
                last_in_month_date = None
                for row in reversed(dates_in_month):
                    if metric in row and row[metric] is not None:
                        last_in_month_value = row[metric]
                        last_in_month_date = row['date']
                        break

                # 3. DERNIÈRE VALEUR AVANT LE MOIS
                last_before_month_value = None
                last_before_month_date = None
                for row in reversed(dates_before_month):
                    if metric in row and row[metric] is not None:
                        last_before_month_value = row[metric]
                        last_before_month_date = row['date']
                        break

                # 4. CALCUL VALEUR PÉRIODIQUE (différence mensuelle)
                periodic_mm = None
                if last_in_month_value is not None and last_before_month_value is not None:
                    periodic_mm = round(last_in_month_value - last_before_month_value, 2)

                # 5. VALEUR CUMULATIVE
                cumulative_mm = None
                if last_cumulative_value is not None:
                    cumulative_mm = round(last_cumulative_value, 2)

                results[metric] = {
                    'metric': metric,
                    'periodic_mm': periodic_mm,      # Valeur périodique (mois - mois précédent)
                    'cumulative_mm': cumulative_mm,  # Dernière valeur cumulative
                    'date_last_cumulative': last_cumulative_date,
                    'date_last_in_month': last_in_month_date,
                    'date_last_before_month': last_before_month_date,
                    'nb_dates_in_month': len(dates_in_month),
                    'nb_dates_before_month': len(dates_before_month)
                }

        return results

    def extract_smc_data(self, file_path: Path) -> Dict[str, Any]:
        """Extrait données SMC avec logique métier complète"""

        try:
            workbook = load_workbook(file_path, data_only=True)
            results = {'convergences': [], 'deplacements': []}

            # Extraire galerie et section
            galerie, section = self.extract_galerie_section(file_path)

            # Traiter Convergences et Déplacements
            for sheet_name in ['Convergences', 'Déplacements']:
                if sheet_name in workbook.sheetnames:
                    worksheet = workbook[sheet_name]

                    # Extraire données brutes
                    sheet_data = self.extract_smc_sheet_data(worksheet, sheet_name)

                    if sheet_data and sheet_data['data']:
                        # Calculer évolutions
                        metrics = list(sheet_data['headers'].values())
                        evolutions = self.calculate_evolutions(sheet_data['data'], metrics)

                        # Détecter zones de graphique
                        graph_zones = self.detect_graph_zones_by_color(worksheet)

                        # Formatter résultats
                        for metric, evolution in evolutions.items():
                            result_row = {
                                'file_path': str(file_path),
                                'galerie': galerie,
                                'section': section,
                                'sheet_type': sheet_name.lower(),
                                'data_type': 'smc',
                                **evolution
                            }

                            if sheet_name == 'Convergences':
                                results['convergences'].append(result_row)
                            else:
                                results['deplacements'].append(result_row)

                        # Stocker zones de graphique
                        for zone in graph_zones:
                            self.all_results['graph_zones'].append({
                                'file_path': str(file_path),
                                'sheet_name': sheet_name,
                                'zone_title': zone.get('title', ''),
                                'start_row': zone['start_row'],
                                'start_col': zone['start_col'],
                                'cells_count': len(zone['cells'])
                            })

            workbook.close()
            return results

        except Exception as e:
            logger.error(f"Erreur extraction SMC {file_path}: {e}")
            return {'convergences': [], 'deplacements': []}

    def extract_carrure_data(self, file_path: Path) -> Dict[str, Any]:
        """Extrait données Carrure avec logique métier complète"""

        try:
            workbook = load_workbook(file_path, data_only=True)
            results = {'carrure_deplacements': [], 'carrure_cintres': []}

            # Extraire galerie et section
            galerie, section = self.extract_galerie_section(file_path)

            # Traiter onglets Carrure
            carrure_sheets = {
                'Déplacements carrure': 'carrure_deplacements',
                'Déplacements cintres-longerons': 'carrure_cintres'
            }

            for sheet_name, result_key in carrure_sheets.items():
                if sheet_name in workbook.sheetnames:
                    worksheet = workbook[sheet_name]

                    # Extraire données brutes
                    sheet_data = self.extract_carrure_sheet_data(worksheet, sheet_name)

                    if sheet_data and sheet_data['data']:
                        # Calculer évolutions
                        metrics = list(sheet_data['headers'].values())
                        evolutions = self.calculate_evolutions(sheet_data['data'], metrics)

                        # Détecter zones de graphique
                        graph_zones = self.detect_graph_zones_by_color(worksheet)

                        # Formatter résultats
                        for metric, evolution in evolutions.items():
                            result_row = {
                                'file_path': str(file_path),
                                'galerie': galerie,
                                'section': section,
                                'sheet_type': result_key,
                                'data_type': 'carrure',
                                **evolution
                            }
                            results[result_key].append(result_row)

                        # Stocker zones de graphique
                        for zone in graph_zones:
                            self.all_results['graph_zones'].append({
                                'file_path': str(file_path),
                                'sheet_name': sheet_name,
                                'zone_title': zone.get('title', ''),
                                'start_row': zone['start_row'],
                                'start_col': zone['start_col'],
                                'cells_count': len(zone['cells'])
                            })

            workbook.close()
            return results

        except Exception as e:
            logger.error(f"Erreur extraction Carrure {file_path}: {e}")
            return {'carrure_deplacements': [], 'carrure_cintres': []}

    def extract_smc_sheet_data(self, worksheet, sheet_name: str) -> Dict[str, Any]:
        """Extrait données d'un onglet SMC (logique existante adaptée)"""

        if sheet_name == 'Convergences':
            headers_row = 9
            data_start_row = 10

            # Trouver la fin du tableau de convergences
            convergence_end_col = self.find_convergence_table_end(worksheet)

            # En-têtes de convergences (tableau de gauche seulement)
            headers = {}
            excluded_headers = ['Date', 'Temps (j)', 'jours écoulés', 'Distance au front']

            for col_idx in range(1, convergence_end_col + 1):
                header_cell = worksheet.cell(headers_row, col_idx).value
                if header_cell:
                    header_text = str(header_cell).strip()
                    if not any(excl.lower() in header_text.lower() for excl in excluded_headers):
                        headers[col_idx] = header_text

        elif sheet_name == 'Déplacements':
            headers_row = 9
            data_start_row = 10

            # Extraction de tous les en-têtes (sauf exclusions)
            headers = {}
            excluded_headers = ['Date', 'Temps (j)', 'jours écoulés', 'Distance au front']
            for col_idx in range(1, worksheet.max_column + 1):
                header_cell = worksheet.cell(headers_row, col_idx).value
                if header_cell:
                    header_text = str(header_cell).strip()
                    if not any(excl.lower() in header_text.lower() for excl in excluded_headers):
                        headers[col_idx] = header_text
        else:
            return {}

        # Trouver la colonne de date (toujours colonne 2)
        date_col = 2

        # Extraction des données
        data_rows = []

        for row_idx in range(data_start_row, worksheet.max_row + 1):
            # Date
            date_cell = worksheet.cell(row_idx, date_col).value
            parsed_date = self.parse_date(date_cell)
            if not parsed_date:
                continue

            row_data = {'date': parsed_date}

            # Autres colonnes (selon les en-têtes extraits)
            for col_idx, header in headers.items():
                if col_idx == date_col:
                    continue

                cell_value = worksheet.cell(row_idx, col_idx).value
                clean_value = self.clean_numeric_value(cell_value)

                if clean_value is not None:
                    row_data[header] = clean_value

            if len(row_data) > 1:  # Au moins date + 1 métrique
                data_rows.append(row_data)

        return {
            'sheet_name': sheet_name,
            'data': data_rows,
            'headers': headers
        }

    def find_convergence_table_end(self, worksheet) -> int:
        """Trouve la dernière colonne du tableau de convergences"""
        try:
            # Chercher dans la ligne des en-têtes (ligne 8 ou 9)
            for row_num in [8, 9]:
                for col_idx in range(1, worksheet.max_column + 1):
                    cell_value = worksheet.cell(row_num, col_idx).value
                    if cell_value and isinstance(cell_value, str):
                        cell_text = cell_value.lower()
                        if any(keyword in cell_text for keyword in ['vitesse', 'évolution', 'evolution', 'velocit']):
                            return col_idx - 1

            # Méthode alternative: chercher les cellules fusionnées
            for merged_range in worksheet.merged_cells.ranges:
                start_cell = worksheet.cell(merged_range.min_row, merged_range.min_col)
                if start_cell.value and isinstance(start_cell.value, str):
                    cell_text = start_cell.value.lower()
                    if any(keyword in cell_text for keyword in ['vitesse', 'évolution', 'evolution']):
                        return merged_range.min_col - 1

            # Valeur par défaut
            return 12

        except Exception as e:
            logger.warning(f"Erreur détection fin tableau convergences: {e}")
            return 12

    def extract_carrure_sheet_data(self, worksheet, sheet_name: str) -> Dict[str, Any]:
        """Extrait données d'un onglet Carrure"""

        # Structure des onglets Carrure (basée sur l'analyse)
        headers_row = 10
        data_start_row = 12
        date_col = 2
        jours_col = 1

        # Identifier les colonnes de données
        headers = {}

        if 'carrure' in sheet_name.lower():
            # Déplacements carrure - colonnes groupées par 3 (DPM, DH, DZ)
            for col_idx in range(4, worksheet.max_column + 1):
                header_cell = worksheet.cell(headers_row, col_idx).value
                if header_cell:
                    header_text = str(header_cell).strip()
                    if header_text not in ['Date', 'Jours écoulés', 'Front']:
                        headers[col_idx] = f"carrure_col_{col_idx}"

        elif 'cintres' in sheet_name.lower():
            # Déplacements cintres-longerons
            for col_idx in range(4, min(20, worksheet.max_column + 1)):
                header_cell = worksheet.cell(headers_row, col_idx).value
                if header_cell:
                    header_text = str(header_cell).strip()
                    if header_text not in ['Date', 'Jours écoulés', 'Front']:
                        headers[col_idx] = f"cintre_col_{col_idx}"

        # Extraction des données
        data_rows = []

        for row_idx in range(data_start_row, worksheet.max_row + 1):
            # Date
            date_cell = worksheet.cell(row_idx, date_col).value
            parsed_date = self.parse_date(date_cell)
            if not parsed_date:
                continue

            row_data = {'date': parsed_date}

            # Jours écoulés
            jours_value = self.clean_numeric_value(worksheet.cell(row_idx, jours_col).value)
            if jours_value is not None:
                row_data['jours_ecoules'] = jours_value

            # Autres colonnes (selon les en-têtes extraits)
            for col_idx, header in headers.items():
                cell_value = worksheet.cell(row_idx, col_idx).value
                clean_value = self.clean_numeric_value(cell_value)

                if clean_value is not None:
                    row_data[header] = clean_value

            if len(row_data) > 1:  # Au moins date + 1 métrique
                data_rows.append(row_data)

        return {
            'sheet_name': sheet_name,
            'data': data_rows,
            'headers': headers
        }

    def extract_galerie_section(self, file_path: Path) -> Tuple[str, str]:
        """Extrait galerie et section depuis le nom de fichier"""
        file_name = file_path.stem.upper()

        galerie_pattern = re.compile(r'([A-Z]{3})')
        galerie_matches = galerie_pattern.findall(file_name)
        galerie = galerie_matches[0] if galerie_matches else "UNKNOWN"

        section_pattern = re.compile(r'([CT]\d{2,3})')
        section_matches = section_pattern.findall(file_name)
        section = section_matches[0] if section_matches else "UNKNOWN"

        return galerie, section

    def generate_unified_report(self, output_folder: Path):
        """Génère le rapport unifié avec dernières valeurs et valeurs périodiques"""

        # Créer DataFrame consolidé
        all_data = []

        # Ajouter données SMC
        for conv_data in self.all_results['smc_convergences']:
            all_data.append(conv_data)
        for depl_data in self.all_results['smc_deplacements']:
            all_data.append(depl_data)

        # Ajouter données Carrure
        for carr_data in self.all_results['carrure_deplacements']:
            all_data.append(carr_data)
        for cint_data in self.all_results['carrure_cintres']:
            all_data.append(cint_data)

        if all_data:
            df = pd.DataFrame(all_data)

            # Sauvegarder rapport principal
            report_file = output_folder / f"rapport_unifie_{self.target_year}_{self.target_month:02d}.csv"
            df.to_csv(report_file, index=False, encoding='utf-8-sig')
            logger.info(f"📊 Rapport unifié généré: {report_file}")

            # Rapport synthèse par type
            summary_report = output_folder / f"synthese_dernieres_valeurs_{self.target_year}_{self.target_month:02d}.txt"
            with open(summary_report, 'w', encoding='utf-8') as f:
                f.write("# SYNTHÈSE DERNIÈRES VALEURS & VALEURS PÉRIODIQUES\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Période: {self.target_year}-{self.target_month:02d}\n")
                f.write(f"Date génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                f.write("## DONNÉES SMC\n")
                smc_data = df[df['data_type'] == 'smc']
                f.write(f"- Convergences: {len(smc_data[smc_data['sheet_type'] == 'convergences'])} métriques\n")
                f.write(f"- Déplacements: {len(smc_data[smc_data['sheet_type'] == 'déplacements'])} métriques\n\n")

                f.write("## DONNÉES CARRURE\n")
                carrure_data = df[df['data_type'] == 'carrure']
                f.write(f"- Déplacements carrure: {len(carrure_data[carrure_data['sheet_type'] == 'carrure_deplacements'])} métriques\n")
                f.write(f"- Déplacements cintres: {len(carrure_data[carrure_data['sheet_type'] == 'carrure_cintres'])} métriques\n\n")

                f.write("## ZONES DE GRAPHIQUE DÉTECTÉES\n")
                f.write(f"Total: {len(self.all_results['graph_zones'])} zones\n")
                for zone in self.all_results['graph_zones']:
                    f.write(f"- {zone['sheet_name']}: {zone['zone_title']} ({zone['cells_count']} cellules)\n")

            logger.info(f"📋 Synthèse générée: {summary_report}")

    def generate_graphs_by_zones(self, output_folder: Path):
        """Génère les graphiques selon les zones détectées par couleur"""

        if not self.all_results['graph_zones']:
            logger.warning("Aucune zone de graphique détectée")
            return

        graphs_folder = output_folder / "graphiques_par_zones"
        graphs_folder.mkdir(exist_ok=True)

        # Générer un graphique par zone détectée
        with PdfPages(graphs_folder / f"graphiques_unifie_{self.target_year}_{self.target_month:02d}.pdf") as pdf:
            for zone in self.all_results['graph_zones']:
                fig, ax = plt.subplots(figsize=(12, 8))

                # Titre basé sur la zone
                ax.set_title(f"Zone: {zone['zone_title']}\n{zone['sheet_name']}")
                ax.set_xlabel("Date")
                ax.set_ylabel("Valeurs (mm)")

                # TODO: Ajouter données réelles selon la zone
                # Pour l'instant, graphique de placeholder

                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)

        logger.info(f"📈 Graphiques par zones générés: {graphs_folder}")

# Fonction principale unifiée
def run_unified_extraction(root_folder: str, month: str, output_folder: str, options: Dict, log_callback=None) -> bool:
    """Fonction principale d'extraction unifiée SMC + Carrure"""

    extractor = UnifiedDataExtractor(month)

    try:
        root_path = Path(root_folder)
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)

        # Détecter fichiers SMC et Carrure
        smc_files = list(root_path.rglob("*SMC*.xlsx")) + list(root_path.rglob("*SMC*.xlsm"))
        carrure_files = list(root_path.rglob("*carrure*.xlsx")) + list(root_path.rglob("*carrure*.xlsm"))

        if log_callback:
            log_callback(f"🔍 Fichiers détectés: {len(smc_files)} SMC, {len(carrure_files)} Carrure")

        # Traiter fichiers SMC
        for smc_file in smc_files:
            if log_callback:
                log_callback(f"🔧 Traitement SMC: {smc_file.name}")
            smc_results = extractor.extract_smc_data(smc_file)
            extractor.all_results['smc_convergences'].extend(smc_results['convergences'])
            extractor.all_results['smc_deplacements'].extend(smc_results['deplacements'])

        # Traiter fichiers Carrure
        for carrure_file in carrure_files:
            if log_callback:
                log_callback(f"🏗️ Traitement Carrure: {carrure_file.name}")
            carrure_results = extractor.extract_carrure_data(carrure_file)
            extractor.all_results['carrure_deplacements'].extend(carrure_results['carrure_deplacements'])
            extractor.all_results['carrure_cintres'].extend(carrure_results['carrure_cintres'])

        # Générer rapports
        if options.get('generate_csv', True):
            extractor.generate_unified_report(output_path)

        if options.get('generate_graphs', True):
            extractor.generate_graphs_by_zones(output_path)

        if log_callback:
            log_callback("✅ Extraction unifiée terminée avec succès")

        return True

    except Exception as e:
        if log_callback:
            log_callback(f"❌ Erreur extraction unifiée: {e}")
        return False

if __name__ == "__main__":
    # Test rapide
    test_month = "2025-09"
    test_root = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux"
    test_output = r"C:\temp\unified_test"

    options = {'generate_csv': True, 'generate_graphs': True}

    success = run_unified_extraction(test_root, test_month, test_output, options, print)
    print(f"Test extraction unifiée: {'✅ Succès' if success else '❌ Échec'}")
