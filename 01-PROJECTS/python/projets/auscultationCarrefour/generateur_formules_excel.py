#!/usr/bin/env python3
"""
GÉNÉRATEUR DE FORMULES - Copier-coller direct
Génère toutes les formules prêtes à copier dans Excel
"""

def generer_formules_deplacements():
    """Génère toutes les formules pour l'onglet Déplacements"""

    print("📊 GÉNÉRATION FORMULES DÉPLACEMENTS")
    print("="*50)

    # Cibles et leurs colonnes
    targets = [
        ("V1", "C", "D", "E"), ("V2", "F", "G", "H"), ("V3", "I", "J", "K"),
        ("H1", "L", "M", "N"), ("H2", "O", "P", "Q"), ("H3", "R", "S", "T"), ("H4", "U", "V", "W"), ("H5", "X", "Y", "Z"),
        ("B1", "AA", "AB", "AC"), ("B2", "AD", "AE", "AF"), ("B3", "AG", "AH", "AI"), ("B4", "AJ", "AK", "AL"), ("B5", "AM", "AN", "AO"),
        ("M1", "AP", "AQ", "AR"), ("M2", "AS", "AT", "AU"), ("M3", "AV", "AW", "AX"), ("M4", "AY", "AZ", "BA"), ("M5", "BB", "BC", "BD"),
        ("REF1", "BE", "BF", "BG"), ("REF2", "BH", "BI", "BJ")
    ]

    # Générer pour les lignes 10 à 15
    formules = []
    for row in range(10, 16):
        ligne_formules = []
        for target, col_x, col_y, col_z in targets:
            for coord_name, col_letter in [("X", col_x), ("Y", col_y), ("Z", col_z)]:
                formule = f"='Résultats observations'!{col_letter}{row}-'Résultats observations'!{col_letter}$10"
                ligne_formules.append(formule)
        formules.append(ligne_formules)

    # Sauvegarder dans un fichier
    with open("FORMULES_DEPLACEMENTS_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES DÉPLACEMENTS - COPIER-COLLER DIRECT\n\n")
        f.write("Instructions: Sélectionnez la ligne entière, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_DEPLACEMENTS_COPIER_COLLER.txt")
    print(f"   {len(formules)} lignes × {len(formules[0])} colonnes")

def generer_formules_evolution():
    """Génère toutes les formules pour l'onglet Évolution PM H V"""

    print("\n📈 GÉNÉRATION FORMULES ÉVOLUTION PM H V")
    print("="*50)

    # Cibles et leurs colonnes (PM/H/V au lieu de X/Y/Z)
    targets = [
        ("V1", "C", "D", "E"), ("V2", "F", "G", "H"), ("V3", "I", "J", "K"),
        ("H1", "L", "M", "N"), ("H2", "O", "P", "Q"), ("H3", "R", "S", "T"), ("H4", "U", "V", "W"), ("H5", "X", "Y", "Z"),
        ("B1", "AA", "AB", "AC"), ("B2", "AD", "AE", "AF"), ("B3", "AG", "AH", "AI"), ("B4", "AJ", "AK", "AL"), ("B5", "AM", "AN", "AO"),
        ("M1", "AP", "AQ", "AR"), ("M2", "AS", "AT", "AU"), ("M3", "AV", "AW", "AX"), ("M4", "AY", "AZ", "BA"), ("M5", "BB", "BC", "BD"),
        ("REF1", "BE", "BF", "BG"), ("REF2", "BH", "BI", "BJ")
    ]

    formules = []
    for row in range(10, 16):
        ligne_formules = []
        for target, col_pm, col_h, col_v in targets:
            for coord_name, col_letter in [("PM", col_pm), ("H", col_h), ("V", col_v)]:
                formule = f"='Résultats Projection'!{col_letter}{row}-'Résultats Projection'!{col_letter}$10"
                ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_EVOLUTION_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES ÉVOLUTION PM H V - COPIER-COLLER DIRECT\n\n")
        f.write("Instructions: Sélectionnez la ligne entière, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_EVOLUTION_COPIER_COLLER.txt")

def generer_formules_cordes_ref1():
    """Génère les formules pour CORDES REF1"""

    print("\n📏 GÉNÉRATION FORMULES CORDES REF1")
    print("="*50)

    # Toutes les cibles sauf REF1
    targets = [
        ("V1", "C", "D", "E"), ("V2", "F", "G", "H"), ("V3", "I", "J", "K"),
        ("H1", "L", "M", "N"), ("H2", "O", "P", "Q"), ("H3", "R", "S", "T"), ("H4", "U", "V", "W"), ("H5", "X", "Y", "Z"),
        ("B1", "AA", "AB", "AC"), ("B2", "AD", "AE", "AF"), ("B3", "AG", "AH", "AI"), ("B4", "AJ", "AK", "AL"), ("B5", "AM", "AN", "AO"),
        ("M1", "AP", "AQ", "AR"), ("M2", "AS", "AT", "AU"), ("M3", "AV", "AW", "AX"), ("M4", "AY", "AZ", "BA"), ("M5", "BB", "BC", "BD"),
        ("REF2", "BH", "BI", "BJ")  # REF2 vers REF1
    ]

    formules = []
    for row in range(10, 16):
        ligne_formules = []
        for target, col_x, col_y, col_z in targets:
            # Formule de distance 3D vers REF1 (BE, BF, BG)
            formule = f"=SQRT(('Résultats observations'!{col_x}{row}-'Résultats observations'!BE{row})^2+('Résultats observations'!{col_y}{row}-'Résultats observations'!BF{row})^2+('Résultats observations'!{col_z}{row}-'Résultats observations'!BG{row})^2)"
            ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_CORDES_REF1_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES CORDES REF1 - COPIER-COLLER DIRECT\n\n")
        f.write("REF1 = colonnes BE, BF, BG\n")
        f.write("Instructions: Sélectionnez la ligne, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_CORDES_REF1_COPIER_COLLER.txt")

