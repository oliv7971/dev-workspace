# TCPOINT Orientation Fixer

## 🎯 Objectif

Ce module AutoLISP résout un problème courant avec les blocs TCPOINT (points topographiques) qui apparaissent mal orientés après des transformations 3D ou des changements de système de coordonnées utilisateur (SCU) dans AutoCAD.

## 🔧 Problème résolu

Après des opérations comme :
- `3DALIGN`
- Changements de SCU (`UCS`)
- Rotations 3D
- Transformations géométriques

Les blocs TCPOINT peuvent apparaître "de profil" au lieu de face à l'utilisateur, ne montrant que le contour de la croix et du cercle au lieu de leur représentation complète.

## 🚀 Fonctionnalités

### **Détection automatique**
- Analyse l'orientation du bloc par rapport au SCU courant
- Compare les vecteurs normaux du bloc et du SCU
- Détecte les blocs mal orientés avec une tolérance configurable

### **Correction intelligente**
- **Méthode 1** : Recréation complète du bloc (recommandée)
  - Sauvegarde toutes les propriétés (position, calque, attributs)
  - Supprime l'ancien bloc
  - Recrée le bloc dans l'orientation correcte du SCU courant

- **Méthode 2** : Transformation en place (en développement)
  - Applique une rotation 3D pour corriger l'orientation
  - Conserve l'instance originale du bloc

### **Sélection flexible**
- Corriger une sélection manuelle
- Corriger tous les TCPOINT du dessin
- Corriger par calque spécifique
- Mode vérification sans correction

## 📋 Installation

1. Copiez les fichiers dans votre dossier AutoLISP
2. Chargez le fichier principal :
   ```lisp
   (load "tcpoint-orientation-main.lsp")
   ```

## 🎮 Utilisation

### **Commandes principales**

| Commande | Description |
|----------|-------------|
| `TCPOINT-FIX-SELECTION` | Corriger les blocs sélectionnés |
| `TCPOINT-FIX-ALL` | Corriger tous les TCPOINT du dessin |
| `TCPOINT-FIX-LAYER` | Corriger un calque spécifique |
| `TCPOINT-CHECK-ORIENTATION` | Vérifier sans corriger |

### **Commandes rapides**

| Commande | Équivalent |
|----------|------------|
| `TCFIX` | `TCPOINT-FIX-SELECTION` |
| `TCFIXALL` | `TCPOINT-FIX-ALL` |
| `TCCHECK` | `TCPOINT-CHECK-ORIENTATION` |

### **Menu interactif**
```
TCP-MENU
```
Ouvre un menu interactif pour accéder à toutes les fonctions.

## ⚙️ Configuration

### **Commandes de configuration**

| Commande | Description |
|----------|-------------|
| `TCP-CONFIG` | Afficher la configuration actuelle |
| `TCP-CONFIG-DEBUG` | Activer/désactiver le mode debug |
| `TCP-CONFIG-METHOD` | Basculer entre recréation/rotation |
| `TCP-CONFIG-TOLERANCE` | Définir la tolérance de détection |

### **Variables de configuration**

```lisp
*TCPOINT_BLOCKS*        ; Liste des noms de blocs reconnus
*DEBUG_MODE*            ; Mode debug (T/nil)
*USE_RECREATION_METHOD* ; Méthode de correction (T/nil)
*ORIENTATION_TOLERANCE* ; Tolérance de détection (0.05)
```

## 🔍 Diagnostic

### **Commandes de diagnostic**

| Commande | Description |
|----------|-------------|
| `TCP-DIAG-UCS` | Informations sur le SCU courant |
| `TCP-DIAG-BLOCK` | Diagnostic d'un bloc sélectionné |
| `TCPOINT-SYSTEM-CHECK` | Vérifier l'installation |

## 📚 Exemples d'utilisation

### **Correction rapide**
```
TCFIXALL
```
Corrige automatiquement tous les TCPOINT mal orientés.

### **Vérification avant correction**
```
TCCHECK
```
Vérifie quels blocs sont mal orientés sans les modifier.

### **Correction par étapes**
1. Diagnostiquer le SCU : `TCP-DIAG-UCS`
2. Vérifier les blocs : `TCCHECK`
3. Corriger si nécessaire : `TCFIX`

## 🛠️ Fonctionnement technique

### **Détection d'orientation**
1. Récupère la normale du bloc (vecteur Z local)
2. Récupère la normale du SCU courant
3. Compare l'alignement des vecteurs
4. Détermine si une correction est nécessaire

### **Processus de correction**
1. Sauvegarde des propriétés :
   - Position d'insertion
   - Calque, couleur, type de ligne
   - Attributs et leurs valeurs
   - Échelles X, Y, Z
   - Rotation

2. Suppression de l'ancien bloc

3. Création du nouveau bloc :
   - Insertion dans le SCU courant
   - Application des propriétés sauvegardées
   - Restauration des attributs

## 🎯 Cas d'usage typiques

### **Après 3DALIGN**
```
TCFIXALL
```

### **Après changement de SCU**
1. Définir le nouveau SCU
2. `TCFIXALL` pour réorienter tous les points

### **Correction sélective**
1. Sélectionner les blocs problématiques
2. `TCFIX`

## 🔧 Personnalisation

### **Ajouter des types de blocs**
```lisp
(tcp-config:add-block-type "MON_TCPOINT")
```

### **Ajuster la tolérance**
```lisp
(tcp-config:set-tolerance 0.1)  ; Plus permissif
```

### **Mode debug**
```lisp
(setq *DEBUG_MODE* T)  ; Voir les détails de traitement
```

## 📋 Limitations

- La méthode par rotation n'est pas encore implémentée
- Nécessite que les blocs TCPOINT existent dans la table des blocs
- Les attributs doivent être compatibles entre l'ancien et le nouveau bloc

## 🆘 Dépannage

### **Les blocs ne sont pas détectés**
- Vérifiez que le nom du bloc est dans `*TCPOINT_BLOCKS*`
- Utilisez `TCP-CONFIG-ADD-BLOCK` pour ajouter de nouveaux types

### **La correction ne fonctionne pas**
- Vérifiez que le bloc TCPOINT existe : `(tblsearch "BLOCK" "TCPOINT")`
- Activez le mode debug : `TCP-CONFIG-DEBUG`
- Vérifiez l'installation : `TCPOINT-SYSTEM-CHECK`

### **Performance lente**
- Désactivez le mode debug pour les gros traitements
- Travaillez par calques plutôt que sur tout le dessin

## 📞 Support

Tapez `TCP-HELP` dans AutoCAD pour une aide contextuelle complète.