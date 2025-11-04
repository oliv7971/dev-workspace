# PDF Standardizer 📄

Outil pour homogénéiser automatiquement tous vos PDF en format A4 standard.

## 🎯 Problème résolu

Quand vous fusionnez des PDF avec PDFSAM, vous vous retrouvez souvent avec :
- ❌ Du A4 (210×297mm)
- ❌ Du A3 (297×420mm) 
- ❌ Des formats bizarres entre A4 et A3
- ❌ Des orientations mélangées

**Résultat** : Un document final avec des pages de tailles différentes ! 😤

## ✅ Solution

Ce programme **standardise automatiquement** tous vos PDF vers un format A4 uniforme tout en :
- 🔍 Préservant la qualité et la lisibilité
- 📏 Adaptant intelligemment l'échelle
- 📊 Générant un rapport détaillé
- 🔗 Proposant la fusion automatique

## 🚀 Installation

```bash
# 1. Installer les dépendances
pip install -r requirements_pdf.txt

# Ou individuellement :
pip install PyPDF2 PyMuPDF reportlab
```

## 📖 Utilisation

### Option 1 : Script simple (recommandé)
```bash
python run_pdf_standardizer.py
```

Le script vous proposera :
1. **Traiter le rapport mensuel septembre 2025** (chemin pré-configuré)
2. **Traiter un dossier personnalisé** (vous choisissez le dossier)

### Option 2 : Ligne de commande avancée
```bash
# Traiter un dossier complet
python pdf_standardizer.py -d "C:\mon\dossier\pdf" --report

# Traiter des fichiers spécifiques
python pdf_standardizer.py file1.pdf file2.pdf -o sortie/

# Traiter et fusionner automatiquement
python pdf_standardizer.py -d input/ -o output/ --merge "Document_final.pdf"
```

## 📊 Exemple de rapport

```
📊 RAPPORT DE STANDARDISATION PDF
==================================================
Total traité : 3 fichier(s)

1. annexe_convergences.pdf
   ➜ annexe_convergences_A4.pdf
   📏 Formats détectés avant :
      • 297x420mm (A3) - pages 1, 2
      • 210x297mm (A4) - pages 3
   ✅ Converti vers A4

2. graphiques_zone1.pdf
   ➜ graphiques_zone1_A4.pdf
   📏 Formats détectés avant :
      • 250x350mm (Personnalisé) - pages 1, 2, 3
   ✅ Converti vers A4
```

## 🔧 Fonctionnalités

### Analyse automatique
- Détecte tous les formats présents (A3, A4, Letter, formats personnalisés)
- Identifie les orientations (portrait/paysage)
- Compte les pages par format

### Standardisation intelligente
- Conversion vers A4 (210×297mm) 
- Préservation des proportions
- Centrage automatique du contenu
- Qualité optimisée

### Traitement par lot
- Traite tous les PDF d'un dossier
- Sauvegarde avec suffixe `_A4`
- Fusion optionnelle en document unique

## 📁 Structure des fichiers

```
📁 Votre dossier source/
├── 📄 document1.pdf          (formats mélangés)
├── 📄 document2.pdf          (A3 + A4)
├── 📄 document3.pdf          (format bizarre)
└── 📁 PDF_standardises_A4/   (créé automatiquement)
    ├── 📄 document1_A4.pdf   ✅ Tout en A4
    ├── 📄 document2_A4.pdf   ✅ Tout en A4  
    ├── 📄 document3_A4.pdf   ✅ Tout en A4
    └── 📄 Document_final.pdf ✅ Fusion complète
```

## 🎯 Cas d'usage typiques

### Rapport mensuel BURE
```python
# Le script détecte automatiquement :
source = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/Rapports d'activité/2025/250902-rapport mensuel septembre"
# Et génère :
output = "LS_34_G_911_EIF_0074_1_RP_mensuel_sept_2025_PARTIE_TOPO_annexes_A4.pdf"
```

### Dossier de rapports techniques
- Convergences (A3) → A4
- Déplacements (A4 paysage) → A4 portrait  
- Graphiques (formats custom) → A4
- **Résultat** : Document uniforme prêt pour impression/archivage

## 🛠️ Paramètres avancés

| Paramètre | Description | Valeur |
|-----------|-------------|--------|
| Format cible | Taille standardisée | A4 (210×297mm) |
| Qualité | Préservation | Optimale |
| Échelle | Adaptation automatique | Proportionnelle |
| Centrage | Positionnement | Automatique |

## 📞 Support

En cas de problème :
1. Vérifiez que les modules sont installés : `pip list | grep -E "(PyPDF2|PyMuPDF|reportlab)"`
2. Testez avec un seul PDF d'abord
3. Consultez les logs d'erreur dans la console

## 🚀 Prochaines améliorations

- [ ] Support des formats A5, Legal, etc.
- [ ] Interface graphique (GUI)
- [ ] Optimisation des gros fichiers
- [ ] Filigrane automatique
- [ ] Numérotation des pages

---

**💡 Astuce** : Gardez vos PDF originaux ! Le programme crée des copies standardisées sans modifier les fichiers sources.