#!/usr/bin/env python3
"""
CORRECTION SYNTAXE - Remplacer les points par des points d'exclamation
"""

def corriger_syntaxe_excel():
    """Corrige la syntaxe des références Excel (. vers !)"""

    instructions_finales = """# INSTRUCTIONS FINALES CORRIGÉES - SYNTAXE EXCEL

## 📏 FORMULES CORDES AVEC SYNTAXE CORRECTE

### ✅ SYNTAXE CORRECTE Excel:
'Résultats observations'!C10 (avec point d'exclamation !)

### ❌ SYNTAXE INCORRECTE:
'Résultats observations'.C10 (avec point .)

## 🎯 ONGLET "CORDES REF1" - FORMULES FINALES

### REF1 (C530) - Colonnes: BE, BF, BG

**CORDE V1 vers REF1 (Colonne C):**
```
=SQRT(('Résultats observations'!C10-'Résultats observations'!BE10)^2+('Résultats observations'!D10-'Résultats observations'!BF10)^2+('Résultats observations'!E10-'Résultats observations'!BG10)^2)
```

**CORDE V2 vers REF1 (Colonne D):**
```
=SQRT(('Résultats observations'!F10-'Résultats observations'!BE10)^2+('Résultats observations'!G10-'Résultats observations'!BF10)^2+('Résultats observations'!H10-'Résultats observations'!BG10)^2)
```

**CORDE V3 vers REF1 (Colonne E):**
```
=SQRT(('Résultats observations'!I10-'Résultats observations'!BE10)^2+('Résultats observations'!J10-'Résultats observations'!BF10)^2+('Résultats observations'!K10-'Résultats observations'!BG10)^2)
```

## 🎯 ONGLET "CORDES REF2" - FORMULES FINALES

### REF2 (C540) - Colonnes: BH, BI, BJ

**CORDE V1 vers REF2 (Colonne C):**
```
=SQRT(('Résultats observations'!C10-'Résultats observations'!BH10)^2+('Résultats observations'!D10-'Résultats observations'!BI10)^2+('Résultats observations'!E10-'Résultats observations'!BJ10)^2)
```

**CORDE V2 vers REF2 (Colonne D):**
```
=SQRT(('Résultats observations'!F10-'Résultats observations'!BH10)^2+('Résultats observations'!G10-'Résultats observations'!BI10)^2+('Résultats observations'!H10-'Résultats observations'!BJ10)^2)
```

## 🎯 ONGLET "DÉPLACEMENTS" - FORMULES FINALES

**Exemple pour colonne C (V1_X):**
```
=IFERROR('Résultats observations'!C11-'Résultats observations'!C$10,"")
```

**Pour les autres colonnes:**
- Colonne D (V1_Y): `='Résultats observations'!D11-'Résultats observations'!D$10`
- Colonne E (V1_Z): `='Résultats observations'!E11-'Résultats observations'!E$10`
- Colonne F (V2_X): `='Résultats observations'!F11-'Résultats observations'!F$10`
- etc.

## 🎯 ONGLET "ÉVOLUTION PM H V" - FORMULES FINALES

**Exemple pour colonne C (ΔV1_PM):**
```
=IFERROR('Résultats Projection'!C11-'Résultats Projection'!C$10,"")
```

**Pour les autres colonnes:**
- Colonne D (ΔV1_H): `='Résultats Projection'!D11-'Résultats Projection'!D$10`
- Colonne E (ΔV1_V): `='Résultats Projection'!E11-'Résultats Projection'!E$10`
- etc.

## 🔧 PROCÉDURE FINALE:

1. **TESTER UNE FORMULE SIMPLE D'ABORD:**
   ```
   =SQRT(9+16+25)
   ```
   Résultat attendu: 7.07...

2. **PUIS TESTER UNE VRAIE FORMULE:**
   Dans CORDES REF1, cellule C10:
   ```
   =SQRT(('Résultats observations'!C10-'Résultats observations'!BE10)^2+('Résultats observations'!D10-'Résultats observations'!BF10)^2+('Résultats observations'!E10-'Résultats observations'!BG10)^2)
   ```

3. **SI ÇA MARCHE:**
   - Copier vers les lignes 11, 12, 13...
   - Adapter pour les autres colonnes (D, E, F...)
   - Sauvegarder fréquemment

4. **ORDRE RECOMMANDÉ:**
   - Déplacements (plus simple)
   - Évolution PM H V (similaire)
   - Cordes REF1 (plus complexe)
   - Cordes REF2 (similaire à REF1)

## ⚠️ POINTS CRITIQUES:

- ✅ Utiliser **!** (point d'exclamation)
- ❌ Ne pas utiliser **.** (point simple)
- ✅ Tester UNE formule à la fois
- ✅ Sauvegarder après chaque succès
- ✅ Utiliser IFERROR pour éviter les erreurs #DIV/0

## 🎯 PREMIÈRE FORMULE À COPIER-COLLER:

Onglet CORDES REF1, cellule C10:
```
=SQRT(('Résultats observations'!C10-'Résultats observations'!BE10)^2+('Résultats observations'!D10-'Résultats observations'!BF10)^2+('Résultats observations'!E10-'Résultats observations'!BG10)^2)
```

Si cette formule fonctionne, vous pouvez faire confiance aux autres !
"""

    with open("FORMULES_FINALES_EXCEL.txt", "w", encoding="utf-8") as f:
        f.write(instructions_finales)

    print("✅ Instructions finales créées: FORMULES_FINALES_EXCEL.txt")

