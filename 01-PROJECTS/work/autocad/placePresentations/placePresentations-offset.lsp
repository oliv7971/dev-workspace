; filepath: c:\data\20-DEVELOPPEMENT\AutoLISP\placePresentations\placePresentations-offset.lsp
; placePresentations-offset.lsp
; Version avec décalage optionnel pour mieux centrer les vues

;; Essayer de charger le fichier principal (si pas déjà chargé)
;; Utilise le même dossier que ce fichier
(if (not (boundp 'get-intersections-on-layer))  ; Vérifier si une fonction du fichier principal existe
  (progn
    (princ "\nChargement du fichier principal placePresentations.lsp...")
    ; Essayer plusieurs méthodes de chargement
    (cond
      ; Méthode 1: même dossier
      ((findfile "placePresentations.lsp")
       (load "placePresentations.lsp"))
      ; Méthode 2: chemin complet
      ((findfile "c:\\data\\20-DEVELOPPEMENT\\AutoLISP\\placePresentations\\placePresentations.lsp")
       (load "c:\\data\\20-DEVELOPPEMENT\\AutoLISP\\placePresentations\\placePresentations.lsp"))
      ; Si non trouvé
      (T 
       (princ "\n⚠ ATTENTION: Le fichier placePresentations.lsp n'a pas été trouvé.")
       (princ "\nVeuillez le charger manuellement avec APPLOAD avant d'utiliser ces commandes.")
       (princ "\nOu placez les deux fichiers dans le même dossier.")
      )
    )
  )
  (princ "\nFichier principal déjà chargé.")
)

;; Fonction batch MODIFIÉE avec décalage du centre
(defun setup-viewport-with-offset (layout-name center scale offset-x offset-y / oldcmdecho xp-factor offset-center)
  ; Vérifier que les fonctions nécessaires existent
  (if (not (boundp 'unlock-all-viewports))
    (progn
      (princ "\n✗ ERREUR: Les fonctions du fichier principal ne sont pas disponibles.")
      (princ "\nChargez d'abord placePresentations.lsp")
      (exit)
    )
  )
  
  (setq oldcmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  ; Calcul du facteur XP basé sur l'échelle papier 1/1000
  (setq xp-factor (/ 1000.0 scale))
  
  ; Appliquer le décalage au centre
  (setq offset-center (list (+ (car center) offset-x)     ; X + décalage
                           (+ (cadr center) offset-y)      ; Y + décalage
                           (if (caddr center) (caddr center) 0.0))) ; Z inchangé
  
  ; Activer la présentation
  (setvar "CTAB" layout-name)
  (command "_.REGEN")
  
  ; DÉVERROUILLER les fenêtres
  (unlock-all-viewports layout-name)
  
  ; Passer en espace objet
  (command "_.MSPACE")
  
  ; Centrer avec le point décalé
  (command "_.ZOOM" "_C" offset-center (rtos xp-factor 2 8))
  
  ; Appliquer l'échelle XP finale
  (command "_.ZOOM" (strcat (rtos xp-factor 2 8) "xp"))
  
  ; Retour espace papier
  (command "_.PSPACE")
  
  ; Reverrouiller la fenêtre
  (command "_.MVIEW" "_L" "_ON" "_L" "")
  
  ; Restaurer
  (setvar "CMDECHO" oldcmdecho)
  T
)

;; COMMANDE: Test avec décalage sur une présentation
(defun c:TEST-OFFSET (/ layout-name center scale xp-factor oldcmdecho offset-x offset-y offset-center)
  (princ "\n=== TEST AVEC DÉCALAGE ===")
  
  ; Obtenir les paramètres
  (setq layout-name (getstring "\nNom de la présentation: "))
  
  ; Obtenir le centre
  (setq center (getpoint "\nCentre de vue (cliquez ou entrez X,Y): "))
  (if (not center)
    (progn
      (princ "\nAnnulé")
      (princ)
      (exit)
    )
  )
  
  ; Demander les décalages
  (setq offset-x (getreal "\nDécalage X en mètres (+ = droite) [1.0]: "))
  (if (not offset-x) (setq offset-x 1.0))
  
  (setq offset-y (getreal "\nDécalage Y en mètres (+ = haut) [0.0]: "))
  (if (not offset-y) (setq offset-y 0.0))
  
  ; Obtenir l'échelle
  (setq scale (getreal "\nÉchelle (ex: 70) [70]: "))
  (if (not scale) (setq scale 70.0))
  
  ; Afficher les informations
  (princ (strcat "\n  Centre original: X=" (rtos (car center) 2 2) ", Y=" (rtos (cadr center) 2 2)))
  (princ (strcat "\n  Décalage: X=" (rtos offset-x 2 2) "m, Y=" (rtos offset-y 2 2) "m"))
  (princ (strcat "\n  Centre final: X=" (rtos (+ (car center) offset-x) 2 2) 
                ", Y=" (rtos (+ (cadr center) offset-y) 2 2)))
  (princ (strcat "\n  Échelle: 1/" (rtos scale 2 0) " = " (rtos (/ 1000.0 scale) 2 2) "XP"))
  
  ; Appliquer avec le décalage
  (if (setup-viewport-with-offset layout-name center scale offset-x offset-y)
    (princ "\n✓ Terminé avec décalage")
    (princ "\n✗ Erreur")
  )
  
  (princ)
)

;; COMMANDE: Configuration automatique avec décalage de 1m à droite
(defun c:AUTO-VP-1M (/ intersections layouts scale old-ctab success-count i layout-name center)
  ; Vérifier que les fonctions du fichier principal sont disponibles
  (if (not (boundp 'get-intersections-on-layer))
    (progn
      (princ "\n✗ ERREUR: Le fichier placePresentations.lsp doit être chargé d'abord.")
      (princ "\nUtilisez APPLOAD pour charger placePresentations.lsp")
      (princ)
      (exit)
    )
  )
  
  (princ "\n=== CONFIGURATION AUTO AVEC DÉCALAGE 1M ===\n")
  (princ "\nParamètres:")
  (princ "\n  - Calque: INS_GC_GAL_Galeries_Axes")
  (princ "\n  - Échelle: 1/70 (14.29 XP)")
  (princ "\n  - Décalage: 1m vers la GAUCHE (espace modèle)")  ; CORRECTION: C'était l'inverse
  (princ "\n  - Exclusion: Model et cartouche")
  
  ; Échelle par défaut 1/70
  (setq scale 70.0)
  
  ; Récupérer les intersections
  (setq intersections (get-intersections-on-layer "INS_GC_GAL_Galeries_Axes"))
  
  (if intersections
    (progn
      (princ (strcat "\n\n" (itoa (length intersections)) " coupe(s) trouvée(s)"))
      
      ; Trier les intersections
      (setq intersections (sort-points-left-right-top-bottom intersections))
      
      ; Récupérer les présentations
      (setq layouts (get-all-layouts))
      (princ (strcat "\n" (itoa (length layouts)) " présentation(s) trouvée(s)"))
      
      ; Traiter automatiquement
      (princ "\n\nTraitement avec décalage de 1m...")
      
      ; Sauvegarder la présentation courante
      (setq old-ctab (getvar "CTAB"))
      (setq success-count 0)
      
      ; Traiter chaque présentation
      (setq i 0)
      (while (and (< i (length intersections)) 
                  (< i (length layouts)))
        (setq layout-name (nth i layouts))
        (setq center (nth i intersections))
        
        (princ (strcat "\n  " (itoa (1+ i)) ". " layout-name))
        
        ; CORRECTION: Utiliser -1.0 pour aller vers la droite (décaler la vue vers la gauche)
        (if (setup-viewport-with-offset layout-name center scale -1.0 0.0)
          (progn
            (princ " ✓")
            (setq success-count (1+ success-count))
          )
          (princ " ✗")
        )
        
        (setq i (1+ i))
      )
      
      ; Restaurer la présentation originale
      (setvar "CTAB" old-ctab)
      
      ; Résumé
      (princ "\n\n=== TERMINÉ ===")
      (princ (strcat "\n✓ " (itoa success-count) "/" (itoa i) " présentations configurées"))
      (princ "\n✓ Échelle: 1/70 (14.29 XP)")
      (princ "\n✓ Décalage: 1m vers la droite (espace modèle)")
      (princ "\n✓ Fenêtres reverrouillées")
    )
    (princ "\n✗ Aucune intersection trouvée")
  )
  
  (princ "\n")
  (princ)
)

;; COMMANDE: Configuration automatique avec décalage personnalisé
(defun c:AUTO-VP-OFFSET (/ offset-x offset-y scale intersections layouts old-ctab success-count i layout-name center)
  ; Vérifier que les fonctions du fichier principal sont disponibles
  (if (not (boundp 'get-intersections-on-layer))
    (progn
      (princ "\n✗ ERREUR: Le fichier placePresentations.lsp doit être chargé d'abord.")
      (princ)
      (exit)
    )
  )
  
  (princ "\n=== CONFIGURATION AUTO AVEC DÉCALAGE PERSONNALISÉ ===\n")
  
  ; CORRECTION: Inverser la logique des signes dans les messages
  (setq offset-x (getreal "\nDécalage X en mètres espace modèle (- = voir plus à droite) [-1.0]: "))
  (if (not offset-x) (setq offset-x -1.0))  ; Par défaut -1 pour voir plus à droite
  
  (setq offset-y (getreal "\nDécalage Y en mètres espace modèle (- = voir plus en bas) [0.0]: "))
  (if (not offset-y) (setq offset-y 0.0))
  
  ; Demander l'échelle
  (setq scale (getreal "\nÉchelle (ex: 70) [70]: "))
  (if (not scale) (setq scale 70.0))
  
  (princ (strcat "\nParamètres choisis:"))
  (princ (strcat "\n  - Échelle: 1/" (rtos scale 2 0) " (" (rtos (/ 1000.0 scale) 2 2) " XP)"))
  (princ (strcat "\n  - Décalage centre vue: X=" (rtos offset-x 2 2) "m, Y=" (rtos offset-y 2 2) "m"))
  
  ; Récupérer les intersections
  (setq intersections (get-intersections-on-layer "INS_GC_GAL_Galeries_Axes"))
  
  (if intersections
    (progn
      (princ (strcat "\n\n" (itoa (length intersections)) " coupe(s) trouvée(s)"))
      
      ; Trier les intersections
      (setq intersections (sort-points-left-right-top-bottom intersections))
      
      ; Récupérer les présentations
      (setq layouts (get-all-layouts))
      (princ (strcat "\n" (itoa (length layouts)) " présentation(s) trouvée(s)"))
      
      ; Traiter automatiquement
      (princ "\n\nTraitement...")
      
      ; Sauvegarder la présentation courante
      (setq old-ctab (getvar "CTAB"))
      (setq success-count 0)
      
      ; Traiter chaque présentation
      (setq i 0)
      (while (and (< i (length intersections)) 
                  (< i (length layouts)))
        (setq layout-name (nth i layouts))
        (setq center (nth i intersections))
        
        (princ (strcat "\n  " layout-name))
        
        ; Configurer la fenêtre avec décalage personnalisé
        (if (setup-viewport-with-offset layout-name center scale offset-x offset-y)
          (progn
            (princ " ✓")
            (setq success-count (1+ success-count))
          )
          (princ " ✗")
        )
        
        (setq i (1+ i))
      )
      
      ; Restaurer la présentation originale
      (setvar "CTAB" old-ctab)
      
      ; Résumé
      (princ "\n\n✓ Terminé: ")
      (princ (strcat (itoa success-count) "/" (itoa i) " présentations"))
      (princ (strcat "\n✓ Décalage appliqué: X=" (rtos offset-x 2 2) "m, Y=" (rtos offset-y 2 2) "m"))
    )
    (princ "\n✗ Aucune intersection trouvée")
  )
  (princ)
)

;; COMMANDE: Comparaison avant/après décalage
(defun c:COMPARE-OFFSET (/ layout-name center scale offset-x)
  (princ "\n=== COMPARAISON AVEC/SANS DÉCALAGE ===")
  
  ; Obtenir les paramètres
  (setq layout-name (getstring "\nNom de la présentation: "))
  (setq center (getpoint "\nCentre de vue: "))
  
  (if center
    (progn
      (setq scale 70.0)
      (setq offset-x 1.0)
      
      ; Demander de basculer entre les vues
      (princ "\n\nAppuyez sur ENTRÉE pour basculer entre:")
      (princ "\n  1. Vue centrée normale")
      (princ "\n  2. Vue décalée de 1m à droite")
      (princ "\nAppuyez sur ESC pour terminer")
      
      ; Vue 1: Sans décalage
      (princ "\n\n[Vue 1: Sans décalage]")
      (setup-viewport-with-offset layout-name center scale 0.0 0.0)
      (getstring "\nENTRÉE pour voir avec décalage...")
      
      ; Vue 2: Avec décalage
      (princ "\n[Vue 2: Avec décalage 1m]")
      (setup-viewport-with-offset layout-name center scale offset-x 0.0)
      (getstring "\nENTRÉE pour revoir sans décalage...")
      
      ; Retour à la vue sans décalage
      (princ "\n[Vue 1: Sans décalage]")
      (setup-viewport-with-offset layout-name center scale 0.0 0.0)
      
      (princ "\n\nComparaison terminée.")
    )
    (princ "\nAnnulé")
  )
  (princ)
)

;; Message de chargement
(princ "\n")
(princ "\n=== COMMANDES AVEC DÉCALAGE (ESPACE MODÈLE) ===")
(princ "\n")
(princ "\n  CONFIGURATION AUTOMATIQUE:")
(princ "\n  AUTO-VP-1M         : Config auto avec décalage 1m à droite (1/70)")
(princ "\n  AUTO-VP-OFFSET     : Config auto avec décalage personnalisé")
(princ "\n")
(princ "\n  TESTS:")
(princ "\n  TEST-OFFSET        : Test sur une présentation avec décalage")
(princ "\n  COMPARE-OFFSET     : Compare avec/sans décalage")
(princ "\n")
(princ "\n⚠ Note: Chargez d'abord placePresentations.lsp si ce n'est pas fait.")
(princ "\nLes décalages sont en mètres dans l'espace modèle.")
(princ "\n")