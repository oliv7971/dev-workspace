;;; CALAGE3D-AUTO.LSP
;;; Commande pour traiter toutes les coupes automatiquement, une par une

(defun c:CALAGE3D-AUTO ( / liste-calage liste-3d tous-pm pm-liste pm courant)
  (vl-load-com)
  
  (princ "\n\n=== CALAGE AUTOMATIQUE DE TOUTES LES COUPES ===")
  
  ;; Collecter tous les points
  (setq liste-calage (collect-blocks "_CALAGE_PT"))
  (setq liste-3d (collect-blocks "_CALAGE_3D_CI"))
  
  ;; Extraire tous les PM uniques
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
  
  ;; Trier les PM
  (setq tous-pm (vl-sort tous-pm '<))
  
  (princ (strcat "\n\nNombre de coupes à traiter : " (itoa (length tous-pm))))
  (princ "\nPM détectés : ")
  (foreach pm tous-pm
    (princ (strcat pm " "))
  )
  
  ;; Traiter chaque coupe
  (foreach pm-courant tous-pm
    (princ (strcat "\n\n--- Traitement de la coupe PM " pm-courant " ---"))
    
    ;; Filtrer les points pour cette coupe - FILTRAGE STRICT
    (setq liste-calage-pm '())
    (foreach item liste-calage
      (setq matricule (car item))
      ;; Vérifier que le matricule se termine EXACTEMENT par "_" + pm-courant
      (if (and (vl-string-search "_" matricule)
               (equal (substr matricule (+ 2 (vl-string-search "_" matricule))) pm-courant))
        (setq liste-calage-pm (cons item liste-calage-pm))
      )
    )
    
    (if (>= (length liste-calage-pm) 3)
      (progn
        ;; Lancer le calage pour cette coupe
        (calage-une-coupe liste-calage-pm liste-3d pm-courant)
      )
      (princ (strcat "\nPas assez de points pour la coupe PM " pm-courant))
    )
  )
  
  (princ "\n\n=== CALAGE AUTOMATIQUE TERMINÉ ===")
  (princ)
)