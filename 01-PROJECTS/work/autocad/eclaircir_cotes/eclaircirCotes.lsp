;; filepath: c:\data\20-DEVELOPPEMENT\AutoLISP\eclaircir cotes\eclaircirCotes.lsp
;;; ECLAIRCIRCOTES.LSP
;;; Éclaircit les cotations de courbes de niveau en masquant les textes qui se chevauchent
;;; Version 5.1 - Correction du calcul de distance

(vl-load-com)

;; Variables globales
(setq *calque-source* "cotations cn")          ; Calque des cotations originales
(setq *calque-masque* "cotations cn_masquees") ; Calque pour les textes masqués
(setq *distance-min* 2.0)                      ; Distance minimale en multiples de hauteur de texte

;; Fonction pour obtenir le point central d'un texte
(defun get-text-center (ent / data pt height angle width txt)
  (setq data (entget ent))
  (setq pt (cdr (assoc 10 data)))      ; Point d'insertion
  (setq height (cdr (assoc 40 data)))   ; Hauteur
  (setq angle (cdr (assoc 50 data)))    ; Angle de rotation
  (setq txt (cdr (assoc 1 data)))       ; Texte
  
  ;; Estimer la largeur
  (setq width (* height 0.6 (strlen txt)))
  
  ;; Calculer le centre approximatif
  (list
    (+ (car pt) (* 0.5 width (cos angle)))
    (+ (cadr pt) (* 0.5 width (sin angle)))
    (caddr pt)
  )
)

;; Fonction pour calculer la distance entre deux points
(defun distance-2d (pt1 pt2)
  (sqrt (+ (expt (- (car pt2) (car pt1)) 2)
           (expt (- (cadr pt2) (cadr pt1)) 2)))
)

;; Fonction pour créer le calque de masquage
(defun create-mask-layer ()
  (if (not (tblsearch "LAYER" *calque-masque*))
    (progn
      (command "_-LAYER" "_N" *calque-masque* 
               "_C" "8" *calque-masque*     
               "_OFF" *calque-masque*        
               "")
      (princ (strcat "\nCalque '" *calque-masque* "' créé et désactivé."))
    )
  )
)

