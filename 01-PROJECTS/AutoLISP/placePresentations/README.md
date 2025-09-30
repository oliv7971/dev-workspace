# AutoLISP Viewport Centering Tool

Ce projet fournit un script AutoLISP pour AutoCAD permettant de recentrer et de paramétrer automatiquement les fenêtres de présentation (viewports) selon un centre et une échelle spécifiés.

## Fonctionnalités
- Recentrer une fenêtre de présentation sur un point donné
- Définir l'échelle d'affichage de la fenêtre


## Utilisation
1. Chargez le script `placePresentations.lsp` dans AutoCAD (commande APPLOAD).
2. Passez en présentation (layout) et sélectionnez la fenêtre de présentation (viewport) à modifier.
3. Lancez la commande `VP-CENTER-SCALE` dans la ligne de commande AutoCAD.
4. Indiquez le centre de la vue (point à viser dans l'espace papier).
5. Indiquez l'échelle souhaitée (par exemple, 100 pour 1/100).
6. La fenêtre sera recentrée et l'échelle appliquée.

## Personnalisation
Vous pouvez modifier le script pour appliquer des règles automatiques, par exemple :
- Récupérer le centre d'un objet ou d'une coupe automatiquement
- Appliquer une échelle selon le nom de la présentation
- Traiter plusieurs fenêtres en boucle

N'hésitez pas à demander des adaptations spécifiques selon vos besoins métier.

## Fichiers
- `placePresentations.lsp` : Script principal
- `README.md` : Ce fichier

---

*Remplacez ce texte par des instructions plus détaillées selon vos besoins.*