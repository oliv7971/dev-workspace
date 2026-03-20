# 📊 SAISIE D'AXES - Guide Complet

## 🎯 **Réponse à votre question : "Comment se fait la saisie d'axes ?"**

**OUI, la saisie d'axes passe principalement par Excel !** Le système propose plusieurs méthodes flexibles et professionnelles.

## 📋 **Méthodes de Saisie Disponibles**

### ✅ **1. Saisie Excel par Éléments Géométriques** ⭐ **RECOMMANDÉE**

**Fichier** : `modele_saisie_elements.xlsx`

#### Feuille "Elements"
```
Element | Type | Param1  | Param2 | Param3 | Description
--------|------|---------|--------|--------|-------------
1       | AD   | 50.0    | 150.0  |        | Alignement 150m, Gis=50g
2       | CL   |         | 500.0  | 100.0  | Clothoïde ∞→R500m
3       | C    | 500.0   | 60.0   |        | Arc R=500m, Δ=60g
4       | CL   | 500.0   |        | 100.0  | Clothoïde R500m→∞
5       | AD   | 110.0   | 200.0  |        | Alignement 200m
```

**Types d'éléments :**
- **AD** (Alignement Droit) : Param1=Gisement(g), Param2=Longueur(m)
- **C** (Arc Circulaire) : Param1=Rayon(m), Param2=Déviation(g)
- **CL** (Clothoïde) : Param1=R_début, Param2=R_fin, Param3=Longueur(m)

#### Feuille "Profil" 
```
PM   | Z     | Pente | Description
-----|-------|-------|-------------
0    | 100.0 | 2.0   | Début
150  | 103.0 | 1.5   | Fin alignement
350  | 106.0 | 1.8   | Milieu arc
550  | 108.5 | 1.2   | Fin axe
```

#### Feuille "Parametres"
```
Parametre     | Valeur        | Description
--------------|---------------|------------------
PM_Debut      | 1000.0       | PM de début d'axe
X_Debut       | 500000.0     | Coordonnée X Lambert93
Y_Debut       | 2000000.0    | Coordonnée Y Lambert93
Z_Debut       | 100.0        | Altitude début
Nom_Axe       | RD123_A      | Identification axe
```

### ✅ **2. Saisie Excel par Sommets**

**Fichier** : `modele_saisie_sommets.xlsx`

```
Sommet | X        | Y         | Z     | PM   | Rayon | Type
-------|----------|-----------|-------|------|-------|----------
S1     | 500000.0 | 2000000.0 | 100.0 | 0.0  |       | Debut
S2     | 500150.0 | 2000000.0 | 103.0 | 150  | 500.0 | Courbe_D
S3     | 500300.0 | 2000100.0 | 106.0 | 350  |       | Tangente
S4     | 500500.0 | 2000150.0 | 108.5 | 550  |       | Fin
```

### ✅ **3. Points à Projeter**

**Fichier** : `modele_points_a_traiter.xlsx`

```
ID   | X        | Y         | Z     | Type     | Description
-----|----------|-----------|-------|----------|------------------
P001 | 500075.0 | 1999980.0 | 102.5 | Borne    | Borne kilométrique
P002 | 500125.0 | 2000020.0 | 103.2 | Ouvrage  | Buse DN800
P003 | 500200.0 | 1999950.0 | 105.8 | Arbre    | Arbre à abattre
```

## 🔄 **Workflow de Travail**

### **Étape 1 : Préparation** 📝
1. Utiliser les modèles Excel fournis dans `exemples/`
2. Adapter les données à votre projet
3. Remplir les feuilles selon vos besoins

### **Étape 2 : Import** 📥
```python
# Via le menu principal (option 7)
# Ou par code :
io_excel = ExcelIO()
elements = io_excel.charger_definition_axe("mon_axe.xlsx", "Elements")
profil = io_excel.charger_profil_long("mon_axe.xlsx", "Profil")
points = io_excel.charger_points("mes_points.xlsx")
```

### **Étape 3 : Construction** 🏗️
L'axe est automatiquement construit depuis la définition Excel :
- **Continuité géométrique** assurée
- **Validation** des paramètres
- **Gestion d'erreurs** avec messages explicites

