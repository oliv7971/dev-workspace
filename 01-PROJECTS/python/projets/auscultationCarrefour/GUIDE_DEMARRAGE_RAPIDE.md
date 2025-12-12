# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## 📦 4 SCRIPTS CRÉÉS

### 1. `visualiseur_dates.py` - 👀 VOIR CE QU'IL Y A
**À utiliser EN PREMIER** pour comprendre vos données

```bash
python visualiseur_dates.py
```

**Résultat :**
```
📊 ANALYSE DATABASE
===================================
✅ 156 mesures trouvées
📅 Première mesure : 28/08/2024 00:00
📅 Dernière mesure  : 27/11/2025 20:00
🎯 7 cibles (V1, V2, V3, H1, H2, REF1, REF2)

🔄 MESURES MULTIPLES PAR JOUR : 3 jours
📅 26/11/2025 : 3 mesures/cible
   ⏰ Heures : 08:00, 14:00, 20:00
```

**Comparer avec les onglets :**
```bash
python visualiseur_dates.py compare
```

---

### 2. `reset_et_mise_a_jour_complet.py` - 🔄 TOUT NETTOYER
**À utiliser quand :** Première fois, problème de données, doute sur la cohérence

```bash
python reset_et_mise_a_jour_complet.py
```

**Ce qu'il fait :**
- ❌ Vide TOUT (colonnes A et B de tous les onglets)
- 📅 Récupère toutes les dates de DATABASE
- ✅ Réinsère dans l'ordre chronologique
- 🔢 Les formules Excel se recalculent automatiquement

---

### 3. `ajouter_nouvelles_mesures.py` - ➕ AJOUTER NOUVELLES DATES
**À utiliser quand :** Nouvelle campagne, mesure supplémentaire, mise à jour régulière

```bash
python ajouter_nouvelles_mesures.py
```

**Ce qu'il fait :**
- 🔍 Compare DATABASE avec les onglets
- ➕ Ajoute seulement les nouvelles dates
- 📊 Garde toutes les données existantes
- ⚡ Plus rapide que le reset complet

---

### 4. `test_systeme_mesures.py` - 🧪 TESTER SANS RISQUE
**À utiliser pour :** S'entraîner avant de toucher au vrai fichier

```bash
python test_systeme_mesures.py
```

**Crée :** `TEST_AUSCULTATION.xlsm` avec :
- 30 jours de mesures normales (1/jour)
- 3 jours de mesures accélérées (3/jour)
- Toutes les structures nécessaires

**Puis testez les autres scripts sur ce fichier de test !**

---

## 📋 SCÉNARIOS D'UTILISATION

### 🟢 Scénario 1 : Première utilisation
```bash
# 1. Voir ce qu'il y a
python visualiseur_dates.py

# 2. Reset complet pour partir sur de bonnes bases
python reset_et_mise_a_jour_complet.py

# 3. Ouvrir Excel et vérifier
```

---

### 🟡 Scénario 2 : Ajout de nouvelles mesures (hebdomadaire)
```bash
# 1. Ajouter les données dans DATABASE (via Excel ou import)

# 2. Vérifier rapidement
python visualiseur_dates.py compare

# 3. Ajouter seulement les nouvelles dates
python ajouter_nouvelles_mesures.py
```

---

### 🔴 Scénario 3 : ALERTE - Mesures accélérées (6h/12h/18h)
```bash
# Les parois bougent vite → mesures toutes les 6 heures

# 1. Ajouter dans DATABASE :
#    26/11/2025 06:00, V1, ...
#    26/11/2025 12:00, V1, ...
#    26/11/2025 18:00, V1, ...

# 2. Vérifier les mesures multiples
python visualiseur_dates.py

# 3. Mettre à jour (gère automatiquement les heures)
python ajouter_nouvelles_mesures.py

# 4. Dans Excel, vous verrez :
#    Ligne 45: 26/11/2025 06:00
#    Ligne 46: 26/11/2025 12:00
#    Ligne 47: 26/11/2025 18:00
```

---

### 🟠 Scénario 4 : Problème détecté / Données corrompues
```bash
# 1. Analyser le problème
python visualiseur_dates.py compare

# 2. Reset complet (solution radicale)
python reset_et_mise_a_jour_complet.py

# 3. Tout est nettoyé et reconstruit à partir de DATABASE
```

---

