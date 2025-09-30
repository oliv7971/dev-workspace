;; TEST-ANGLE.LSP - Test simple de la fonction angle

(defun c:test-angle ()
  (princ "\n=== TEST FONCTION ANGLE ===")
  
  ;; Test avec des coordonnées problématiques
  (setq centre-orig (list 100.0 -1.05315e-06))
  (setq pos-orig (list 102.278 -2.178))
  
  (princ (strcat "\nCentre original : (" (vl-princ-to-string (car centre-orig)) "," (vl-princ-to-string (cadr centre-orig)) ")"))
  (princ (strcat "\nPos original : (" (vl-princ-to-string (car pos-orig)) "," (vl-princ-to-string (cadr pos-orig)) ")"))
  
  ;; Nettoyage
  (setq centre-clean (list (if (< (abs (car centre-orig)) 1e-6) 0.0 (car centre-orig))
                          (if (< (abs (cadr centre-orig)) 1e-6) 0.0 (cadr centre-orig))))
  (setq pos-clean (list (if (< (abs (car pos-orig)) 1e-6) 0.0 (car pos-orig))
                       (if (< (abs (cadr pos-orig)) 1e-6) 0.0 (cadr pos-orig))))
                       
  (princ (strcat "\nCentre nettoyé : (" (vl-princ-to-string (car centre-clean)) "," (vl-princ-to-string (cadr centre-clean)) ")"))
  (princ (strcat "\nPos nettoyé : (" (vl-princ-to-string (car pos-clean)) "," (vl-princ-to-string (cadr pos-clean)) ")"))
  
  ;; Test fonction angle directe
  (princ "\n\nTest 1 - Angle direct avec coordonnées originales :")
  (setq angle1 (vl-catch-all-apply 'angle (list centre-orig pos-orig)))
  (if (vl-catch-all-error-p angle1)
    (princ (strcat "\n  ERREUR : " (vl-princ-to-string angle1)))
    (princ (strcat "\n  SUCCÈS : " (vl-princ-to-string angle1) " rad = " (vl-princ-to-string (* angle1 (/ 180.0 pi))) " deg"))
  )
  
  ;; Test avec coordonnées nettoyées
  (princ "\n\nTest 2 - Angle avec coordonnées nettoyées :")
  (setq angle2 (vl-catch-all-apply 'angle (list centre-clean pos-clean)))
  (if (vl-catch-all-error-p angle2)
    (princ (strcat "\n  ERREUR : " (vl-princ-to-string angle2)))
    (princ (strcat "\n  SUCCÈS : " (vl-princ-to-string angle2) " rad = " (vl-princ-to-string (* angle2 (/ 180.0 pi))) " deg"))
  )
  
  ;; Test avec coordonnées entièrement arrondies
  (setq centre-round (list 100.0 0.0))
  (setq pos-round (list 102.278 -2.178))
  
  (princ "\n\nTest 3 - Angle avec centre totalement arrondi (100.0, 0.0) :")
  (setq angle3 (vl-catch-all-apply 'angle (list centre-round pos-round)))
  (if (vl-catch-all-error-p angle3)
    (princ (strcat "\n  ERREUR : " (vl-princ-to-string angle3)))
    (princ (strcat "\n  SUCCÈS : " (vl-princ-to-string angle3) " rad = " (vl-princ-to-string (* angle3 (/ 180.0 pi))) " deg"))
  )
  
  (princ "\n\n=== FIN TEST ===")
  (princ)
)

(princ "\n=== TEST-ANGLE.LSP chargé ===")
(princ "\nTapez TEST-ANGLE pour diagnostiquer le problème")
(princ)
