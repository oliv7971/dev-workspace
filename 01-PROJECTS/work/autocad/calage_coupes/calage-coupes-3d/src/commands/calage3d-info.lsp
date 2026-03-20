;;; CALAGE3D-INFO.LSP
;;; Commande pour visualiser les correspondances trouvées

;; Fonction pour collecter les blocs d'un calque avec leurs matricules
(defun collect-blocks (calque / ss i bloc mat pt liste)
  (setq liste '())
  (if (setq ss (ssget "X" (list (cons 0 "INSERT") (cons 8 calque))))
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq bloc (vlax-ename->vla-object (ssname ss i)))
        (setq mat (get-matricule bloc))
        (setq pt (get-point bloc))
        (if mat
          (setq liste (cons (list mat pt bloc) liste))
        )
        (setq i (1+ i))
      )
    )
  )
  liste
)

;; Fonction pour trouver les correspondances entre les listes
(defun find-pairs (liste-calage liste-3d / paires mat1 item2)
  (setq paires '())
  (foreach item1 liste-calage
    (setq mat1 (car item1))
    (setq item2 (assoc mat1 liste-3d))
    (if item2
      (setq paires (cons (list item1 item2) paires))
    )
  )
  paires
)

(defun c:CALAGE3D-INFO ( / liste-calage liste-3d paires tous-pm mat pm item)
  (vl-load-com)
  
  (setq liste-calage (collect-blocks "_CALAGE_PT"))
  (setq liste-3d (collect-blocks "_CALAGE_3D_CI"))
  (setq paires (find-pairs liste-calage liste-3d))
  
  (princ "\n\n=== POINTS DE CALAGE ===")
  (princ (strcat "\nPoints dans _CALAGE_PT : " (itoa (length liste-calage))))
  (princ (strcat "\nPoints dans _CALAGE_3D_CI : " (itoa (length liste-3d))))
  (princ (strcat "\nCorrespondances trouvées : " (itoa (length paires))))
  
  (princ "\n\nListe des correspondances :")
  (foreach paire paires
    (princ (strcat "\n  " (caar paire) " -> " (caadr paire)))
  )
  
  ;; Afficher les PM détectés
  (setq tous-pm '())
  (foreach item liste-calage
    (setq mat (car item))
    (if (vl-string-search "_" mat)
      (progn
        (setq pm (substr mat (+ 2 (vl-string-search "_" mat))))
        (if (not (member pm tous-pm))
          (setq tous-pm (cons pm tous-pm))
        )
      )
    )
  )
  
  (if tous-pm
    (progn
      (setq tous-pm (vl-sort tous-pm '<))
      (princ "\n\nPM détectés : ")
      (foreach pm tous-pm
        (princ (strcat pm " "))
      )
    )
  )
  
  (princ)
)

(princ "\nCALAGE3D-INFO.LSP loaded")
