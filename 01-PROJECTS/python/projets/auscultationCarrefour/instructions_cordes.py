#!/usr/bin/env python3
"""
Création des instructions détaillées pour les formules CORDES
"""

def creer_instructions_cordes_detaillees():
    """Crée des instructions détaillées pour les formules de cordes"""

    # Définir les cibles
    targets_all = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

    # Pour REF1, exclure REF1 elle-même
    targets_ref1 = [t for t in targets_all if t != "REF1"]
    targets_ref2 = [t for t in targets_all if t != "REF2"]

    instructions = f"""# INSTRUCTIONS COMPLÈTES POUR LES FORMULES CORDES

## 📏 PRINCIPE DES CORDES
Une corde = distance 3D entre deux points
Formule: √((X₁-X₂)² + (Y₁-Y₂)² + (Z₁-Z₂)²)

## 🎯 ONGLET "CORDES REF1"
Distances de chaque cible vers REF1 (C530)

### Structure des colonnes dans "Résultats observations":
- REF1_X en colonne BG (59)
- REF1_Y en colonne BH (60)
- REF1_Z en colonne BI (61)

### Cibles à traiter ({len(targets_ref1)} cibles):"""

    # Ajouter les cibles REF1
    col_ref1 = 3  # Commencer en colonne C
    for target in targets_ref1:
        col_letter = chr(ord('A') + col_ref1 - 1) if col_ref1 <= 26 else f"A{chr(ord('A') + col_ref1 - 27)}"
        if col_ref1 <= 26:
            col_letter = chr(ord('A') + col_ref1 - 1)
        else:
            col_letter = f"A{chr(ord('A') + col_ref1 - 27)}"

        instructions += f"\nColonne {col_letter} ({target}): CORDE_{target}_REF1"
        col_ref1 += 1

    instructions += f"""

### FORMULES POUR CORDES REF1:
Pour chaque cible, la formule générale est:
=SQRT(('Résultats observations'.C11-'Résultats observations'.BG11)^2+('Résultats observations'.D11-'Résultats observations'.BH11)^2+('Résultats observations'.E11-'Résultats observations'.BI11)^2)

⚠️ ATTENTION: Adapter les colonnes C,D,E selon la cible!

### EXEMPLES CONCRETS:

**Colonne C (CORDE_V1_REF1):**
- Ligne 11: =SQRT(('Résultats observations'.C11-'Résultats observations'.BG11)^2+('Résultats observations'.D11-'Résultats observations'.BH11)^2+('Résultats observations'.E11-'Résultats observations'.BI11)^2)
- Ligne 12: =SQRT(('Résultats observations'.C12-'Résultats observations'.BG12)^2+('Résultats observations'.D12-'Résultats observations'.BH12)^2+('Résultats observations'.E12-'Résultats observations'.BI12)^2)

**Colonne D (CORDE_V2_REF1):**
- Ligne 11: =SQRT(('Résultats observations'.F11-'Résultats observations'.BG11)^2+('Résultats observations'.G11-'Résultats observations'.BH11)^2+('Résultats observations'.H11-'Résultats observations'.BI11)^2)

## 🎯 ONGLET "CORDES REF2"
Distances de chaque cible vers REF2 (C540)

### Structure des colonnes dans "Résultats observations":
- REF2_X en colonne BJ (62)
- REF2_Y en colonne BK (63)
- REF2_Z en colonne BL (64)

### FORMULES POUR CORDES REF2:
Même principe que REF1 mais avec les colonnes BJ, BK, BL

**Exemple pour V1 vers REF2:**
=SQRT(('Résultats observations'.C11-'Résultats observations'.BJ11)^2+('Résultats observations'.D11-'Résultats observations'.BK11)^2+('Résultats observations'.E11-'Résultats observations'.BL11)^2)

## 📊 CORRESPONDANCE DES COLONNES (Résultats observations)

### Cibles et leurs colonnes X,Y,Z:"""

    # Ajouter la correspondance des colonnes
    col = 3  # Commencer en colonne C (3)
    for target in targets_all:
        col_x = chr(ord('A') + col - 1) if col <= 26 else f"A{chr(ord('A') + col - 27)}"
        col_y = chr(ord('A') + col) if col + 1 <= 26 else f"A{chr(ord('A') + col - 26)}"
        col_z = chr(ord('A') + col + 1) if col + 2 <= 26 else f"A{chr(ord('A') + col - 25)}"

        # Correction pour les colonnes > Z
        if col <= 26:
            col_x = chr(ord('A') + col - 1)
        elif col <= 52:
            col_x = f"A{chr(ord('A') + col - 27)}"
        else:
            col_x = f"B{chr(ord('A') + col - 53)}"

        if col + 1 <= 26:
            col_y = chr(ord('A') + col)
        elif col + 1 <= 52:
            col_y = f"A{chr(ord('A') + col - 26)}"
        else:
            col_y = f"B{chr(ord('A') + col - 52)}"

        if col + 2 <= 26:
            col_z = chr(ord('A') + col + 1)
        elif col + 2 <= 52:
            col_z = f"A{chr(ord('A') + col - 25)}"
        else:
            col_z = f"B{chr(ord('A') + col - 51)}"

        instructions += f"\n{target}: X={col_x}, Y={col_y}, Z={col_z}"
        col += 3

    instructions += """

## 🔧 PROCÉDURE RECOMMANDÉE:

1. **COMMENCER PAR UNE FORMULE DE TEST**
   - Choisir CORDES REF1, colonne C, ligne 11
   - Saisir la formule pour V1 vers REF1
   - Vérifier que ça fonctionne

2. **COPIER LA FORMULE**
   - Si OK, copier vers le bas (lignes 12, 13, etc.)
   - Puis adapter pour la colonne D (V2), etc.

3. **SAUVEGARDER FRÉQUEMMENT**
   - Après chaque colonne réussie
   - Avant de passer à l'onglet suivant

4. **EN CAS D'ERREUR**
   - Vérifier les références de colonnes
   - S'assurer que les noms d'onglets sont corrects
   - Tester avec une formule plus simple d'abord

## ⚠️ POINTS D'ATTENTION:

- Les colonnes BG, BH, BI = REF1 (C530)
- Les colonnes BJ, BK, BL = REF2 (C540)
- Adapter les colonnes source selon chaque cible
- Utiliser des références absolues ($) si nécessaire
- Tester UNE formule avant de tout copier

## 💡 FORMULE SIMPLIFIÉE POUR TESTER:
Si les formules complexes ne marchent pas, essayez d'abord:
=SQRT(9+16+25)  (doit donner 7.07...)

Si ça marche, remplacez progressivement par les vraies références."""

    # Sauvegarder les instructions
    with open("INSTRUCTIONS_CORDES_DETAILLEES.txt", "w", encoding="utf-8") as f:
        f.write(instructions)

    print("📝 Instructions détaillées créées: INSTRUCTIONS_CORDES_DETAILLEES.txt")

    return instructions

