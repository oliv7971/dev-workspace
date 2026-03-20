# 🔄 SYSTÈME DE GESTION DES MESURES MULTIPLES

## 📋 PROBLÉMATIQUE RÉSOLUE

### Problèmes identifiés :
1. ❌ **Données résiduelles** : Les anciennes valeurs restaient dans les cellules
2. ❌ **Dates manquantes** : Certaines mesures de DATABASE n'apparaissaient pas
3. ❌ **Mesures multiples par jour** : Impossible de gérer 2-3 mesures le même jour (surveillance accélérée 6h/12h/18h)

### Solution implémentée :
✅ **Reset complet** : Vide et reconstruit à partir de DATABASE  
✅ **Extraction intelligente** : Récupère TOUTES les dates avec horodatage  
✅ **Gestion multi-mesures** : Supporte plusieurs mesures par jour  
✅ **Ordre chronologique** : Tri parfait pour visualiser l'évolution  

---

## 🚀 LES DEUX SCRIPTS

### 1️⃣ `reset_et_mise_a_jour_complet.py` - RESET COMPLET

**Quand l'utiliser ?**
- 🔴 Première utilisation
- 🔴 Problème de données corrompues
- 🔴 Restructuration complète nécessaire
- 🔴 Doute sur la cohérence des données

**Ce qu'il fait :**
1. ❌ VIDE toutes les données de tous les onglets
2. 📅 Extrait TOUTES les dates de DATABASE
3. ✅ Réinsère les dates triées chronologiquement
4. 🔄 Les formules Excel se recalculent automatiquement

**Commande :**
```bash
python reset_et_mise_a_jour_complet.py
```

**Exemple de sortie :**
```
📅 EXTRACTION DES DATES DE DATABASE
✅ Colonne DATE trouvée : AB
📊 156 mesures trouvées dans DATABASE

🔄 MESURES MULTIPLES DÉTECTÉES :
   26/11/2025: 3 mesures (08:00, 14:00, 20:00)
   27/11/2025: 2 mesures (09:00, 15:00)

✅ 156 dates extraites et triées
   📅 Première : 28/08/2024 00:00
   📅 Dernière : 27/11/2025 20:00

🔧 TRAITEMENT DES ONGLETS
📋 Résultats observations:
   🗑️ 45 lignes supprimées
   ✅ 156 dates insérées (lignes 10-165)

✅ TRAITEMENT TERMINÉ
```

---

### 2️⃣ `ajouter_nouvelles_mesures.py` - AJOUT INCRÉMENTAL

**Quand l'utiliser ?**
- 🟢 Ajout d'une nouvelle campagne de mesure
- 🟢 Mesure accélérée supplémentaire (14h alors que 08h existe)
- 🟢 Mise à jour quotidienne/hebdomadaire
- 🟢 Pas besoin de tout recalculer

**Ce qu'il fait :**
1. 📖 Lit les dates déjà présentes dans les onglets
2. 🔍 Compare avec DATABASE
3. ➕ Ajoute UNIQUEMENT les dates manquantes
4. 📊 Maintient l'ordre chronologique

**Commande :**
```bash
python ajouter_nouvelles_mesures.py
```

**Exemple de sortie :**
```
📅 Extraction des dates existantes...
   ✅ 45 dates déjà présentes

📊 Extraction des dates de DATABASE...
   ✅ 48 dates dans DATABASE

🔍 Recherche des nouvelles dates...
   🆕 3 nouvelles dates trouvées :
      - 26/11/2025 14:00
      - 26/11/2025 20:00
      - 27/11/2025 09:00

📝 Mise à jour des onglets...
   ✅ Résultats observations : Mis à jour
   ✅ OBSERVATIONS : Mis à jour
   ✅ PROJECTION : Mis à jour
   ...

✅ AJOUT TERMINÉ
📊 Résumé :
   - 3 nouvelles dates ajoutées
   - 9 onglets mis à jour
   - 48 dates au total
```

---

## 📊 FORMAT DES DATES

### Mesures uniques (1 fois par jour) :
```
Ligne 10: 28/08/2024
Ligne 11: 05/09/2024
Ligne 12: 09/09/2024
```

### Mesures multiples (surveillance accélérée) :
```
Ligne 10: 26/11/2025 08:00  ← Mesure du matin
Ligne 11: 26/11/2025 14:00  ← Mesure de l'après-midi
Ligne 12: 26/11/2025 20:00  ← Mesure du soir
Ligne 13: 27/11/2025 09:00  ← Jour suivant
```

---

## 🎯 WORKFLOW RECOMMANDÉ

### Cas 1 : Première mise en place
```bash
python reset_et_mise_a_jour_complet.py
```

### Cas 2 : Ajout régulier de nouvelles mesures
```bash
# 1. Ajouter les données dans DATABASE (colonnes AB-AG)
# 2. Exécuter le script d'ajout
python ajouter_nouvelles_mesures.py
```

