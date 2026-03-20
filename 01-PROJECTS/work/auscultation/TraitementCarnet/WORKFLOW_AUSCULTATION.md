# 📊 WORKFLOW D'ANALYSE D'AUSCULTATION EN GALERIES
## Guide d'utilisation des outils d'analyse de déformation

---

## 🎯 CONTEXTE

**Problématique** : Surveillance d'auscultation en galeries souterraines **sans référentiel stable**.
- Toute la zone peut bouger
- Pas de points fixes absolus disponibles
- Nécessité de détecter les **mouvements différentiels** entre zones

**Solution** : Calcul en bloc multi-stations + analyse des écarts relatifs

---

## 🛠️ OUTILS DISPONIBLES

### 1. **Préparation des carnets** (avant calcul Covadis)

#### Suppression des préfixes de stations
```bash
# Supprime S1., S2., S3., S4., S5., S6. des noms de points
$content = Get-Content "carnet/MON-FICHIER.geo" -Raw
$content = $content -replace 'S2\.', '' -replace 'S3\.', '' -replace 'S5\.', '' -replace 'S6\.', ''
$content | Set-Content "carnet/MON-FICHIER.geo" -NoNewline
```

#### Remplacement de points temporaires
Utiliser les analogies entre points P. temporaires et noms définitifs
- **ATTENTION** : respecter les suffixes D/G (si P.14D → chercher un point en D)

---

### 2. **analyser_auscultation_GGS.py** - Analyse basique

**Quand l'utiliser** : Premier aperçu rapide après calcul

**Ce qu'il fait** :
- Calcule les écarts entre points mesurés et références (ref_Sxxxx)
- Statistiques globales (% ≤2mm, ≤5mm, moyennes)
- Détection de séries avec mouvements cohérents

**Commande** :
```bash
.\.venv\Scripts\python.exe analyser_auscultation_GGS.py
```

**Fichier à modifier** : Ligne finale du script
```python
analyser_ecarts('carnet/VOTRE-FICHIER-CALCULÉ.geo')
```

**Exemple de résultat** :
```
✅ 90.5% des points ≤2mm en XY
✅ Écart moyen : 0.9mm
⚠️  Série S031x : COHÉRENT - (affaissement -1mm)
```

---

### 3. **analyse_deformation_avancee.py** ⭐ - Analyse intelligente

**Quand l'utiliser** : **SYSTÉMATIQUEMENT** après chaque campagne de mesure

**Ce qu'il fait** :
1. **Détection automatique de zones cohérentes**
   - Regroupe les points proches avec mouvements similaires
   - Identifie les zones stables, en affaissement, en soulèvement

2. **Analyse des mouvements différentiels** 🚨
   - Compare les zones entre elles
   - **CRITIQUE** : Détecte les risques de fissuration (diff > 1.5mm)
   - **ATTENTION** : Surveiller les zones avec diff > 1mm

3. **Points isolés suspects**
   - Identifie les points avec comportement incohérent
   - Peut indiquer un problème de mesure ou point instable

4. **Recommandations de surveillance**
   - Priorité HAUTE/MOYENNE/FAIBLE pour chaque zone
   - Actions concrètes à entreprendre

**Commande** :
```bash
.\.venv\Scripts\python.exe analyse_deformation_avancee.py
```

**Fichier à modifier** : Ligne finale du script
```python
analyser_deformations('carnet/VOTRE-FICHIER-CALCULÉ.geo')
```

**Paramètres ajustables** (dans le script) :
```python
seuil_distance = 10.0        # Distance max pour regrouper en zone (mètres)
seuil_dz_similaire = 0.5     # Similarité de mouvement vertical (mm)
```

**Exemple de résultat** :
```
Zone #1 ✅ - STABLE COHÉRENT (5 points)
  dZ moyen: -0.1mm

Zone #3 ⬇️ - AFFAISSEMENT COHÉRENT (2 points: S0203, S0315)
  dZ moyen: -1.7mm
  ⚠️  ATTENTION: Mouvement cohérent de 1.7mm détecté

🚨 MOUVEMENTS DIFFÉRENTIELS DÉTECTÉS:
  Zone #1 vs Zone #3: Différence 1.6mm
  ⚠️⚠️  CRITIQUE: Mouvement différentiel > 1.5mm → risque de fissuration

🎯 Zone #3 (Priorité: 🔴 HAUTE)
  - Mouvement 1.7mm
  - Mouvement différentiel vs global (1.0mm)
```

---

### 4. **comparateur_epoques.py** ⭐⭐ - Suivi temporel

**Quand l'utiliser** : Comparer 2 campagnes de mesure (suivi dans le temps)

**Ce qu'il fait** :
1. **Calcule les déplacements** entre 2 époques
   - dX, dY, dZ pour chaque point
   - Déplacements XY et 3D