def corriger_ancien_fichier():
    """Met à jour l'ancien fichier avec la bonne syntaxe"""

    try:
        # Lire l'ancien fichier
        with open("INSTRUCTIONS_FORMULES_MANUELLES.txt", "r", encoding="utf-8") as f:
            contenu = f.read()

        # Remplacer la syntaxe
        contenu_corrige = contenu.replace("'Résultats observations'.", "'Résultats observations'!")
        contenu_corrige = contenu_corrige.replace("'Résultats Projection'.", "'Résultats Projection'!")

        # Sauvegarder la version corrigée
        with open("INSTRUCTIONS_FORMULES_MANUELLES_CORRIGEES.txt", "w", encoding="utf-8") as f:
            f.write(contenu_corrige)

        print("✅ Ancien fichier corrigé: INSTRUCTIONS_FORMULES_MANUELLES_CORRIGEES.txt")

    except FileNotFoundError:
        print("ℹ️ Fichier INSTRUCTIONS_FORMULES_MANUELLES.txt non trouvé")

def creer_resume_final():
    """Crée le résumé final de toutes les corrections"""

    resume = """# RÉSUMÉ FINAL - TOUTES LES CORRECTIONS

## 🔧 CORRECTIONS APPORTÉES:

### 1️⃣ COLONNES DES RÉFÉRENCES:
- REF1 (C530): BE, BF, BG ✅
- REF2 (C540): BH, BI, BJ ✅

### 2️⃣ SYNTAXE EXCEL:
- CORRECT: 'Résultats observations'!C10 ✅
- FAUX: 'Résultats observations'.C10 ❌

## 📁 FICHIERS À UTILISER:

✅ **FORMULES_FINALES_EXCEL.txt** - Instructions complètes finales
✅ **INSTRUCTIONS_FORMULES_MANUELLES_CORRIGEES.txt** - Déplacements & Évolution corrigés
✅ **RESUME_CORRECTIONS.txt** - Résumé des colonnes

❌ Ignorer les anciens fichiers avec la mauvaise syntaxe

## 🎯 ORDRE DE TRAVAIL RECOMMANDÉ:

1. **Déplacements** (formules simples)
2. **Évolution PM H V** (similaires)
3. **Cordes REF1** (plus complexes)
4. **Cordes REF2** (similaires à REF1)

## ⚡ FORMULE TEST:
=SQRT(9+16+25) → doit donner 7.07...

## 🚀 PREMIÈRE VRAIE FORMULE:
CORDES REF1, cellule C10:
=SQRT(('Résultats observations'!C10-'Résultats observations'!BE10)^2+('Résultats observations'!D10-'Résultats observations'!BF10)^2+('Résultats observations'!E10-'Résultats observations'!BG10)^2)
"""

    with open("RESUME_FINAL_CORRECTIONS.txt", "w", encoding="utf-8") as f:
        f.write(resume)

    print("📋 Résumé final créé: RESUME_FINAL_CORRECTIONS.txt")

if __name__ == "__main__":
    print("🔧 CORRECTION FINALE - SYNTAXE EXCEL")
    print("Changement: '.' → '!' dans les références d'onglets")
    print()

    corriger_syntaxe_excel()
    corriger_ancien_fichier()
    creer_resume_final()

    print(f"\n🎉 TOUTES LES CORRECTIONS FINALES APPLIQUÉES!")
    print(f"📝 Fichier principal: FORMULES_FINALES_EXCEL.txt")
    print(f"📋 Résumé: RESUME_FINAL_CORRECTIONS.txt")
    print(f"✅ Syntaxe Excel correcte: ! au lieu de .")
