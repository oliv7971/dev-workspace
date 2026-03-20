;;; CALAGE3D.LSP
;;; Commande pour effectuer le calage 3D des objets basés sur des points de référence

;; ============================================
;; COMMANDES PRINCIPALES
;; ============================================

(defun c:CALAGE3D ( / ss-calage ss-3d pt-calage pt-3d mat-calage mat-3d
                      liste-calage liste-3d paires objets-coupe
                      pt1 pt2 pt3 pt1-3d pt2-3d pt3-3d
                      xmin xmax ymin ymax matrice-trans)
  
  ;; Programme principal
  (vl-load-com)
  
  (princ "\nCollecte des points de calage...")
  
  ;; Collecter les blocs des deux calques
  (setq liste-calage (collect-blocks "_CALAGE_PT"))
  (setq liste-3d (collect-blocks "_CALAGE_3D_CI"))
  
  (if (< (length liste-calage) 3)
    (progn
      (alert "Il faut au moins 3 points de calage dans le calque _CALAGE_PT !")
      (exit)
    )
  )
  
  (if (< (length liste-3d) 3)
    (progn
      (alert "Il faut au moins 3 points de calage dans le calque _CALAGE_3D_CI !")
      (exit)
    )
  )
  
  ;; Trouver les correspondances
  (setq paires (find-pairs liste-calage liste-3d))
  
  (if (< (length paires) 3)
    (progn
      (alert (strcat "Seulement " (itoa (length paires)) " correspondances trouvées. Il en faut au moins 3 !"))
      (exit)
    )
  )
  
  (princ (strcat "\n" (itoa (length paires)) " correspondances trouvées."))
  
  ;; Prendre les 3 premières paires pour le calage
  ;; Idéalement, prendre A_, B_ et C_ si disponibles
  (setq pt1 nil pt2 nil pt3 nil)
  (setq pt1-3d nil pt2-3d nil pt3-3d nil)
  
  ;; Chercher un point A_, B_ et C_
  (foreach paire paires
    (setq mat-calage (caar paire))
    (cond
      ((and (not pt1) (wcmatch mat-calage "A_*"))
       (setq pt1 (cadar paire))
       (setq pt1-3d (cadadr paire)))
      ((and (not pt2) (wcmatch mat-calage "B_*"))
       (setq pt2 (cadar paire))
       (setq pt2-3d (cadadr paire)))
      ((and (not pt3) (wcmatch mat-calage "C_*"))
       (setq pt3 (cadar paire))
       (setq pt3-3d (cadadr paire)))
    )
  )
  
  ;; Si on n'a pas trouvé A, B et C, prendre les 3 premiers
  (if (not (and pt1 pt2 pt3))
    (progn
      (setq pt1 (cadar (nth 0 paires)))
      (setq pt1-3d (cadadr (nth 0 paires)))
      (setq pt2 (cadar (nth 1 paires)))
      (setq pt2-3d (cadadr (nth 1 paires)))
      (setq pt3 (cadar (nth 2 paires)))
      (setq pt3-3d (cadadr (nth 2 paires)))
    )
  )
  
  ;; Sélectionner les objets de la coupe dans l'emprise (SANS les points _CALAGE_PT)
  (princ "\nSélection des objets de la coupe (hors points de calage)...")
  (setq objets-coupe (select-objects-for-coupe liste-calage nil))
  
  ;; Debug : afficher les détails de sélection
  (princ "\nDétails de la sélection :")
  (princ (strcat "\n  Zone d'emprise calculée sur " (itoa (length liste-calage)) " points de calage"))
  
  (if objets-coupe
    (princ (strcat "\n  " (itoa (sslength objets-coupe)) " objets sélectionnés pour le calage"))
    (princ "\n  AUCUN objet sélectionné !")
  )
  
  (if objets-coupe
    (progn
      (princ (strcat "\n" (itoa (sslength objets-coupe)) " objets sélectionnés (hors calage)."))
      
      ;; Afficher les points utilisés pour le calage
      (princ "\n\nPoints de calage utilisés :")
      (princ (strcat "\n  Point 1 : " (caar (assoc pt1 liste-calage))))
      (princ (strcat "\n  Point 2 : " (caar (assoc pt2 liste-calage))))
      (princ (strcat "\n  Point 3 : " (caar (assoc pt3 liste-calage))))
      
      ;; Effectuer l'alignement 3D avec syntaxe corrigée
      (princ "\n\nCalage en cours...")
      
      ;; Sauvegarder les paramètres système
      (setq old-osmode (getvar "OSMODE"))
      (setq old-cmdecho (getvar "CMDECHO"))
      (setvar "OSMODE" 0)     ; Désactiver l'accrochage
      (setvar "CMDECHO" 0)    ; Mode silencieux
      
      (command "_3DALIGN" 
         objets-coupe ""     ; Sélection des objets + fin de sélection
         "_none" pt1         ; Point source 1 (mode _none pour éviter l'accrochage)
         "_none" pt2         ; Point source 2  
         "_none" pt3         ; Point source 3
         "_none" pt1-3d      ; Point destination 1
         "_none" pt2-3d      ; Point destination 2
         "_none" pt3-3d      ; Point destination 3
      )
      
      ;; Restaurer les paramètres système
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      
      ;; Vérification post-calage
      (princ "\n\nVÉRIFICATION POST-CALAGE:")
      (verify-transformation pt1 pt1-3d pt2 pt2-3d pt3 pt3-3d)
      
      (princ "\nCalage terminé !")
    )
    (alert "Aucun objet trouvé dans l'emprise de la coupe !")
  )
  
  (princ)
)

(princ "\nCommande CALAGE3D chargée.")
(princ)