;; ========================================
;; MISE À JOUR DES BLOCS VECTEURS DE DÉPLACEMENT
;; ========================================
;; Lit un fichier CSV et met à jour les blocs vecteurDXY
;; Format CSV: ID;X_base;Y_base;dX_mm;dY_mm
;; Usage: (C:UPDATEVEC)

;; ========================================
;; FONCTIONS UTILITAIRES
;; ========================================

;; Lire un fichier CSV et retourner une liste de listes
(defun lire-csv (fichier separateur / f ligne lignes champs)
  (setq lignes '())
  (if (setq f (open fichier "r"))
    (progn
      (while (setq ligne (read-line f))
        (setq champs (parse-csv-ligne ligne separateur))
        (setq lignes (append lignes (list champs)))
      )
      (close f)
    )
  )
  lignes
)

;; Parser une ligne CSV
(defun parse-csv-ligne (ligne sep / result pos debut)
  (setq result '())
  (setq debut 0)
  (while (setq pos (vl-string-search sep ligne debut))
    (setq result (append result (list (substr ligne (1+ debut) (- pos debut)))))
    (setq debut (1+ pos))
  )
  (setq result (append result (list (substr ligne (1+ debut)))))
  result
)

;; Convertir une chaîne en nombre (gère virgule et point)
(defun str->num (str / s)
  (setq s (vl-string-subst "." "," str))
  (if (numberp (read s)) (read s) 0.0)
)

;; Trouver le bloc le plus proche d'un point
(defun trouver-bloc-proche (pt tolerance nom-bloc / ss i ent ed pt-ins dist dist-min bloc-proche)
  (setq ss (ssget "X" (list '(0 . "INSERT") 
                             (cons 2 nom-bloc)
                             (cons 410 (getvar "CTAB")))))
  (setq dist-min 999999.9)
  (setq bloc-proche nil)
  
  (if ss
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq ed (entget ent))
        (setq pt-ins (list (cdr (assoc 10 ed)) 
                           (cdr (assoc 20 ed))))
        (setq pt-ins (list (cadr (assoc 10 ed)) (caddr (assoc 10 ed))))
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
  
  ;; Retourner le bloc si dans la tolerance
  (if (and bloc-proche (< dist-min tolerance))
    bloc-proche
    nil
  )
)

;; Modifier l'échelle et la rotation d'un bloc
(defun modifier-bloc (ent-name dx dy facteur / ed new-scale new-angle)
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
  T
)

;; ========================================
;; COMMANDE PRINCIPALE
;; ========================================

(defun C:UPDATEVEC (/ csv-file data separateur tolerance facteur 
                     count-ok count-erreur ligne id x y dx dy pt-base bloc)
  (princ "\n=== MISE À JOUR DES VECTEURS DE DÉPLACEMENT ===\n")
  
  ;; Sélectionner le fichier CSV
  (setq csv-file (getfiled "Sélectionnez le fichier CSV avec les déplacements" "" "csv" 0))
  
  (if (not csv-file)
    (progn
      (princ "\nOpération annulée.\n")
      (princ)
      (exit)
    )
  )
  
  ;; Paramètres
  (princ "\nSéparateur CSV (défaut: ;): ")
  (setq sep-input (getstring))
  (if (= sep-input "")
    (setq separateur ";")
    (setq separateur sep-input)
  )
  
  (princ "\nTolérance de recherche en mètres (défaut: 0.1): ")
  (setq tol-input (getstring))
  (if (= tol-input "")
    (setq tolerance 0.1)
    (setq tolerance (str->num tol-input))
  )
  
  (princ "\nFacteur d'échelle (défaut: 10): ")
  (setq fact-input (getstring))
  (if (= fact-input "")
    (setq facteur 10.0)
    (setq facteur (str->num fact-input))
  )
  
  ;; Lire le fichier CSV
  (princ (strcat "\nLecture du fichier: " csv-file "\n"))
  (setq data (lire-csv csv-file separateur))
  
  (if (null data)
    (progn
      (princ "\nErreur: impossible de lire le fichier CSV.\n")
      (princ)
      (exit)
    )
  )
  
  (princ (strcat (itoa (length data)) " ligne(s) lue(s)\n"))
  (princ "\nTraitement en cours...\n\n")
  
  ;; Initialiser les compteurs
  (setq count-ok 0)
  (setq count-erreur 0)
  
  ;; Parcourir les données (ignorer la première ligne si c'est un en-tête)
  (setq data (cdr data))  ; Ignorer l'en-tête
  
  (foreach ligne data
    (if (>= (length ligne) 5)
      (progn
        ;; Extraire les données
        (setq id (nth 0 ligne))
        (setq x (str->num (nth 1 ligne)))
        (setq y (str->num (nth 2 ligne)))
        (setq dx (str->num (nth 3 ligne)))
        (setq dy (str->num (nth 4 ligne)))
        
        (setq pt-base (list x y))
        
        (princ (strcat "Point " id " (" (rtos x 2 3) ", " (rtos y 2 3) 
                       ") dX=" (rtos dx 2 1) " dY=" (rtos dy 2 1) " -> "))
        
        ;; Trouver le bloc le plus proche
        (setq bloc (trouver-bloc-proche pt-base tolerance "vecteurDXY"))
        
        (if bloc
          (progn
            ;; Modifier le bloc
            (if (modifier-bloc bloc dx dy facteur)
              (progn
                (princ "OK\n")
                (setq count-ok (1+ count-ok))
              )
              (progn
                (princ "ERREUR modification\n")
                (setq count-erreur (1+ count-erreur))
              )
            )
          )
          (progn
            (princ "BLOC NON TROUVÉ\n")
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
(princ "\n  UPDATEVEC - Mettre à jour les vecteurs depuis un CSV")
(princ "\n")
(princ "\nFormat CSV attendu:")
(princ "\n  ID;X_base;Y_base;dX_mm;dY_mm")
(princ "\n  1.1;18644.160;97030.990;-0.8;1.1")
(princ "\n  2.1;18633.690;97064.510;-0.4;0.6")
(princ "\n")
(princ)
