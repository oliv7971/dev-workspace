#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION DE L'INSTALLATION
================================

Script de diagnostic pour vérifier que tous les composants
du système de gestion des mesures sont correctement installés.
"""

import os
import sys
from pathlib import Path

def verifier_installation():
    """Vérifie que tous les fichiers nécessaires sont présents"""
    
    print("\n" + "🔍 " * 30)
    print("VÉRIFICATION DE L'INSTALLATION")
    print("🔍 " * 30 + "\n")
    
    dossier_actuel = Path.cwd()
    print(f"📂 Dossier de travail : {dossier_actuel}\n")
    
    # Fichiers attendus
    fichiers_scripts = {
        'reset_et_mise_a_jour_complet.py': 'Reset complet des onglets',
        'ajouter_nouvelles_mesures.py': 'Ajout incrémental de nouvelles dates',
        'visualiseur_dates.py': 'Analyse et visualisation DATABASE',
        'test_systeme_mesures.py': 'Création de fichier de test'
    }
    
    fichiers_doc = {
        'GUIDE_DEMARRAGE_RAPIDE.md': 'Guide utilisateur',
        'README_GESTION_MESURES.md': 'Documentation technique',
        'INDEX_SOLUTION.md': 'Vue d\'ensemble complète'
    }
    
    fichiers_excel = {
        '01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm': 'Fichier Excel principal (optionnel)'
    }
    
    # Vérification scripts Python
    print("📜 SCRIPTS PYTHON")
    print("-" * 70)
    scripts_ok = 0
    for fichier, description in fichiers_scripts.items():
        chemin = dossier_actuel / fichier
        if chemin.exists():
            taille = chemin.stat().st_size
            print(f"✅ {fichier:<40} ({taille:>6} octets)")
            scripts_ok += 1
        else:
            print(f"❌ {fichier:<40} MANQUANT")
    
    print(f"\n   {scripts_ok}/{len(fichiers_scripts)} scripts trouvés\n")
    
    # Vérification documentation
    print("📖 DOCUMENTATION")
    print("-" * 70)
    docs_ok = 0
    for fichier, description in fichiers_doc.items():
        chemin = dossier_actuel / fichier
        if chemin.exists():
            taille = chemin.stat().st_size
            print(f"✅ {fichier:<40} ({taille:>6} octets)")
            docs_ok += 1
        else:
            print(f"❌ {fichier:<40} MANQUANT")
    
    print(f"\n   {docs_ok}/{len(fichiers_doc)} documents trouvés\n")
    
    # Vérification fichier Excel
    print("📊 FICHIERS EXCEL")
    print("-" * 70)
    excel_ok = 0
    for fichier, description in fichiers_excel.items():
        chemin = dossier_actuel / fichier
        if chemin.exists():
            taille = chemin.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ {fichier:<40} ({taille:.1f} MB)")
            excel_ok += 1
        else:
            print(f"⚠️  {fichier:<40} Non trouvé (normal si premier test)")
    
    print()
    
    # Vérification modules Python
    print("🐍 MODULES PYTHON REQUIS")
    print("-" * 70)
    
    modules_requis = {
        'openpyxl': 'Manipulation fichiers Excel',
        'pandas': 'Analyse de données (optionnel)',
        'datetime': 'Gestion des dates (standard)',
        'collections': 'Structures de données (standard)'
    }
    
    modules_ok = 0
    for module, description in modules_requis.items():
        try:
            __import__(module)
            print(f"✅ {module:<20} installé")
            modules_ok += 1
        except ImportError:
            if module in ['pandas']:  # Optionnel
                print(f"⚠️  {module:<20} non installé (optionnel)")
                modules_ok += 1
            else:
                print(f"❌ {module:<20} MANQUANT - installer avec: pip install {module}")
    
    print(f"\n   {modules_ok}/{len(modules_requis)} modules disponibles\n")
    
    # Tests de syntaxe
    print("✅ TESTS DE SYNTAXE")
    print("-" * 70)
    
    tests_ok = 0
    for fichier in fichiers_scripts.keys():
        chemin = dossier_actuel / fichier
        if chemin.exists():
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    compile(f.read(), fichier, 'exec')
                print(f"✅ {fichier:<40} Syntaxe OK")
                tests_ok += 1
            except SyntaxError as e:
                print(f"❌ {fichier:<40} Erreur syntaxe: {e}")
        else:
            print(f"⚠️  {fichier:<40} Fichier absent")
    
    print(f"\n   {tests_ok}/{len(fichiers_scripts)} scripts valides\n")
    
    # Résumé final
    print("=" * 70)
    print("📊 RÉSUMÉ DE L'INSTALLATION")
    print("=" * 70)
    
    total_fichiers = len(fichiers_scripts) + len(fichiers_doc)
    total_ok = scripts_ok + docs_ok
    
    pourcentage = (total_ok / total_fichiers) * 100
    
    print(f"\n✅ {total_ok}/{total_fichiers} fichiers essentiels présents ({pourcentage:.0f}%)")
    print(f"✅ {modules_ok}/{len(modules_requis)} modules Python disponibles")
    print(f"✅ {tests_ok}/{len(fichiers_scripts)} scripts sans erreur de syntaxe")
    
    if total_ok == total_fichiers and modules_ok >= len(modules_requis) - 1:
        print("\n" + "🎉 " * 30)
        print("INSTALLATION COMPLÈTE ET FONCTIONNELLE !")
        print("🎉 " * 30)
        
        print("\n📋 PROCHAINES ÉTAPES :")
        print("   1. Lire GUIDE_DEMARRAGE_RAPIDE.md")
        print("   2. Exécuter : python visualiseur_dates.py")
        print("   3. Faire une sauvegarde de votre fichier Excel")
        print("   4. Tester : python reset_et_mise_a_jour_complet.py")
        
    elif modules_ok < len(modules_requis) - 1:
        print("\n⚠️ MODULES MANQUANTS")
        print("   Installer avec : pip install openpyxl")
        
    else:
        print("\n⚠️ INSTALLATION INCOMPLÈTE")
        print("   Vérifier les fichiers manquants ci-dessus")
    
    print("\n" + "=" * 70 + "\n")
    
    return total_ok == total_fichiers


def tester_fonctionnement_basique():
    """Test basique du fonctionnement"""
    
    print("\n🧪 TEST DE FONCTIONNEMENT BASIQUE")
    print("=" * 70)
    
    try:
        import openpyxl
        from datetime import datetime
        from collections import defaultdict
        
        print("✅ Imports OK")
        
        # Test création date
        date_test = datetime(2025, 11, 26, 14, 30)
        print(f"✅ Création date OK : {date_test.strftime('%d/%m/%Y %H:%M')}")
        
        # Test structures
        dict_test = defaultdict(int)
        dict_test['test'] += 1
        print(f"✅ Structures de données OK")
        
        print("\n✅ Tous les tests basiques passent !\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests : {e}\n")
        return False


if __name__ == "__main__":
    print()
    
    # Vérification installation
    installation_ok = verifier_installation()
    
    # Tests basiques
    if installation_ok:
        fonctionnement_ok = tester_fonctionnement_basique()
        
        if fonctionnement_ok:
            print("🚀 " * 30)
            print("SYSTÈME PRÊT À L'EMPLOI !")
            print("🚀 " * 30)
            print()
            sys.exit(0)
        else:
            print("⚠️  Installation OK mais problème fonctionnel détecté")
            sys.exit(1)
    else:
        print("❌ Installation incomplète")
        sys.exit(1)
