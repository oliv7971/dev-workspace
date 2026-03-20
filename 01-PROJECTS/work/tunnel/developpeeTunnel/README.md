# Calculateur d'Angles pour Profils de Tunnel

Ce programme calcule l'angle de chaque point par rapport à l'axe du tunnel à partir des données générées par le logiciel Amberg.

## Fonctionnalités

- Lit les fichiers CSV générés par Amberg
- Calcule l'angle de chaque point par rapport à l'axe du tunnel
- Utilise les coordonnées X/L (transversale) et Y/H (longitudinale)
- Sauvegarde les résultats dans un nouveau fichier CSV
- Affiche des statistiques détaillées

## Utilisation

### 1. Script simple (recommandé pour usage quotidien)

```bash
python calcul_angle_simple.py fichier_amberg.csv
```

Exemple :
```bash
python calcul_angle_simple.py AnalysisData_PM_13.408m.csv
```

### 2. Script complet (pour tests et développement)

```bash
python calculateur_angles_tunnel.py
```

## Format des données d'entrée

Le programme attend un fichier CSV avec la structure suivante :
- Séparateur : point-virgule (;)
- Encodage : Latin-1
- Colonnes G et H : Coordonnées X/L et Y/H par rapport à l'axe

Exemple de structure :
```
#Nom du point;Est;Nord;Hauteur;PM Tunnel;PM 3D;Coordonnée X/L;Coordonnée Y/H;...
1;823283.340603;1091528.57314;-122.988765171;13.4001052121;13.4007752006;5.07818254092;-0.353766222667;...
```

## Calcul de l'angle

L'angle est calculé avec la formule :
```
angle = arctan2(Y, X)
```

Où :
- X = Coordonnée transversale (colonne G)
- Y = Coordonnée longitudinale (colonne H)
- Résultat en degrés

### Convention d'angles (référence : axe X transversal)

- **0°** = Direction transversale pure (perpendiculaire à l'axe du tunnel)
- **90°** = Direction longitudinale pure (dans l'axe du tunnel vers l'avant)
- **-90°** = Direction longitudinale pure (dans l'axe du tunnel vers l'arrière)
- **±180°** = Direction transversale opposée

Cette convention est adaptée aux profils de tunnel car elle donne directement l'orientation du point par rapport à la section transversale.

## Fichiers de sortie

Le programme génère un nouveau fichier CSV avec :
- Toutes les colonnes originales
- Une colonne supplémentaire "Angle (degres)"
- Même format que le fichier d'entrée

## Statistiques affichées

- Nombre de points traités
- Angle minimum et maximum
- Angle moyen
- Écart-type
- Aperçu des premiers points

## Prérequis

- Python 3.x
- Bibliothèques : pandas, numpy

Installation des dépendances :
```bash
pip install pandas numpy
```

## Exemples de résultats

Pour le fichier exemple `AnalysisData_PM_13.408m.csv` :
- 54 points traités
- Angles de -178.941° à +177.672°
- Angle moyen : 75.824°

### Interprétation des résultats :
- **Points 1-2** : Angles négatifs (-3.985°, -0.450°) = Points légèrement en arrière de l'axe transversal
- **Points suivants** : Angles positifs croissants = Points de plus en plus orientés vers l'avant du tunnel
- **Plage complète** : Couvre quasiment toutes les orientations possibles (-179° à +178°)

## Structure des fichiers

```
developpeeTunnel/
├── calculateur_angles_tunnel.py   # Classe complète
├── calcul_angle_simple.py         # Script simple d'utilisation
├── README.md                      # Cette documentation
├── AnalysisData_PM_13.408m.csv   # Fichier exemple d'Amberg
└── resultats/                     # Fichiers de sortie générés
```

## Support

Pour toute question ou amélioration, contactez l'équipe de développement.