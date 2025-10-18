#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMC Excel Native Print to PDF - Version conforme aux spécifications
Imprime Convergences, Déplacements et Graphiques avec détection automatique des zones
"""

import win32com.client as win32
from pathlib import Path
import time
import os
from typing import List, Optional, Tuple
import re

class SMCExcelNativePrinter:
    """Imprimante PDF conforme aux spécifications avec détection automatique des zones"""
    
    def __init__(self, output_folder: str, month: str):
        self.output_folder = Path(output_folder)
        self.month = month
        self.excel_app = None
        
    def start_excel(self):
        """Démarre Excel en mode automatisation"""
        try:
            self.excel_app = win32.Dispatch("Excel.Application")
            self.excel_app.Visible = False
            self.excel_app.DisplayAlerts = False
            self.excel_app.ScreenUpdating = False
            self.excel_app.EnableEvents = False
            print("✅ Excel démarré")
            return True
        except Exception as e:
            print(f"❌ Erreur démarrage Excel: {e}")
            return False
    
    def close_excel(self):
        """Ferme Excel proprement"""
        if self.excel_app:
            try:
                self.excel_app.Quit()
                self.excel_app = None
                print("✅ Excel fermé")
            except:
                pass
    
    def extract_galerie_section(self, file_path: Path) -> tuple:
        """Extrait galerie et section depuis le nom de fichier"""
        file_name = file_path.stem.upper()
        
        galerie_pattern = re.compile(r'([A-Z]{3})')
        galerie_matches = galerie_pattern.findall(file_name)
        galerie = galerie_matches[0] if galerie_matches else "UNKNOWN"
        
        section_pattern = re.compile(r'([CT]\d{2,3})')
        section_matches = section_pattern.findall(file_name)
        section = section_matches[0] if section_matches else "UNKNOWN"
        
        return galerie, section
    
    def detect_table_print_area(self, worksheet, sheet_name=None) -> Optional[str]:
        """Détecte la zone d'impression pour les tableaux basée sur la fusion A5"""
        try:
            print(f"🔍 Détection zone tableau ({sheet_name}) via cellule fusionnée A5...")
            
            # ✅ NOUVELLE LOGIQUE: Détecter la largeur via la fusion A5
            a5_cell = worksheet.Cells(5, 1)  # Cellule A5
            
            # Vérifier si A5 est fusionnée
            if a5_cell.MergeCells:
                merge_area = a5_cell.MergeArea
                merge_start_col = merge_area.Column
                merge_end_col = merge_area.Column + merge_area.Columns.Count - 1
                print(f"   🎯 A5 fusionnée détectée: C{merge_start_col} à C{merge_end_col}")
                print(f"   📏 Largeur fusion: {merge_area.Columns.Count} colonnes")
                
                # Utiliser la largeur de la fusion comme référence
                detected_width = merge_end_col
                print(f"   📊 Largeur zone détectée: {detected_width} colonnes")
            else:
                print("   ⚠️ A5 non fusionnée, scan manuel des métriques...")
                # Fallback: scan manuel limité
                detected_width = min(30, worksheet.UsedRange.Columns.Count)
            
            # Rechercher R_title = ligne contenant DATE/JOUR/HEURE
            r_title = None
            for row in range(6, min(15, worksheet.UsedRange.Rows.Count + 1)):  # Commencer après A5
                for col in range(1, min(8, detected_width + 1)):
                    cell_value = worksheet.Cells(row, col).Value
                    if cell_value and isinstance(cell_value, str):
                        cell_upper = cell_value.upper()
                        if any(keyword in cell_upper for keyword in ['DATE', 'JOUR', 'HEURE', 'TEMPS']):
                            r_title = row
                            print(f"   🎯 Ligne titre: R{row} - '{cell_value}'")
                            break
                if r_title:
                    break
            
            if not r_title:
                print("⚠️ Ligne titre non trouvée")
                return None
            
            # Zone de départ
            r_start = 1
            c_start = 1
            
            # ✅ NOUVELLE LOGIQUE: C_end basé sur la largeur de fusion A5
            if a5_cell.MergeCells:
                c_end = detected_width
                print(f"   📐 Zone finale basée sur fusion A5: C{c_start} à C{c_end}")
            else:
                # Fallback: détection manuelle des métriques
                print("   🔍 Fallback: détection manuelle des métriques...")
                c_end = c_start
                metric_keywords = ['BG', 'HG', 'HD', 'BD', 'LH', 'LB', 'DPM', 'DH', 'DZ']
                
                # Colonnes à exclure pour les Déplacements
                excluded_columns = []
                if sheet_name == 'Déplacements':
                    excluded_columns = ['DZ CENTRE HAUT X2', 'VITESSE EVOL', 'INTERPOLÉ']
                    print(f"   ⚠️ Exclusions Déplacements: {excluded_columns}")
                
                for col in range(c_start, min(detected_width + 1, worksheet.UsedRange.Columns.Count + 1)):
                    cell_value = worksheet.Cells(r_title, col).Value
                    if cell_value and isinstance(cell_value, str):
                        cell_upper = cell_value.upper()
                        
                        # Vérifier si c'est une métrique reconnue
                        if any(metric in cell_upper for metric in metric_keywords):
                            # Exclure les colonnes indésirables pour Déplacements
                            if sheet_name == 'Déplacements':
                                should_exclude = any(excl in cell_upper for excl in excluded_columns)
                                if should_exclude:
                                    print(f"   ❌ Colonne exclue: C{col} - '{cell_value}'")
                                    continue
                        
                            c_end = col
                            print(f"   ✅ Métrique: C{col} - '{cell_value}'")
            
            print(f"📊 Zone colonnes finale: C{c_start} à C{c_end} ({c_end - c_start + 1} colonnes)")
            
            # Détection dernière ligne (optimisée)
            print("🔍 Recherche dernière ligne avec données...")
            
            # Trouver colonne de date
            date_col = 1
            for col in range(1, min(6, c_end + 1)):
                cell_value = worksheet.Cells(r_title, col).Value
                if cell_value and isinstance(cell_value, str):
                    if any(keyword in cell_value.upper() for keyword in ['DATE', 'TEMPS', 'JOUR']):
                        date_col = col
                        print(f"   📅 Colonne date: C{col}")
                        break
            
            # Scan optimisé des lignes
            max_scan = min(200, worksheet.UsedRange.Rows.Count + 1)
            last_data_row = r_title
            
            for row in range(r_title + 1, max_scan):
                has_data = False
                
                # Vérifier quelques colonnes clés dans la largeur détectée
                test_cols = [date_col, min(c_start + 2, c_end), min(c_start + 5, c_end), c_end]
                for col in test_cols:
                    if col <= c_end and col >= c_start:
                        cell_value = worksheet.Cells(row, col).Value
                        if cell_value is not None:
                            if isinstance(cell_value, (int, float)) and cell_value != 0:
                                has_data = True
                                break
                            elif isinstance(cell_value, str) and len(cell_value.strip()) > 0:
                                has_data = True
                                break
                            elif hasattr(cell_value, 'year'):  # datetime
                                has_data = True
                                break
                
                if has_data:
                    last_data_row = row
                
                # Log périodique
                if row % 50 == 0:
                    print(f"   🔍 Scan ligne {row}...")
            
            r_end = last_data_row
            print(f"   📊 Ligne finale: R{r_end}")
            
            # Construction zone finale
            start_cell = worksheet.Cells(r_start, c_start)
            end_cell = worksheet.Cells(r_end, c_end)
            
            start_address = start_cell.Address.replace('$', '')
            end_address = end_cell.Address.replace('$', '')
            print_area = f"{start_address}:{end_address}"
            
            print(f"✅ Zone tableau détectée: {print_area}")
            print(f"   📏 Dimensions: {r_end - r_start + 1} lignes × {c_end - c_start + 1} colonnes")
            print(f"   🎯 Basée sur fusion A5: {a5_cell.MergeCells}")
            
            return print_area
            
        except Exception as e:
            print(f"❌ Erreur détection: {e}")
            import traceback
            traceback.print_exc()
            return None
    
   
    def is_color_frame(self, worksheet, start_row: int, start_col: int, end_row: int, end_col: int, target_color) -> bool:
        """Vérifie si les bordures forment un encadrement - VERSION STRICTE"""
        try:
            print(f"      🔍 Test encadrement R{start_row}:R{end_row} × C{start_col}:C{end_col}")
            
            # Vérifier bordure supérieure (toutes les cellules)
            for col in range(start_col, end_col + 1):
                cell_color = worksheet.Cells(start_row, col).Interior.Color
                if cell_color != target_color:
                    print(f"      ❌ Bordure sup C{col}: #{cell_color:x} ≠ #{target_color:x}")
                    return False
            
            # Vérifier bordure inférieure (toutes les cellules)
            for col in range(start_col, end_col + 1):
                cell_color = worksheet.Cells(end_row, col).Interior.Color
                if cell_color != target_color:
                    print(f"      ❌ Bordure inf C{col}: #{cell_color:x} ≠ #{target_color:x}")
                    return False
            
            # Vérifier bordure gauche (toutes les cellules)
            for row in range(start_row, end_row + 1):
                cell_color = worksheet.Cells(row, start_col).Interior.Color
                if cell_color != target_color:
                    print(f"      ❌ Bordure gauche R{row}: #{cell_color:x} ≠ #{target_color:x}")
                    return False
            
            # Vérifier bordure droite (toutes les cellules)
            for row in range(start_row, end_row + 1):
                cell_color = worksheet.Cells(row, end_col).Interior.Color
                if cell_color != target_color:
                    print(f"      ❌ Bordure droite R{row}: #{cell_color:x} ≠ #{target_color:x}")
                    return False
            
            print(f"      ✅ Bordures OK, test intérieur...")
            
            # Vérifier que l'intérieur est différent
            center_row = (start_row + end_row) // 2
            center_col = (start_col + end_col) // 2
            
            if start_row < center_row < end_row and start_col < center_col < end_col:
                interior_color = worksheet.Cells(center_row, center_col).Interior.Color
                interior_different = (interior_color != target_color)
                
                print(f"      💡 Centre R{center_row}C{center_col}: #{interior_color:x}, différent: {interior_different}")
                
                return interior_different
            
            return False
            
        except Exception as e:
            print(f"      ⚠️ Erreur vérification encadrement: {e}")
            return False
    
    def print_worksheet_to_pdf(self, file_path: Path, sheet_name: str, zone_info=None) -> Optional[str]:
        """Imprime une feuille Excel en PDF avec détection automatique des zones"""
        
        if not self.excel_app:
            return None
        
        try:
            workbook = self.excel_app.Workbooks.Open(str(file_path), ReadOnly=True)
            
            # Vérifier que la feuille existe
            sheet_names = [ws.Name for ws in workbook.Worksheets]
            if sheet_name not in sheet_names:
                print(f"⚠️ Feuille '{sheet_name}' non trouvée")
                workbook.Close(SaveChanges=False)
                return None
            
            worksheet = workbook.Worksheets(sheet_name)
            worksheet.Activate()
            
            # Détecter la zone d'impression selon le type de feuille
            if sheet_name in ['Convergences', 'Déplacements']:
                print_area = self.detect_table_print_area(worksheet, sheet_name)
                orientation = 2
                fit_width = 1
                fit_height = False
                use_title_rows = True
            elif 'Graphique' in sheet_name:
                # ✅ POUR LES GRAPHIQUES: Utiliser zone_info si fournie
                if zone_info:
                    print_area = zone_info['address']
                    print(f"🎯 Zone graphique individuelle: {print_area}")
                    orientation = 2  # Paysage
                    fit_width = 1
                    fit_height = 1
                    use_title_rows = False
                else:
                    # Fallback: zone par défaut si pas de zone_info
                    print_area = "A1:T30"
                    print(f"⚠️ Pas de zone spécifique, utilisation zone par défaut: {print_area}")
                    orientation = 2
                    fit_width = 1
                    fit_height = 1
                    use_title_rows = False
            else:
                print_area = None
                orientation = 2
                fit_width = 1
                fit_height = False
                use_title_rows = False
            
            # ✅ DEBUG: Voir l'état avant modification
            print(f"🔍 AVANT config - PrintArea: '{worksheet.PageSetup.PrintArea}'")
            print(f"🔍 AVANT config - PrintTitleRows: '{worksheet.PageSetup.PrintTitleRows}'")
            
            # Configurer la zone d'impression
            if print_area:
                print(f"🔧 Application zone d'impression: {print_area}")
                
                # ✅ SOLUTION: Configurer PrintTitleRows AVANT PrintArea
                if use_title_rows:
                    worksheet.PageSetup.PrintTitleRows = "$1:$9"
                    print(f"📋 En-têtes répétés: lignes 1 à 9 (tableaux)")
                else:
                    # ✅ CRUCIAL: Vider PrintTitleRows pour les graphiques
                    worksheet.PageSetup.PrintTitleRows = ""
                    print(f"📋 Pas de répétition d'en-têtes (graphiques)")
                
                # Appliquer la zone d'impression APRÈS avoir configuré PrintTitleRows
                worksheet.PageSetup.PrintArea = print_area
                
                # Vérification finale
                applied_area = worksheet.PageSetup.PrintArea
                print(f"✅ Zone finale appliquée: {applied_area}")
                print(f"🔍 PrintTitleRows final: '{worksheet.PageSetup.PrintTitleRows}'")
                
            else:
                print("⚠️ Aucune zone d'impression détectée")
            
            # Configuration page
            page_setup = worksheet.PageSetup
            page_setup.Orientation = orientation
            page_setup.PaperSize = 9
            page_setup.LeftMargin = self.excel_app.InchesToPoints(0.79)
            page_setup.RightMargin = self.excel_app.InchesToPoints(0.79)
            page_setup.TopMargin = self.excel_app.InchesToPoints(0.79)
            page_setup.BottomMargin = self.excel_app.InchesToPoints(0.79)
            
            page_setup.Zoom = False
            page_setup.FitToPagesWide = fit_width
            if fit_height:
                page_setup.FitToPagesTall = fit_height
            else:
                page_setup.FitToPagesTall = False
            
            page_setup.PrintHeadings = False
            page_setup.PrintGridlines = False
            
            # Nom du fichier PDF
            galerie, section = self.extract_galerie_section(file_path)
            if zone_info:
                pdf_name = f"{file_path.stem}_{sheet_name}_{zone_info['name']}-A4_landscape_marged.pdf"
            else:
                pdf_name = f"{file_path.stem}_{sheet_name}-A4_landscape_marged.pdf"
            
            pdf_path = self.output_folder / pdf_name
            
            # Exporter en PDF
            worksheet.ExportAsFixedFormat(Type=0, Filename=str(pdf_path))
            workbook.Close(SaveChanges=False)
            
            print(f"✅ PDF créé: {pdf_name}")
            return str(pdf_path)
            
        except Exception as e:
            print(f"❌ Erreur impression: {e}")
            try:
                workbook.Close(SaveChanges=False)
            except:
                pass
            return None
    
    def print_excel_file(self, file_path: Path, log_callback=None) -> List[str]:
        """Imprime toutes les feuilles d'un fichier Excel"""
        
        pdf_files = []
        
        try:
            workbook = self.excel_app.Workbooks.Open(str(file_path), ReadOnly=True)
            sheet_names = [ws.Name for ws in workbook.Worksheets]
            workbook.Close(SaveChanges=False)
            
            # Traiter chaque feuille
            for sheet_name in sheet_names:
                if sheet_name in ['Convergences', 'Déplacements']:
                    # Tableaux: 1 PDF par feuille
                    pdf_path = self.print_worksheet_to_pdf(file_path, sheet_name)
                    if pdf_path:
                        pdf_files.append(pdf_path)
                        
                elif 'Graphique' in sheet_name:
                    # ✅ GRAPHIQUES: Détecter toutes les zones et imprimer séparément
                    workbook = self.excel_app.Workbooks.Open(str(file_path), ReadOnly=True)
                    worksheet = workbook.Worksheets(sheet_name)
                    
                    # Détecter toutes les zones graphiques INDIVIDUELLES
                    all_zones = self.detect_all_graph_zones(worksheet)
                    workbook.Close(SaveChanges=False)
                    
                    if all_zones:
                        print(f"🎯 {len(all_zones)} zones graphiques trouvées dans {sheet_name}")
                        
                        # Imprimer chaque zone séparément
                        for zone_info in all_zones:
                            if log_callback:
                                log_callback(f"   📊 Zone {zone_info['name']}: {zone_info['address']}")
                            
                            pdf_path = self.print_worksheet_to_pdf(file_path, sheet_name, zone_info)
                            if pdf_path:
                                pdf_files.append(pdf_path)
                    else:
                        # Si aucune zone détectée, imprimer la feuille complète
                        print(f"⚠️ Aucune zone détectée, impression complète de {sheet_name}")
                        pdf_path = self.print_worksheet_to_pdf(file_path, sheet_name)
                        if pdf_path:
                            pdf_files.append(pdf_path)
        
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Erreur: {e}")
        
        return pdf_files

    def detect_all_graph_zones(self, worksheet) -> List[dict]:
        """Version améliorée - retourne chaque zone individuellement"""
        try:
            print("🔍 Détection zones graphiques individuelles...")
            
            # Constantes VBA
            MAX_ROW = 256
            MAX_COL = 128
            LIG_TEST = 15
            COL_TEST = 5
            
            # Couleur de référence
            couleur_ref = worksheet.Cells(1, 1).Interior.Color
            
            # Recherche des séparateurs
            tab_lig_sep = []
            tab_col_sep = []
            
            # Lignes colorées
            for i in range(1, MAX_ROW + 1):
                try:
                    if worksheet.Cells(i, LIG_TEST).Interior.Color == couleur_ref:
                        tab_lig_sep.append(i)
                except:
                    pass
            
            # Colonnes colorées
            for i in range(1, MAX_COL + 1):
                try:
                    if worksheet.Cells(COL_TEST, i).Interior.Color == couleur_ref:
                        tab_col_sep.append(i)
                except:
                    pass
            
            print(f"📊 {len(tab_lig_sep)} lignes × {len(tab_col_sep)} colonnes")
            
            # Créer les zones
            zones = []
            
            for j in range(1, len(tab_lig_sep)):
                for i in range(1, len(tab_col_sep)):
                    r1 = tab_lig_sep[j - 1] + 1
                    r2 = tab_lig_sep[j] - 1
                    c1 = tab_col_sep[i - 1] + 1
                    c2 = tab_col_sep[i] - 1
                    
                    if r1 <= r2 and c1 <= c2:
                        start_cell = worksheet.Cells(r1, c1)
                        end_cell = worksheet.Cells(r2, c2)
                        
                        zones.append({
                            'address': f"{start_cell.Address}:{end_cell.Address}",
                            'name': f"Zone_{j}_{i}",
                            'start_row': r1,
                            'end_row': r2,
                            'start_col': c1,
                            'end_col': c2
                        })
            
            return zones
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []
    