2. **Vue d'ensemble des mouvements**
   - Mouvement vertical moyen global
   - Écart-type (hétérogénéité)
   - Amplitude des mouvements

3. **Top mouvements**
   - Les 10 points qui ont le plus bougé verticalement
   - Les 5 points avec plus grands déplacements horizontaux

4. **Classification par zones**
   - Affaissement fort/modéré
   - Stable
   - Soulèvement modéré/fort

5. **Points critiques et recommandations**
   - Identifie les points stables (références locales potentielles)
   - Actions à entreprendre

**Commande** :
```bash
.\.venv\Scripts\python.exe comparateur_epoques.py
```

**Fichier à modifier** : Variables au début de `if __name__ == '__main__':`
```python
fichier_epoque1 = 'carnet/GGS-auscultation-251210-g.geo'  # Ancien
fichier_epoque2 = 'carnet/GGS-auscultation-260115-g.geo'  # Nouveau

deplacements = comparer_epoques(
    fichier_epoque1, 
    fichier_epoque2,
    nom_epoque_ancien="Campagne 10/12/2025",
    nom_epoque_nouveau="Campagne 15/01/2026"
)
```

**Exemple de résultat** :
```
Déplacement vertical (dZ):
  Moyen:      -1.2mm
  Écart-type: 1.8mm
  Amplitude:  4.5mm

🚨 FORTE HÉTÉROGÉNÉITÉ (σ = 1.8mm) → mouvements différentiels importants

🔽 Top 10 - Plus grands mouvements verticaux:
Point               dZ         dX         dY         XY
S0315            -3.2      +1.5      -0.8       1.7    ⬇️ Affaissement
S0203            -2.8      +0.3      -1.2       1.2    ⬇️ Affaissement

🚨 Affaissement fort (< -1.5mm): 8 points
⚠️  Affaissement modéré: 12 points
✅ Stable: 15 points

🚨 POINTS CRITIQUES (3) - Action immédiate requise:
   S0315, S0203, S0312
   → Re-mesurer dès que possible
   → Inspection visuelle de la structure

✅ 15 points stables peuvent servir de références locales
   Points les plus stables: S0031, S0032, S0071
```

---

## 📋 WORKFLOW COMPLET

### **Étape 1 : Préparation du carnet** (fichier -b.geo ou -C.geo)
```bash
# 1. Copier le carnet terrain dans carnet/
# 2. Supprimer les préfixes de stations S2., S3., etc.
# 3. Renommer les points temporaires P.xxx vers noms définitifs
#    (respecter les suffixes D/G)
```

### **Étape 2 : Calcul dans Covadis**
```
1. Ouvrir le carnet -b.geo dans Covadis
2. Calcul en bloc multi-stations
3. Sauvegarder le résultat (fichier -g.geo ou -H.geo)
4. Copier le fichier calculé dans carnet/
```

### **Étape 3 : Analyse de la campagne** 🔍
```bash
# Modifier le nom de fichier dans le script
# Puis lancer l'analyse avancée
.\.venv\Scripts\python.exe analyse_deformation_avancee.py
```

**À retenir de l'analyse :**
- Quelles zones ont bougé ? (liste des points)
- Y a-t-il des mouvements différentiels critiques ? (> 1.5mm)
- Zones prioritaires à surveiller

### **Étape 4 : Comparaison avec campagne précédente** 📈
```bash
# Modifier les noms de fichiers dans comparateur_epoques.py
# fichier_epoque1 = campagne précédente
# fichier_epoque2 = campagne actuelle

.\.venv\Scripts\python.exe comparateur_epoques.py
```

**À retenir de la comparaison :**
- Amplitude des mouvements depuis la dernière fois
- Zones en accélération
- Nouveaux points critiques
- Points stables utilisables comme références

### **Étape 5 : Actions et surveillance**
Selon les résultats :

**🚨 CRITIQUE (mouvement diff > 1.5mm ou dZ > 3mm)** :
- Re-mesurer rapidement (< 1 semaine)
- Inspection visuelle de la structure
- Alerte équipe sécurité

