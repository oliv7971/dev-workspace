;; SIMPLIF-COTES-SIMPLE.LSP
;; Version ultra-simplifiée pour éliminer les erreurs

(setq *CALQUE-COTES* "REC_INS_GC_GAL_Beton soutenement_texte")
(setq *AFFICHAGE-DEBUG* T)

(defun c:simplif-test ()
  (princ "\n=== TEST SIMPLIFIE ===")
  
  ;; Sélection
  (setq ss-zone (ssget))
  
  (if ss-zone
    (progn
      ;; Filtrage simple
      (setq liste-textes '())
      (setq i 0)
      
      (repeat (sslength ss-zone)
        (setq ent (ssname ss-zone i))
        (setq data (entget ent))
        (setq type-obj (cdr (assoc 0 data)))
        (setq calque-obj (cdr (assoc 8 data)))
        
        (if (and (or (= type-obj "TEXT") (= type-obj "MTEXT"))
                 (= (strcase calque-obj) (strcase *CALQUE-COTES*)))
          (progn
            (setq pos (cdr (assoc 10 data)))
            (setq liste-textes (cons (list ent pos) liste-textes))
            (princ (strcat "\n  Trouvé: " type-obj " sur " calque-obj))
          )
        )
        (setq i (1+ i))
      )
      
      (princ (strcat "\n" (itoa (length liste-textes)) " textes trouvés"))
      
      (if (> (length liste-textes) 0)
        (progn
          ;; Centre
          (setq centre (getpoint "\nCentre de la coupe : "))
          
          (if centre
            (progn
              (princ (strcat "\nCentre : (" (rtos (car centre) 2 3) "," (rtos (cadr centre) 2 3) ")"))
              
              ;; Calcul angles simple
              (setq liste-angles '())
              (setq nb-ok 0)
              (setq nb-erreur 0)
              
              (foreach item liste-textes
                (setq ent (car item))
                (setq pos (cadr item))
                
                ;; Nettoyage coordonnées
                (setq cx (car centre))
                (setq cy (cadr centre))
                (setq px (car pos))
                (setq py (cadr pos))
                
                (if (< (abs cy) 0.001) (setq cy 0.0))
                (if (< (abs py) 0.001) (setq py 0.0))
                (if (< (abs cx) 0.001) (setq cx 0.0))
                (if (< (abs px) 0.001) (setq px 0.0))
                
                (setq centre-clean (list cx cy))
                (setq pos-clean (list px py))
                
                (if (and (not (= cx px)) (not (= cy py)))
                  (progn
                    ;; Test calcul angle SANS vl-catch-all
                    (setq angle-rad (angle centre-clean pos-clean))
                    (setq angle-deg (* angle-rad 57.2958))  ;; Conversion directe
                    (if (< angle-deg 0) (setq angle-deg (+ angle-deg 360)))
                    
                    (setq liste-angles (cons (list ent angle-deg) liste-angles))
                    (setq nb-ok (1+ nb-ok))
                    (princ (strcat "\n  OK: angle = " (rtos angle-deg 2 1)))
                  )
                  (progn
                    (setq nb-erreur (1+ nb-erreur))
                    (princ "\n  ERREUR: points trop proches")
                  )
                )
              )
              
              (princ (strcat "\nRésultat: " (itoa nb-ok) " OK, " (itoa nb-erreur) " erreurs"))
              
              (if (> (length liste-angles) 1)
                (progn
                  ;; Tri simple
                  (setq liste-triee (vl-sort liste-angles '(lambda (a b) (< (cadr a) (cadr b)))))
                  
                  ;; Suppression alternée
                  (setq compteur 0)
                  (foreach item liste-triee
                    (setq compteur (1+ compteur))
                    (setq ent (car item))
                    (setq angle (cadr item))
                    
                    (if (= (rem compteur 2) 0)  ;; Supprimer les positions paires
                      (progn
                        (entdel ent)
                        (princ (strcat "\n  " (itoa compteur) ". SUPPRIME (angle " (rtos angle 2 1) ")"))
                      )
                      (princ (strcat "\n  " (itoa compteur) ". GARDE (angle " (rtos angle 2 1) ")"))
                    )
                  )
                  (princ "\nTerminé!")
                )
                (princ "\nPas assez de textes valides pour la suppression")
              )
            )
            (princ "\nAnnulé")
          )
        )
        (princ "\nAucun texte trouvé sur le calque")
      )
    )
    (princ "\nAucune sélection")
  )
  (princ)
)

(princ "\n=== SIMPLIF-COTES-SIMPLE.LSP chargé ===")
(princ "\nCommande: SIMPLIF-TEST")
(princ)