def print_excel_files_native(root_folder: str, output_folder: str, month: str, log_callback=None) -> bool:
    """Fonction principale d'impression native Excel vers PDF conforme aux spécifications"""
    
    if log_callback:
        log_callback("🖨️ Impression native Excel vers PDF (spécifications complètes)...")
    
    # Créer le dossier de sortie
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Scanner les fichiers SMC
    root_path = Path(root_folder)
    excel_files = []
    
    for file_path in root_path.rglob("*.xlsm"):
        if 'SMC' in file_path.name.upper():
            excel_files.append(file_path)
    
    if not excel_files:
        if log_callback:
            log_callback("❌ Aucun fichier SMC trouvé")
        return False
    
    if log_callback:
        log_callback(f"📊 {len(excel_files)} fichiers SMC trouvés")
    
    # Initialiser l'imprimante
    printer = SMCExcelNativePrinter(output_folder, month)
    
    try:
        # Démarrer Excel
        if not printer.start_excel():
            if log_callback:
                log_callback("❌ Impossible de démarrer Excel")
            return False
        
        all_pdf_files = []
        
        # Traiter chaque fichier
        for i, file_path in enumerate(excel_files, 1):
            if log_callback:
                log_callback(f"📈 Traitement {i}/{len(excel_files)}: {file_path.name}")
            
            pdf_files = printer.print_excel_file(file_path, log_callback)
            all_pdf_files.extend(pdf_files)
            
            # Petite pause entre les fichiers
            time.sleep(1)
        
        if log_callback:
            log_callback("")
            log_callback(f"🎉 IMPRESSION TERMINÉE!")
            log_callback(f"📄 {len(all_pdf_files)} PDF générés")
            log_callback(f"📁 Dossier: {output_folder}")
        
        return True
        
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Erreur: {str(e)}")
        return False
        
    finally:
        # Toujours fermer Excel
        printer.close_excel()

if __name__ == "__main__":
    # Test
    root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250901-rapport mensuel aout\1-tableaux"
    output_folder = r"C:\temp\smc_output"
    month = "2025-08"
    
    print_excel_files_native(root_folder, output_folder, month)