### Cas 3 : Surveillance accélérée (mesures 6h/12h)
```bash
# DATABASE doit contenir :
# 26/11/2025 06:00, V1, V1.Test, 823147.xxx, ...
# 26/11/2025 12:00, V1, V1.Test, 823147.xxx, ...
# 26/11/2025 18:00, V1, V1.Test, 823147.xxx, ...

# Puis :
python ajouter_nouvelles_mesures.py
```

### Cas 4 : Problème détecté / Doute
```bash
python reset_et_mise_a_jour_complet.py  # Tout nettoyer et recommencer
```

---

## 📁 STRUCTURE DATABASE

**Format attendu dans l'onglet DATABASE :**

| DATE (AB) | NO (AC) | NO (AD) | X (AE) | Y (AF) | Z (AG) |
|-----------|---------|---------|---------|---------|---------|
| 2024-08-28 00:00 | V1 | V1.Test | 823147.6488 | 1091710.0857 | -121.5674 |
| 2024-08-28 00:00 | V2 | V2.Test | 823147.5852 | 1091710.2506 | -121.9302 |
| 2025-11-26 08:00 | V1 | V1.Test | 823147.6490 | 1091710.0850 | -121.5690 |
| 2025-11-26 14:00 | V1 | V1.Test | 823147.6492 | 1091710.0848 | -121.5688 |
| 2025-11-26 20:00 | V1 | V1.Test | 823147.6495 | 1091710.0845 | -121.5685 |

**Notes importantes :**
- Les en-têtes DATABASE sont en ligne 12
- Les données commencent ligne 14
- La colonne DATE doit être nommée exactement "DATE"
- Format date : `YYYY-MM-DD HH:MM:SS` ou `DD/MM/YYYY HH:MM:SS`

---

## 🛡️ SÉCURITÉ

### Sauvegarde automatique :
- Si erreur lors de la sauvegarde → fichier `*_BACKUP.xlsm` créé automatiquement
- Toujours garder une copie du fichier original avant manipulation

### Confirmation utilisateur :
Les deux scripts demandent confirmation avant de modifier le fichier :
```
⚠️ Ce script va :
   1. VIDER toutes les données des onglets (garde structure)
   2. Extraire toutes les dates de DATABASE
   ...

Voulez-vous continuer ? (oui/non) :
```

---

## 📝 ONGLETS TRAITÉS

Les scripts mettent à jour ces onglets :
1. ✅ **Résultats observations** (coordonnées brutes)
2. ✅ **OBSERVATIONS** (coordonnées XYZ)
3. ✅ **PROJECTION** (coordonnées PM/H/V)
4. ✅ **EVOLUTIONS XYZ** (évolutions XYZ)
5. ✅ **ÉVOLUTION PM H V** (évolutions déports)
6. ✅ **cordes ref1** (distances vers REF1)
7. ✅ **cordes ref2** (distances vers REF2)
8. ✅ **EVOLUTIONS CORDES REF1** (évolutions cordes REF1)
9. ✅ **EVOLUTIONS CORDES REF2** (évolutions cordes REF2)

**Colonnes modifiées :**
- **Colonne A** : Dates (avec heure si mesure multiple)
- **Colonne B** : Jours depuis point 0 (avec décimales)

---

## ⚠️ LIMITATIONS ET NOTES

1. **Les formules Excel doivent déjà être en place**  
   Les scripts ne créent pas les formules, ils gèrent uniquement les dates

2. **DATABASE est la source de vérité**  
   Toutes les dates proviennent de l'onglet DATABASE

3. **Ordre chronologique strict**  
   Les dates sont toujours triées du plus ancien au plus récent

4. **Décimales pour jours**  
   Colonne B utilise des décimales (ex: 0.5 = 12 heures)

---

## 🐛 DÉPANNAGE

### Problème : "Colonne DATE non trouvée"
➡️ Vérifier que l'onglet DATABASE a bien "DATE" en ligne 12

### Problème : "Aucune date trouvée"
➡️ Vérifier que DATABASE contient des données à partir de la ligne 14

### Problème : Dates mal formatées
➡️ Les formats acceptés : `YYYY-MM-DD`, `DD/MM/YYYY`, avec ou sans heure

### Problème : Erreur de sauvegarde
➡️ Vérifier que le fichier Excel n'est pas ouvert dans Excel
➡️ Chercher le fichier `*_BACKUP.xlsm`

---

## 📞 SUPPORT

En cas de problème, vérifier :
1. ✅ Le fichier Excel existe
2. ✅ L'onglet DATABASE existe
3. ✅ La colonne DATE est en ligne 12
4. ✅ Des données existent à partir de ligne 14
5. ✅ Le fichier n'est pas ouvert dans Excel

---

**Dernière mise à jour : 26/11/2025**  
**Version : 1.0**