def creer_aide_memoire_colonnes():
    """Crée un aide-mémoire pour les colonnes"""

    aide_memoire = """# AIDE-MÉMOIRE COLONNES EXCEL

## Correspondance numéro ↔ lettre:
1=A, 2=B, 3=C, ..., 26=Z, 27=AA, 28=AB, ...

## Colonnes importantes:
- REF1_X = BG (colonne 59)
- REF1_Y = BH (colonne 60)
- REF1_Z = BI (colonne 61)
- REF2_X = BJ (colonne 62)
- REF2_Y = BK (colonne 63)
- REF2_Z = BL (colonne 64)

## Première cible (V1):
- V1_X = C (colonne 3)
- V1_Y = D (colonne 4)
- V1_Z = E (colonne 5)

## Pour trouver une colonne:
Dans Excel: Ctrl+G puis saisir par ex. "BG1" pour aller à la colonne BG
"""

    with open("AIDE_MEMOIRE_COLONNES.txt", "w", encoding="utf-8") as f:
        f.write(aide_memoire)

    print("📋 Aide-mémoire créé: AIDE_MEMOIRE_COLONNES.txt")

if __name__ == "__main__":
    print("📏 CRÉATION DES INSTRUCTIONS POUR LES CORDES")

    creer_instructions_cordes_detaillees()
    creer_aide_memoire_colonnes()

    print(f"\n🎉 INSTRUCTIONS CRÉÉES!")
    print(f"📝 Fichier principal: INSTRUCTIONS_CORDES_DETAILLEES.txt")
    print(f"📋 Aide-mémoire: AIDE_MEMOIRE_COLONNES.txt")
    print(f"💡 Suivez les instructions étape par étape pour éviter les erreurs")
