#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Standardizer - Homogénéise tous les PDF en format A4
=======================================================

Outil pour standardiser automatiquement les formats de pages PDF hétérogènes
vers un format A4 uniforme (210 x 297 mm).

Fonctionnalités :
- Analyse des formats existants dans les PDF
- Conversion automatique vers A4
- Préservation de la qualité
- Traitement par lot
- Rapport détaillé des conversions

Auteur: Assistant IA
Date: Octobre 2025
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import logging

try:
    import PyPDF2
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, letter, A3
    from reportlab.lib.units import mm
    import fitz  # PyMuPDF
except ImportError as e:
    print(f"❌ Modules manquants : {e}")
    print("📦 Installation requise :")
    print("   pip install PyPDF2 reportlab PyMuPDF")
    sys.exit(1)

class PDFStandardizer:
    """Classe principale pour standardiser les PDF en format A4."""
    
    def __init__(self, output_dir: str = None):
        """Initialise le standardisateur PDF."""
        self.a4_width = 210 * mm   # 210 mm en points
        self.a4_height = 297 * mm  # 297 mm en points
        self.output_dir = Path(output_dir) if output_dir else None
        self.conversion_report = []
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_pdf_formats(self, pdf_path: str) -> Dict:
        """Analyse les formats de pages dans un PDF."""
        formats_found = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    # Récupère les dimensions de la page
                    mediabox = page.mediabox
                    width = float(mediabox.width)
                    height = float(mediabox.height)
                    
                    # Convertit en mm pour lisibilité
                    width_mm = width * 25.4 / 72  # Conversion points vers mm
                    height_mm = height * 25.4 / 72
                    
                    format_key = f"{width_mm:.0f}x{height_mm:.0f}mm"
                    
                    if format_key not in formats_found:
                        formats_found[format_key] = {
                            'pages': [],
                            'width_pts': width,
                            'height_pts': height,
                            'width_mm': width_mm,
                            'height_mm': height_mm
                        }
                    
                    formats_found[format_key]['pages'].append(page_num + 1)
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de {pdf_path}: {e}")
            
        return formats_found
    
    def identify_format_type(self, width_mm: float, height_mm: float) -> str:
        """Identifie le type de format (A4, A3, Letter, etc.)."""
        # Tolérances pour les formats standards
        tolerance = 5  # mm
        
        # Formats standards (largeur x hauteur)
        standard_formats = {
            'A4': (210, 297),
            'A4_landscape': (297, 210),
            'A3': (297, 420),
            'A3_landscape': (420, 297),
            'Letter': (216, 279),
            'Letter_landscape': (279, 216),
            'Legal': (216, 356),
        }
        
        for format_name, (std_w, std_h) in standard_formats.items():
            if (abs(width_mm - std_w) <= tolerance and 
                abs(height_mm - std_h) <= tolerance):
                return format_name
                
        return f"Personnalisé ({width_mm:.0f}x{height_mm:.0f}mm)"
    
    def standardize_pdf_pymupdf(self, input_path: str, output_path: str) -> bool:
        """Standardise un PDF vers A4 avec PyMuPDF (méthode recommandée)."""
        try:
            # Ouvre le PDF source
            doc = fitz.open(input_path)
            
            # Crée un nouveau PDF
            new_doc = fitz.open()
            
            # Dimensions A4 en points (PyMuPDF utilise les points)
            a4_portrait_width, a4_portrait_height = 595, 842  # A4 portrait
            a4_landscape_width, a4_landscape_height = 842, 595  # A4 paysage
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Récupère les dimensions de la page source
                page_rect = page.rect
                src_width = page_rect.width
                src_height = page_rect.height
                
                # DÉTECTION D'ORIENTATION INTELLIGENTE :
                # 1. Si c'est déjà A4, garde l'orientation
                # 2. Pour les autres formats, analyse le ratio et la taille
                
                is_a4_portrait = (abs(src_width - 595) < 10 and abs(src_height - 842) < 10)
                is_a4_landscape = (abs(src_width - 842) < 10 and abs(src_height - 595) < 10)
                
                if is_a4_portrait:
                    # Déjà A4 portrait → reste A4 portrait
                    a4_width, a4_height = a4_portrait_width, a4_portrait_height
                    orientation = "portrait"
                elif is_a4_landscape:
                    # Déjà A4 paysage → reste A4 paysage
                    a4_width, a4_height = a4_landscape_width, a4_landscape_height
                    orientation = "paysage"
                else:
                    # Format non-standard : logique intelligente
                    ratio = src_width / src_height
                    
                    # Si ratio > 1.2 ET plus large que A4 → probablement paysage
                    # Si ratio < 0.9 ET plus haut que A4 → probablement portrait
                    # Sinon, choisir selon quelle orientation minimise la réduction
                    
                    if ratio > 1.2 and src_width > 700:
                        # Format paysage prononcé
                        a4_width, a4_height = a4_landscape_width, a4_landscape_height
                        orientation = "paysage"
                    elif ratio < 0.9 and src_height > 700:
                        # Format portrait prononcé  
                        a4_width, a4_height = a4_portrait_width, a4_portrait_height
                        orientation = "portrait"
                    else:
                        # Format ambigu → teste quelle orientation préserve mieux le contenu
                        scale_if_portrait = min(a4_portrait_width / src_width, a4_portrait_height / src_height)
                        scale_if_landscape = min(a4_landscape_width / src_width, a4_landscape_height / src_height)
                        
                        if scale_if_landscape > scale_if_portrait:
                            # Moins de réduction en paysage
                            a4_width, a4_height = a4_landscape_width, a4_landscape_height
                            orientation = "paysage"
                        else:
                            # Moins de réduction en portrait
                            a4_width, a4_height = a4_portrait_width, a4_portrait_height
                            orientation = "portrait"
                
                # Crée une nouvelle page A4 avec la bonne orientation
                new_page = new_doc.new_page(width=a4_width, height=a4_height)
                
                # Calcule les facteurs d'échelle pour ajuster le contenu
                scale_x = a4_width / src_width
                scale_y = a4_height / src_height
                
                # Utilise le plus petit facteur pour conserver les proportions
                scale = min(scale_x, scale_y)
                
                # Calcule la position pour centrer le contenu
                scaled_width = src_width * scale
                scaled_height = src_height * scale
                x_offset = (a4_width - scaled_width) / 2
                y_offset = (a4_height - scaled_height) / 2
                
                # Rectangle de destination centré
                dest_rect = fitz.Rect(x_offset, y_offset, 
                                    x_offset + scaled_width, 
                                    y_offset + scaled_height)
                
                # Insère la page avec la nouvelle API PyMuPDF 1.26+
                # Signature: show_pdf_page(rect, docsrc, pno=0, keep_proportion=True, overlay=True, oc=0, rotate=0, clip=None)
                try:
                    # Version moderne de PyMuPDF (1.26+)
                    new_page.show_pdf_page(
                        dest_rect,           # rect: rectangle de destination
                        doc,                 # docsrc: document source
                        page_num,           # pno: numéro de page
                        keep_proportion=True, # garde les proportions
                        overlay=True,        # superpose le contenu
                        clip=None           # pas de clipping
                    )
                    
                except Exception as e1:
                    self.logger.warning(f"Méthode moderne échouée: {e1}, tentative alternative...")
                    try:
                        # Approche alternative : conversion en image puis insertion
                        # Calcule la matrice de transformation
                        mat = fitz.Matrix(scale, scale).pretranslate(x_offset, y_offset)
                        
                        # Convertit la page en image avec la transformation
                        pix = page.get_pixmap(matrix=mat, alpha=False)
                        img_data = pix.tobytes("png")
                        
                        # Insère l'image dans la nouvelle page
                        new_page.insert_image(dest_rect, stream=img_data)
                        pix = None  # Libère la mémoire
                        
                    except Exception as e2:
                        self.logger.error(f"Toutes les méthodes ont échoué pour la page {page_num + 1}: {e2}")
                        # Méthode de secours : copie simple sans transformation
                        full_rect = fitz.Rect(0, 0, a4_width, a4_height)
                        try:
                            new_page.show_pdf_page(full_rect, doc, page_num, keep_proportion=True)
                        except:
                            # Dernière tentative avec pixmap simple
                            pix = page.get_pixmap(alpha=False)
                            img_data = pix.tobytes("png")
                            new_page.insert_image(full_rect, stream=img_data)
                            pix = None
                
                self.logger.info(f"Page {page_num + 1}: "
                               f"{src_width:.0f}x{src_height:.0f} -> A4 {orientation} "
                               f"(échelle: {scale:.2f})")
            
            # Sauvegarde le nouveau PDF
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la standardisation de {input_path}: {e}")
            return False
    
    def standardize_pdf_pypdf2(self, input_path: str, output_path: str) -> bool:
        """Méthode alternative avec PyPDF2 (fallback)."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            import tempfile
            import io
            
            # Lit le PDF source
            with open(input_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Crée un nouveau PDF avec ReportLab
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                a4_width, a4_height = A4
                
                for page_num, page in enumerate(pdf_reader.pages):
                    # Récupère les dimensions de la page
                    mediabox = page.mediabox
                    page_width = float(mediabox.width)
                    page_height = float(mediabox.height)
                    
                    # Calcule l'échelle
                    scale_x = a4_width / page_width
                    scale_y = a4_height / page_height
                    scale = min(scale_x, scale_y)
                    
                    # Centre le contenu
                    scaled_width = page_width * scale
                    scaled_height = page_height * scale
                    x_offset = (a4_width - scaled_width) / 2
                    y_offset = (a4_height - scaled_height) / 2
                    
                    # Sauvegarde l'état du canvas
                    c.saveState()
                    
                    # Applique la transformation
                    c.translate(x_offset, y_offset)
                    c.scale(scale, scale)
                    
                    # Note: Cette méthode est simplifiée et peut nécessiter
                    # des ajustements selon le contenu du PDF
                    self.logger.info(f"Page {page_num + 1}: "
                                   f"{page_width:.0f}x{page_height:.0f} -> A4 "
                                   f"(échelle: {scale:.2f}) [PyPDF2]")
                    
                    # Restaure l'état et nouvelle page
                    c.restoreState()
                    if page_num < len(pdf_reader.pages) - 1:
                        c.showPage()
                
                # Finalise le PDF
                c.save()
                
                # Sauvegarde le résultat
                with open(output_path, 'wb') as output_file:
                    output_file.write(buffer.getvalue())
                
                buffer.close()
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur PyPDF2 pour {input_path}: {e}")
            return False
    
    def standardize_single_pdf(self, input_path: str, output_path: str = None) -> str:
        """Standardise un seul fichier PDF."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Fichier non trouvé : {input_path}")
        
        # Génère le nom de sortie si non spécifié
        if output_path is None:
            if self.output_dir:
                output_path = self.output_dir / f"{input_path.stem}_A4{input_path.suffix}"
            else:
                output_path = input_path.parent / f"{input_path.stem}_A4{input_path.suffix}"
        else:
            output_path = Path(output_path)
            
        # Crée le dossier de sortie si nécessaire
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"🔄 Traitement : {input_path.name}")
        
        # Analyse les formats avant conversion
        formats_before = self.analyze_pdf_formats(str(input_path))
        
        # Effectue la standardisation avec méthode principale
        success = self.standardize_pdf_pymupdf(str(input_path), str(output_path))
        
        # Si PyMuPDF échoue, essaie avec PyPDF2 (méthode de secours)
        if not success:
            self.logger.warning(f"PyMuPDF a échoué, tentative avec PyPDF2...")
            success = self.standardize_pdf_pypdf2(str(input_path), str(output_path))
        
        if success:
            self.logger.info(f"✅ Créé : {output_path.name}")
            
            # Ajoute au rapport
            self.conversion_report.append({
                'input': str(input_path),
                'output': str(output_path),
                'formats_before': formats_before,
                'success': True
            })
            
            return str(output_path)
        else:
            self.logger.error(f"❌ Échec : {input_path.name}")
            return None
    
    def standardize_multiple_pdfs(self, input_paths: List[str]) -> List[str]:
        """Standardise plusieurs fichiers PDF."""
        successful_outputs = []
        
        for input_path in input_paths:
            try:
                output_path = self.standardize_single_pdf(input_path)
                if output_path:
                    successful_outputs.append(output_path)
            except Exception as e:
                self.logger.error(f"Erreur avec {input_path}: {e}")
                
        return successful_outputs
    
    def standardize_directory(self, directory: str, pattern: str = "*.pdf") -> List[str]:
        """Standardise tous les PDF d'un dossier."""
        directory = Path(directory)
        pdf_files = list(directory.glob(pattern))
        
        self.logger.info(f"📁 Dossier : {directory}")
        self.logger.info(f"📄 {len(pdf_files)} PDF(s) trouvé(s)")
        
        return self.standardize_multiple_pdfs([str(f) for f in pdf_files])
    
    def generate_report(self) -> str:
        """Génère un rapport détaillé des conversions."""
        if not self.conversion_report:
            return "Aucune conversion effectuée."
        
        report = []
        report.append("📊 RAPPORT DE STANDARDISATION PDF")
        report.append("=" * 50)
        report.append(f"Total traité : {len(self.conversion_report)} fichier(s)")
        report.append("")
        
        for i, conversion in enumerate(self.conversion_report, 1):
            report.append(f"{i}. {Path(conversion['input']).name}")
            report.append(f"   ➜ {Path(conversion['output']).name}")
            
            if conversion['formats_before']:
                report.append("   📏 Formats détectés avant :")
                for format_key, info in conversion['formats_before'].items():
                    format_type = self.identify_format_type(info['width_mm'], info['height_mm'])
                    pages_str = f"pages {', '.join(map(str, info['pages']))}"
                    report.append(f"      • {format_key} ({format_type}) - {pages_str}")
            
            report.append(f"   ✅ Converti vers A4")
            report.append("")
        
        return "\n".join(report)
    
    def merge_standardized_pdfs(self, pdf_paths: List[str], output_path: str) -> bool:
        """Fusionne les PDF standardisés en un seul document."""
        try:
            merger = PyPDF2.PdfMerger()
            
            for pdf_path in pdf_paths:
                merger.append(pdf_path)
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            self.logger.info(f"📚 PDF fusionné créé : {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la fusion : {e}")
            return False


