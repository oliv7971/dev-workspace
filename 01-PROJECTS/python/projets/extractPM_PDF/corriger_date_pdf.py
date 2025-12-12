#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger une date dans un PDF
"""

import fitz  # PyMuPDF
from pathlib import Path
import argparse


def remplacer_texte_pdf(fichier_pdf, ancien_texte, nouveau_texte, fichier_sortie=None):
    """
    Remplace du texte dans un PDF
    
    Args:
        fichier_pdf: chemin du PDF à modifier
        ancien_texte: texte à remplacer (ex: "2025-11-05")
        nouveau_texte: nouveau texte (ex: "2025-11-06")
        fichier_sortie: fichier de sortie (si None, ajoute "_corrigé" au nom)
    """
    pdf_path = Path(fichier_pdf)
    
    if not pdf_path.exists():
        print(f"❌ Erreur: Le fichier {fichier_pdf} n'existe pas")
        return False
    
    # Détermine le fichier de sortie
    if fichier_sortie is None:
        fichier_sortie = pdf_path.parent / f"{pdf_path.stem}_corrigé{pdf_path.suffix}"
    else:
        fichier_sortie = Path(fichier_sortie)
    
    print(f"📄 Ouverture de {pdf_path.name}...")
    doc = fitz.open(str(pdf_path))
    
    nb_remplacements = 0
    
    # Parcourt toutes les pages
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Cherche le texte
        text_instances = page.search_for(ancien_texte)
        
        if text_instances:
            print(f"   Page {page_num + 1}: {len(text_instances)} occurrence(s) trouvée(s)")
        
        # Pour chaque occurrence trouvée
        for inst in text_instances:
            # Récupère les infos du texte existant
            text_dict = page.get_text("dict")
            font_size = 10  # Taille par défaut
            font_name = "helv"  # Police par défaut
            
            # Essaie de trouver la taille de police réelle
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if ancien_texte in span["text"]:
                                font_size = span["size"]
                                font_name = span["font"]
                                break
            
            # Efface l'ancien texte (recouvre en blanc)
            page.add_redact_annot(inst, fill=(1, 1, 1))
            
            nb_remplacements += 1
        
        # Applique les suppressions
        page.apply_redactions()
        
        # Ajoute le nouveau texte aux mêmes positions
        text_instances = page.search_for(ancien_texte)  # Recherche à nouveau pour les positions
        
    # Deuxième passe pour ajouter le nouveau texte
    doc.close()
    doc = fitz.open(str(pdf_path))
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.search_for(ancien_texte)
        
        for inst in text_instances:
            # Récupère la taille de police
            text_dict = page.get_text("dict")
            font_size = 10
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if ancien_texte in span["text"]:
                                font_size = span["size"]
                                break
            
            # Efface
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()
            
            # Ajoute le nouveau texte à la même position
            page.insert_text(
                (inst.x0, inst.y1 - 2),  # Position ajustée
                nouveau_texte,
                fontsize=font_size,
                color=(0, 0, 0)
            )
    
    # Sauvegarde
    print(f"💾 Sauvegarde dans {fichier_sortie.name}...")
    doc.save(str(fichier_sortie))
    doc.close()
    
    print(f"✅ Terminé ! {nb_remplacements} remplacement(s) effectué(s)")
    print(f"📁 Fichier créé : {fichier_sortie}")
    
    return True


def main():
    ap = argparse.ArgumentParser(
        description="Corriger une date (ou tout texte) dans un PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python corriger_date_pdf.py mon_leve.pdf "2025-11-05" "2025-11-06"
  python corriger_date_pdf.py mon_leve.pdf "05/11/2025" "06/11/2025" -o leve_corrige.pdf
        """
    )
    ap.add_argument("pdf", help="Fichier PDF à corriger")
    ap.add_argument("ancien", help="Texte à remplacer (ex: '2025-11-05')")
    ap.add_argument("nouveau", help="Nouveau texte (ex: '2025-11-06')")
    ap.add_argument("-o", "--output", help="Fichier de sortie (par défaut: ajoute '_corrigé' au nom)")
    
    args = ap.parse_args()
    
    remplacer_texte_pdf(args.pdf, args.ancien, args.nouveau, args.output)


if __name__ == "__main__":
    main()
