# Calculateur de Développée de Tunnel

Ce programme transforme un profil circulaire de tunnel en **développée plane** pour cartographier les écarts le long de la voûte "déroulée".

## Principe

Au lieu d'analyser les écarts en coordonnées polaires (angle, écart), la développée permet de visualiser les écarts sur une **cartographie 2D linéaire** :
- **Axe X** : Longueur développée le long de la voûte (en mètres)
- **Axe Y** : Écart par rapport au profil théorique (en millimètres)

## Fonctionnalités

### 🔍 **Estimation automatique du rayon**
- Calcul du rayon moyen à partir des coordonnées X,Y
- Validation de la qualité de l'approximation circulaire
- Écart relatif < 5% = bon profil circulaire

### 📏 **Calcul de la développée**
- Conversion angles → longueurs développées : `L = R × angle`
- Tri des points par angle pour développée continue
- Référence au premier point de la série

### 📊 **Visualisation graphique**
- **Graphique 1** : Développée plane (longueur vs écart)
- **Graphique 2** : Profil original coloré par écart
- Sauvegarde automatique en PNG haute résolution

## Utilisation

### Script simple (recommandé)
```bash
python developpee_simple.py fichier_amberg.csv
```

### Script complet
```bash
python calculateur_developpee_tunnel.py
```

## Résultats pour l'exemple

### Estimation du rayon
- **Rayon moyen** : 5.149 m
- **Écart relatif** : 1.62% (excellent profil circulaire)
- **Étendue** : 5.008 m à 5.312 m

### Développée calculée
- **Longueur totale** : 32.05 m
- **Étendue angulaire** : 356.6° (profil quasi-complet)
- **Écarts** : 58 mm à 362 mm (moyenne : 199 mm)

## Format de sortie

### Fichier CSV généré
```
Point_Original;Angle_deg;Longueur_Developpee_m;Ecart_mm;X_original;Y_original
53;-178.94;0.000;171.94;-5.121;-0.095
54;-177.10;0.166;167.44;-5.111;-0.259
1;-3.99;15.724;140.49;5.078;-0.354
...
```

### Colonnes explicatives
- **Point_Original** : Numéro du point d'origine
- **Angle_deg** : Angle par rapport à l'axe X (degrés)
- **Longueur_Developpee_m** : Position sur la développée (mètres)
- **Ecart_mm** : Écart par rapport au profil théorique (millimètres)
- **X_original, Y_original** : Coordonnées originales Amberg

## Applications pratiques

### 🎯 **Analyse linéaire des défauts**
- Détection de zones problématiques par position linéaire
- Corrélation avec les travaux de terrassement
- Suivi de l'évolution des déformations

### 📈 **Visualisation intuitive**
- Cartographie "déroulée" plus lisible que les coordonnées polaires
- Identification des patterns d'écart
- Comparaison entre différents profils

### 🔧 **Contrôle qualité**
- Validation des tolérances sur la longueur développée
- Localisation précise des dépassements de seuil
- Rapport de conformité par section

## Avantages de la méthode

1. **Simplicité** : Rayon moyen suffisant pour la plupart des tunnels
2. **Précision** : Écart relatif < 2% sur l'exemple
3. **Lisibilité** : Développée plus intuitive que les coordonnées polaires
4. **Automatisation** : Traitement batch possible

## Prérequis

```bash
pip install pandas numpy matplotlib
```

## Structure des fichiers

```
developpeeTunnel/
├── calculateur_developpee_tunnel.py  # Classe complète
├── developpee_simple.py              # Script d'utilisation simple
├── README_DEVELOPPEE.md              # Cette documentation
└── resultats/
    ├── *.csv                         # Fichiers de développée
    └── *.png                         # Graphiques générés
```

La développée de tunnel vous donne une vision **linéaire et intuitive** des écarts de votre profil ! 🚇