def generer_formules_cordes_ref2():
    """Génère les formules pour CORDES REF2"""

    print("\n📏 GÉNÉRATION FORMULES CORDES REF2")
    print("="*50)

    # Toutes les cibles sauf REF2
    targets = [
        ("V1", "C", "D", "E"), ("V2", "F", "G", "H"), ("V3", "I", "J", "K"),
        ("H1", "L", "M", "N"), ("H2", "O", "P", "Q"), ("H3", "R", "S", "T"), ("H4", "U", "V", "W"), ("H5", "X", "Y", "Z"),
        ("B1", "AA", "AB", "AC"), ("B2", "AD", "AE", "AF"), ("B3", "AG", "AH", "AI"), ("B4", "AJ", "AK", "AL"), ("B5", "AM", "AN", "AO"),
        ("M1", "AP", "AQ", "AR"), ("M2", "AS", "AT", "AU"), ("M3", "AV", "AW", "AX"), ("M4", "AY", "AZ", "BA"), ("M5", "BB", "BC", "BD"),
        ("REF1", "BE", "BF", "BG")  # REF1 vers REF2
    ]

    formules = []
    for row in range(10, 16):
        ligne_formules = []
        for target, col_x, col_y, col_z in targets:
            # Formule de distance 3D vers REF2 (BH, BI, BJ)
            formule = f"=SQRT(('Résultats observations'!{col_x}{row}-'Résultats observations'!BH{row})^2+('Résultats observations'!{col_y}{row}-'Résultats observations'!BI{row})^2+('Résultats observations'!{col_z}{row}-'Résultats observations'!BJ{row})^2)"
            ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_CORDES_REF2_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES CORDES REF2 - COPIER-COLLER DIRECT\n\n")
        f.write("REF2 = colonnes BH, BI, BJ\n")
        f.write("Instructions: Sélectionnez la ligne, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_CORDES_REF2_COPIER_COLLER.txt")

def creer_guide_utilisation():
    """Crée le guide d'utilisation pour les fichiers générés"""

    guide = """# GUIDE D'UTILISATION - FORMULES GÉNÉRÉES

## 🚀 PROCÉDURE ULTRA-RAPIDE:

### 1️⃣ DÉPLACEMENTS:
1. Ouvrir: FORMULES_DEPLACEMENTS_COPIER_COLLER.txt
2. Copier la ligne "LIGNE 10"
3. Dans Excel: Sélectionner C10:BJ10 et coller
4. Répéter pour lignes 11, 12, 13, 14, 15

### 2️⃣ ÉVOLUTION PM H V:
1. Ouvrir: FORMULES_EVOLUTION_COPIER_COLLER.txt
2. Copier la ligne "LIGNE 10"
3. Dans Excel: Sélectionner C10:BJ10 et coller
4. Répéter pour lignes 11, 12, 13, 14, 15

### 3️⃣ CORDES REF1:
1. Ouvrir: FORMULES_CORDES_REF1_COPIER_COLLER.txt
2. Copier la ligne "LIGNE 10"
3. Dans Excel: Sélectionner C10:U10 et coller (19 colonnes)
4. Répéter pour lignes 11, 12, 13, 14, 15

### 4️⃣ CORDES REF2:
1. Ouvrir: FORMULES_CORDES_REF2_COPIER_COLLER.txt
2. Copier la ligne "LIGNE 10"
3. Dans Excel: Sélectionner C10:U10 et coller (19 colonnes)
4. Répéter pour lignes 11, 12, 13, 14, 15

## ⚡ ASTUCE EXCEL:
- Sélectionner une plage: Clic sur C10, puis Shift+Clic sur BJ10
- Coller: Ctrl+V
- Les formules se placeront automatiquement aux bonnes endroits!

## ⚠️ IMPORTANT:
- Sauvegarder après chaque onglet réussi
- Tester avec une ligne d'abord
- Les formules sont séparées par des tabulations (TAB)

## 📊 NOMBRE DE FORMULES:
- Déplacements: 6 lignes × 60 colonnes = 360 formules
- Évolution: 6 lignes × 60 colonnes = 360 formules
- Cordes REF1: 6 lignes × 19 colonnes = 114 formules
- Cordes REF2: 6 lignes × 19 colonnes = 114 formules
- **TOTAL: 948 formules générées automatiquement!** 🚀
"""

    with open("GUIDE_UTILISATION_FORMULES.txt", "w", encoding="utf-8") as f:
        f.write(guide)

    print("\n📋 Guide créé: GUIDE_UTILISATION_FORMULES.txt")

if __name__ == "__main__":
    print("🚀 GÉNÉRATEUR DE FORMULES EXCEL")
    print("Génération de toutes les formules prêtes à copier-coller...")
    print()

    generer_formules_deplacements()
    generer_formules_evolution()
    generer_formules_cordes_ref1()
    generer_formules_cordes_ref2()
    creer_guide_utilisation()

    print(f"\n🎉 GÉNÉRATION TERMINÉE!")
    print(f"📁 4 fichiers de formules créés")
    print(f"📋 Guide d'utilisation créé")
    print(f"⚡ Plus besoin de copier-coller manuel!")
    print(f"🚀 Toutes les formules sont prêtes!")
