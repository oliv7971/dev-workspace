;; TEST-DEBUG.LSP - Version simplifiée pour diagnostiquer le problème

(setq *CALQUE-COTES* "REC_INS_GC_GAL_Beton soutenement_texte")
(setq *AFFICHAGE-DEBUG* T)

(defun c:test-debug ()
  (princ "\n=== TEST DEBUG SIMPLIFIE ===")
  
  ;; Sélection rapide
  (setq ss-zone (ssget))
  
  (if ss-zone
    (progn
      (princ (strcat "\nEntités sélectionnées : " (itoa (sslength ss-zone))))
      
      ;; Test simple : lister tous les textes sans filtrage par calque
      (setq i 0)
      (setq nb-text 0)
      (setq nb-mtext 0)
      (setq nb-autres 0)
      
      (repeat (sslength ss-zone)
        (setq ent (ssname ss-zone i))
        (setq data (entget ent))
        (setq type-obj (cdr (assoc 0 data)))
        (setq calque-obj (cdr (assoc 8 data)))
        
        (cond
          ((= type-obj "TEXT") 
           (setq nb-text (1+ nb-text))
           (princ (strcat "\n  TEXT trouvé sur calque : " calque-obj)))
          ((= type-obj "MTEXT") 
           (setq nb-mtext (1+ nb-mtext))
           (princ (strcat "\n  MTEXT trouvé sur calque : " calque-obj)))
          (T 
           (setq nb-autres (1+ nb-autres))
           (if *AFFICHAGE-DEBUG*
             (princ (strcat "\n  " type-obj " sur calque : " calque-obj))))
        )
        
        (setq i (1+ i))
      )
      
      (princ "\n")
      (princ "\n=== RÉSUMÉ ===")
      (princ (strcat "\n- TEXT : " (itoa nb-text)))
      (princ (strcat "\n- MTEXT : " (itoa nb-mtext)))
      (princ (strcat "\n- Autres : " (itoa nb-autres)))
      (princ (strcat "\n- Total : " (itoa (sslength ss-zone))))
      
      ;; Test du centre
      (princ "\n\nCliquez pour définir un centre de test...")
      (setq centre (getpoint))
      
      (if centre
        (progn
          (princ (strcat "\nCentre défini : X=" (vl-princ-to-string (car centre))))
          (princ (strcat " Y=" (vl-princ-to-string (cadr centre))))
          (princ (strcat " Type=" (vl-princ-to-string (type centre))))
          
          ;; Test de calcul d'angle avec le premier texte trouvé
          (setq i 0)
          (setq ent-test nil)
          
          (repeat (sslength ss-zone)
            (setq ent (ssname ss-zone i))
            (setq data (entget ent))
            (setq type-obj (cdr (assoc 0 data)))
            
            (if (and (not ent-test) (or (= type-obj "TEXT") (= type-obj "MTEXT")))
              (progn
                (setq ent-test ent)
                (setq pos (cdr (assoc 10 data)))
                (princ (strcat "\nTest angle avec premier texte trouvé (" type-obj ")"))
                (princ (strcat "\n  Position : X=" (vl-princ-to-string (car pos))))
                (princ (strcat " Y=" (vl-princ-to-string (cadr pos))))
                
                ;; Test direct de la fonction angle
                (setq angle-test (angle centre pos))
                (princ (strcat "\n  Angle calculé : " (vl-princ-to-string angle-test)))
                (princ (strcat "\n  Angle en degrés : " (vl-princ-to-string (* angle-test (/ 180.0 pi)))))
              )
            )
            (setq i (1+ i))
          )
        )
        (princ "\nAnnulé.")
      )
    )
    (princ "\nAucune sélection.")
  )
  (princ)
)

(princ "\n=== TEST-DEBUG.LSP chargé ===")
(princ "\nTapez TEST-DEBUG pour lancer le diagnostic")
(princ)
