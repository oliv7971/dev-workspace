#!/usr/bin/env python3
"""
CORRECTION des instructions avec les bonnes colonnes de références
"""

def creer_instructions_cordes_corrigees():
    """Crée les instructions corrigées avec les vraies colonnes"""

    targets_all = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]
    targets_ref1 = [t for t in targets_all if t != "REF1"]
    targets_ref2 = [t for t in targets_all if t != "REF2"]

    instructions = f"""# INSTRUCTIONS CORRIGÉES POUR LES FORMULES CORDES

## 📏 PRINCIPE DES CORDES
Une corde = distance 3D entre deux points
Formule: √((X₁-X₂)² + (Y₁-Y₂)² + (Z₁-Z₂)²)

## 🎯 ONGLET "CORDES REF1"
Distances de chaque cible vers REF1 (C530)

### ✅ COLONNES CORRECTES pour REF1 dans "Résultats observations":
- REF1_X en colonne BE (57)
- REF1_Y en colonne BF (58)
- REF1_Z en colonne BG (59)

### FORMULE GÉNÉRALE CORRIGÉE POUR REF1:
=SQRT(('Résultats observations'.C11-'Résultats observations'.BE11)^2+('Résultats observations'.D11-'Résultats observations'.BF11)^2+('Résultats observations'.E11-'Résultats observations'.BG11)^2)

### EXEMPLES CONCRETS CORRIGÉS:

**Colonne C (CORDE_V1_REF1) - V1 vers REF1:**
- Ligne 10: =SQRT(('Résultats observations'.C10-'Résultats observations'.BE10)^2+('Résultats observations'.D10-'Résultats observations'.BF10)^2+('Résultats observations'.E10-'Résultats observations'.BG10)^2)
- Ligne 11: =SQRT(('Résultats observations'.C11-'Résultats observations'.BE11)^2+('Résultats observations'.D11-'Résultats observations'.BF11)^2+('Résultats observations'.E11-'Résultats observations'.BG11)^2)
- Ligne 12: =SQRT(('Résultats observations'.C12-'Résultats observations'.BE12)^2+('Résultats observations'.D12-'Résultats observations'.BF12)^2+('Résultats observations'.E12-'Résultats observations'.BG12)^2)

**Colonne D (CORDE_V2_REF1) - V2 vers REF1:**
- Ligne 10: =SQRT(('Résultats observations'.F10-'Résultats observations'.BE10)^2+('Résultats observations'.G10-'Résultats observations'.BF10)^2+('Résultats observations'.H10-'Résultats observations'.BG10)^2)

**Colonne E (CORDE_V3_REF1) - V3 vers REF1:**
- Ligne 10: =SQRT(('Résultats observations'.I10-'Résultats observations'.BE10)^2+('Résultats observations'.J10-'Résultats observations'.BF10)^2+('Résultats observations'.K10-'Résultats observations'.BG10)^2)

## 🎯 ONGLET "CORDES REF2"
Distances de chaque cible vers REF2 (C540)

### ✅ COLONNES CORRECTES pour REF2 dans "Résultats observations":
- REF2_X en colonne BH (60)
- REF2_Y en colonne BI (61)
- REF2_Z en colonne BJ (62)

### FORMULE GÉNÉRALE CORRIGÉE POUR REF2:
=SQRT(('Résultats observations'.C11-'Résultats observations'.BH11)^2+('Résultats observations'.D11-'Résultats observations'.BI11)^2+('Résultats observations'.E11-'Résultats observations'.BJ11)^2)

### EXEMPLES CONCRETS CORRIGÉS:

**Colonne C (CORDE_V1_REF2) - V1 vers REF2:**
- Ligne 10: =SQRT(('Résultats observations'.C10-'Résultats observations'.BH10)^2+('Résultats observations'.D10-'Résultats observations'.BI10)^2+('Résultats observations'.E10-'Résultats observations'.BJ10)^2)

**Colonne D (CORDE_V2_REF2) - V2 vers REF2:**
- Ligne 10: =SQRT(('Résultats observations'.F10-'Résultats observations'.BH10)^2+('Résultats observations'.G10-'Résultats observations'.BI10)^2+('Résultats observations'.H10-'Résultats observations'.BJ10)^2)

## 📊 CORRESPONDANCE DES COLONNES (Résultats observations)

### ✅ RÉFÉRENCES CORRIGÉES:
- **REF1 (C530)**: X=BE(57), Y=BF(58), Z=BG(59)
- **REF2 (C540)**: X=BH(60), Y=BI(61), Z=BJ(62)

### Cibles et leurs colonnes X,Y,Z:
V1: X=C(3), Y=D(4), Z=E(5)
V2: X=F(6), Y=G(7), Z=H(8)
V3: X=I(9), Y=J(10), Z=K(11)
H1: X=L(12), Y=M(13), Z=N(14)
H2: X=O(15), Y=P(16), Z=Q(17)
H3: X=R(18), Y=S(19), Z=T(20)
H4: X=U(21), Y=V(22), Z=W(23)
H5: X=X(24), Y=Y(25), Z=Z(26)
B1: X=AA(27), Y=AB(28), Z=AC(29)
B2: X=AD(30), Y=AE(31), Z=AF(32)
B3: X=AG(33), Y=AH(34), Z=AI(35)
B4: X=AJ(36), Y=AK(37), Z=AL(38)
B5: X=AM(39), Y=AN(40), Z=AO(41)
M1: X=AP(42), Y=AQ(43), Z=AR(44)
M2: X=AS(45), Y=AT(46), Z=AU(47)
M3: X=AV(48), Y=AW(49), Z=AX(50)
M4: X=AY(51), Y=AZ(52), Z=BA(53)
M5: X=BB(54), Y=BC(55), Z=BD(56)

## 🔧 PROCÉDURE RECOMMANDÉE:

1. **COMMENCER PAR UNE FORMULE DE TEST**
   - CORDES REF1, colonne C (V1), ligne 10
   - Formule: =SQRT(('Résultats observations'.C10-'Résultats observations'.BE10)^2+('Résultats observations'.D10-'Résultats observations'.BF10)^2+('Résultats observations'.E10-'Résultats observations'.BG10)^2)
   - Vérifier que ça donne un résultat cohérent

2. **COPIER LA FORMULE**
   - Si OK, copier vers le bas (lignes 11, 12, etc.)
   - Puis passer à la colonne D (V2 vers REF1)

3. **ADAPTER POUR CHAQUE CIBLE**
   - V2: Remplacer C,D,E par F,G,H
   - V3: Remplacer C,D,E par I,J,K
   - H1: Remplacer C,D,E par L,M,N
   - etc.

4. **SAUVEGARDER FRÉQUEMMENT**
   - Après chaque colonne réussie
   - Avant de passer à CORDES REF2

## ⚠️ RÉSUMÉ DES CORRECTIONS:

**ANCIEN (FAUX):**
- REF1: BG, BH, BI
- REF2: BJ, BK, BL

**NOUVEAU (CORRECT):**
- REF1: BE, BF, BG
- REF2: BH, BI, BJ

## 💡 FORMULE TEST SIMPLIFIÉE:
=SQRT(1+4+9)  (doit donner 3.74...)
Si cette formule marche, vous pouvez remplacer par les vraies références.

## 🎯 PREMIÈRE FORMULE À TESTER:
Onglet CORDES REF1, cellule C10:
=SQRT(('Résultats observations'.C10-'Résultats observations'.BE10)^2+('Résultats observations'.D10-'Résultats observations'.BF10)^2+('Résultats observations'.E10-'Résultats observations'.BG10)^2)
"""

    with open("INSTRUCTIONS_CORDES_CORRIGEES.txt", "w", encoding="utf-8") as f:
        f.write(instructions)

    print("✅ Instructions corrigées créées: INSTRUCTIONS_CORDES_CORRIGEES.txt")

