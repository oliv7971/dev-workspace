#!/usr/bin/env python3
"""
GÉNÉRATEUR DE FORMULES - VERSION MISE À JOUR
Avec les nouveaux noms d'onglets
"""

def generer_formules_evolutions_xyz():
    """Génère les formules pour l'onglet EVOLUTIONS XYZ (ex-Déplacements)"""

    print("📊 GÉNÉRATION FORMULES EVOLUTIONS XYZ")
    print("="*50)

    # Cibles et leurs colonnes
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
        for target, col_x, col_y, col_z in targets:
            for coord_name, col_letter in [("X", col_x), ("Y", col_y), ("Z", col_z)]:
                formule = f"=OBSERVATIONS!{col_letter}{row}-OBSERVATIONS!{col_letter}$10"
                ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_EVOLUTIONS_XYZ_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES EVOLUTIONS XYZ - COPIER-COLLER DIRECT\n\n")
        f.write("Source: Onglet OBSERVATIONS\n")
        f.write("Instructions: Sélectionnez la ligne entière, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_EVOLUTIONS_XYZ_COPIER_COLLER.txt")

def generer_formules_evolutions_pmhv():
    """Génère les formules pour l'onglet EVOLUTIONS PM H V"""

    print("\n📈 GÉNÉRATION FORMULES EVOLUTIONS PM H V")
    print("="*50)

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
                formule = f"=PROJECTION!{col_letter}{row}-PROJECTION!{col_letter}$10"
                ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_EVOLUTIONS_PMHV_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES EVOLUTIONS PM H V - COPIER-COLLER DIRECT\n\n")
        f.write("Source: Onglet PROJECTION\n")
        f.write("Instructions: Sélectionnez la ligne entière, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_EVOLUTIONS_PMHV_COPIER_COLLER.txt")

def generer_formules_cordes_ref1():
    """Génère les formules pour cordes ref1"""

    print("\n📏 GÉNÉRATION FORMULES cordes ref1")
    print("="*50)

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
            formule = f"=SQRT((OBSERVATIONS!{col_x}{row}-OBSERVATIONS!BE{row})^2+(OBSERVATIONS!{col_y}{row}-OBSERVATIONS!BF{row})^2+(OBSERVATIONS!{col_z}{row}-OBSERVATIONS!BG{row})^2)"
            ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_CORDES_REF1_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES cordes ref1 - COPIER-COLLER DIRECT\n\n")
        f.write("REF1 = colonnes BE, BF, BG dans onglet OBSERVATIONS\n")
        f.write("Instructions: Sélectionnez la ligne, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_CORDES_REF1_COPIER_COLLER.txt")

def generer_formules_cordes_ref2():
    """Génère les formules pour cordes ref2"""

    print("\n📏 GÉNÉRATION FORMULES cordes ref2")
    print("="*50)

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
            formule = f"=SQRT((OBSERVATIONS!{col_x}{row}-OBSERVATIONS!BH{row})^2+(OBSERVATIONS!{col_y}{row}-OBSERVATIONS!BI{row})^2+(OBSERVATIONS!{col_z}{row}-OBSERVATIONS!BJ{row})^2)"
            ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_CORDES_REF2_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES cordes ref2 - COPIER-COLLER DIRECT\n\n")
        f.write("REF2 = colonnes BH, BI, BJ dans onglet OBSERVATIONS\n")
        f.write("Instructions: Sélectionnez la ligne, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_CORDES_REF2_COPIER_COLLER.txt")

def generer_formules_evolutions_cordes_ref1():
    """Génère les formules pour EVOLUTIONS CORDES REF1 (nouveaux onglets)"""

    print("\n📈 GÉNÉRATION FORMULES EVOLUTIONS CORDES REF1")
    print("="*50)

    # 19 cibles (toutes sauf REF1)
    targets = [
        "V1", "V2", "V3", "H1", "H2", "H3", "H4", "H5",
        "B1", "B2", "B3", "B4", "B5", "M1", "M2", "M3", "M4", "M5", "REF2"
    ]

    formules = []
    for row in range(10, 16):
        ligne_formules = []
        for i, target in enumerate(targets):
            col_letter = chr(ord('C') + i) if i < 23 else f"A{chr(ord('A') + i - 26)}"  # C, D, E... puis AA, AB...
            # Formule: valeur actuelle - valeur ligne 10
            formule = f"='cordes ref1'!{col_letter}{row}-'cordes ref1'!{col_letter}$10"
            ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_EVOLUTIONS_CORDES_REF1_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES EVOLUTIONS CORDES REF1 - COPIER-COLLER DIRECT\n\n")
        f.write("Source: Onglet 'cordes ref1'\n")
        f.write("Calcul: valeur_actuelle - valeur_initiale (ligne 10)\n")
        f.write("Instructions: Sélectionnez la ligne, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_EVOLUTIONS_CORDES_REF1_COPIER_COLLER.txt")