;; Fonction principale simplifiée
(defun c:ECLAIRCIR ( / ss i j textes-data txt1 txt2 center1 center2 dist height1 height2 
                       min-dist to-mask processed total-masques ent data avg-height)
  
  (princ "\n=== ÉCLAIRCISSEMENT DES COTATIONS V5.1 ===")
  
  ;; Créer le calque de masquage
  (create-mask-layer)
  
  ;; Sélectionner tous les textes
  (princ "\nRecherche des textes...")
  (setq ss (ssget "X" (list '(0 . "TEXT") (cons 8 *calque-source*))))
  
  (if (not ss)
    (progn
      (princ "\nAucun texte trouvé")
      (exit)
    )
  )
  
  (princ (strcat "\n" (itoa (sslength ss)) " textes trouvés."))
  
  ;; Collecter les données des textes
  (princ "\nAnalyse des textes...")
  (setq textes-data '())
  (setq i 0)
  
  (repeat (sslength ss)
    (setq ent (ssname ss i))
    (setq data (entget ent))
    (setq center1 (get-text-center ent))
    (setq height1 (cdr (assoc 40 data)))
    (setq txt1 (cdr (assoc 1 data)))
    
    (setq textes-data (cons (list ent center1 height1 txt1) textes-data))
    (setq i (1+ i))
  )
  
  ;; Trier par altitude décroissante (garder les plus hautes)
  (setq textes-data (vl-sort textes-data 
                    '(lambda (a b) (> (atof (nth 3 a)) (atof (nth 3 b))))))
  
  ;; Identifier les textes à masquer
  (princ "\nRecherche des chevauchements...")
  (setq to-mask '())
  (setq processed '())
  
  (setq i 0)
  (repeat (1- (length textes-data))
    (setq txt1 (nth i textes-data))
    
    ;; Si ce texte n'est pas déjà marqué pour masquage
    (if (not (member (car txt1) to-mask))
      (progn
        (setq j (1+ i))
        (repeat (- (length textes-data) j)
          (setq txt2 (nth j textes-data))
          
          ;; Si txt2 n'est pas déjà marqué pour masquage
          (if (not (member (car txt2) to-mask))
            (progn
              ;; Calculer la distance entre les centres
              (setq center1 (cadr txt1))
              (setq center2 (cadr txt2))
              (setq dist (distance-2d center1 center2))
              
              ;; Distance minimale basée sur la hauteur moyenne des textes
              (setq height1 (caddr txt1))
              (setq height2 (caddr txt2))
              (setq avg-height (/ (+ height1 height2) 2.0))
              (setq min-dist (* *distance-min* avg-height))  ; CORRECTION ICI
              
              ;; Si trop proches, marquer le texte avec l'altitude la plus basse
              (if (< dist min-dist)
                (progn
                  (setq to-mask (cons (car txt2) to-mask))
                  ;; Debug - afficher quelques exemples
                  (if (< (length to-mask) 5)
                    (princ (strcat "\n  Masque " (nth 3 txt2) " (trop proche de " (nth 3 txt1) 
                                   ", dist=" (rtos dist 2 2) " < " (rtos min-dist 2 2) ")"))
                  )
                )
              )
            )
          )
          (setq j (1+ j))
        )
      )
    )
    (setq i (1+ i))
    
    ;; Afficher progression
    (if (= (rem i 50) 0)
      (princ (strcat "\r" (itoa i) "/" (itoa (1- (length textes-data))) " textes traités..."))
    )
  )
  
  ;; Masquer les textes identifiés
  (princ "\nMasquage des textes...")
  (setq total-masques 0)
  
  (foreach ent to-mask
    (entmod (subst (cons 8 *calque-masque*) 
                  (assoc 8 (entget ent))
                  (entget ent)))
    (setq total-masques (1+ total-masques))
  )
  
  ;; Rapport final
  (princ "\n\n=== RÉSULTATS ===")
  (princ (strcat "\n" (itoa total-masques) " textes masqués"))
  (princ (strcat "\n" (itoa (- (sslength ss) total-masques)) " textes visibles"))
  
  (command "_REGEN")
  (princ "\n\nUtilisez RESTAURER pour réafficher tous les textes.")
  (princ)
)

;; Version par zone
(defun c:ECLAIRCIR-ZONE ( / ss)
  (princ "\n=== ÉCLAIRCISSEMENT PAR ZONE ===")
  (princ "\nSélectionnez les textes à traiter : ")
  
  (setq ss (ssget (list '(0 . "TEXT") (cons 8 *calque-source*))))
  
  (if ss
    (progn
      (princ (strcat "\n" (itoa (sslength ss)) " textes sélectionnés."))
      (eclaircir-selection ss)
    )
    (princ "\nAucun texte sélectionné.")
  )
  (princ)
)

;; Traiter une sélection
(defun eclaircir-selection (ss / i j textes-data txt1 txt2 center1 center2 dist height1 height2 
                                min-dist to-mask total-masques ent data avg-height)
  
  (create-mask-layer)
  
  ;; Collecter les données
  (setq textes-data '())
  (setq i 0)
  
  (repeat (sslength ss)
    (setq ent (ssname ss i))
    (setq data (entget ent))
    (setq center1 (get-text-center ent))
    (setq height1 (cdr (assoc 40 data)))
    (setq txt1 (cdr (assoc 1 data)))
    
    (setq textes-data (cons (list ent center1 height1 txt1) textes-data))
    (setq i (1+ i))
  )
  
  ;; Trier par altitude
  (setq textes-data (vl-sort textes-data 
                    '(lambda (a b) (> (atof (nth 3 a)) (atof (nth 3 b))))))
  
  ;; Identifier les textes à masquer
  (setq to-mask '())
  
  (setq i 0)
  (repeat (1- (length textes-data))
    (setq txt1 (nth i textes-data))
    
    (if (not (member (car txt1) to-mask))
      (progn
        (setq j (1+ i))
        (repeat (- (length textes-data) j)
          (setq txt2 (nth j textes-data))
          
          (if (not (member (car txt2) to-mask))
            (progn
              (setq dist (distance-2d (cadr txt1) (cadr txt2)))
              (setq avg-height (/ (+ (caddr txt1) (caddr txt2)) 2.0))
              (setq min-dist (* *distance-min* avg-height))  ; CORRECTION ICI AUSSI
              
              (if (< dist min-dist)
                (setq to-mask (cons (car txt2) to-mask))
              )
            )
          )
          (setq j (1+ j))
        )
      )
    )
    (setq i (1+ i))
  )
  
  ;; Masquer
  (setq total-masques 0)
  (foreach ent to-mask
    (entmod (subst (cons 8 *calque-masque*) 
                  (assoc 8 (entget ent))
                  (entget ent)))
    (setq total-masques (1+ total-masques))
  )
  
  (princ (strcat "\n" (itoa total-masques) " textes masqués."))
  (command "_REGEN")
)

;; Ajuster la distance
(defun c:ECLAIRCIR-DISTANCE ( / nouvelle-distance)
  (princ (strcat "\nDistance minimale actuelle : " (rtos *distance-min* 2 2)))
  (princ "\n  1.0 = Très serré (masque beaucoup)")
  (princ "\n  2.0 = Normal") 
  (princ "\n  4.0 = Espacé (masque peu)")
  (princ "\n  6.0 = Très espacé")
  (setq nouvelle-distance (getreal "\nNouvelle distance (1.0 à 10.0) <2.0> : "))
  (if nouvelle-distance
    (setq *distance-min* nouvelle-distance)
  )
  (princ (strcat "\nDistance minimale : " (rtos *distance-min* 2 2) " x hauteur du texte"))
  (princ)
)

;; Restaurer
(defun c:RESTAURER ( / ss i ent)
  (princ "\n=== RESTAURATION DES COTATIONS ===")
  
  (setq ss (ssget "X" (list '(0 . "TEXT") (cons 8 *calque-masque*))))

  (if ss
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (entmod (subst (cons 8 *calque-source*) 
                      (assoc 8 (entget ent))
                      (entget ent)))
        (setq i (1+ i))
      )
      (princ (strcat "\n" (itoa (sslength ss)) " textes restaurés."))
      (command "_-LAYER" "_ON" *calque-source* "")
    )
    (princ "\nAucun texte à restaurer.")
  )
  
  (command "_REGEN")
  (princ)
)

;; Message de chargement
(princ "\n")
(princ "\n=== ÉCLAIRCIR COTATIONS V5.1 ===")
(princ "\nVersion simplifiée et robuste")
(princ "\n")
(princ "\nCommandes :")
(princ "\n  ECLAIRCIR          - Traite tous les textes")
(princ "\n  ECLAIRCIR-ZONE     - Traite une zone sélectionnée")
(princ "\n  ECLAIRCIR-DISTANCE - Ajuste la distance (défaut: 2.0)")
(princ "\n  RESTAURER          - Restaure tous les textes")
(princ "\n")
(princ)