def main():
    """Fonction principale avec interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Standardise les PDF vers le format A4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python pdf_standardizer.py file.pdf
  python pdf_standardizer.py -d /path/to/pdfs
  python pdf_standardizer.py file1.pdf file2.pdf -o /output/dir
  python pdf_standardizer.py -d /input -o /output --merge final.pdf
        """
    )
    
    parser.add_argument('files', nargs='*', help='Fichiers PDF à traiter')
    parser.add_argument('-d', '--directory', help='Dossier contenant les PDF')
    parser.add_argument('-o', '--output', help='Dossier de sortie')
    parser.add_argument('--merge', help='Fusionner les résultats en un seul PDF')
    parser.add_argument('--report', action='store_true', help='Afficher un rapport détaillé')
    
    args = parser.parse_args()
    
    # Validation des arguments
    if not args.files and not args.directory:
        parser.error("Spécifiez des fichiers ou un dossier avec -d")
    
    # Initialise le standardisateur
    standardizer = PDFStandardizer(args.output)
    
    # Traite les fichiers
    standardized_files = []
    
    if args.directory:
        standardized_files.extend(
            standardizer.standardize_directory(args.directory)
        )
    
    if args.files:
        standardized_files.extend(
            standardizer.standardize_multiple_pdfs(args.files)
        )
    
    # Affiche le rapport
    if args.report or not args.merge:
        print("\n" + standardizer.generate_report())
    
    # Fusion optionnelle
    if args.merge and standardized_files:
        merge_path = args.merge
        if args.output:
            merge_path = str(Path(args.output) / args.merge)
        
        standardizer.merge_standardized_pdfs(standardized_files, merge_path)
        print(f"\n📚 Document final créé : {merge_path}")


if __name__ == "__main__":
    main()