def creer_resume_corrections():
    """Crée un résumé des corrections apportées"""

    resume = """# RÉSUMÉ DES CORRECTIONS - COLONNES RÉFÉRENCES

## ❌ ERREUR DANS LES PREMIÈRES INSTRUCTIONS:
- REF1 était indiqué en BG, BH, BI (FAUX)
- REF2 était indiqué en BJ, BK, BL (FAUX)

## ✅ COLONNES CORRECTES:
- **REF1 (C530)**: BE, BF, BG (colonnes 57, 58, 59)
- **REF2 (C540)**: BH, BI, BJ (colonnes 60, 61, 62)

## 🎯 FORMULES CORRIGÉES:

### CORDE V1 vers REF1:
=SQRT(('Résultats observations'.C10-'Résultats observations'.BE10)^2+('Résultats observations'.D10-'Résultats observations'.BF10)^2+('Résultats observations'.E10-'Résultats observations'.BG10)^2)

### CORDE V1 vers REF2:
=SQRT(('Résultats observations'.C10-'Résultats observations'.BH10)^2+('Résultats observations'.D10-'Résultats observations'.BI10)^2+('Résultats observations'.E10-'Résultats observations'.BJ10)^2)

## 📁 FICHIERS MIS À JOUR:
- INSTRUCTIONS_CORDES_CORRIGEES.txt (NOUVEAU - À UTILISER)
- INSTRUCTIONS_CORDES_DETAILLEES.txt (ANCIEN - IGNORER)
"""

    with open("RESUME_CORRECTIONS.txt", "w", encoding="utf-8") as f:
        f.write(resume)

    print("📋 Résumé des corrections créé: RESUME_CORRECTIONS.txt")

if __name__ == "__main__":
    print("🔧 CORRECTION DES INSTRUCTIONS CORDES")
    print("Colonnes corrigées:")
    print("- REF1 (C530): BE, BF, BG")
    print("- REF2 (C540): BH, BI, BJ")
    print()

    creer_instructions_cordes_corrigees()
    creer_resume_corrections()

    print(f"\n🎉 CORRECTIONS APPLIQUÉES!")
    print(f"📝 Utilisez: INSTRUCTIONS_CORDES_CORRIGEES.txt")
    print(f"📋 Résumé: RESUME_CORRECTIONS.txt")
    print(f"⚠️ Ignorez l'ancien fichier INSTRUCTIONS_CORDES_DETAILLEES.txt")
