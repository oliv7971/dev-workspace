;; ============================================================================
;; Programme AutoLISP pour placer des points aux sommets les plus bas
;; des polylignes 3D dans des calques spécifiques
;; ============================================================================

(defun c:POINTBAS ()
  (setvar "CMDECHO" 0)
  (setvar "OSMODE" 0)
  
  (princ "\nPlacement de points aux sommets les plus bas des polylignes 3D...")
  
  ;; Définition des calques à traiter
  (setq calques-cibles '("REC_INS_GC_GAL_Boulons_Epinglage_Cintres_mes"
                         "REC_INS_GC_GAL_Boulons_Epinglage_Cintres_theo"))
  
  (setq nb-points-places 0)
  
  ;; Traitement de chaque calque
  (foreach calque calques-cibles
    (princ (strcat "\nTraitement du calque : " calque))
    
    ;; Création du jeu de sélection pour les LWPOLYLINE du calque
    (setq ss (ssget "X" (list (cons 0 "LWPOLYLINE")
                             (cons 8 calque))))
    
    (if ss
      (progn
        (setq nb-polylignes (sslength ss))
        (princ (strcat "\n  Nombre de LWPOLYLINE trouvées : " (itoa nb-polylignes)))
        
        ;; Traitement de chaque polyligne
        (setq i 0)
        (while (< i nb-polylignes)
          (setq ent (ssname ss i))
          (setq entdata (entget ent))
          
          ;; Traitement de la polyligne avec le calque source
          (if (traiter-polyligne ent calque)
            (setq nb-points-places (1+ nb-points-places))
          )
          
          (setq i (1+ i))
        )
      )
      (princ (strcat "\n  Aucune LWPOLYLINE trouvée dans le calque " calque))
    )
  )
  
  (princ (strcat "\nTerminé ! " (itoa nb-points-places) " points placés."))
  (setvar "CMDECHO" 1)
  (princ)
)

;; ============================================================================
;; Fonction pour traiter une LWPOLYLINE et placer le point au sommet le plus bas
;; ============================================================================
(defun traiter-polyligne (ent calque-source / entdata sommets pt-debut pt-fin z-debut z-fin pt-bas)
  (setq entdata (entget ent))
  (setq sommets (extraire-sommets-lwpoly ent))
  
  (if (and sommets (>= (length sommets) 2))
    (progn
      ;; Récupération du premier et dernier sommet
      (setq pt-debut (car sommets))
      (setq pt-fin (last sommets))
      
      ;; Récupération des altitudes (coordonnée Z)
      (setq z-debut (caddr pt-debut))
      (setq z-fin (caddr pt-fin))
      
      ;; Détermination du point le plus bas
      (if (< z-debut z-fin)
        (setq pt-bas pt-debut)
        (setq pt-bas pt-fin)
      )
      
      ;; Placement du point dans le même calque que la polyligne
      (placer-point pt-bas calque-source)
      (princ (strcat "\n    Point placé à l'altitude : " (rtos (caddr pt-bas) 2 3)))
      T ; Retourne vrai si un point a été placé
    )
    (progn
      (princ "\n    Erreur : impossible d'extraire les sommets de la LWPOLYLINE")
      nil
    )
  )
)

