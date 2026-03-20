;;; ========================================================================
;;; DECALAGE-LIMITES-RACCORDEMENT.LSP
;;; ========================================================================
;;; Description : Décale les lignes limites haute et basse pour créer
;;;               des lignes de raccordement
;;; Auteur      : 
;;; Date        : 2025-11-19
;;; ========================================================================

(defun C:DECALIM ( / *error* old-osmode old-cmdecho 
                    axe-ents intersections int-pt 
                    limites-group ligne-haut ligne-bas
                    nouvelle-haut nouvelle-bas count
                    lines poly-old poly-lw)
  
  ;; Chargement des fonctions Visual LISP
  (vl-load-com)
  
  ;; Fonction de gestion d'erreur
  (defun *error* (msg)
    (if old-osmode (setvar "OSMODE" old-osmode))
    (if old-cmdecho (setvar "CMDECHO" old-cmdecho))
    (if (not (member msg '("Function cancelled" "quit / exit abort")))
      (princ (strcat "\nErreur: " msg))
    )
    (princ)
  )
  
  ;; Sauvegarde des variables système
  (setq old-osmode (getvar "OSMODE")
        old-cmdecho (getvar "CMDECHO"))
  (setvar "OSMODE" 0)
  (setvar "CMDECHO" 0)
  
  (princ "\n========================================")
  (princ "\n  DÉCALAGE LIMITES RACCORDEMENT")
  (princ "\n========================================")
  
  ;; Création du calque RACCORDEMENT s'il n'existe pas
  (if (not (tblsearch "LAYER" "RACCORDEMENT"))
    (progn
      (command "_.-LAYER" "_N" "RACCORDEMENT" "_C" "6" "RACCORDEMENT" "")
      (princ "\nCalque RACCORDEMENT créé (couleur magenta).")
    )
  )
  
  ;; Étape 1 : Collecter toutes les lignes du calque DESIGN_AXIS
  (princ "\n\nRecherche des lignes du calque DESIGN_AXIS...")
  (setq axe-ents '())
  
  ;; Chercher les LINE
  (setq lines (get-entities-by-layer "DESIGN_AXIS" "LINE"))
  (if lines
    (progn
      (setq axe-ents (append axe-ents lines))
      (princ (strcat "\n  " (itoa (length lines)) " LINE(s) trouvée(s)"))
    )
  )
  
  ;; Chercher aussi les POLYLINE au cas où
  (setq poly-old (get-entities-by-layer "DESIGN_AXIS" "POLYLINE"))
  (if poly-old
    (progn
      (setq axe-ents (append axe-ents poly-old))
      (princ (strcat "\n  " (itoa (length poly-old)) " POLYLINE(s) trouvée(s)"))
    )
  )
  
  ;; Chercher les LWPOLYLINE (légères)
  (setq poly-lw (get-entities-by-layer "DESIGN_AXIS" "LWPOLYLINE"))
  (if poly-lw
    (progn
      (setq axe-ents (append axe-ents poly-lw))
      (princ (strcat "\n  " (itoa (length poly-lw)) " LWPOLYLINE(s) trouvée(s)"))
    )
  )
  
  (if (not axe-ents)
    (progn
      (princ "\nAUCUNE ligne/polyligne trouvée sur le calque DESIGN_AXIS !")
      (princ "\nVérifiez que le calque existe et contient des lignes.")
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      (princ)
      (exit)
    )
  )
  
  (princ (strcat "\n  TOTAL : " (itoa (length axe-ents)) " entité(s) trouvée(s)."))
  
  ;; Étape 2 : Trouver toutes les intersections
  (princ "\n\nRecherche des intersections...")
  (setq intersections (find-all-intersections axe-ents))
  
  (if (not intersections)
    (progn
      (princ "\nAUCUNE intersection trouvée !")
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      (princ)
      (exit)
    )
  )
  
  (princ (strcat "\n" (itoa (length intersections)) " point(s) d'intersection trouvé(s)."))
  
  ;; Étape 3 : Pour chaque intersection, traiter les lignes limites
  (setq count 0)
  (princ "\n\nTraitement des groupes de lignes limites...")
  
  (foreach int-pt intersections
    (princ (strcat "\n\nPoint d'intersection: " 
                   (rtos (car int-pt) 2 3) ", "
                   (rtos (cadr int-pt) 2 3) ", "
                   (rtos (caddr int-pt) 2 3)))
    
    ;; Chercher les lignes du calque LIMITE autour de ce point
    (setq limites-group (get-limite-lines-near-point int-pt 10.0))
    
    (if (and limites-group (= (length limites-group) 3))
      (progn
        (princ (strcat "\n  -> " (itoa (length limites-group)) " ligne(s) limite trouvée(s)"))
        
        ;; Identifier la ligne haute et basse
        (setq ligne-haut (get-top-line limites-group)
              ligne-bas (get-bottom-line limites-group))
        
        (if (and ligne-haut ligne-bas)
          (progn
            ;; Décaler la ligne haute de +0.20 m (vers le haut)
            (setq nouvelle-haut (offset-line ligne-haut 0.20 "RACCORDEMENT"))
            
            ;; Décaler la ligne basse de -0.20 m (vers le bas)
            (setq nouvelle-bas (offset-line ligne-bas -0.20 "RACCORDEMENT"))
            
            (if (and nouvelle-haut nouvelle-bas)
              (progn
                (setq count (+ count 1))
                (princ (strcat "\n  -> Lignes de raccordement créées (groupe " (itoa count) ")"))
                
                ;; Étape 4 : Créer l'arc de raccordement
                (create-raccordement-arc int-pt nouvelle-haut nouvelle-bas "RACCORDEMENT")
              )
              (princ "\n  -> ERREUR lors du décalage des lignes")
            )
          )
          (princ "\n  -> Impossible d'identifier les lignes haute/basse")
        )
      )
      (princ (strcat "\n  -> " 
                     (if limites-group 
                       (strcat (itoa (length limites-group)) " ligne(s)")
                       "0 ligne")
                     " trouvée(s) (attendu: 3)"))
    )
  )
  
  ;; Résumé
  (princ "\n\n========================================")
  (princ (strcat "\nTraitement terminé : " (itoa count) " groupe(s) traité(s)"))
  (princ "\n========================================")
  
  ;; Restauration des variables système
  (setvar "OSMODE" old-osmode)
  (setvar "CMDECHO" old-cmdecho)
  (princ)
)

;;; ========================================================================
;;; FONCTIONS UTILITAIRES
;;; ========================================================================

;; Récupère toutes les entités d'un calque donné et d'un type donné
(defun get-entities-by-layer (layer-name ent-type / ss ent-list i ent)
  (setq ss (ssget "_X" (list (cons 8 layer-name) (cons 0 ent-type))))
  (if ss
    (progn
      (setq ent-list '()
            i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq ent-list (append ent-list (list ent)))
        (setq i (1+ i))
      )
      ent-list
    )
    nil
  )
)

;; Trouve toutes les intersections entre les lignes
(defun find-all-intersections (line-list / intersections all-points pt ent-data pt-start pt-end pt-mid tolerance clusters cluster avg-pt sum-x sum-y sum-z i found-cluster)
  (setq intersections '())
  (setq all-points '())
  (setq tolerance 0.1)  ; Tolérance de 10 cm pour grouper les points proches
  
  (princ "\n  Collecte des points milieux des lignes...")
  
  ;; Collecter les points MILIEUX de chaque ligne
  (foreach line line-list
    (setq ent-data (entget line))
    (setq pt-start (cdr (assoc 10 ent-data))
          pt-end (cdr (assoc 11 ent-data)))
    ;; Calculer le point milieu
    (setq pt-mid (list (/ (+ (car pt-start) (car pt-end)) 2.0)
                       (/ (+ (cadr pt-start) (cadr pt-end)) 2.0)
                       (/ (+ (caddr pt-start) (caddr pt-end)) 2.0)))
    (setq all-points (append all-points (list pt-mid)))
  )
  
  (princ (strcat "\n  " (itoa (length all-points)) " points milieux collectés"))
  (princ "\n  Regroupement des points proches (tolérance 10 cm)...")
  
  ;; Créer des clusters de points proches
  (setq clusters '())
  (foreach pt all-points
    ;; Chercher un cluster existant proche
    (setq found-cluster nil)
    (setq i 0)
    (foreach cluster clusters
      (setq avg-pt (car cluster))  ; Point moyen du cluster
      (if (< (distance pt avg-pt) tolerance)
        (progn
          (setq found-cluster i)
        )
      )
      (setq i (1+ i))
    )
    
    ;; Si un cluster est trouvé, ajouter le point
    (if found-cluster
      (progn
        (setq cluster (nth found-cluster clusters))
        (setq cluster (append cluster (list pt)))
        (setq clusters (subst cluster (nth found-cluster clusters) clusters))
      )
      ;; Sinon, créer un nouveau cluster
      (setq clusters (append clusters (list (list pt))))
    )
  )
  
  (princ (strcat "\n  " (itoa (length clusters)) " groupe(s) de points trouvé(s)"))
  (princ "\n  Identification des intersections (2+ lignes)...")
  
  ;; Les clusters avec 2+ points sont des intersections
  (foreach cluster clusters
    (if (>= (length cluster) 2)
      (progn
        ;; Calculer le point moyen du cluster
        (setq sum-x 0.0 sum-y 0.0 sum-z 0.0)
        (foreach pt cluster
          (setq sum-x (+ sum-x (car pt))
                sum-y (+ sum-y (cadr pt))
                sum-z (+ sum-z (caddr pt)))
        )
        (setq avg-pt (list (/ sum-x (length cluster))
                          (/ sum-y (length cluster))
                          (/ sum-z (length cluster))))
        (setq intersections (append intersections (list avg-pt)))
      )
    )
  )
  
  (princ (strcat "\n  " (itoa (length intersections)) " intersection(s) trouvée(s)."))
  intersections
)

;; Chercher les lignes du calque LIMITE près d'un point donné
(defun get-limite-lines-near-point (pt radius / ss ent-list i ent ent-data 
                                         pt-start pt-end pt-mid dist-mid-x dist-mid-y
                                         length-line)
  (setq ss (ssget "_X" (list (cons 8 "LIMITE") (cons 0 "LINE"))))
  (setq ent-list '())
  
  (if ss
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq ent-data (entget ent))
        (setq pt-start (cdr (assoc 10 ent-data))
              pt-end (cdr (assoc 11 ent-data)))
        
        ;; Calculer le point milieu de la ligne
        (setq pt-mid (list (/ (+ (car pt-start) (car pt-end)) 2.0)
                           (/ (+ (cadr pt-start) (cadr pt-end)) 2.0)
                           (/ (+ (caddr pt-start) (caddr pt-end)) 2.0)))
        
        ;; Vérifier la distance en X et Y du milieu par rapport à l'intersection
        (setq dist-mid-x (abs (- (car pt-mid) (car pt)))
              dist-mid-y (abs (- (cadr pt-mid) (cadr pt))))
        
        ;; Vérifier la longueur de la ligne (environ 11.86 m)
        (setq length-line (distance pt-start pt-end))
        
        ;; La ligne doit avoir son milieu proche du X de l'intersection (< radius)
        ;; et être dans un rayon acceptable en Y aussi
        (if (and (< dist-mid-x radius)
                 (< dist-mid-y radius)
                 (> length-line 11.5)
                 (< length-line 12.2))
          (setq ent-list (append ent-list (list ent)))
        )
        
        (setq i (1+ i))
      )
    )
  )
  ent-list
)

;; Obtenir la ligne la plus haute (Y maximum)
(defun get-top-line (line-list / max-y max-line ent ent-data pt-start pt-end avg-y)
  (setq max-y -1e99
        max-line nil)
  
  (foreach ent line-list
    (setq ent-data (entget ent))
    (setq pt-start (cdr (assoc 10 ent-data))
          pt-end (cdr (assoc 11 ent-data)))
    (setq avg-y (/ (+ (cadr pt-start) (cadr pt-end)) 2.0))
    
    (if (> avg-y max-y)
      (progn
        (setq max-y avg-y)
        (setq max-line ent)
      )
    )
  )
  max-line
)

;; Obtenir la ligne la plus basse (Y minimum)
(defun get-bottom-line (line-list / min-y min-line ent ent-data pt-start pt-end avg-y)
  (setq min-y 1e99
        min-line nil)
  
  (foreach ent line-list
    (setq ent-data (entget ent))
    (setq pt-start (cdr (assoc 10 ent-data))
          pt-end (cdr (assoc 11 ent-data)))
    (setq avg-y (/ (+ (cadr pt-start) (cadr pt-end)) 2.0))
    
    (if (< avg-y min-y)
      (progn
        (setq min-y avg-y)
        (setq min-line ent)
      )
    )
  )
  min-line
)

;; Décale une ligne et place la copie sur le calque spécifié
(defun offset-line (ent offset-dist target-layer / ent-data pt-start pt-end
                         new-pt-start new-pt-end new-ent)
  (setq ent-data (entget ent))
  (setq pt-start (cdr (assoc 10 ent-data))
        pt-end (cdr (assoc 11 ent-data)))
  
  ;; Décalage en Y (lignes horizontales)
  (setq new-pt-start (list (car pt-start) 
                           (+ (cadr pt-start) offset-dist)
                           (caddr pt-start))
        new-pt-end (list (car pt-end)
                         (+ (cadr pt-end) offset-dist)
                         (caddr pt-end)))
  
  ;; Créer la nouvelle ligne
  (entmake (list (cons 0 "LINE")
                 (cons 8 target-layer)
                 (cons 10 new-pt-start)
                 (cons 11 new-pt-end)))
  
  ;; Retourner l'entité créée
  (entlast)
)

;; Créer un arc de raccordement
(defun create-raccordement-arc (int-pt ligne-haut ligne-bas target-layer / 
                                 meas-lines meas-lines-lw pt-inter-haut pt-inter-bas
                                 arc-center arc-angle1 arc-angle2
                                 dist-center mid-pt bulge)
  
  (princ "\n     Recherche des intersections avec MEAS_POINTS_LINE...")
  
  ;; Récupérer toutes les lignes ET polylignes du calque MEAS_POINTS_LINE
  (setq meas-lines (get-entities-by-layer "MEAS_POINTS_LINE" "LINE"))
  (setq meas-lines-lw (get-entities-by-layer "MEAS_POINTS_LINE" "LWPOLYLINE"))
  
  ;; DEBUG: Afficher le nombre d'entités trouvées
  (princ (strcat "\n     DEBUG: " (itoa (length meas-lines)) " LINE(s), " 
                 (itoa (length meas-lines-lw)) " LWPOLYLINE(s)"))
  
  ;; Combiner les deux listes
  (if meas-lines-lw
    (setq meas-lines (append meas-lines meas-lines-lw))
  )
  
  (princ (strcat "\n     DEBUG: " (itoa (length meas-lines)) " entité(s) MEAS_POINTS_LINE au total"))
  
  ;; DEBUG: Afficher les coordonnées des lignes de raccordement
  (setq ligne-haut-data (entget ligne-haut))
  (setq ligne-bas-data (entget ligne-bas))
  (princ (strcat "\n     DEBUG: Ligne HAUT: X1=" (rtos (car (cdr (assoc 10 ligne-haut-data))) 2 2)
                 " X2=" (rtos (car (cdr (assoc 11 ligne-haut-data))) 2 2)
                 " Y=" (rtos (cadr (cdr (assoc 10 ligne-haut-data))) 2 2)))
  (princ (strcat "\n     DEBUG: Ligne BAS : X1=" (rtos (car (cdr (assoc 10 ligne-bas-data))) 2 2)
                 " X2=" (rtos (car (cdr (assoc 11 ligne-bas-data))) 2 2)
                 " Y=" (rtos (cadr (cdr (assoc 10 ligne-bas-data))) 2 2)))
  (princ (strcat "\n     DEBUG: Point d'intersection DESIGN_AXIS: X=" (rtos (car int-pt) 2 2)
                 " Y=" (rtos (cadr int-pt) 2 2)))
  
  (if meas-lines
    (progn
      ;; Chercher l'intersection de la ligne haute avec MEAS_POINTS_LINE
      (setq pt-inter-haut (find-intersection-right ligne-haut meas-lines int-pt 10.0))
      
      ;; Chercher l'intersection de la ligne basse avec MEAS_POINTS_LINE
      (setq pt-inter-bas (find-intersection-right ligne-bas meas-lines int-pt 10.0))
      
      (if (and pt-inter-haut pt-inter-bas)
        (progn
          (princ "\n     -> Points d'intersection trouvés")
          (princ (strcat "\n        Haut: " (rtos (car pt-inter-haut) 2 3) ", " (rtos (cadr pt-inter-haut) 2 3)))
          (princ (strcat "\n        Bas : " (rtos (car pt-inter-bas) 2 3) ", " (rtos (cadr pt-inter-bas) 2 3)))
          
          ;; Créer l'arc de rayon 4.19 m passant par ces 2 points
          ;; Calculer les 2 centres possibles
          (setq arc-center1 (calculate-arc-center pt-inter-haut pt-inter-bas 4.19 T))
          (setq arc-center2 (calculate-arc-center pt-inter-haut pt-inter-bas 4.19 nil))
          
          (if (and arc-center1 arc-center2)
            (progn
              (princ "\n     -> Création de l'arc de raccordement...")
              
              ;; Calculer les angles pour les 2 centres
              (setq angle1-c1 (angle arc-center1 pt-inter-haut))
              (setq angle2-c1 (angle arc-center1 pt-inter-bas))
              (setq angle1-c2 (angle arc-center2 pt-inter-haut))
              (setq angle2-c2 (angle arc-center2 pt-inter-bas))
              
              ;; Calculer l'amplitude de l'arc pour chaque centre
              (setq amp1 (abs (- angle2-c1 angle1-c1)))
              (if (> amp1 pi) (setq amp1 (- (* 2 pi) amp1)))
              
              (setq amp2 (abs (- angle2-c2 angle1-c2)))
              (if (> amp2 pi) (setq amp2 (- (* 2 pi) amp2)))
              
              (princ (strcat "\n        Centre 1 - amplitude: " (rtos (/ (* amp1 180.0) pi) 2 1) "°"))
              (princ (strcat "\n        Centre 2 - amplitude: " (rtos (/ (* amp2 180.0) pi) 2 1) "°"))
              (princ (strcat "\n        Centre 1 X: " (rtos (car arc-center1) 2 2)))
              (princ (strcat "\n        Centre 2 X: " (rtos (car arc-center2) 2 2)))
              (princ (strcat "\n        Point inter X: " (rtos (car int-pt) 2 2)))
              
              ;; Choisir le centre le plus proche de X_intersection + 0.5m
              (setq target-x (+ (car int-pt) 0.5))
              (setq dist1 (abs (- (car arc-center1) target-x)))
              (setq dist2 (abs (- (car arc-center2) target-x)))
              
              (princ (strcat "\n        Target X: " (rtos target-x 2 2)))
              (princ (strcat "\n        Distance centre 1: " (rtos dist1 2 2)))
              (princ (strcat "\n        Distance centre 2: " (rtos dist2 2 2)))
              
              (if (< dist1 dist2)
                (progn
                  (princ "\n        -> Utilisation du centre 1 (plus proche de target)")
                  (setq arc-center arc-center1)
                  (setq arc-angle1 angle2-c1)  ; Point BAS (inversé)
                  (setq arc-angle2 angle1-c1)  ; Point HAUT (inversé)
                )
                (progn
                  (princ "\n        -> Utilisation du centre 2 (plus proche de target)")
                  (setq arc-center arc-center2)
                  (setq arc-angle1 angle2-c2)  ; Point BAS (inversé)
                  (setq arc-angle2 angle1-c2)  ; Point HAUT (inversé)
                )
              )
              
              ;; Créer l'arc
              (setq new-arc (entmake (list (cons 0 "ARC")
                            (cons 8 target-layer)
                            (cons 10 arc-center)
                            (cons 40 4.19)
                            (cons 50 arc-angle1)
                            (cons 51 arc-angle2))))
              
              (princ "\n     -> Arc créé avec succès")
              
              ;; Retourner l'entité arc créée
              (entlast)
            )
            (princ "\n     -> ERREUR: Impossible de calculer le centre de l'arc")
          )
        )
        (princ "\n     -> Aucune intersection à droite trouvée avec MEAS_POINTS_LINE")
      )
    )
    (princ "\n     -> Aucune ligne trouvée sur le calque MEAS_POINTS_LINE")
  )
)

;; Trouver l'intersection d'une ligne avec des lignes MEAS, à droite du point de référence
(defun find-intersection-right (line meas-lines ref-pt radius / 
                                 line-obj meas-obj int-pts best-pt pt dist-x dist-total nb-checked nb-inter)
  (setq best-pt nil)
  (setq nb-checked 0)
  (setq nb-inter 0)
  (setq line-obj (vlax-ename->vla-object line))
  
  (princ (strcat "\n     DEBUG: Recherche parmi " (itoa (length meas-lines)) " entités MEAS"))
  
  (foreach meas-line meas-lines
    (setq nb-checked (1+ nb-checked))
    (setq meas-obj (vlax-ename->vla-object meas-line))
    
    ;; Chercher les intersections
    (setq int-pts (get-intersection-points-simple line-obj meas-obj))
    
    (if int-pts
      (progn
        (setq nb-inter (+ nb-inter (length int-pts)))
        (princ (strcat "\n     DEBUG: " (itoa (length int-pts)) " intersection(s) trouvée(s)"))
        (foreach pt int-pts
          (setq dist-x (- (car pt) (car ref-pt)))
          (setq dist-total (distance pt ref-pt))
          (princ (strcat "\n       Point: X=" (rtos (car pt) 2 2) 
                        " dist-X=" (rtos dist-x 2 2)
                        " dist-tot=" (rtos dist-total 2 2)))
          ;; Vérifier que le point est à droite (X > ref-pt X) et dans le rayon
          (if (and (> (car pt) (car ref-pt))
                   (< (distance pt ref-pt) radius))
            (progn
              (setq best-pt pt)
              (princ " -> OK!")
            )
            (princ " -> Rejeté")
          )
        )
      )
    )
  )
  
  (princ (strcat "\n     DEBUG: " (itoa nb-checked) " entités vérifiées, " 
                (itoa nb-inter) " intersections trouvées"))
  best-pt
)

;; Version simplifiée pour obtenir les points d'intersection
(defun get-intersection-points-simple (obj1 obj2 / result err upper-bound point-list num-points i)
  (setq result (vl-catch-all-apply 'vlax-invoke (list obj1 'IntersectWith obj2 acExtendNone)))
  
  (if (not (vl-catch-all-error-p result))
    (progn
      ;; Vérifier si c'est déjà une liste de points (variante de certaines versions AutoCAD)
      (if (and (listp result) (= (type (car result)) 'REAL))
        ;; C'est une liste plate de coordonnées (x1 y1 z1 x2 y2 z2 ...)
        (progn
          (setq point-list '())
          (setq i 0)
          (while (< i (length result))
            (setq point-list 
                  (append point-list 
                          (list (list (nth i result)
                                      (nth (+ i 1) result)
                                      (nth (+ i 2) result)))))
            (setq i (+ i 3))
          )
          point-list
        )
        ;; Sinon, c'est un SafeArray, traiter comme avant
        (progn
          (setq err (vl-catch-all-apply 'vlax-safearray-get-u-bound (list result 1)))
          (if (not (vl-catch-all-error-p err))
            (progn
              (setq upper-bound err)
              (if (>= upper-bound 0)
                (progn
                  (setq point-list '())
                  (setq num-points (1+ (/ upper-bound 3)))
                  (setq i 0)
                  (repeat num-points
                    (setq point-list 
                          (append point-list 
                                  (list (list (vlax-safearray-get-element result (* i 3))
                                              (vlax-safearray-get-element result (+ (* i 3) 1))
                                              (vlax-safearray-get-element result (+ (* i 3) 2))))))
                    (setq i (1+ i))
                  )
                  point-list
                )
                nil
              )
            )
            nil
          )
        )
      )
    )
    nil
  )
)

;; Calculer le centre d'un arc passant par 2 points avec un rayon donné
(defun calculate-arc-center (pt1 pt2 radius right-side / 
                              mid-pt dist-pts half-dist offset-dist
                              dx dy perp-x perp-y center)
  
  ;; Point milieu entre pt1 et pt2
  (setq mid-pt (list (/ (+ (car pt1) (car pt2)) 2.0)
                     (/ (+ (cadr pt1) (cadr pt2)) 2.0)
                     (/ (+ (caddr pt1) (caddr pt2)) 2.0)))
  
  ;; Distance entre les 2 points
  (setq dist-pts (distance pt1 pt2))
  (setq half-dist (/ dist-pts 2.0))
  
  ;; Vérifier que le rayon est suffisant
  (if (< radius half-dist)
    (progn
      (princ "\n     ERREUR: Rayon trop petit pour ces points")
      nil
    )
    (progn
      ;; Distance du milieu au centre de l'arc
      (setq offset-dist (sqrt (- (* radius radius) (* half-dist half-dist))))
      
      ;; Vecteur perpendiculaire
      (setq dx (- (car pt2) (car pt1)))
      (setq dy (- (cadr pt2) (cadr pt1)))
      
      ;; Perpendiculaire normalisée (vers la droite si right-side = T)
      (if right-side
        (progn
          (setq perp-x (/ dy dist-pts))
          (setq perp-y (/ (- dx) dist-pts))
        )
        (progn
          (setq perp-x (/ (- dy) dist-pts))
          (setq perp-y (/ dx dist-pts))
        )
      )
      
      ;; Centre de l'arc
      (setq center (list (+ (car mid-pt) (* perp-x offset-dist))
                        (+ (cadr mid-pt) (* perp-y offset-dist))
                        (caddr mid-pt)))
      center
    )
  )
)

;;; ========================================================================
;;; CHARGEMENT
;;; ========================================================================

(princ "\n========================================")
(princ "\n  DÉCALAGE LIMITES RACCORDEMENT")
(princ "\n========================================")
(princ "\nCommande disponible : DECALIM")
(princ "\n")
(princ "\nCe script va :")
(princ "\n  1. Trouver les intersections des lignes (DESIGN_AXIS)")
(princ "\n  2. Chercher les 3 lignes limites autour de chaque intersection")
(princ "\n  3. Décaler les lignes haute (+20cm) et basse (-20cm)")
(princ "\n  4. Placer les nouvelles lignes sur le calque RACCORDEMENT")
(princ "\n========================================")
(princ "\nCommande disponible : AJUSTRAC")
(princ "\nAjuste les lignes de raccordement avec les arcs")
(princ "\n========================================")
(princ)

;;; ========================================================================
;;; COMMANDE AJUSTRAC - Ajuster les lignes de raccordement avec les arcs
;;; ========================================================================

(defun C:AJUSTRAC (/ arcs arc-list arc-ent arc-data arc-center arc-radius
                      lines line-ent line-obj arc-obj int-pts pt1 pt2
                      line-start line-end new-start new-end keep-part)
  
  (vl-load-com)
  
  (princ "\n========================================")
  (princ "\n  AJUSTER LIGNES AVEC ARCS")
  (princ "\n========================================")
  
  ;; Récupérer tous les arcs du calque RACCORDEMENT
  (princ "\nRecherche des arcs sur RACCORDEMENT...")
  (setq arcs (get-entities-by-layer "RACCORDEMENT" "ARC"))
  
  (if (not arcs)
    (princ "\nAucun arc trouvé sur le calque RACCORDEMENT.")
    (progn
      (princ (strcat "\n" (itoa (length arcs)) " arc(s) trouvé(s)"))
      
      ;; Récupérer toutes les lignes du calque RACCORDEMENT
      (setq lines (get-entities-by-layer "RACCORDEMENT" "LINE"))
      
      (if (not lines)
        (princ "\nAucune ligne trouvée sur le calque RACCORDEMENT.")
        (progn
          (princ (strcat "\n" (itoa (length lines)) " ligne(s) trouvée(s)"))
          (princ "\n\nTraitement des arcs...")
          
          ;; Pour chaque arc
          (foreach arc-ent arcs
            (setq arc-data (entget arc-ent))
            (setq arc-center (cdr (assoc 10 arc-data)))
            (setq arc-radius (cdr (assoc 40 arc-data)))
            
            (princ (strcat "\n\nArc centre X=" (rtos (car arc-center) 2 2)))
            
            (setq arc-obj (vlax-ename->vla-object arc-ent))
            
            ;; Pour chaque ligne, chercher intersection avec cet arc
            (foreach line-ent lines
              (setq line-obj (vlax-ename->vla-object line-ent))
              
              ;; Trouver intersections
              (setq int-pts (get-intersection-points-simple arc-obj line-obj))
              
              (if int-pts
                (progn
                  (princ (strcat "\n  Ligne intersectée (" (itoa (length int-pts)) " point(s))"))
                  
                  ;; Récupérer les extrémités de la ligne
                  (setq line-start (cdr (assoc 10 (entget line-ent))))
                  (setq line-end (cdr (assoc 11 (entget line-ent))))
                  
                  ;; Utiliser le premier point d'intersection
                  (setq pt1 (car int-pts))
                  
                  ;; Déterminer quelle partie garder : celle dont l'extrémité a le X le plus GRAND (plus à droite)
                  (princ (strcat " start-X=" (rtos (car line-start) 2 2) " end-X=" (rtos (car line-end) 2 2)))
                  
                  (if (> (car line-start) (car line-end))
                    ;; Start a un X plus grand - garder cette partie
                    (progn
                      (setq new-start pt1
                            new-end line-start)
                      (princ " -> Garde start (X plus grand)")
                    )
                    ;; End a un X plus grand - garder cette partie
                    (progn
                      (setq new-start pt1
                            new-end line-end)
                      (princ " -> Garde end (X plus grand)")
                    )
                  )
                  
                  ;; Supprimer l'ancienne ligne
                  (entdel line-ent)
                  
                  ;; Créer la nouvelle ligne ajustée
                  (entmake (list (cons 0 "LINE")
                                (cons 8 "RACCORDEMENT")
                                (cons 10 new-start)
                                (cons 11 new-end)))
                  
                  (princ " -> Ligne ajustée")
                )
              )
            )
          )
          
          (princ "\n\n========================================")
          (princ "\nTraitement terminé")
          (princ "\n========================================")
        )
      )
    )
  )
  
  (princ)
)

;;; ========================================================================
;;; COMMANDE CREERBOITE - Créer une polyligne englobante
;;; ========================================================================

(defun C:CREERBOITE (/ lines line-haut line-bas pt-haut-droite pt-bas-droite
                        pt1 pt2 pt3 pt4 pt5 y-haut y-bas)
  
  (princ "\n========================================")
  (princ "\n  CRÉER BOÎTE ENGLOBANTE")
  (princ "\n========================================")
  
  ;; Récupérer toutes les lignes du calque RACCORDEMENT
  (setq lines (get-entities-by-layer "RACCORDEMENT" "LINE"))
  
  (if (not lines)
    (princ "\nAucune ligne trouvée sur le calque RACCORDEMENT.")
    (progn
      (princ (strcat "\n" (itoa (length lines)) " ligne(s) trouvée(s)"))
      
      ;; Identifier la ligne haute et la ligne basse (par Y)
      (setq line-haut (get-top-line lines))
      (setq line-bas (get-bottom-line lines))
      
      (if (and line-haut line-bas)
        (progn
          ;; Trouver l'extrémité droite (X max) de chaque ligne
          (setq pt-haut-start (cdr (assoc 10 (entget line-haut))))
          (setq pt-haut-end (cdr (assoc 11 (entget line-haut))))
          (setq pt-bas-start (cdr (assoc 10 (entget line-bas))))
          (setq pt-bas-end (cdr (assoc 11 (entget line-bas))))
          
          ;; Extrémité droite = X le plus grand
          (if (> (car pt-haut-start) (car pt-haut-end))
            (setq pt-haut-droite pt-haut-start)
            (setq pt-haut-droite pt-haut-end)
          )
          
          (if (> (car pt-bas-start) (car pt-bas-end))
            (setq pt-bas-droite pt-bas-start)
            (setq pt-bas-droite pt-bas-end)
          )
          
          (setq y-haut (cadr pt-haut-droite))
          (setq y-bas (cadr pt-bas-droite))
          
          (princ (strcat "\nLigne haute Y=" (rtos y-haut 2 2)))
          (princ (strcat "\nLigne basse Y=" (rtos y-bas 2 2)))
          (princ (strcat "\nPoint bas droite X=" (rtos (car pt-bas-droite) 2 2)))
          
          ;; Construire les 5 points de la polyligne
          ;; Point 1 : Départ = extrémité droite ligne basse
          (setq pt1 pt-bas-droite)
          
          ;; Point 2 : Descendre de 5.16 m
          (setq pt2 (list (car pt1)
                         (- (cadr pt1) 5.16)
                         (caddr pt1)))
          
          ;; Point 3 : Aller à gauche de 10.93 m
          (setq pt3 (list (- (car pt2) 10.93)
                         (cadr pt2)
                         (caddr pt2)))
          
          ;; Point 4 : Remonter de 10 m
          (setq pt4 (list (car pt3)
                         (+ (cadr pt3) 10.0)
                         (caddr pt3)))
          
          ;; Point 5 : Aller à droite de 10.93 m (revenir au X initial)
          (setq pt5 (list (+ (car pt4) 10.93)
                         (cadr pt4)
                         (caddr pt4)))
          
          ;; Point 6 : Descendre de 2.59 m
          (setq pt6 (list (car pt5)
                         (- (cadr pt5) 2.59)
                         (caddr pt5)))
          
          ;; Vérifier la distance entre pt6 et pt1 (point de départ)
          (setq dist-fermeture (distance pt6 pt1))
          (princ (strcat "\n\nDistance de fermeture: " (rtos dist-fermeture 2 3) " m"))
          
          ;; Si la distance est < 1 cm (0.01 m), on considère que c'est fermé
          (if (< dist-fermeture 0.01)
            (progn
              (princ " -> Fermeture automatique (tolérance OK)")
              (setq poly-fermee 1)  ; Polyligne fermée
              (setq nb-sommets 6)
            )
            (progn
              (princ " -> Ajout d'un point de fermeture")
              (setq poly-fermee 1)  ; Polyligne fermée quand même
              (setq nb-sommets 6)   ; On garde 6 points, AutoCAD fermera automatiquement
            )
          )
          
          (princ "\n\nCréation de la polyligne englobante...")
          (princ (strcat "\n  Pt1: " (rtos (car pt1) 2 2) ", " (rtos (cadr pt1) 2 2)))
          (princ (strcat "\n  Pt2: " (rtos (car pt2) 2 2) ", " (rtos (cadr pt2) 2 2)))
          (princ (strcat "\n  Pt3: " (rtos (car pt3) 2 2) ", " (rtos (cadr pt3) 2 2)))
          (princ (strcat "\n  Pt4: " (rtos (car pt4) 2 2) ", " (rtos (cadr pt4) 2 2)))
          (princ (strcat "\n  Pt5: " (rtos (car pt5) 2 2) ", " (rtos (cadr pt5) 2 2)))
          (princ (strcat "\n  Pt6: " (rtos (car pt6) 2 2) ", " (rtos (cadr pt6) 2 2)))
          
          ;; Créer la polyligne FERMÉE
          (entmake (list (cons 0 "LWPOLYLINE")
                        (cons 100 "AcDbEntity")
                        (cons 100 "AcDbPolyline")
                        (cons 8 "RACCORDEMENT")
                        (cons 90 nb-sommets)
                        (cons 70 1)  ; Fermée (1 au lieu de 0)
                        (cons 10 (list (car pt1) (cadr pt1)))
                        (cons 10 (list (car pt2) (cadr pt2)))
                        (cons 10 (list (car pt3) (cadr pt3)))
                        (cons 10 (list (car pt4) (cadr pt4)))
                        (cons 10 (list (car pt5) (cadr pt5)))
                        (cons 10 (list (car pt6) (cadr pt6)))))
          
          (princ "\n\n-> Polyligne englobante créée !")
          (princ "\n========================================")
        )
        (princ "\nErreur: Impossible de trouver les lignes haute et basse")
      )
    )
  )
  
  (princ)
)

;;; ========================================================================
;;; COMMANDE BOITECOMPLETE - Créer une polyligne fermée complète avec lignes + arc + boîte
;;; ========================================================================

(defun C:BOITECOMPLETE (/ lines arcs line-haut line-bas arc-ent
                           pt-haut-gauche pt-haut-droite pt-bas-gauche pt-bas-droite
                           y-haut y-bas all-points pt1 pt2 pt3 pt4 pt5 pt6
                           arc-data arc-center arc-radius arc-start-angle arc-end-angle
                           arc-points angle-step current-angle num-segments i)
  
  (princ "\n========================================")
  (princ "\n  CRÉER BOÎTE COMPLÈTE (Lignes + Arc + Boîte)")
  (princ "\n========================================")
  
  ;; Récupérer lignes et arcs
  (setq lines (get-entities-by-layer "RACCORDEMENT" "LINE"))
  (setq arcs (get-entities-by-layer "RACCORDEMENT" "ARC"))
  
  (if (or (not lines) (not arcs))
    (princ "\nErreur: Lignes ou arcs manquants sur RACCORDEMENT")
    (progn
      (princ (strcat "\n" (itoa (length lines)) " ligne(s), " (itoa (length arcs)) " arc(s)"))
      
      ;; Identifier lignes haute et basse
      (setq line-haut (get-top-line lines))
      (setq line-bas (get-bottom-line lines))
      (setq arc-ent (car arcs))  ; Premier arc
      
      (if (and line-haut line-bas arc-ent)
        (progn
          ;; Récupérer les extrémités des lignes
          (setq pt-haut-start (cdr (assoc 10 (entget line-haut))))
          (setq pt-haut-end (cdr (assoc 11 (entget line-haut))))
          (setq pt-bas-start (cdr (assoc 10 (entget line-bas))))
          (setq pt-bas-end (cdr (assoc 11 (entget line-bas))))
          
          ;; Identifier gauche (X min) et droite (X max)
          (if (< (car pt-haut-start) (car pt-haut-end))
            (progn
              (setq pt-haut-gauche pt-haut-start)
              (setq pt-haut-droite pt-haut-end)
            )
            (progn
              (setq pt-haut-gauche pt-haut-end)
              (setq pt-haut-droite pt-haut-start)
            )
          )
          
          (if (< (car pt-bas-start) (car pt-bas-end))
            (progn
              (setq pt-bas-gauche pt-bas-start)
              (setq pt-bas-droite pt-bas-end)
            )
            (progn
              (setq pt-bas-gauche pt-bas-end)
              (setq pt-bas-droite pt-bas-start)
            )
          )
          
          (setq y-haut (cadr pt-haut-droite))
          (setq y-bas (cadr pt-bas-droite))
          
          ;; Récupérer info arc
          (setq arc-data (entget arc-ent))
          (setq arc-center (cdr (assoc 10 arc-data)))
          (setq arc-radius (cdr (assoc 40 arc-data)))
          (setq arc-start-angle (cdr (assoc 50 arc-data)))
          (setq arc-end-angle (cdr (assoc 51 arc-data)))
          
          ;; Calculer les points de début et fin de l'arc
          (setq arc-start-pt (list (+ (car arc-center) (* arc-radius (cos arc-start-angle)))
                                   (+ (cadr arc-center) (* arc-radius (sin arc-start-angle)))
                                   0.0))
          (setq arc-end-pt (list (+ (car arc-center) (* arc-radius (cos arc-end-angle)))
                                 (+ (cadr arc-center) (* arc-radius (sin arc-end-angle)))
                                 0.0))
          
          ;; Calculer le bulge pour l'arc
          ;; bulge = tan(angle/4) où angle est l'angle balayé par l'arc
          (setq arc-angle (- arc-end-angle arc-start-angle))
          (if (< arc-angle 0)
            (setq arc-angle (+ arc-angle (* 2 pi)))
          )
          ;; tan(x) = sin(x) / cos(x)
          (setq bulge (/ (sin (/ arc-angle 4.0)) (cos (/ arc-angle 4.0))))
          
          (princ (strcat "\n  Arc angle: " (rtos (/ (* arc-angle 180.0) pi) 2 1) "°"))
          (princ (strcat "\n  Bulge: " (rtos bulge 2 3)))
          (princ (strcat "\n  Arc start: " (rtos (car arc-start-pt) 2 2) ", " (rtos (cadr arc-start-pt) 2 2)))
          (princ (strcat "\n  Arc end: " (rtos (car arc-end-pt) 2 2) ", " (rtos (cadr arc-end-pt) 2 2)))
          (princ (strcat "\n  Haut gauche: " (rtos (car pt-haut-gauche) 2 2) ", " (rtos (cadr pt-haut-gauche) 2 2)))
          (princ (strcat "\n  Bas gauche: " (rtos (car pt-bas-gauche) 2 2) ", " (rtos (cadr pt-bas-gauche) 2 2)))
          
          (princ "\n\nConstruction de la polyligne complète...")
          
          ;; Construire la liste de tous les points dans l'ordre
          (setq all-points '())
          
          ;; 1. Ligne basse de gauche à droite
          (setq all-points (append all-points (list (list pt-bas-gauche 0.0))))  ; Point + bulge
          (setq all-points (append all-points (list (list pt-bas-droite 0.0))))
          
          ;; 2. Boîte englobante (partie droite)
          (setq pt1 pt-bas-droite)
          (setq pt2 (list (car pt1) (- (cadr pt1) 5.16) 0.0))
          (setq pt3 (list (- (car pt2) 10.93) (cadr pt2) 0.0))
          (setq pt4 (list (car pt3) (+ (cadr pt3) 10.0) 0.0))
          (setq pt5 (list (+ (car pt4) 10.93) (cadr pt4) 0.0))
          (setq pt6 (list (car pt5) (- (cadr pt5) 2.59) 0.0))
          
          (setq all-points (append all-points (list (list pt2 0.0) (list pt3 0.0) (list pt4 0.0) (list pt5 0.0) (list pt6 0.0))))
          
          ;; 3. Ligne haute de droite à gauche
          (setq all-points (append all-points (list (list pt-haut-droite 0.0))))
          
          ;; Vérifier quel point de l'arc est le plus proche de pt-haut-gauche
          (setq dist-start (distance pt-haut-gauche arc-start-pt))
          (setq dist-end (distance pt-haut-gauche arc-end-pt))
          
          (princ (strcat "\n  Distance haut-gauche -> arc-start: " (rtos dist-start 2 3)))
          (princ (strcat "\n  Distance haut-gauche -> arc-end: " (rtos dist-end 2 3)))
          
          (if (< dist-start dist-end)
            ;; L'arc commence en haut, on le parcourt normalement
            (progn
              (princ "\n  -> Arc dans le sens normal (haut vers bas)")
              (setq all-points (append all-points (list (list arc-start-pt bulge))))
            )
            ;; L'arc finit en haut, on le parcourt à l'envers (bulge négatif)
            (progn
              (princ "\n  -> Arc inversé (haut vers bas avec bulge négatif)")
              (setq all-points (append all-points (list (list arc-end-pt (- bulge)))))
            )
          )
          
          ;; 5. La fermeture de la polyligne rejoindra automatiquement le point 1 (pt-bas-gauche)
          
          (princ (strcat "\n  Total points: " (itoa (length all-points))))
          
          ;; Créer la polyligne fermée avec bulges
          (setq poly-list (list (cons 0 "LWPOLYLINE")
                               (cons 100 "AcDbEntity")
                               (cons 100 "AcDbPolyline")
                               (cons 8 "RACCORDEMENT")
                               (cons 90 (length all-points))
                               (cons 70 1)))  ; Fermée
          
          (foreach pt-bulge all-points
            (setq pt (car pt-bulge))
            (setq blg (cadr pt-bulge))
            (setq poly-list (append poly-list (list (cons 10 (list (car pt) (cadr pt))))))
            (if (/= blg 0.0)
              (setq poly-list (append poly-list (list (cons 42 blg))))
            )
          )
          
          (entmake poly-list)
          
          (princ "\n\n-> Polyligne complète créée !")
          (princ "\n========================================")
        )
        (princ "\nErreur: Impossible de trouver les éléments nécessaires")
      )
    )
  )
  
  (princ)
)

;;; ========================================================================
;;; C:BOITEAUTO2 - Crée les boîtes pour les lignes/arcs EXISTANTS
;;; ========================================================================
(defun C:BOITEAUTO2 ( / *error* old-osmode old-cmdecho 
                       axe-ents intersections int-pt count
                       lines-racc arcs-racc coupes-groupees
                       lines poly-old poly-lw)
  
  (vl-load-com)
  
  ;; Fonction de gestion d'erreur
  (defun *error* (msg)
    (if old-osmode (setvar "OSMODE" old-osmode))
    (if old-cmdecho (setvar "CMDECHO" old-cmdecho))
    (if (not (member msg '("Function cancelled" "quit / exit abort")))
      (princ (strcat "\nErreur: " msg))
    )
    (princ)
  )
  
  ;; Sauvegarde des variables système
  (setq old-osmode (getvar "OSMODE")
        old-cmdecho (getvar "CMDECHO"))
  (setvar "OSMODE" 0)
  (setvar "CMDECHO" 0)
  
  (princ "\n========================================")
  (princ "\n  CRÉATION BOÎTES (lignes existantes)")
  (princ "\n========================================")
  
  ;; Étape 1 : Collecter toutes les lignes du calque DESIGN_AXIS pour trouver les intersections
  (princ "\n\n[1/3] Recherche des intersections DESIGN_AXIS...")
  (setq axe-ents '())
  
  (setq lines (get-entities-by-layer "DESIGN_AXIS" "LINE"))
  (if lines (setq axe-ents (append axe-ents lines)))
  
  (setq poly-old (get-entities-by-layer "DESIGN_AXIS" "POLYLINE"))
  (if poly-old (setq axe-ents (append axe-ents poly-old)))
  
  (setq poly-lw (get-entities-by-layer "DESIGN_AXIS" "LWPOLYLINE"))
  (if poly-lw (setq axe-ents (append axe-ents poly-lw)))
  
  (if (not axe-ents)
    (progn
      (princ "\nAUCUNE ligne trouvée sur DESIGN_AXIS !")
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      (princ)
      (exit)
    )
  )
  
  (setq intersections (find-all-intersections axe-ents))
  (princ (strcat "\n" (itoa (length intersections)) " intersection(s) trouvée(s)."))
  
  ;; Étape 2 : Récupérer les lignes et arcs EXISTANTS sur RACCORDEMENT
  (princ "\n\n[2/3] Récupération des lignes/arcs RACCORDEMENT...")
  (setq lines-racc (get-entities-by-layer "RACCORDEMENT" "LINE"))
  (setq arcs-racc (get-entities-by-layer "RACCORDEMENT" "ARC"))
  
  (if (not lines-racc)
    (setq lines-racc '())
  )
  (if (not arcs-racc)
    (setq arcs-racc '())
  )
  
  (princ (strcat "\n" (itoa (length lines-racc)) " ligne(s), " (itoa (length arcs-racc)) " arc(s)"))
  
  (if (or (= (length lines-racc) 0) (= (length arcs-racc) 0))
    (progn
      (princ "\n\nERREUR: Aucune ligne ou arc sur RACCORDEMENT !")
      (princ "\nVeuillez d'abord exécuter DECALIM et AJUSTRAC")
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      (princ)
      (exit)
    )
  )
  
  ;; Étape 3 : Pour chaque intersection, trouver les lignes/arc proches et créer la boîte
  (princ "\n\n[3/3] Création des boîtes englobantes...")
  (setq count 0)
  
  (foreach int-pt intersections
    (setq count (+ count 1))
    (princ (strcat "\n  Boîte " (itoa count) "/" (itoa (length intersections))))
    
    ;; Trouver les 2 lignes et 1 arc dans un rayon de 8m autour de l'intersection
    (setq local-lines-haut '())
    (setq local-lines-bas '())
    (setq local-arc nil)
    
    ;; Séparateur Y : intersection + 1.5m (milieu entre ligne basse et ligne haute)
    (setq y-separateur (+ (cadr int-pt) 1.5))
    
    ;; Classifier les lignes par rapport au séparateur
    (foreach line-ent lines-racc
      (setq line-data (entget line-ent))
      (setq pt-mid (list (/ (+ (car (cdr (assoc 10 line-data))) 
                              (car (cdr (assoc 11 line-data)))) 2.0)
                        (/ (+ (cadr (cdr (assoc 10 line-data))) 
                              (cadr (cdr (assoc 11 line-data)))) 2.0)
                        0.0))
      
      (if (< (distance int-pt pt-mid) 8.0)
        (progn
          ;; Si Y > séparateur = ligne haute, sinon ligne basse
          (if (> (cadr pt-mid) y-separateur)
            (setq local-lines-haut (append local-lines-haut (list line-ent)))
            (setq local-lines-bas (append local-lines-bas (list line-ent)))
          )
        )
      )
    )
    
    ;; Trouver l'arc proche
    (foreach arc-ent arcs-racc
      (setq arc-data (entget arc-ent))
      (setq arc-center (cdr (assoc 10 arc-data)))
      (if (and (not local-arc) (< (distance int-pt arc-center) 8.0))
        (setq local-arc arc-ent)
      )
    )
    
    ;; Debug: afficher ce qui a été trouvé
    (princ (strcat " [H:" (itoa (length local-lines-haut)) 
                   " B:" (itoa (length local-lines-bas))
                   " A:" (if local-arc "1" "0") "]"))
    
    ;; Créer la boîte si on a bien 1 ligne haute, 1 ligne basse et 1 arc
    (if (and (>= (length local-lines-haut) 1) 
             (>= (length local-lines-bas) 1) 
             local-arc)
      (creer-boite-locale (car local-lines-haut) (car local-lines-bas) local-arc int-pt)
      (princ " -> Éléments manquants")
    )
  )
  
  (princ "\n\n========================================")
  (princ (strcat "\nTraitement terminé : " (itoa count) " boîtes"))
  (princ "\n========================================")
  
  (setvar "OSMODE" old-osmode)
  (setvar "CMDECHO" old-cmdecho)
  (princ)
)

;;; ========================================================================
;;; C:BOITEAUTO - Traite automatiquement toutes les coupes
;;; ========================================================================
(defun C:BOITEAUTO ( / *error* old-osmode old-cmdecho 
                      axe-ents intersections int-pt 
                      limites-group ligne-haut ligne-bas
                      nouvelle-haut nouvelle-bas count success-count
                      lines poly-old poly-lw coupes-data coupe-info arc-ent)
  
  (vl-load-com)
  
  ;; Fonction de gestion d'erreur
  (defun *error* (msg)
    (if old-osmode (setvar "OSMODE" old-osmode))
    (if old-cmdecho (setvar "CMDECHO" old-cmdecho))
    (if (not (member msg '("Function cancelled" "quit / exit abort")))
      (princ (strcat "\nErreur: " msg))
    )
    (princ)
  )
  
  ;; Sauvegarde des variables système
  (setq old-osmode (getvar "OSMODE")
        old-cmdecho (getvar "CMDECHO"))
  (setvar "OSMODE" 0)
  (setvar "CMDECHO" 0)
  
  (princ "\n========================================")
  (princ "\n  TRAITEMENT AUTOMATIQUE DES COUPES")
  (princ "\n========================================")
  
  ;; Création du calque RACCORDEMENT s'il n'existe pas
  (if (not (tblsearch "LAYER" "RACCORDEMENT"))
    (progn
      (command "_.-LAYER" "_N" "RACCORDEMENT" "_C" "6" "RACCORDEMENT" "")
      (princ "\nCalque RACCORDEMENT créé (couleur magenta).")
    )
  )
  
  ;; Étape 1 : Collecter toutes les lignes du calque DESIGN_AXIS
  (princ "\n\n[1/5] Recherche des lignes du calque DESIGN_AXIS...")
  (setq axe-ents '())
  
  (setq lines (get-entities-by-layer "DESIGN_AXIS" "LINE"))
  (if lines
    (progn
      (setq axe-ents (append axe-ents lines))
      (princ (strcat "\n  " (itoa (length lines)) " LINE(s) trouvée(s)"))
    )
  )
  
  (setq poly-old (get-entities-by-layer "DESIGN_AXIS" "POLYLINE"))
  (if poly-old
    (progn
      (setq axe-ents (append axe-ents poly-old))
      (princ (strcat "\n  " (itoa (length poly-old)) " POLYLINE(s) trouvée(s)"))
    )
  )
  
  (setq poly-lw (get-entities-by-layer "DESIGN_AXIS" "LWPOLYLINE"))
  (if poly-lw
    (progn
      (setq axe-ents (append axe-ents poly-lw))
      (princ (strcat "\n  " (itoa (length poly-lw)) " LWPOLYLINE(s) trouvée(s)"))
    )
  )
  
  (if (not axe-ents)
    (progn
      (princ "\nAUCUNE ligne/polyligne trouvée sur le calque DESIGN_AXIS !")
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      (princ)
      (exit)
    )
  )
  
  (princ (strcat "\n  TOTAL : " (itoa (length axe-ents)) " entité(s) trouvée(s)."))
  
  ;; Étape 2 : Trouver toutes les intersections
  (princ "\n\n[2/5] Recherche des intersections...")
  (setq intersections (find-all-intersections axe-ents))
  
  (if (not intersections)
    (progn
      (princ "\nAUCUNE intersection trouvée !")
      (setvar "OSMODE" old-osmode)
      (setvar "CMDECHO" old-cmdecho)
      (princ)
      (exit)
    )
  )
  
  (princ (strcat "\n" (itoa (length intersections)) " point(s) d'intersection trouvé(s)."))
  
  ;; Étape 3 : Pour chaque intersection, créer les lignes de raccordement et les arcs
  (setq count 0
        success-count 0
        coupes-data '())  ; Liste pour stocker les infos de chaque coupe
  (princ "\n\n[3/5] Création des lignes de raccordement et arcs...")
  
  (foreach int-pt intersections
    (setq count (+ count 1))
    (princ (strcat "\n\n  Coupe " (itoa count) "/" (itoa (length intersections)) ": ("
                   (rtos (car int-pt) 2 2) ", "
                   (rtos (cadr int-pt) 2 2) ")"))
    
    (setq limites-group (get-limite-lines-near-point int-pt 10.0))
    
    (if (and limites-group (= (length limites-group) 3))
      (progn
        (setq ligne-haut (get-top-line limites-group)
              ligne-bas (get-bottom-line limites-group))
        
        (if (and ligne-haut ligne-bas)
          (progn
            (setq nouvelle-haut (offset-line ligne-haut 0.20 "RACCORDEMENT"))
            (setq nouvelle-bas (offset-line ligne-bas -0.20 "RACCORDEMENT"))
            
            (if (and nouvelle-haut nouvelle-bas)
              (progn
                (setq arc-ent (create-raccordement-arc int-pt nouvelle-haut nouvelle-bas "RACCORDEMENT"))
                (setq success-count (+ success-count 1))
                
                ;; Stocker les informations de cette coupe
                (setq coupe-info (list int-pt nouvelle-haut nouvelle-bas arc-ent))
                (setq coupes-data (append coupes-data (list coupe-info)))
                
                (princ " -> OK")
              )
              (princ " -> ERREUR décalage")
            )
          )
          (princ " -> ERREUR identification haut/bas")
        )
      )
      (princ (strcat " -> ERREUR: " 
                     (if limites-group (itoa (length limites-group)) "0")
                     " ligne(s) limite (attendu: 3)"))
    )
  )
  
  (princ "\n\n[4/5] Création des boîtes englobantes...")
  
  ;; Pour chaque coupe, créer la boîte complète en isolant les entités locales
  (setq count 0)
  (foreach coupe-info coupes-data
    (setq count (+ count 1))
    (princ (strcat "\n  Boîte " (itoa count) "/" (itoa (length coupes-data))))
    
    ;; Extraire les données de la coupe
    (setq int-pt (nth 0 coupe-info))
    (setq nouvelle-haut (nth 1 coupe-info))
    (setq nouvelle-bas (nth 2 coupe-info))
    (setq arc-ent (nth 3 coupe-info))
    
    ;; Appliquer la logique de BOITECOMPLETE pour cette coupe
    ;; en utilisant uniquement les entités dans un rayon de 5m
    (creer-boite-locale nouvelle-haut nouvelle-bas arc-ent int-pt)
  )
  
  ;; Résumé final
  (princ "\n\n========================================")
  (princ (strcat "\nTraitement terminé:"))
  (princ (strcat "\n  - " (itoa success-count) "/" (itoa (length intersections)) " coupes traitées"))
  (princ (strcat "\n  - " (itoa count) " boîtes englobantes créées"))
  (princ "\n========================================")
  
  (setvar "OSMODE" old-osmode)
  (setvar "CMDECHO" old-cmdecho)
  (princ)
)

;;; ========================================================================
;;; Fonction pour créer boîte locale autour d'une intersection
;;; ========================================================================
(defun creer-boite-locale (line-haut-ent line-bas-ent arc-ent int-pt / 
                            pt-haut-start pt-haut-end pt-bas-start pt-bas-end
                            pt-haut-gauche pt-haut-droite pt-bas-gauche pt-bas-droite
                            haut-data bas-data y-haut y-bas
                            arc-data arc-center arc-radius arc-start-angle arc-end-angle
                            arc-start-pt arc-end-pt arc-angle bulge
                            pt1 pt2 pt3 pt4 pt5 pt6 all-points
                            dist-start dist-end poly-list pt-bulge pt blg)
  
  (if (and line-haut-ent line-bas-ent arc-ent)
    (progn
      ;; Récupérer les données des lignes directement (pas d'ajustement nécessaire)
      (setq haut-data (entget line-haut-ent))
      (setq bas-data (entget line-bas-ent))
      
      (setq pt-haut-start (cdr (assoc 10 haut-data)))
      (setq pt-haut-end (cdr (assoc 11 haut-data)))
      (setq pt-bas-start (cdr (assoc 10 bas-data)))
      (setq pt-bas-end (cdr (assoc 11 bas-data)))
      
      ;; Vérifier que les lignes sont proches de l'intersection
      (if (and (< (distance int-pt pt-haut-start) 10.0)
               (< (distance int-pt pt-bas-start) 10.0))
        (progn
          ;; Identifier gauche/droite selon X
          (if (< (car pt-haut-start) (car pt-haut-end))
            (progn
              (setq pt-haut-gauche pt-haut-start)
              (setq pt-haut-droite pt-haut-end)
            )
            (progn
              (setq pt-haut-gauche pt-haut-end)
              (setq pt-haut-droite pt-haut-start)
            )
          )
          
          (if (< (car pt-bas-start) (car pt-bas-end))
            (progn
              (setq pt-bas-gauche pt-bas-start)
              (setq pt-bas-droite pt-bas-end)
            )
            (progn
              (setq pt-bas-gauche pt-bas-end)
              (setq pt-bas-droite pt-bas-start)
            )
          )
          
          (setq y-haut (cadr pt-haut-droite))
          (setq y-bas (cadr pt-bas-droite))
          
          ;; Récupérer info arc
          (setq arc-data (entget arc-ent))
          (setq arc-center (cdr (assoc 10 arc-data)))
          (setq arc-radius (cdr (assoc 40 arc-data)))
          (setq arc-start-angle (cdr (assoc 50 arc-data)))
          (setq arc-end-angle (cdr (assoc 51 arc-data)))
          
          (setq arc-start-pt (list (+ (car arc-center) (* arc-radius (cos arc-start-angle)))
                                   (+ (cadr arc-center) (* arc-radius (sin arc-start-angle)))
                                   0.0))
          (setq arc-end-pt (list (+ (car arc-center) (* arc-radius (cos arc-end-angle)))
                                 (+ (cadr arc-center) (* arc-radius (sin arc-end-angle)))
                                 0.0))
          
          (setq arc-angle (- arc-end-angle arc-start-angle))
          (if (< arc-angle 0)
            (setq arc-angle (+ arc-angle (* 2 pi)))
          )
          (setq bulge (/ (sin (/ arc-angle 4.0)) (cos (/ arc-angle 4.0))))
          
          ;; Construire la polyligne complète
          (setq all-points '())
          
          ;; 1. Ligne basse
          (setq all-points (append all-points (list (list pt-bas-gauche 0.0))))
          (setq all-points (append all-points (list (list pt-bas-droite 0.0))))
          
          ;; 2. Boîte englobante
          (setq pt1 pt-bas-droite)
          (setq pt2 (list (car pt1) (- (cadr pt1) 5.16) 0.0))
          (setq pt3 (list (- (car pt2) 10.93) (cadr pt2) 0.0))
          (setq pt4 (list (car pt3) (+ (cadr pt3) 10.0) 0.0))
          (setq pt5 (list (+ (car pt4) 10.93) (cadr pt4) 0.0))
          (setq pt6 (list (car pt5) (- (cadr pt5) 2.59) 0.0))
          
          (setq all-points (append all-points (list (list pt2 0.0) (list pt3 0.0) (list pt4 0.0) (list pt5 0.0) (list pt6 0.0))))
          
          ;; 3. Ligne haute
          (setq all-points (append all-points (list (list pt-haut-droite 0.0))))
          
          ;; 4. Arc avec bulge
          (setq dist-start (distance pt-haut-gauche arc-start-pt))
          (setq dist-end (distance pt-haut-gauche arc-end-pt))
          
          (if (< dist-start dist-end)
            (setq all-points (append all-points (list (list arc-start-pt bulge))))
            (setq all-points (append all-points (list (list arc-end-pt (- bulge)))))
          )
          
          ;; Créer la polyligne fermée
          (setq poly-list (list (cons 0 "LWPOLYLINE")
                               (cons 100 "AcDbEntity")
                               (cons 100 "AcDbPolyline")
                               (cons 8 "RACCORDEMENT")
                               (cons 90 (length all-points))
                               (cons 70 1)))
          
          (foreach pt-bulge all-points
            (setq pt (car pt-bulge))
            (setq blg (cadr pt-bulge))
            (setq poly-list (append poly-list (list (cons 10 (list (car pt) (cadr pt))))))
            (if (/= blg 0.0)
              (setq poly-list (append poly-list (list (cons 42 blg))))
            )
          )
          
          (entmake poly-list)
          (princ " -> OK")
        )
        (princ " -> Lignes trop éloignées de l'intersection")
      )
    )
    (princ " -> Données manquantes")
  )
)

;;; ========================================================================
;;; Fonction auxiliaire pour ajuster UNE ligne avec UN arc (version locale)
;;; ========================================================================
(defun ajuster-ligne-avec-arc-local (line-ent arc-ent / 
                                      intersections-pts int-pt line-data 
                                      pt-start pt-end x-start x-end new-line)
  
  (if (and line-ent arc-ent)
    (progn
      ;; Chercher intersection entre cette ligne et cet arc
      (setq intersections-pts (get-intersection-points-simple arc-ent line-ent))
      
      (if intersections-pts
        (progn
          ;; Prendre le premier point d'intersection
          (setq int-pt (car intersections-pts))
          
          ;; Récupérer les extrémités de la ligne
          (setq line-data (entget line-ent))
          (setq pt-start (cdr (assoc 10 line-data)))
          (setq pt-end (cdr (assoc 11 line-data)))
          
          ;; Récupérer les coordonnées X
          (setq x-start (car pt-start))
          (setq x-end (car pt-end))
          
          ;; Garder la portion vers la DROITE (X le plus grand)
          ;; On va de l'intersection vers l'extrémité la plus à droite
          (if (> x-start x-end)
            ;; start est plus à droite, on va de int-pt vers start
            (progn
              (entdel line-ent)
              (entmake (list (cons 0 "LINE")
                           (cons 8 "RACCORDEMENT")
                           (cons 10 int-pt)
                           (cons 11 pt-start)))
              (entlast)
            )
            ;; end est plus à droite, on va de int-pt vers end
            (progn
              (entdel line-ent)
              (entmake (list (cons 0 "LINE")
                           (cons 8 "RACCORDEMENT")
                           (cons 10 int-pt)
                           (cons 11 pt-end)))
              (entlast)
            )
          )
        )
        ;; Pas d'intersection, retourner la ligne originale
        line-ent
      )
    )
    nil
  )
)

;;; ========================================================================
;;; Fonction auxiliaire pour ajuster UNE ligne avec UN arc
;;; ========================================================================
(defun ajuster-ligne-avec-arc (line-ent arc-ent / 
                                 intersections-pts int-pt line-data 
                                 pt-start pt-end new-start new-end
                                 x-start x-end x-inter new-line)
  
  (if (and line-ent arc-ent)
    (progn
      ;; Chercher intersection entre cette ligne et cet arc
      (setq intersections-pts (get-intersection-points-simple arc-ent line-ent))
      
      (if intersections-pts
        (progn
          ;; Prendre le premier point d'intersection
          (setq int-pt (car intersections-pts))
          
          ;; Récupérer les extrémités de la ligne
          (setq line-data (entget line-ent))
          (setq pt-start (cdr (assoc 10 line-data)))
          (setq pt-end (cdr (assoc 11 line-data)))
          
          ;; Récupérer les coordonnées X
          (setq x-start (car pt-start))
          (setq x-end (car pt-end))
          (setq x-inter (car int-pt))
          
          ;; Garder la portion qui va de l'arc vers la DROITE (X le plus grand)
          ;; Si start est à droite de l'intersection, garder start
          ;; Si end est à droite de l'intersection, garder end
          (if (> x-start x-end)
            ;; start a le X le plus grand
            (setq new-start int-pt
                  new-end pt-start)
            ;; end a le X le plus grand
            (setq new-start int-pt
                  new-end pt-end)
          )
          
          ;; Supprimer l'ancienne ligne
          (entdel line-ent)
          
          ;; Créer la nouvelle ligne ajustée
          (entmake (list (cons 0 "LINE")
                       (cons 8 "RACCORDEMENT")
                       (cons 10 new-start)
                       (cons 11 new-end)))
          
          ;; Retourner la nouvelle entité
          (entlast)
        )
        ;; Pas d'intersection, retourner la ligne originale
        line-ent
      )
    )
    nil
  )
)

;;; ========================================================================
;;; Fonction auxiliaire pour créer boîte complète avec lignes données
;;; ========================================================================
(defun creer-boite-complete-avec-lignes (line-haut-ent line-bas-ent arc-ent / 
                                          haut-data bas-data pt-haut-start pt-haut-end
                                          pt-bas-start pt-bas-end pt-haut-droite pt-haut-gauche
                                          pt-bas-droite pt-bas-gauche y-haut y-bas
                                          arc-data arc-center arc-radius arc-start-angle arc-end-angle
                                          arc-start-pt arc-end-pt arc-angle bulge
                                          pt1 pt2 pt3 pt4 pt5 pt6 all-points
                                          dist-start dist-end poly-list pt-bulge pt blg)
  
  (if (and line-haut-ent line-bas-ent arc-ent)
    (progn
      ;; Récupérer les données des lignes
      (setq haut-data (entget line-haut-ent))
      (setq bas-data (entget line-bas-ent))
      
      (setq pt-haut-start (cdr (assoc 10 haut-data)))
      (setq pt-haut-end (cdr (assoc 11 haut-data)))
      (setq pt-bas-start (cdr (assoc 10 bas-data)))
      (setq pt-bas-end (cdr (assoc 11 bas-data)))
      
      ;; Identifier gauche/droite selon X
      (if (< (car pt-haut-start) (car pt-haut-end))
        (progn
          (setq pt-haut-gauche pt-haut-start)
          (setq pt-haut-droite pt-haut-end)
        )
        (progn
          (setq pt-haut-gauche pt-haut-end)
          (setq pt-haut-droite pt-haut-start)
        )
      )
      
      (if (< (car pt-bas-start) (car pt-bas-end))
        (progn
          (setq pt-bas-gauche pt-bas-start)
          (setq pt-bas-droite pt-bas-end)
        )
        (progn
          (setq pt-bas-gauche pt-bas-end)
          (setq pt-bas-droite pt-bas-start)
        )
      )
      
      (setq y-haut (cadr pt-haut-droite))
      (setq y-bas (cadr pt-bas-droite))
      
      ;; Récupérer info arc
      (setq arc-data (entget arc-ent))
      (setq arc-center (cdr (assoc 10 arc-data)))
      (setq arc-radius (cdr (assoc 40 arc-data)))
      (setq arc-start-angle (cdr (assoc 50 arc-data)))
      (setq arc-end-angle (cdr (assoc 51 arc-data)))
      
      (setq arc-start-pt (list (+ (car arc-center) (* arc-radius (cos arc-start-angle)))
                               (+ (cadr arc-center) (* arc-radius (sin arc-start-angle)))
                               0.0))
      (setq arc-end-pt (list (+ (car arc-center) (* arc-radius (cos arc-end-angle)))
                             (+ (cadr arc-center) (* arc-radius (sin arc-end-angle)))
                             0.0))
      
      (setq arc-angle (- arc-end-angle arc-start-angle))
      (if (< arc-angle 0)
        (setq arc-angle (+ arc-angle (* 2 pi)))
      )
      (setq bulge (/ (sin (/ arc-angle 4.0)) (cos (/ arc-angle 4.0))))
      
      ;; Construire la polyligne complète
      (setq all-points '())
      
      ;; 1. Ligne basse
      (setq all-points (append all-points (list (list pt-bas-gauche 0.0))))
      (setq all-points (append all-points (list (list pt-bas-droite 0.0))))
      
      ;; 2. Boîte englobante
      (setq pt1 pt-bas-droite)
      (setq pt2 (list (car pt1) (- (cadr pt1) 5.16) 0.0))
      (setq pt3 (list (- (car pt2) 10.93) (cadr pt2) 0.0))
      (setq pt4 (list (car pt3) (+ (cadr pt3) 10.0) 0.0))
      (setq pt5 (list (+ (car pt4) 10.93) (cadr pt4) 0.0))
      (setq pt6 (list (car pt5) (- (cadr pt5) 2.59) 0.0))
      
      (setq all-points (append all-points (list (list pt2 0.0) (list pt3 0.0) (list pt4 0.0) (list pt5 0.0) (list pt6 0.0))))
      
      ;; 3. Ligne haute
      (setq all-points (append all-points (list (list pt-haut-droite 0.0))))
      
      ;; 4. Arc avec bulge
      (setq dist-start (distance pt-haut-gauche arc-start-pt))
      (setq dist-end (distance pt-haut-gauche arc-end-pt))
      
      (if (< dist-start dist-end)
        (setq all-points (append all-points (list (list arc-start-pt bulge))))
        (setq all-points (append all-points (list (list arc-end-pt (- bulge)))))
      )
      
      ;; Créer la polyligne fermée
      (setq poly-list (list (cons 0 "LWPOLYLINE")
                           (cons 100 "AcDbEntity")
                           (cons 100 "AcDbPolyline")
                           (cons 8 "RACCORDEMENT")
                           (cons 90 (length all-points))
                           (cons 70 1)))
      
      (foreach pt-bulge all-points
        (setq pt (car pt-bulge))
        (setq blg (cadr pt-bulge))
        (setq poly-list (append poly-list (list (cons 10 (list (car pt) (cadr pt))))))
        (if (/= blg 0.0)
          (setq poly-list (append poly-list (list (cons 42 blg))))
        )
      )
      
      (entmake poly-list)
      (princ " -> OK")
    )
    (princ " -> Données manquantes")
  )
)

;;; ========================================================================
;;; Fonction auxiliaire pour créer boîte complète (appelée par BOITEAUTO)
;;; ========================================================================
(defun creer-boite-complete-pour-intersection (int-pt / lines-haut lines-bas arcs-list
                                                line-haut-ent line-bas-ent arc-ent
                                                haut-data bas-data pt-haut-start pt-haut-end
                                                pt-bas-start pt-bas-end pt-haut-droite pt-haut-gauche
                                                pt-bas-droite pt-bas-gauche y-haut y-bas
                                                arc-data arc-center arc-radius arc-start-angle arc-end-angle
                                                arc-start-pt arc-end-pt arc-angle bulge
                                                pt1 pt2 pt3 pt4 pt5 pt6 all-points
                                                dist-start dist-end poly-list pt-bulge pt blg)
  
  ;; Trouver les lignes de raccordement près de ce point d'intersection
  (setq lines-haut '()
        lines-bas '())
  
  ;; Récupérer toutes les lignes RACCORDEMENT
  (setq all-lines (get-entities-by-layer "RACCORDEMENT" "LINE"))
  
  (if all-lines
    (foreach line-ent all-lines
      (setq line-data (entget line-ent))
      (setq pt-mid (list (/ (+ (car (cdr (assoc 10 line-data))) 
                              (car (cdr (assoc 11 line-data)))) 2.0)
                        (/ (+ (cadr (cdr (assoc 10 line-data))) 
                              (cadr (cdr (assoc 11 line-data)))) 2.0)
                        0.0))
      
      ;; Si la ligne est proche de l'intersection (dans un rayon de 3m)
      (if (< (distance int-pt pt-mid) 3.0)
        (progn
          ;; Classifier selon Y
          (if (> (cadr pt-mid) (cadr int-pt))
            (setq lines-haut (append lines-haut (list line-ent)))
            (setq lines-bas (append lines-bas (list line-ent)))
          )
        )
      )
    )
  )
  
  ;; Vérifier qu'on a bien une ligne haute et une ligne basse
  (if (and lines-haut lines-bas (>= (length lines-haut) 1) (>= (length lines-bas) 1))
    (progn
      (setq line-haut-ent (car lines-haut))
      (setq line-bas-ent (car lines-bas))
      
      ;; Récupérer les arcs
      (setq arcs-list (get-entities-by-layer "RACCORDEMENT" "ARC"))
      
      (if (and arcs-list (>= (length arcs-list) 1))
        (progn
          ;; Prendre le premier arc proche (simplification: on suppose 1 arc par coupe)
          (setq arc-ent nil)
          (foreach test-arc arcs-list
            (setq arc-data-test (entget test-arc))
            (setq arc-center-test (cdr (assoc 10 arc-data-test)))
            (if (and (not arc-ent) (< (distance int-pt arc-center-test) 10.0))
              (setq arc-ent test-arc)
            )
          )
          
          (if arc-ent
            (progn
              ;; Récupérer les données des lignes
              (setq haut-data (entget line-haut-ent))
              (setq bas-data (entget line-bas-ent))
              
              (setq pt-haut-start (cdr (assoc 10 haut-data)))
              (setq pt-haut-end (cdr (assoc 11 haut-data)))
              (setq pt-bas-start (cdr (assoc 10 bas-data)))
              (setq pt-bas-end (cdr (assoc 11 bas-data)))
              
              ;; Identifier gauche/droite selon X
              (if (< (car pt-haut-start) (car pt-haut-end))
                (progn
                  (setq pt-haut-gauche pt-haut-start)
                  (setq pt-haut-droite pt-haut-end)
                )
                (progn
                  (setq pt-haut-gauche pt-haut-end)
                  (setq pt-haut-droite pt-haut-start)
                )
              )
              
              (if (< (car pt-bas-start) (car pt-bas-end))
                (progn
                  (setq pt-bas-gauche pt-bas-start)
                  (setq pt-bas-droite pt-bas-end)
                )
                (progn
                  (setq pt-bas-gauche pt-bas-end)
                  (setq pt-bas-droite pt-bas-start)
                )
              )
              
              (setq y-haut (cadr pt-haut-droite))
              (setq y-bas (cadr pt-bas-droite))
              
              ;; Récupérer info arc
              (setq arc-data (entget arc-ent))
              (setq arc-center (cdr (assoc 10 arc-data)))
              (setq arc-radius (cdr (assoc 40 arc-data)))
              (setq arc-start-angle (cdr (assoc 50 arc-data)))
              (setq arc-end-angle (cdr (assoc 51 arc-data)))
              
              (setq arc-start-pt (list (+ (car arc-center) (* arc-radius (cos arc-start-angle)))
                                       (+ (cadr arc-center) (* arc-radius (sin arc-start-angle)))
                                       0.0))
              (setq arc-end-pt (list (+ (car arc-center) (* arc-radius (cos arc-end-angle)))
                                     (+ (cadr arc-center) (* arc-radius (sin arc-end-angle)))
                                     0.0))
              
              (setq arc-angle (- arc-end-angle arc-start-angle))
              (if (< arc-angle 0)
                (setq arc-angle (+ arc-angle (* 2 pi)))
              )
              (setq bulge (/ (sin (/ arc-angle 4.0)) (cos (/ arc-angle 4.0))))
              
              ;; Construire la polyligne complète
              (setq all-points '())
              
              ;; 1. Ligne basse
              (setq all-points (append all-points (list (list pt-bas-gauche 0.0))))
              (setq all-points (append all-points (list (list pt-bas-droite 0.0))))
              
              ;; 2. Boîte englobante
              (setq pt1 pt-bas-droite)
              (setq pt2 (list (car pt1) (- (cadr pt1) 5.16) 0.0))
              (setq pt3 (list (- (car pt2) 10.93) (cadr pt2) 0.0))
              (setq pt4 (list (car pt3) (+ (cadr pt3) 10.0) 0.0))
              (setq pt5 (list (+ (car pt4) 10.93) (cadr pt4) 0.0))
              (setq pt6 (list (car pt5) (- (cadr pt5) 2.59) 0.0))
              
              (setq all-points (append all-points (list (list pt2 0.0) (list pt3 0.0) (list pt4 0.0) (list pt5 0.0) (list pt6 0.0))))
              
              ;; 3. Ligne haute
              (setq all-points (append all-points (list (list pt-haut-droite 0.0))))
              
              ;; 4. Arc avec bulge
              (setq dist-start (distance pt-haut-gauche arc-start-pt))
              (setq dist-end (distance pt-haut-gauche arc-end-pt))
              
              (if (< dist-start dist-end)
                (setq all-points (append all-points (list (list arc-start-pt bulge))))
                (setq all-points (append all-points (list (list arc-end-pt (- bulge)))))
              )
              
              ;; Créer la polyligne fermée
              (setq poly-list (list (cons 0 "LWPOLYLINE")
                                   (cons 100 "AcDbEntity")
                                   (cons 100 "AcDbPolyline")
                                   (cons 8 "RACCORDEMENT")
                                   (cons 90 (length all-points))
                                   (cons 70 1)))
              
              (foreach pt-bulge all-points
                (setq pt (car pt-bulge))
                (setq blg (cadr pt-bulge))
                (setq poly-list (append poly-list (list (cons 10 (list (car pt) (cadr pt))))))
                (if (/= blg 0.0)
                  (setq poly-list (append poly-list (list (cons 42 blg))))
                )
              )
              
              (entmake poly-list)
              (princ " -> OK")
            )
            (princ " -> Arc non trouvé")
          )
        )
        (princ " -> Arcs non trouvés")
      )
    )
    (princ " -> Lignes haut/bas non trouvées")
  )
)

;;; Fin du fichier