### **Étape 4 : Calculs** 🎯
```python
# Projections automatiques
for point in points:
    pm, deport = axe.projeter_point(point)
    print(f"{point.id}: PM={pm:.1f}m, Déport={deport:.1f}m")
```

### **Étape 5 : Export** 📤
```python
# Résultats vers Excel
resultats = calculer_projections(axe, points)
io_excel.exporter_points(resultats, "resultats.xlsx", "complet")
```

## 📊 **Fichiers de Sortie**

### **Résultats Complets**
```
ID   | X        | Y         | Z     | PM     | Deport_H | Deport_V | Distance_3D
-----|----------|-----------|-------|--------|----------|----------|-------------
P001 | 500075.0 | 1999980.0 | 102.5 | 1075.0 | -20.0    | 0.5      | 20.01
P002 | 500125.0 | 2000020.0 | 103.2 | 1125.0 | 20.0     | 0.2      | 20.01
```

## 🛠️ **Fonctionnalités Avancées**

### **Détection Automatique de Format**
```python
format_detecte, df = io_excel.detecter_format("fichier.xlsx")
# Reconnaît automatiquement : points, sommets, elements, profil
```

### **Validation Intégrée**
- ✅ **Coordonnées** : Limites géographiques
- ✅ **Gisements** : 0-400g, cohérence
- ✅ **Rayons** : Valeurs minimales/maximales
- ✅ **PM** : Continuité, ordre croissant

### **Export Multi-formats**
- **Excel** : `.xlsx` avec mise en forme
- **DXF** : Export CAO (optionnel)
- **CSV** : Format universel

## 💡 **Avantages de la Saisie Excel**

### ✅ **Familiarité**
- Interface connue des topographes
- Formules Excel utilisables
- Copier/coller depuis autres sources

### ✅ **Flexibilité**  
- Modification facile des données
- Ajout de colonnes personnalisées
- Commentaires et descriptions

### ✅ **Traçabilité**
- Historique des modifications
- Validation des données
- Documentation intégrée

### ✅ **Intégration**
- Compatible avec logiciels topographiques
- Export depuis stations totales
- Import de bases de données

## 🎯 **Cas d'Usage Typiques**

### **1. Projet Routier**
1. **Géomètre** : Saisit les sommets dans Excel
2. **Projeteur** : Définit les éléments géométriques  
3. **Calculateur** : Import et validation automatique
4. **Résultats** : Export pour implantation terrain

### **2. Étude d'Impact**
1. **Points relevés** : Import depuis fichier terrain
2. **Axe projet** : Saisie par éléments
3. **Calculs** : Projections automatiques
4. **Analyse** : Export pour SIG/CAO

### **3. Contrôle Qualité**
1. **Données existantes** : Import multi-sources
2. **Validation** : Contrôles automatiques
3. **Corrections** : Retour Excel pour ajustements
4. **Certification** : Export résultats validés

## 📁 **Fichiers Disponibles**

Après exécution de `demo_saisie_excel.py` :

```
exemples/
├── modele_saisie_elements.xlsx    ⭐ Modèle principal
├── modele_saisie_sommets.xlsx     📍 Saisie par points
├── modele_points_a_traiter.xlsx   🎯 Points à projeter  
├── exemple_resultats.xlsx         📊 Format de sortie
├── resultats_calculs.xlsx         💾 Résultats exemple
├── export_points_axe.xlsx         📤 Export axe
└── GUIDE_SAISIE_EXCEL.md         📚 Documentation
```

## 🚀 **Pour Commencer**

```bash
# 1. Lancer l'application
python main.py

# 2. Choisir option 7 "Import/Export Excel"
# 3. Les modèles sont créés automatiquement
# 4. Modifier les fichiers Excel selon vos besoins
# 5. Relancer l'import

# Ou directement :
python demo_saisie_excel.py
```

## ✅ **Conclusion**

**La saisie d'axes via Excel est la méthode principale et recommandée !**

Le système offre :
- 🎯 **Interface familière** (Excel) 
- 🔧 **Import/Export automatisés**
- ✅ **Validation complète** des données
- 📊 **Formats standardisés** et flexibles
- 🚀 **Workflow professionnel** complet

**Vous disposez d'un véritable système de saisie d'axes industriel !** 🎉