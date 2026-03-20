;; ========================================
;; MISE À JOUR DES VECTEURS DEPUIS TCPOINT2
;; ========================================
;; Lit les blocs TCPOINT2 avec attributs MAT (ex: 1.1 et 1.2)
;; et met à jour les blocs vecteurDXY correspondants
;; Usage: (C:UPDATEVEC2)

;; ========================================
;; FONCTIONS UTILITAIRES
;; ========================================

;; Récupérer la valeur d'un attribut dans un bloc (méthode simple)
(defun get-attribut-value (bloc-ename tag-name / ent ed mat-value found)
  (setq mat-value nil)
  (setq found nil)
  (setq ent bloc-ename)
  
  ;; Parcourir les entités suivantes (attributs)
  (while (and (not found) (setq ent (entnext ent)))
    (setq ed (entget ent))
    (if (= (cdr (assoc 0 ed)) "ATTRIB")
      (progn
        ;; Debug: afficher le tag trouvé
        ;(princ (strcat "\n  Tag: " (cdr (assoc 2 ed)) " = " (cdr (assoc 1 ed))))
        
        (if (= (strcase (cdr (assoc 2 ed))) (strcase tag-name))
          (progn
            (setq mat-value (cdr (assoc 1 ed)))
            (setq found T)
          )
        )
      )
      ;; Si on arrive à SEQEND, on arrête
      (if (= (cdr (assoc 0 ed)) "SEQEND")
        (setq found T)
      )
    )
  )
  mat-value
)

;; Récupérer tous les blocs TCPOINT2 avec leurs attributs MAT
(defun lire-tcpoints (/ ss i ent ed pt mat liste)
  (setq liste '())
  (setq ss (ssget "X" (list '(0 . "INSERT") 
                             '(2 . "TCPOINT2")
                             (cons 410 (getvar "CTAB")))))
  
  (if ss
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq ed (entget ent))
        
        ;; Coordonnées du point d'insertion
        (setq pt (cdr (assoc 10 ed)))
        
        ;; Récupérer l'attribut MAT
        (setq mat (get-attribut-value ent "MAT"))
        
        (if mat
          (setq liste (append liste (list (list mat pt ent))))
        )
        
        (setq i (1+ i))
      )
    )
  )
  liste
)

;; Trouver un TCPOINT2 par son matricule
(defun trouver-tcpoint-par-mat (mat liste / result)
  (setq result nil)
  (foreach item liste
    (if (= (car item) mat)
      (setq result item)
    )
  )
  result
)

;; Trouver le bloc vecteurDXY le plus proche d'un point
(defun trouver-bloc-vecteur-proche (pt tolerance / ss i ent ed pt-ins dist dist-min bloc-proche)
  (setq ss (ssget "X" (list '(0 . "INSERT") 
                             '(2 . "vecteurDXY")
                             (cons 410 (getvar "CTAB")))))
  (setq dist-min 999999.9)
  (setq bloc-proche nil)
  
  (if ss
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq ed (entget ent))
        (setq pt-ins (cdr (assoc 10 ed)))
        (setq dist (distance pt pt-ins))
        
        (if (< dist dist-min)
          (progn
            (setq dist-min dist)
            (setq bloc-proche ent)
          )
        )
        (setq i (1+ i))
      )
    )
  )
  
  ;; Retourner le bloc si dans la tolérance
  (if (and bloc-proche (< dist-min tolerance))
    (list bloc-proche dist-min)
    nil
  )
)

;; Modifier l'échelle et la rotation d'un bloc
(defun modifier-bloc-vecteur (ent-name dx dy facteur / ed new-scale new-angle)
  ;; Calculer la nouvelle échelle (distance 2D × facteur)
  (setq new-scale (* facteur (sqrt (+ (* dx dx) (* dy dy)))))
  
  ;; Calculer la nouvelle rotation (en radians)
  (if (and (= dx 0.0) (= dy 0.0))
    (setq new-angle 0.0)
    (setq new-angle (atan dy dx))
  )
  
  ;; Récupérer et modifier les données du bloc
  (setq ed (entget ent-name))
  
  ;; Modifier XScale (code 41)
  (if (assoc 41 ed)
    (setq ed (subst (cons 41 new-scale) (assoc 41 ed) ed))
    (setq ed (append ed (list (cons 41 new-scale))))
  )
  
  ;; Modifier YScale (code 42)
  (if (assoc 42 ed)
    (setq ed (subst (cons 42 new-scale) (assoc 42 ed) ed))
    (setq ed (append ed (list (cons 42 new-scale))))
  )
  
  ;; Modifier ZScale (code 43)
  (if (assoc 43 ed)
    (setq ed (subst (cons 43 new-scale) (assoc 43 ed) ed))
    (setq ed (append ed (list (cons 43 new-scale))))
  )
  
  ;; Modifier Rotation (code 50)
  (if (assoc 50 ed)
    (setq ed (subst (cons 50 new-angle) (assoc 50 ed) ed))
    (setq ed (append ed (list (cons 50 new-angle))))
  )
  
  (entmod ed)
  (entupd ent-name)
  (list new-scale new-angle)
)

