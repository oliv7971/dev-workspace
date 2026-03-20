;;; ALIGNMENT.LSP
;;; Functions for 3D alignment operations

;; Fonction pour caler une seule coupe
(defun calage-une-coupe (liste-calage-pm liste-3d pm-nom / paires pt1 pt2 pt3 pt1-3d pt2-3d pt3-3d objets-coupe mat-a mat-b mat-c mat-calage)
  
  ;; Trouver les correspondances pour cette coupe
  (setq paires (find-pairs liste-calage-pm liste-3d))
  
  (princ (strcat "\n\n--- Traitement coupe PM " pm-nom " ---"))
  (princ (strcat "\n  " (itoa (length liste-calage-pm)) " points sources (_CALAGE_PT)"))
  (princ (strcat "\n  " (itoa (length paires)) " correspondances trouvées"))
  
  (if (>= (length paires) 3)
    (progn
      ;; Sélectionner les points A, B, C SPECIFIQUES A CE PM
      (setq pt1 nil pt2 nil pt3 nil)
      (setq pt1-3d nil pt2-3d nil pt3-3d nil)
      
      ;; Construire les matricules exacts pour ce PM
      (setq mat-a (strcat "A_" pm-nom))
      (setq mat-b (strcat "B_" pm-nom))
      (setq mat-c (strcat "C_" pm-nom))
      
      ;; Chercher les correspondances exactes
      (foreach paire paires
        (setq mat-calage (caar paire))
        (cond
          ((equal mat-calage mat-a)
           (setq pt1 (cadar paire))      ; Point source A
           (setq pt1-3d (cadadr paire))  ; Point destination A
           (princ (strcat "\n  ✓ Trouvé A : " mat-a)))
          ((equal mat-calage mat-b)
           (setq pt2 (cadar paire))      ; Point source B
           (setq pt2-3d (cadadr paire))  ; Point destination B
           (princ (strcat "\n  ✓ Trouvé B : " mat-b)))
          ((equal mat-calage mat-c)
           (setq pt3 (cadar paire))      ; Point source C
           (setq pt3-3d (cadadr paire))  ; Point destination C
           (princ (strcat "\n  ✓ Trouvé C : " mat-c)))
        )
      )
      
      ;; Vérifier qu'on a bien trouvé les 3 points
      (if (and pt1 pt2 pt3 pt1-3d pt2-3d pt3-3d)
        (progn
          ;; Debug - afficher les coordonnées
          (princ "\n\n  VERIFICATION DES POINTS:")
          (princ "\n  Points SOURCE (sur la coupe):")
          (princ (strcat "\n    A: " (rtos (car pt1) 2 3) ", " (rtos (cadr pt1) 2 3) ", " (rtos (caddr pt1) 2 3)))
          (princ (strcat "\n    B: " (rtos (car pt2) 2 3) ", " (rtos (cadr pt2) 2 3) ", " (rtos (caddr pt2) 2 3)))
          (princ (strcat "\n    C: " (rtos (car pt3) 2 3) ", " (rtos (cadr pt3) 2 3) ", " (rtos (caddr pt3) 2 3)))
          
          (princ "\n  Points DESTINATION (cibles 3D):")
          (princ (strcat "\n    A: " (rtos (car pt1-3d) 2 3) ", " (rtos (cadr pt1-3d) 2 3) ", " (rtos (caddr pt1-3d) 2 3)))
          (princ (strcat "\n    B: " (rtos (car pt2-3d) 2 3) ", " (rtos (cadr pt2-3d) 2 3) ", " (rtos (caddr pt2-3d) 2 3)))
          (princ (strcat "\n    C: " (rtos (car pt3-3d) 2 3) ", " (rtos (cadr pt3-3d) 2 3) ", " (rtos (caddr pt3-3d) 2 3)))
          
          ;; Sélectionner les objets de la coupe (PAS les points de calage !)
          (princ "\n\n  Sélection des objets...")
          
          ;; Utiliser la sélection par zone autour des points de calage
          (setq objets-coupe (select-objects-for-coupe liste-calage-pm pm-nom))
          
          ;; DEBUG : Affichage détaillé de la sélection
          (princ (strcat "\n  DEBUG sélection pour PM " pm-nom ":"))
          (if objets-coupe
            (progn
              (princ (strcat "\n    " (itoa (sslength objets-coupe)) " objets trouvés"))
              ;; Afficher les premiers objets pour debug
              (setq i 0)
              (while (and (< i (min 5 (sslength objets-coupe))))
                (setq ent (ssname objets-coupe i))
                (setq entdata (entget ent))
                (princ (strcat "\n    Objet " (itoa i) ": " 
                              (cdr (assoc 0 entdata)) " sur calque " 
                              (cdr (assoc 8 entdata))))
                (setq i (1+ i))
              )
              (if (> (sslength objets-coupe) 5)
                (princ "\n    ...")
              )
            )
            (princ "\n    AUCUN objet sélectionné !")
          )
          
          (if (and objets-coupe (> (sslength objets-coupe) 0))
            (progn
              (princ (strcat "\n  " (itoa (sslength objets-coupe)) " objets sélectionnés"))
              
              ;; CALAGE 3D avec la syntaxe corrigée et sécurisée
              (princ "\n  Calage en cours...")
              
              ;; Sauvegarder et configurer les paramètres système
              (setq old-osmode (getvar "OSMODE"))
              (setq old-cmdecho (getvar "CMDECHO"))
              (setvar "OSMODE" 0)     ; Désactiver l'accrochage
              (setvar "CMDECHO" 0)    ; Mode silencieux
              
              (command "_3DALIGN" 
                objets-coupe ""      ; Sélection des objets + fin de sélection
                "_none" pt1          ; Point source A
                "_none" pt2          ; Point source B  
                "_none" pt3          ; Point source C
                "_none" pt1-3d       ; Point destination A
                "_none" pt2-3d       ; Point destination B
                "_none" pt3-3d       ; Point destination C
              )
              
              ;; Restaurer les paramètres système
              (setvar "OSMODE" old-osmode)
              (setvar "CMDECHO" old-cmdecho)
              
              ;; VERIFICATION POST-CALAGE
              (princ "\n\n  VERIFICATION POST-CALAGE:")
              (verify-transformation pt1 pt1-3d pt2 pt2-3d pt3 pt3-3d)
              
              (princ "\n  ✓ Calage effectué !")
            )
            (princ "\n  ⚠ Aucun objet trouvé pour cette coupe")
          )
        )
        (progn
          (princ (strcat "\n  ⚠ ERREUR: Points manquants pour PM " pm-nom))
          (if (not pt1) (princ (strcat "\n    ✗ Manque : " mat-a)))
          (if (not pt2) (princ (strcat "\n    ✗ Manque : " mat-b)))
          (if (not pt3) (princ (strcat "\n    ✗ Manque : " mat-c)))
        )
      )
    )
    (princ "\n  ⚠ Pas assez de correspondances")
  )
)