### 🧪 Scénario 5 : Test avant utilisation réelle
```bash
# 1. Créer un fichier de test
python test_systeme_mesures.py

# 2. Modifier les scripts pour utiliser TEST_AUSCULTATION.xlsm
#    (changer FICHIER_EXCEL = "TEST_AUSCULTATION.xlsm")

# 3. Tester tous les scripts sur le fichier de test

# 4. Une fois confiant, revenir au vrai fichier
```

---

## ⚙️ CONFIGURATION

Dans chaque script, vous pouvez modifier :

```python
# Nom du fichier Excel
FICHIER_EXCEL = "01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm"

# Onglets à traiter
ONGLETS_A_TRAITER = [
    "Résultats observations",
    "OBSERVATIONS",
    "PROJECTION",
    ...
]

# Ligne de début des données
LIGNE_DEBUT_DONNEES = 10
```

---

## 🛡️ SÉCURITÉ

### ✅ Confirmations automatiques
Tous les scripts demandent confirmation avant modification :
```
⚠️ Ce script va modifier le fichier Excel
Voulez-vous continuer ? (oui/non) :
```

### 💾 Sauvegardes automatiques
En cas d'erreur lors de la sauvegarde :
- Fichier `*_BACKUP.xlsm` créé automatiquement
- Toujours garder une copie du fichier original !

### 🔍 Mode lecture seule
Le `visualiseur_dates.py` ne modifie JAMAIS le fichier

---

## 📊 FORMAT DATABASE ATTENDU

```
| Ligne 12 | AB (DATE) | AC (NO) | AD (NO) | AE (X) | AF (Y) | AG (Z) |
|----------|-----------|---------|---------|--------|--------|--------|
| Ligne 14 | 2024-08-28 00:00:00 | V1 | V1.Test | 823147.6488 | ... | ... |
| Ligne 15 | 2024-08-28 00:00:00 | V2 | V2.Test | 823147.5852 | ... | ... |
| Ligne 16 | 2025-11-26 08:00:00 | V1 | V1.Test | 823147.6490 | ... | ... |
| Ligne 17 | 2025-11-26 14:00:00 | V1 | V1.Test | 823147.6492 | ... | ... |
```

**Important :**
- En-têtes en ligne 12
- Données à partir de ligne 14
- Colonne DATE doit s'appeler exactement "DATE"
- Format date : `YYYY-MM-DD HH:MM:SS` ou `DD/MM/YYYY HH:MM:SS`

---

## ❓ QUESTIONS FRÉQUENTES

### Q: Quelle différence entre reset et ajouter ?
**R:** 
- **Reset** = Vide tout et reconstruit (première fois, problème)
- **Ajouter** = Garde existant et ajoute nouvelles dates (mise à jour régulière)

### Q: Comment gérer 3 mesures le même jour ?
**R:** Les scripts gèrent automatiquement ! Les dates incluent l'heure :
```
26/11/2025 08:00
26/11/2025 14:00
26/11/2025 20:00
```

### Q: Les formules Excel sont-elles conservées ?
**R:** Oui ! Les scripts modifient uniquement les colonnes A et B (dates). Les formules dans les autres colonnes restent intactes et se recalculent automatiquement.

### Q: Que faire si erreur "Colonne DATE non trouvée" ?
**R:** Vérifier que l'onglet DATABASE a bien "DATE" écrit exactement comme ça en ligne 12.

### Q: Puis-je annuler une opération ?
**R:** Avant d'exécuter, faites une copie du fichier Excel. Si problème, revenez à la copie.

---

## 🎯 CHECKLIST AVANT PREMIÈRE UTILISATION

- [ ] J'ai fait une copie de sauvegarde du fichier Excel
- [ ] J'ai vérifié que DATABASE existe et contient des données
- [ ] J'ai testé avec `python visualiseur_dates.py`
- [ ] J'ai lu la sortie et compris combien de mesures j'ai
- [ ] Je sais quel script utiliser (reset ou ajouter)
- [ ] J'ai fermé Excel avant d'exécuter le script

---

## 📞 EN CAS DE PROBLÈME

1. **NE PAS PANIQUER** 🧘
2. Fermer Excel
3. Chercher le fichier `*_BACKUP.xlsm`
4. Relancer avec `visualiseur_dates.py` pour diagnostiquer
5. Si besoin, exécuter `reset_et_mise_a_jour_complet.py`

---

**Version : 1.0**  
**Date : 26/11/2025**
