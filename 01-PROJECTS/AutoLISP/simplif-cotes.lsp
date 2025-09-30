;; SIMPLIF-COTES.LSP
;; Script AutoLISP pour simplifier les cotes en supprimant une cote sur deux
;; selon un parcours geometrique logique
;; 
;; Usage :
;; 1. Charger le script : (load "simplif-cotes.lsp")
;; 2. Lancer la commande : SIMPLIF-COTES
;;
;; Deux modes disponibles :
;; - Mode automatique : detecte l'ordre des cotes automatiquement
;; - Mode polyligne : utilise une polyligne de reference pour l'ordre

(defun c:simplif-cotes ()
  (setq oldcmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  (princ "\n=== SIMPLIFICATION DES COTES ===")
  (princ "\nChoisissez le mode :")
  (princ "\n[A]utomatique - Detection automatique de l'ordre")
  (princ "\n[P]olyligne - Utiliser une polyligne de reference")
  
  (setq mode (getkword "\nMode [Automatique/Polyligne] <A>: "))
  (if (= mode nil) (setq mode "A"))
  
  (cond
    ((= mode "A") (simplif-auto))
    ((= mode "P") (simplif-poly))
    (t (princ "\nMode invalide."))
  )
  
  (setvar "CMDECHO" oldcmdecho)
  (princ)
)

;; Mode automatique : detection geometrique de l'ordre des cotes
(defun simplif-auto ()
  (princ "\n--- Mode automatique ---")
  (princ "\nSelectionnez les cotes a simplifier :")
  
  (setq ss (ssget '((0 . "DIMENSION"))))
  
  (if ss
    (progn
      (setq nb-cotes (sslength ss))
      (princ (strcat "\n" (itoa nb-cotes) " cotes selectionnees."))
      
      ;; Recuperation des positions et tri
      (setq liste-cotes (extraire-positions-cotes ss))
      (setq liste-triee (trier-cotes-geometriquement liste-cotes))
      
      ;; Suppression d'une cote sur deux
      (supprimer-une-sur-deux liste-triee)
    )
    (princ "\nAucune cote selectionnee.")
  )
)

;; Mode polyligne : utilise une polyligne pour definir l'ordre
(defun simplif-poly ()
  (princ "\n--- Mode polyligne ---")
  (princ "\nSelectionnez la polyligne de reference :")
  
  (setq ent-poly (car (entsel)))
  
  (if (and ent-poly 
           (= (cdr (assoc 0 (entget ent-poly))) "LWPOLYLINE"))
    (progn
      (princ "\nSelectionnez les cotes a simplifier :")
      (setq ss (ssget '((0 . "DIMENSION"))))
      
      (if ss
        (progn
          (setq nb-cotes (sslength ss))
          (princ (strcat "\n" (itoa nb-cotes) " cotes selectionnees."))
          
          ;; Tri selon la polyligne
          (setq liste-cotes (extraire-positions-cotes ss))
          (setq liste-triee (trier-selon-polyligne liste-cotes ent-poly))
          
          ;; Suppression d'une cote sur deux
          (supprimer-une-sur-deux liste-triee)
        )
        (princ "\nAucune cote selectionnee.")
      )
    )
    (princ "\nVeuillez selectionner une polyligne valide.")
  )
)

;; Fonction pour extraire les positions des cotes
(defun extraire-positions-cotes (ss)
  (setq liste '())
  (setq i 0)
  
  (repeat (sslength ss)
    (setq ent (ssname ss i))
    (setq data (entget ent))
    
    ;; Position de la cote (point de definition)
    (setq pos (cdr (assoc 10 data)))
    
    ;; Ajouter a la liste : (entite position)
    (setq liste (cons (list ent pos) liste))
    (setq i (1+ i))
  )
  
  (reverse liste)
)

;; Tri geometrique automatique (tri par angle depuis un centre)
(defun trier-cotes-geometriquement (liste-cotes)
  (princ "\nCalcul du centre geometrique...")
  
  ;; Calcul du centroide
  (setq centre (calculer-centroide liste-cotes))
  
  ;; Tri par angle polaire
  (setq liste-avec-angles
    (mapcar '(lambda (item)
               (setq pos (cadr item))
               (setq angle (angle centre pos))
               (list (car item) pos angle)
             )
             liste-cotes
    )
  )
  
  ;; Tri par angle croissant
  (setq liste-triee
    (vl-sort liste-avec-angles
             '(lambda (a b) (< (caddr a) (caddr b)))
    )
  )
  
  ;; Retourner juste entite et position
  (mapcar '(lambda (item) (list (car item) (cadr item))) liste-triee)
)

;; Calcul du centroide
(defun calculer-centroide (liste-cotes)
  (setq sum-x 0.0 sum-y 0.0 count 0)
  
  (foreach item liste-cotes
    (setq pos (cadr item))
    (setq sum-x (+ sum-x (car pos)))
    (setq sum-y (+ sum-y (cadr pos)))
    (setq count (1+ count))
  )
  
  (list (/ sum-x count) (/ sum-y count))
)

;; Tri selon une polyligne de reference
(defun trier-selon-polyligne (liste-cotes ent-poly)
  (princ "\nTri selon la polyligne...")
  
  ;; Pour chaque cote, calculer la distance le long de la polyligne
  (setq liste-avec-distances
    (mapcar '(lambda (item)
               (setq pos (cadr item))
               (setq dist (distance-sur-polyligne pos ent-poly))
               (list (car item) pos dist)
             )
             liste-cotes
    )
  )
  
  ;; Tri par distance croissante
  (setq liste-triee
    (vl-sort liste-avec-distances
             '(lambda (a b) (< (caddr a) (caddr b)))
    )
  )
  
  ;; Retourner juste entite et position
  (mapcar '(lambda (item) (list (car item) (cadr item))) liste-triee)
)

;; Calcul de la distance d'un point le long d'une polyligne
(defun distance-sur-polyligne (point ent-poly)
  ;; Simplification : utilise la distance au premier vertex
  ;; Dans une version plus complexe, on pourrait calculer la vraie projection
  (setq data (entget ent-poly))
  (setq premier-vertex (cdr (assoc 10 data)))
  (distance point premier-vertex)
)

;; Suppression d'une cote sur deux
(defun supprimer-une-sur-deux (liste-triee)
  (princ "\nSuppression d'une cote sur deux...")
  
  (setq compteur 0)
  (setq nb-supprimees 0)
  
  (foreach item liste-triee
    (setq compteur (1+ compteur))
    
    ;; Supprimer les cotes aux positions paires (2, 4, 6, ...)
    (if (= (rem compteur 2) 0)
      (progn
        (entdel (car item))
        (setq nb-supprimees (1+ nb-supprimees))
      )
    )
  )
  
  (princ (strcat "\n" (itoa nb-supprimees) " cotes supprimees."))
  (princ "\nSimplification terminee !")
)

;; Message de chargement
(princ "\n--- SIMPLIF-COTES.LSP charge ---")
(princ "\nCommande disponible : SIMPLIF-COTES")
(princ "\nUsage : Tapez SIMPLIF-COTES dans AutoCAD")
(princ)
