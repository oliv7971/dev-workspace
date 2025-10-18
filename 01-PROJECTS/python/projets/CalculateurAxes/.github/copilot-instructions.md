<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Calculateur d'Axes - Instructions Copilot

## Vue d'ensemble du projet
Application Python pour calculs topographiques d'axes routiers/ferroviaires avec gestion des projections cartographiques.

## Architecture des modules
- `core/` : Classes géométriques de base (Point, Vecteur, Éléments d'axe)
- `calculs/` : Algorithmes de calcul par lots et transformations
- `io/` : Import/Export Excel, DXF et formats terrain
- `interface/` : Interface utilisateur (GUI ou CLI)

## Spécificités métier
- Calculs en grades (0-400g) pour les gisements
- Gestion des altérations linéaires (Lambert, terrain)
- Projections point/axe avec PM (Point Métrique) et déports
- Éléments géométriques : alignements, arcs, clothoïdes, paraboles

## Conventions de codage
- Utiliser numpy/pandas pour calculs vectoriels
- Classes abstraites pour éléments d'axe
- Gestion d'erreurs explicite pour valeurs hors limites
- Documentation claire des formules topographiques utilisées

## Workflow principal
1. Définition axe (par sommets ou paramètres)
2. Configuration projection/altération
3. Calculs par lots (XYZ ↔ PM/Déport)
4. Export résultats Excel/DXF