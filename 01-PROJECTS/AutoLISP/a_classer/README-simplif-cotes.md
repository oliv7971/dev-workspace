# SIMPLIF-COTES.LSP - Simplification des cotes en tunnel

## Description
Ce script AutoLISP permet de simplifier vos plans de coupes de tunnel en supprimant automatiquement une cote sur deux selon un parcours geometrique logique.

## Installation
1. Copier le fichier `simplif-cotes.lsp` dans un repertoire accessible
2. Dans AutoCAD, charger le script :
   ```
   (load "C:/data/20-DEVELOPPEMENT/AutoLISP/simplif-cotes.lsp")
   ```
3. Ou utiliser la commande APPLOAD dans AutoCAD

## Utilisation

### Commande principale : `SIMPLIF-COTES`

Le script propose deux modes :

### Mode Automatique [A]
- Detecte automatiquement l'ordre geometrique des cotes
- Calcule le centre des cotes et les trie par angle polaire
- Ideal pour des cotes disposees en arc ou en cercle autour d'un cintre

**Procedure :**
1. Tapez `SIMPLIF-COTES`
2. Choisissez `A` pour automatique
3. Selectionnez toutes les cotes a simplifier
4. Le script supprime automatiquement une cote sur deux

### Mode Polyligne [P]
- Utilise une polyligne de reference pour definir l'ordre de parcours
- Plus precis pour des formes complexes ou irregulieres
- Vous controlez exactement le parcours

**Procedure :**
1. Dessinez une polyligne qui suit le parcours souhaite
2. Tapez `SIMPLIF-COTES`
3. Choisissez `P` pour polyligne
4. Selectionnez la polyligne de reference
5. Selectionnez toutes les cotes a simplifier
6. Le script trie les cotes selon la polyligne et supprime une sur deux

## Conseils d'utilisation

### Pour les profils de cintres :
- **Mode automatique** : Ideal si les cotes sont disposees regulierement autour du cintre
- **Mode polyligne** : Recommande pour des formes complexes ou si vous voulez controler precisement l'ordre

### Preparation :
- Verifiez que toutes vos cotes sont bien des objets DIMENSION
- En mode polyligne, dessinez la polyligne dans le sens ou vous voulez parcourir les cotes
- Faites une sauvegarde avant d'executer le script

### Verification :
- Le script affiche le nombre de cotes trouvees et supprimees
- Utilisez CTRL+Z si le resultat ne convient pas

## Exemple d'usage typique

Pour un profil de cintre avec 20 cotes tout autour :
1. `SIMPLIF-COTES`
2. Mode `A` (automatique)
3. Selection des 20 cotes
4. Resultat : 10 cotes supprimees, 10 conservees en alternance

## Personnalisation

Le script peut etre modifie pour :
- Changer le ratio (ex: supprimer 2 sur 3 au lieu d'1 sur 2)
- Modifier l'algorithme de tri
- Ajouter des filtres par calque ou proprietes

## Troubleshooting

**"Aucune cote selectionnee"** : Verifiez que vous selectionnez des objets DIMENSION
**Ordre bizarre** : En mode automatique, essayez le mode polyligne pour plus de controle
**Script non charge** : Verifiez le chemin d'acces au fichier .lsp