;; ============================================================================
;; Fonction de vérification post-calage
;; ============================================================================
(defun verify-transformation (pt1-src pt1-dst pt2-src pt2-dst pt3-src pt3-dst / 
                             dist1-src dist2-src dist3-src dist1-dst dist2-dst dist3-dst
                             tolerance)
  
  ;; Tolérance pour les vérifications (en unités de dessin)
  (setq tolerance 0.01)
  
  ;; Calcul des distances dans le système source
  (setq dist1-src (distance pt1-src pt2-src))
  (setq dist2-src (distance pt2-src pt3-src))
  (setq dist3-src (distance pt3-src pt1-src))
  
  ;; Calcul des distances dans le système destination
  (setq dist1-dst (distance pt1-dst pt2-dst))
  (setq dist2-dst (distance pt2-dst pt3-dst))
  (setq dist3-dst (distance pt3-dst pt1-dst))
  
  (princ "\n    Distances triangulaires:")
  (princ (strcat "\n      A-B: src=" (rtos dist1-src 2 3) " dst=" (rtos dist1-dst 2 3) 
                " diff=" (rtos (abs (- dist1-src dist1-dst)) 2 3)))
  (princ (strcat "\n      B-C: src=" (rtos dist2-src 2 3) " dst=" (rtos dist2-dst 2 3) 
                " diff=" (rtos (abs (- dist2-src dist2-dst)) 2 3)))
  (princ (strcat "\n      C-A: src=" (rtos dist3-src 2 3) " dst=" (rtos dist3-dst 2 3) 
                " diff=" (rtos (abs (- dist3-src dist3-dst)) 2 3)))
  
  ;; Vérification des écarts
  (if (and (< (abs (- dist1-src dist1-dst)) tolerance)
           (< (abs (- dist2-src dist2-dst)) tolerance)
           (< (abs (- dist3-src dist3-dst)) tolerance))
    (princ "\n    ✓ Transformation géométriquement cohérente")
    (princ "\n    ⚠ ATTENTION: Écarts géométriques détectés !")
  )
)

(princ "\nALIGNMENT.LSP loaded - Version corrigée avec debug")