;; ============================================================================
;; Fonction pour extraire les sommets d'une LWPOLYLINE - Version corrigée
;; ============================================================================
(defun extraire-sommets-lwpoly (ent / entdata sommets pt-2d elevation pt-3d ferme)
  (setq sommets '())
  (setq entdata (entget ent))
  
  ;; Récupération de l'élévation
  (setq elevation (cdr (assoc 38 entdata)))
  (if (not elevation) (setq elevation 0.0))
  
  ;; Vérification si la polyligne est fermée (bit 1 du code 70)
  (setq ferme (logand (cdr (assoc 70 entdata)) 1))
  
  ;; Extraction de tous les vertices (code 10)
  (foreach item entdata
    (if (= (car item) 10)
      (progn
        (setq pt-2d (cdr item))
        ;; Transformation des coordonnées OCS vers WCS
        (setq pt-3d (trans (list (car pt-2d) (cadr pt-2d) elevation) 
                          (cdr (assoc 210 entdata)) 
                          0))
        (setq sommets (append sommets (list pt-3d)))
      )
    )
  )
  
  ;; Debug : affichage du nombre de sommets trouvés
  (princ (strcat " [" (itoa (length sommets)) " sommets]"))
  
  ;; Retourne tous les sommets pour le moment (pour debug)
  sommets
)

;; ============================================================================
;; Méthode alternative d'extraction (sans VLAX)
;; ============================================================================
(defun extraire-sommets-lwpoly-alternatif (ent / entdata sommets pt-2d elevation pt-3d)
  (setq sommets '())
  (setq entdata (entget ent))
  
  ;; Récupération de l'élévation
  (setq elevation (cdr (assoc 38 entdata)))
  (if (not elevation) (setq elevation 0.0))
  
  ;; Extraction des vertices (code 10)
  (foreach item entdata
    (if (= (car item) 10)
      (progn
        (setq pt-2d (cdr item))
        (setq pt-3d (list (car pt-2d) (cadr pt-2d) elevation))
        (setq sommets (append sommets (list pt-3d)))
      )
    )
  )
  
  ;; Retourne seulement le premier et le dernier point
  (if (>= (length sommets) 2)
    (list (car sommets) (last sommets))
    sommets
  )
)

;; ============================================================================
;; Fonction pour placer un point à une coordonnée donnée dans un calque spécifié
;; ============================================================================
(defun placer-point (pt calque / point-ent)
  (setq point-ent (entmakex (list (cons 0 "POINT")
                                 (cons 10 pt)
                                 (cons 8 calque)))) ; Même calque que la polyligne
  point-ent
)

;; ============================================================================
;; Version alternative avec gestion d'erreurs améliorée
;; ============================================================================
(defun c:POINTBAS2 ()
  (setvar "CMDECHO" 0)
  (setvar "OSMODE" 0)
  
  (princ "\nPlacement de points aux sommets les plus bas des LWPOLYLINE...")
  (princ "\nVersion avec gestion d'erreurs améliorée")
  
  ;; Définition des calques à traiter
  (setq calques-cibles '("REC_INS_GC_GAL_Boulons_Epinglage_Cintres_mes"
                         "REC_INS_GC_GAL_Boulons_Epinglage_Cintres_theo"))
  
  (setq nb-points-places 0)
  (setq nb-erreurs 0)
  
  ;; Traitement de chaque calque
  (foreach calque calques-cibles
    (princ (strcat "\nTraitement du calque : " calque))
    
    ;; Vérification de l'existence du calque
    (if (tblsearch "LAYER" calque)
      (progn
        ;; Création du jeu de sélection pour toutes les LWPOLYLINE du calque
        (setq ss (ssget "X" (list (cons 0 "LWPOLYLINE")
                                 (cons 8 calque))))
        
        (if ss
          (progn
            (setq nb-polylignes (sslength ss))
            (princ (strcat "\n  Nombre de LWPOLYLINE trouvées : " (itoa nb-polylignes)))
            
            ;; Traitement de chaque polyligne
            (setq i 0)
            (while (< i nb-polylignes)
              (setq ent (ssname ss i))
              (setq entdata (entget ent))
              
              ;; Traitement de la LWPOLYLINE
              (if (traiter-polyligne-v2 ent i calque)
                (setq nb-points-places (1+ nb-points-places))
                (setq nb-erreurs (1+ nb-erreurs))
              )
              
              (setq i (1+ i))
            )
          )
          (princ (strcat "\n  Aucune LWPOLYLINE trouvée dans le calque " calque))
        )
      )
      (princ (strcat "\n  Attention : Le calque " calque " n'existe pas dans le dessin"))
    )
  )
  
  (princ (strcat "\nTerminé ! " (itoa nb-points-places) " points placés"))
  (if (> nb-erreurs 0)
    (princ (strcat " (" (itoa nb-erreurs) " erreurs)"))
  )
  (princ ".")
  (setvar "CMDECHO" 1)
  (princ)
)

;; ============================================================================
;; Version améliorée de traitement d'une LWPOLYLINE avec debug
;; ============================================================================
(defun traiter-polyligne-v2 (ent index calque-source / entdata sommets pt-debut pt-fin z-debut z-fin pt-bas)
  (princ (strcat "\n    Traitement LWPOLYLINE " (itoa (1+ index)) " : "))
  
  (setq sommets (extraire-sommets-lwpoly ent))
  
  (if (and sommets (>= (length sommets) 2))
    (progn
      ;; Récupération du premier et dernier sommet
      (setq pt-debut (car sommets))
      (setq pt-fin (last sommets))
      
      ;; Debug : affichage des coordonnées complètes
      (princ (strcat "\n      Début: X=" (rtos (car pt-debut) 2 3) 
                    " Y=" (rtos (cadr pt-debut) 2 3) 
                    " Z=" (rtos (caddr pt-debut) 2 3)))
      (princ (strcat "\n      Fin:   X=" (rtos (car pt-fin) 2 3) 
                    " Y=" (rtos (cadr pt-fin) 2 3) 
                    " Z=" (rtos (caddr pt-fin) 2 3)))
      
      ;; Récupération des altitudes (coordonnée Z)
      (setq z-debut (caddr pt-debut))
      (setq z-fin (caddr pt-fin))
      
      ;; Détermination du point le plus bas
      (if (< z-debut z-fin)
        (progn
          (setq pt-bas pt-debut)
          (princ "\n      -> Point placé au début (altitude plus basse)")
        )
        (progn
          (setq pt-bas pt-fin)
          (princ "\n      -> Point placé à la fin (altitude plus basse)")
        )
      )
      
      ;; Placement du point dans le même calque
      (placer-point pt-bas calque-source)
      T ; Retourne vrai si un point a été placé
    )
    (progn
      (princ "ERREUR - Impossible d'extraire les sommets")
      nil
    )
  )
)



(princ "\nCommandes disponibles :")
(princ "\n  POINTBAS  - Version simple")
(princ "\n  POINTBAS2 - Version avec gestion d'erreurs détaillée")
(princ "\nTapez une de ces commandes pour placer les points aux sommets les plus bas.")
(princ)