**⚠️ ATTENTION (mouvement diff > 1mm ou dZ > 2mm)** :
- Augmenter fréquence de mesure (diviser par 2 l'intervalle)
- Surveiller visuellement les zones concernées

**✅ NORMAL** :
- Surveillance standard
- Archiver les résultats

---

## 🎓 MÉTHODOLOGIE

### Principe de l'analyse sans référentiel stable

**Problème** : Impossible de savoir si un point a bougé en valeur absolue

**Solution** : Analyser les **mouvements relatifs** entre points/zones

### Ce qui est important :

✅ **Mouvements différentiels** (zones qui bougent différemment)
- Risque de contraintes, fissures, déformations structurelles

✅ **Cohérence des mouvements** par zone
- Si plusieurs points bougent ensemble → mouvement de zone (réel)
- Si un point bouge seul → suspect (erreur mesure ou point instable)

✅ **Évolution temporelle**
- Accélération des mouvements
- Apparition de nouvelles zones critiques

❌ **Ne PAS se focaliser sur** :
- Valeurs absolues des déplacements (tout bouge)
- Comparaison à un "zéro" théorique (n'existe pas)

### Seuils d'interprétation

| Mouvement différentiel | Interprétation |
|------------------------|----------------|
| < 0.8mm | Normal - Précision des mesures |
| 0.8 - 1.5mm | Surveillance - Mouvement réel mais acceptable |
| 1.5 - 3.0mm | ⚠️ Critique - Risque de fissuration |
| > 3.0mm | 🚨 Alerte - Action immédiate |

---

## 📁 ORGANISATION DES FICHIERS

```
TraitementCarnet/
├── carnet/                           # Tous les fichiers .geo
│   ├── GGS-auscultation-251210-b.geo    # Carnet terrain (brut)
│   ├── GGS-auscultation-251210-g.geo    # Carnet calculé
│   ├── GGS-auscultation-260115-g.geo    # Campagne suivante
│   └── ...
│
├── analyser_auscultation_GGS.py      # Analyse basique
├── analyse_deformation_avancee.py    # ⭐ Analyse intelligente
├── comparateur_epoques.py            # ⭐⭐ Comparaison temporelle
│
├── analyser_ecarts_GHA.py           # Pour carnets GHA (autre zone)
└── analyser_ecarts_stations.py      # Analyse écarts entre stations

```

**Convention de nommage recommandée** :
```
ZONE-auscultation-AAMMJJ-lettre.geo

Exemples:
- GGS-auscultation-251210-b.geo  (brut du 10/12/2025)
- GGS-auscultation-251210-g.geo  (calculé du 10/12/2025)
- GHA-poly&aucultations-251209-C.geo
- GHA-poly&aucultations-251209-H.geo
```

---

## 🔧 PARAMÈTRES AJUSTABLES

### Dans `analyse_deformation_avancee.py` :

```python
# Ligne ~60
seuil_distance = 10.0        # Distance max pour regrouper en zone (mètres)
                             # ↑ Augmenter si zones trop fragmentées
                             # ↓ Réduire si zones trop grandes

seuil_dz_similaire = 0.5     # Similarité de mouvement vertical (mm)
                             # ↑ Augmenter pour regrouper plus facilement
                             # ↓ Réduire pour être plus strict
```

### Critères de mouvements différentiels :

```python
# Ligne ~143
if diff > 0.8:  # Différence significative
    # ↑ Augmenter pour filtrer plus
    # ↓ Réduire pour être plus sensible
```

---

## 💡 ASTUCES

### Identifier rapidement les zones critiques
```bash
# Chercher les lignes avec 🚨 ou ⚠️⚠️ dans les résultats
.\.venv\Scripts\python.exe analyse_deformation_avancee.py | Select-String "🚨"
```

### Garder un historique
Créer un fichier `RESULTATS.txt` après chaque campagne :
```bash
.\.venv\Scripts\python.exe analyse_deformation_avancee.py > resultats-251210.txt
```

### Comparer plusieurs campagnes d'un coup
Modifier `comparateur_epoques.py` pour boucler sur plusieurs fichiers

---

## 🆘 TROUBLESHOOTING

**Erreur "FileNotFoundError"** :
- Vérifier le chemin du fichier (doit être dans `carnet/`)
- Vérifier l'orthographe exacte du nom de fichier

**"Aucun point d'auscultation trouvé"** :
- Vérifier le format des noms de points (S0xxx attendu)
- Vérifier que les points ref_S0xxx existent

**Résultats incohérents** :
- Vérifier que les préfixes de stations ont bien été supprimés
- Vérifier que le calcul Covadis s'est bien déroulé
- Comparer avec l'analyse basique

**Zones trop fragmentées** :
- Augmenter `seuil_distance` dans le script
- Augmenter `seuil_dz_similaire`

**Pas de mouvements différentiels détectés mais résultats suspects** :
- Réduire le seuil `if diff > 0.8` à 0.5 par exemple

---

## 📞 AIDE-MÉMOIRE RAPIDE

```bash
# 1. Préparer carnet (supprimer préfixes, renommer points)
# 2. Calculer dans Covadis
# 3. Analyse de la campagne
.\.venv\Scripts\python.exe analyse_deformation_avancee.py

# 4. Comparaison avec campagne précédente (si existe)
.\.venv\Scripts\python.exe comparateur_epoques.py

# 5. Archiver les résultats
Copy-Item carnet\GGS-auscultation-251210-g.geo archive\
```

**Points clés à surveiller** :
- 🚨 Mouvements différentiels > 1.5mm
- ⚠️ Zones prioritaires HAUTE
- 📊 Évolution de l'écart-type entre campagnes

---

*Dernière mise à jour : 11 décembre 2025*