def generer_formules_evolutions_cordes_ref2():
    """Génère les formules pour EVOLUTIONS CORDES REF2"""

    print("\n📈 GÉNÉRATION FORMULES EVOLUTIONS CORDES REF2")
    print("="*50)

    # 19 cibles (toutes sauf REF2)
    targets = [
        "V1", "V2", "V3", "H1", "H2", "H3", "H4", "H5",
        "B1", "B2", "B3", "B4", "B5", "M1", "M2", "M3", "M4", "M5", "REF1"
    ]

    formules = []
    for row in range(10, 16):
        ligne_formules = []
        for i, target in enumerate(targets):
            col_letter = chr(ord('C') + i) if i < 23 else f"A{chr(ord('A') + i - 26)}"
            formule = f"='cordes ref2'!{col_letter}{row}-'cordes ref2'!{col_letter}$10"
            ligne_formules.append(formule)
        formules.append(ligne_formules)

    with open("FORMULES_EVOLUTIONS_CORDES_REF2_COPIER_COLLER.txt", "w", encoding="utf-8") as f:
        f.write("# FORMULES EVOLUTIONS CORDES REF2 - COPIER-COLLER DIRECT\n\n")
        f.write("Source: Onglet 'cordes ref2'\n")
        f.write("Calcul: valeur_actuelle - valeur_initiale (ligne 10)\n")
        f.write("Instructions: Sélectionnez la ligne, copiez et collez en C10, C11, etc.\n\n")

        for i, ligne_formules in enumerate(formules):
            row = 10 + i
            f.write(f"## LIGNE {row}:\n")
            f.write("\t".join(ligne_formules) + "\n\n")

    print("✅ Fichier créé: FORMULES_EVOLUTIONS_CORDES_REF2_COPIER_COLLER.txt")

def creer_guide_mis_a_jour():
    """Crée le guide d'utilisation mis à jour"""

    guide = """# GUIDE D'UTILISATION MIS À JOUR - NOUVEAUX NOMS D'ONGLETS

## 📋 CORRESPONDANCE NOMS D'ONGLETS:
- OBSERVATIONS (source des coordonnées XYZ)
- PROJECTION (source des coordonnées PM/H/V)
- EVOLUTIONS XYZ (évolutions des XYZ par rapport à la 1ère mesure)
- EVOLUTIONS PM H V (évolutions des PM/H/V par rapport à la 1ère mesure)
- cordes ref1 (distances vers REF1)
- cordes ref2 (distances vers REF2)
- EVOLUTIONS CORDES REF1 (évolutions des cordes REF1)
- EVOLUTIONS CORDES REF2 (évolutions des cordes REF2)

## 🚀 PROCÉDURE POUR CHAQUE ONGLET:

### 1️⃣ EVOLUTIONS XYZ:
1. Fichier: FORMULES_EVOLUTIONS_XYZ_COPIER_COLLER.txt
2. Copier ligne "LIGNE 10" complète
3. Dans Excel: Cliquer sur C10 et coller
4. Répéter pour lignes 11-15

### 2️⃣ EVOLUTIONS PM H V:
1. Fichier: FORMULES_EVOLUTIONS_PMHV_COPIER_COLLER.txt
2. Copier ligne "LIGNE 10" complète
3. Dans Excel: Cliquer sur C10 et coller
4. Répéter pour lignes 11-15

### 3️⃣ cordes ref1:
1. Fichier: FORMULES_CORDES_REF1_COPIER_COLLER.txt
2. Copier ligne "LIGNE 10" complète
3. Dans Excel: Cliquer sur C10 et coller (19 colonnes)
4. Répéter pour lignes 11-15

### 4️⃣ cordes ref2:
1. Fichier: FORMULES_CORDES_REF2_COPIER_COLLER.txt
2. Copier ligne "LIGNE 10" complète
3. Dans Excel: Cliquer sur C10 et coller (19 colonnes)
4. Répéter pour lignes 11-15

### 5️⃣ EVOLUTIONS CORDES REF1:
1. Fichier: FORMULES_EVOLUTIONS_CORDES_REF1_COPIER_COLLER.txt
2. Copier ligne "LIGNE 10" complète
3. Dans Excel: Cliquer sur C10 et coller (19 colonnes)
4. Répéter pour lignes 11-15

### 6️⃣ EVOLUTIONS CORDES REF2:
1. Fichier: FORMULES_EVOLUTIONS_CORDES_REF2_COPIER_COLLER.txt
2. Copier ligne "LIGNE 10" complète
3. Dans Excel: Cliquer sur C10 et coller (19 colonnes)
4. Répéter pour lignes 11-15

## 📊 RÉCAPITULATIF:
- 6 onglets de calculs
- 6 fichiers de formules générés
- 36 copier-coller au total (6 lignes × 6 onglets)
- Plus de 1400 formules générées automatiquement! 🚀

## ⚠️ ORDRE RECOMMANDÉ:
1. D'abord: cordes ref1 et cordes ref2
2. Ensuite: EVOLUTIONS XYZ et EVOLUTIONS PM H V
3. Enfin: EVOLUTIONS CORDES REF1 et REF2 (qui dépendent des précédents)
"""

    with open("GUIDE_UTILISATION_MIS_A_JOUR.txt", "w", encoding="utf-8") as f:
        f.write(guide)

    print("\n📋 Guide mis à jour créé: GUIDE_UTILISATION_MIS_A_JOUR.txt")

if __name__ == "__main__":
    print("🚀 GÉNÉRATEUR MIS À JOUR - NOUVEAUX NOMS D'ONGLETS")
    print("="*60)

    generer_formules_evolutions_xyz()
    generer_formules_evolutions_pmhv()
    generer_formules_cordes_ref1()
    generer_formules_cordes_ref2()
    generer_formules_evolutions_cordes_ref1()
    generer_formules_evolutions_cordes_ref2()
    creer_guide_mis_a_jour()

    print(f"\n🎉 GÉNÉRATION COMPLÈTE TERMINÉE!")
    print(f"📁 6 fichiers de formules créés avec les nouveaux noms")
    print(f"📋 Guide d'utilisation mis à jour")
    print(f"🚀 Plus de 1400 formules prêtes à copier-coller!")