;; Remplacer .1 par .2 dans un matricule
(defun mat-base-vers-tete (mat / pos)
  (if (setq pos (vl-string-search ".1" mat))
    (strcat (substr mat 1 pos) ".2" (substr mat (+ pos 3)))
    nil
  )
)

;; ========================================
;; COMMANDE PRINCIPALE
;; ========================================

(defun C:UPDATEVEC2 (/ tcpoints tolerance facteur count-ok count-erreur
                       pt-base pt-tete mat-base mat-tete dx dy bloc-vec result)
  (princ "\n=== MISE À JOUR DES VECTEURS DEPUIS TCPOINT2 ===\n")
  
  ;; Paramètres
  (initget 6)
  (setq tol-input (getdist "\nTolérance de recherche en m (défaut 0.5): "))
  (if (null tol-input)
    (setq tolerance 0.5)
    (setq tolerance tol-input)
  )
  
  (initget 6)
  (setq fact-input (getreal "\nFacteur d'échelle (défaut 1): "))
  (if (null fact-input)
    (setq facteur 1.0)
    (setq facteur fact-input)
  )
  
  ;; Lire tous les TCPOINT2
  (princ "\nLecture des TCPOINT2...\n")
  (setq tcpoints (lire-tcpoints))
  
  (if (null tcpoints)
    (progn
      (princ "\nAucun bloc TCPOINT2 trouvé.\n")
      (princ)
      (exit)
    )
  )
  
  (princ (strcat (itoa (length tcpoints)) " TCPOINT2 trouvé(s)\n"))
  (princ "\nTraitement en cours...\n\n")
  
  ;; Initialiser les compteurs
  (setq count-ok 0)
  (setq count-erreur 0)
  
  ;; Parcourir tous les points .1 (base)
  (foreach item tcpoints
    (setq mat-base (car item))
    
    ;; Vérifier si c'est un point de base (.1)
    (if (vl-string-search ".1" mat-base)
      (progn
        (setq pt-base (cadr item))
        
        ;; Chercher le point correspondant .2 (tête)
        (setq mat-tete (mat-base-vers-tete mat-base))
        
        (princ (strcat "Point " mat-base " -> " mat-tete " : "))
        
        (setq item-tete (trouver-tcpoint-par-mat mat-tete tcpoints))
        
        (if item-tete
          (progn
            (setq pt-tete (cadr item-tete))
            
            ;; Calculer les déplacements
            (setq dx (- (car pt-tete) (car pt-base)))
            (setq dy (- (cadr pt-tete) (cadr pt-base)))
            
            ;; Convertir en mm
            (setq dx dx)
            (setq dy dy)
            
            (princ (strcat "dX=" (rtos dx 2 1) " dY=" (rtos dy 2 1) " -> "))
            
            ;; Trouver le bloc vecteurDXY à la position du point base
            (setq result (trouver-bloc-vecteur-proche pt-base tolerance))
            
            (if result
              (progn
                (setq bloc-vec (car result))
                (setq dist-trouvee (cadr result))
                
                ;; Modifier le bloc
                (setq modif-result (modifier-bloc-vecteur bloc-vec dx dy facteur))
                
                (princ (strcat "OK (dist=" (rtos dist-trouvee 2 3) 
                              " échelle=" (rtos (car modif-result) 2 1) ")\n"))
                (setq count-ok (1+ count-ok))
              )
              (progn
                (princ "BLOC VECTEUR NON TROUVÉ\n")
                (setq count-erreur (1+ count-erreur))
              )
            )
          )
          (progn
            (princ "POINT .2 NON TROUVÉ\n")
            (setq count-erreur (1+ count-erreur))
          )
        )
      )
    )
  )
  
  ;; Résumé
  (princ "\n=== TRAITEMENT TERMINÉ ===\n")
  (princ (strcat "Blocs mis à jour: " (itoa count-ok) "\n"))
  (princ (strcat "Erreurs: " (itoa count-erreur) "\n"))
  
  (princ)
)

(princ "\n*** Script chargé ***")
(princ "\nCommandes disponibles:")
(princ "\n  UPDATEVEC2 - Mettre à jour les vecteurs depuis les TCPOINT2")
(princ "\n")
(princ "\nPrérequis:")
(princ "\n  - Blocs TCPOINT2 avec attribut MAT (ex: 1.1, 1.2, 2.1, 2.2...)")
(princ "\n  - Points .1 = base des vecteurs")
(princ "\n  - Points .2 = tête des vecteurs")
(princ "\n  - Blocs vecteurDXY positionnés sur les points .1")
(princ "\n")
(princ)
