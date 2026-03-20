;;; CALAGE3D-COUPES.LSP
;;; Calage automatique de coupes 3D par points de référence
;;; Associe les points du calque _CALAGE_PT aux points du calque _CALAGE_3D_CI

;; ============================================
;; FONCTIONS UTILITAIRES GLOBALES
;; ============================================

;; Fonction pour extraire le matricule d'un bloc
(defun get-matricule (bloc / att mat)
  (setq mat nil)
  (foreach att (vlax-invoke bloc 'GetAttributes)
    (if (= (vla-get-TagString att) "MAT")
      (setq mat (vla-get-TextString att))
    )
  )
  mat
)

;; Fonction pour obtenir le point d'insertion d'un bloc
(defun get-point (bloc)
  (vlax-get bloc 'InsertionPoint)
)

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

;; Fonction améliorée pour sélectionner les objets de la coupe
;; EXCLUT les points du calque _CALAGE_PT pour ne pas les déplacer
;; Fonction améliorée pour sélectionner les objets de la coupe
;; EXCLUT les points du calque _CALAGE_PT pour ne pas les déplacer
(defun select-in-bounds (pt-list / xmin xmax ymin ymax pts xcenter ycenter marge ss-filter ss ss-filtered i ent entdata layer pt-a item)
  (setq pts (mapcar 'cadr pt-list))
  (setq xmin (apply 'min (mapcar 'car pts)))
  (setq xmax (apply 'max (mapcar 'car pts)))
  (setq ymin (apply 'min (mapcar 'cadr pts)))
  (setq ymax (apply 'max (mapcar 'cadr pts)))
  
  ;; LOGIQUE OPTIMISÉE : Zone 19.6x20m centrée sur le point A
  ;; Trouver le point A (origine/centre de la coupe)
  (setq pt-a nil)
  (foreach item pt-list
    (if (wcmatch (car item) "A_*")
      (setq pt-a (cadr item))
    )
  )
  
  (if pt-a
    (progn
      ;; Zone pour ligne 1 : capture tous les objets entre les points de calage
      ;; Les points A,B,C sont automatiquement exclus par filtrage de calque
      ;; Zone de -9.8m à +9.8m pour éviter les objets des coupes voisines
      (setq xmin (- (car pt-a) 9.8))   ; 9.8m à gauche (marge sécurité)
      (setq xmax (+ (car pt-a) 9.8))   ; 9.8m à droite (marge sécurité)  
      (setq ymin (- (cadr pt-a) 10.0)) ; 10m en bas (coupe complète)
      (setq ymax (+ (cadr pt-a) 10.0)) ; 10m en haut (coupe complète)
    )
    (progn
      ;; Fallback : extension importante si pas de point A
      (setq xcenter (/ (+ xmin xmax) 2.0))
      (setq ycenter (/ (+ ymin ymax) 2.0))
      (setq marge (* 0.5 (max (- xmax xmin) (- ymax ymin))))
      (setq xmin (- xmin marge))
      (setq xmax (+ xmax marge))
      (setq ymin (- ymin marge))
      (setq ymax (+ ymax marge))
    )
  )
  
  ;; Sélectionner TOUS les objets puis filtrer manuellement
  (setq ss (ssget "_W" (list xmin ymin) (list xmax ymax)))
  
  ;; Filtrer pour exclure les points de calage
  (if ss
    (progn
      (setq ss-filtered (ssadd))
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq entdata (entget ent))
        (setq layer (cdr (assoc 8 entdata)))
        
        ;; Exclure les calques de points de calage
        (if (not (or (equal layer "_CALAGE_PT")
                     (equal layer "_CALAGE_3D_CI")))
          (ssadd ent ss-filtered)
        )
        (setq i (1+ i))
      )
      ss-filtered
    )
    nil
  )
)

;; Fonction de diagnostic pour la sélection
(defun select-in-bounds-debug (pt-list pm-nom / xmin xmax ymin ymax pts xcenter ycenter marge ss-filter ss largeur hauteur ss-filtered i ent entdata layer pt-a item)
  (setq pts (mapcar 'cadr pt-list))
  (setq xmin (apply 'min (mapcar 'car pts)))
  (setq xmax (apply 'max (mapcar 'car pts)))
  (setq ymin (apply 'min (mapcar 'cadr pts)))
  (setq ymax (apply 'max (mapcar 'cadr pts)))
  
  ;; Afficher les coordonnées des points de référence
  (princ (strcat "\n  Points de référence PM " pm-nom ":"))
  (foreach item pt-list
    (setq pt (cadr item))
    (princ (strcat "\n    " (car item) ": X=" (rtos (car pt) 2 2) " Y=" (rtos (cadr pt) 2 2)))
  )
  
  ;; Afficher la zone initiale
  (princ "\n  Zone initiale calculée:")
  (princ (strcat "\n    X: " (rtos xmin 2 2) " à " (rtos xmax 2 2)))
  (princ (strcat "\n    Y: " (rtos ymin 2 2) " à " (rtos ymax 2 2)))
  
  ;; LOGIQUE OPTIMISÉE : Zone 19.6x20m centrée sur le point A
  ;; Trouver le point A (origine/centre de la coupe)
  (setq pt-a nil)
  (foreach item pt-list
    (if (wcmatch (car item) "A_*")
      (setq pt-a (cadr item))
    )
  )
  
  (if pt-a
    (progn
      ;; Zone pour ligne 1 : capture tous les objets entre les points de calage
      ;; Les points A,B,C sont automatiquement exclus par filtrage de calque
      ;; Zone de -9.8m à +9.8m pour éviter les objets des coupes voisines
      (setq xmin (- (car pt-a) 9.8))   ; 9.8m à gauche (marge sécurité)
      (setq xmax (+ (car pt-a) 9.8))   ; 9.8m à droite (marge sécurité)  
      (setq ymin (- (cadr pt-a) 10.0)) ; 10m en bas (coupe complète)
      (setq ymax (+ (cadr pt-a) 10.0)) ; 10m en haut (coupe complète)
      (princ "\n  📐 Zone 19.6x20m centrée sur A (points calage auto-exclus)")
    )
    (progn
      ;; Fallback : extension importante si pas de point A
      (setq xcenter (/ (+ xmin xmax) 2.0))
      (setq ycenter (/ (+ ymin ymax) 2.0))
      (setq marge (* 0.5 (max (- xmax xmin) (- ymax ymin))))
      (setq xmin (- xmin marge))
      (setq xmax (+ xmax marge))
      (setq ymin (- ymin marge))
      (setq ymax (+ ymax marge))
      (princ "\n  ⚠ Fallback : extension +50% (point A non trouvé)")
    )
  )
  
  ;; Afficher la zone finale
  (princ "\n  Zone de sélection finale :")
  (princ (strcat "\n    X: " (rtos xmin 2 2) " à " (rtos xmax 2 2)))
  (princ (strcat "\n    Y: " (rtos ymin 2 2) " à " (rtos ymax 2 2)))
  
  ;; Sélectionner TOUS les objets dans la zone d'abord
  (princ "\n  Sélection de tous les objets dans la zone...")
  (setq ss (ssget "_W" (list xmin ymin) (list xmax ymax)))
  
  (princ (strcat "\n  Objets trouvés AVANT filtrage: " (if ss (itoa (sslength ss)) "0")))
  
  ;; Puis filtrer manuellement pour exclure les points de calage
  (if ss
    (progn
      (setq ss-filtered (ssadd))
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq entdata (entget ent))
        (setq layer (cdr (assoc 8 entdata)))
        
        ;; Exclure les calques de points de calage
        (if (not (or (equal layer "_CALAGE_PT")
                     (equal layer "_CALAGE_3D_CI")))
          (ssadd ent ss-filtered)
        )
        (setq i (1+ i))
      )
      (setq ss ss-filtered)
    )
  )
  
  (if ss
    (princ (strcat "\n  Objets sélectionnés: " (itoa (sslength ss))))
    (princ "\n  ⚠ AUCUN objet sélectionné!")
  )
  
  ss
)

;; Fonction pour caler une seule coupe
(defun calage-une-coupe (liste-calage-pm liste-3d pm-nom / paires pt1 pt2 pt3 pt1-3d pt2-3d pt3-3d objets-coupe mat-a mat-b mat-c mat-calage)
  ;; Trouver les correspondances pour cette coupe
  (setq paires (find-pairs liste-calage-pm liste-3d))
  
  (if (>= (length paires) 3)
    (progn
      ;; Sélectionner les points A, B, C
      (setq pt1 nil pt2 nil pt3 nil)
      (setq pt1-3d nil pt2-3d nil pt3-3d nil)
      
      ;; Construire les matricules exacts pour ce PM
      (setq mat-a (strcat "A_" pm-nom))
      (setq mat-b (strcat "B_" pm-nom))
      (setq mat-c (strcat "C_" pm-nom))
      
      ;; Chercher les correspondances exactes A→A, B→B, C→C
      (foreach paire paires
        (setq mat-calage (caar paire))
        (cond
          ((equal mat-calage mat-a)
           (setq pt1 (cadar paire))      ; Point source A
           (setq pt1-3d (cadadr paire))  ; Point destination A
           (princ (strcat "\n  ✓ Trouvé A : " mat-a " → A")))
          ((equal mat-calage mat-b)
           (setq pt2 (cadar paire))      ; Point source B
           (setq pt2-3d (cadadr paire))  ; Point destination B
           (princ (strcat "\n  ✓ Trouvé B : " mat-b " → B")))
          ((equal mat-calage mat-c)
           (setq pt3 (cadar paire))      ; Point source C
           (setq pt3-3d (cadadr paire))  ; Point destination C
           (princ (strcat "\n  ✓ Trouvé C : " mat-c " → C")))
        )
      )
      
      ;; Vérifier qu'on a bien trouvé les 3 points spécifiques
      (if (not (and pt1 pt2 pt3 pt1-3d pt2-3d pt3-3d))
        (progn
          (princ (strcat "\n  ⚠ ERREUR: Points manquants pour PM " pm-nom))
          (if (not pt1) (princ (strcat "\n    ✗ Manque : " mat-a)))
          (if (not pt2) (princ (strcat "\n    ✗ Manque : " mat-b)))
          (if (not pt3) (princ (strcat "\n    ✗ Manque : " mat-c)))
          (princ "\n    Le calage de cette coupe est annulé !")
          nil  ; Retourner nil au lieu d'exit
        )
      )
      
      ;; Sélectionner les objets avec diagnostic
      (princ "\n  === DIAGNOSTIC SÉLECTION ===")
      (setq objets-coupe (select-in-bounds-debug liste-calage-pm pm-nom))
      
      (if objets-coupe
        (progn
          (princ (strcat "\n  " (itoa (sslength objets-coupe)) " objets à déplacer"))
          
          ;; Calage
          (command "_3DALIGN" 
            objets-coupe ""      ; Sélection des objets + fin de sélection
            "_none" pt1          ; Point source A
            "_none" pt2          ; Point source B  
            "_none" pt3          ; Point source C
            "_none" pt1-3d       ; Point destination A
            "_none" pt2-3d       ; Point destination B
            "_none" pt3-3d       ; Point destination C
          )
          
          (princ " - Calage effectué !")
          t  ; Retourner succès
        )
        (progn
          (princ "\n  Aucun objet trouvé pour cette coupe")
          nil  ; Retourner échec
        )
      )
    )
    (progn
      (princ "\n  Pas assez de correspondances")
      nil  ; Retourner échec
    )
  )
)

;; ============================================
;; COMMANDES PRINCIPALES
;; ============================================

(defun c:CALAGE3D ( / ss-calage ss-3d pt-calage pt-3d mat-calage mat-3d
                      liste-calage liste-3d paires objets-coupe
                      pt1 pt2 pt3 pt1-3d pt2-3d pt3-3d
                      xmin xmax ymin ymax matrice-trans)
  
  ;; Programme principal
  (vl-load-com)
  
  (princ "\nCollecte des points de calage...")
  
  ;; Collecter les blocs des deux calques
  (setq liste-calage (collect-blocks "_CALAGE_PT"))
  (setq liste-3d (collect-blocks "_CALAGE_3D_CI"))
  
  (if (< (length liste-calage) 3)
    (progn
      (alert "Il faut au moins 3 points de calage dans le calque _CALAGE_PT !")
      (princ)
      (return)
    )
  )
  
  (if (< (length liste-3d) 3)
    (progn
      (alert "Il faut au moins 3 points de calage dans le calque _CALAGE_3D_CI !")
      (princ)
      (return)
    )
  )
  
  ;; Trouver les correspondances
  (setq paires (find-pairs liste-calage liste-3d))
  
  (if (< (length paires) 3)
    (progn
      (alert (strcat "Seulement " (itoa (length paires)) " correspondances trouvées. Il en faut au moins 3 !"))
      (princ)
      (return)
    )
  )
  
  (princ (strcat "\n" (itoa (length paires)) " correspondances trouvées."))
  
  ;; Prendre les 3 premières paires pour le calage
  ;; Idéalement, prendre A_, B_ et C_ si disponibles
  (setq pt1 nil pt2 nil pt3 nil)
  (setq pt1-3d nil pt2-3d nil pt3-3d nil)
  
  ;; ⚠ ATTENTION : Cette logique est DEFECTUEUSE !
  ;; Elle mélange les points de différents PM
  ;; Utilisez plutôt CALAGE3D-AUTO qui traite PM par PM
  
  (princ "\n⚠ ATTENTION: Cette commande traite TOUS les points ensemble")
  (princ "\n⚠ Risque de mélanger les PM ! Utilisez CALAGE3D-AUTO à la place")
  
  ;; Chercher un point A_, B_ et C_ (LOGIQUE DEFECTUEUSE - gardée pour compatibilité)
  (foreach paire paires
    (setq mat-calage (caar paire))
    (cond
      ((and (not pt1) (wcmatch mat-calage "A_*"))
       (setq pt1 (cadar paire))
       (setq pt1-3d (cadadr paire))
       (princ (strcat "\nUtilise A: " mat-calage)))
      ((and (not pt2) (wcmatch mat-calage "B_*"))
       (setq pt2 (cadar paire))
       (setq pt2-3d (cadadr paire))
       (princ (strcat "\nUtilise B: " mat-calage)))
      ((and (not pt3) (wcmatch mat-calage "C_*"))
       (setq pt3 (cadar paire))
       (setq pt3-3d (cadadr paire))
       (princ (strcat "\nUtilise C: " mat-calage)))
    )
  )
  
  ;; Si on n'a pas trouvé A, B et C, prendre les 3 premiers
  (if (not (and pt1 pt2 pt3))
    (progn
      (setq pt1 (cadar (nth 0 paires)))
      (setq pt1-3d (cadadr (nth 0 paires)))
      (setq pt2 (cadar (nth 1 paires)))
      (setq pt2-3d (cadadr (nth 1 paires)))
      (setq pt3 (cadar (nth 2 paires)))
      (setq pt3-3d (cadadr (nth 2 paires)))
    )
  )
  
  ;; Sélectionner les objets de la coupe dans l'emprise (SANS les points _CALAGE_PT)
  (princ "\nSélection des objets de la coupe (hors points de calage)...")
  (setq objets-coupe (select-in-bounds liste-calage))
  
  (if objets-coupe
    (progn
      (princ (strcat "\n" (itoa (sslength objets-coupe)) " objets sélectionnés (hors calage)."))
      
      ;; Afficher les points utilisés pour le calage
      (princ "\n\nPoints de calage utilisés :")
      (princ (strcat "\n  Point 1 : " (caar (assoc pt1 liste-calage))))
      (princ (strcat "\n  Point 2 : " (caar (assoc pt2 liste-calage))))
      (princ (strcat "\n  Point 3 : " (caar (assoc pt3 liste-calage))))
      
      ;; Effectuer l'alignement 3D
      (princ "\n\nCalage en cours...")
      (command "_3DALIGN" 
        objets-coupe ""      ; Sélection des objets + fin de sélection
        "_none" pt1          ; Point source A
        "_none" pt2          ; Point source B  
        "_none" pt3          ; Point source C
        "_none" pt1-3d       ; Point destination A
        "_none" pt2-3d       ; Point destination B
        "_none" pt3-3d       ; Point destination C
      )
      
      (princ "\nCalage terminé !")
    )
    (alert "Aucun objet trouvé dans l'emprise de la coupe !")
  )
  
  (princ)
)

;; Commande pour visualiser les correspondances trouvées
(defun c:CALAGE3D-INFO ( / liste-calage liste-3d paires)
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
  
  (princ)
)

;; Nouvelle commande pour traiter toutes les coupes automatiquement
(defun c:CALAGE3D-AUTO ( / liste-calage liste-3d tous-pm pm-liste pm courant mat pm-courant liste-calage-pm)
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
    
    ;; Filtrer les points pour cette coupe
    (setq liste-calage-pm '())
    (foreach item liste-calage
      (if (wcmatch (car item) (strcat "*_" pm-courant))
        (setq liste-calage-pm (cons item liste-calage-pm))
      )
    )
    
    (if (>= (length liste-calage-pm) 3)
      (progn
        ;; Lancer le calage pour cette coupe
        (if (calage-une-coupe liste-calage-pm liste-3d pm-courant)
          (princ "\n  ✓ Coupe traitée avec succès")
          (princ "\n  ✗ Erreur lors du traitement de cette coupe")
        )
      )
      (princ (strcat "\nPas assez de points pour la coupe PM " pm-courant))
    )
  )
  
  (princ "\n\n=== CALAGE AUTOMATIQUE TERMINÉ ===")
  (princ)
)

;; Commande pour visualiser les zones de sélection
(defun c:CALAGE3D-ZONES ( / liste-calage tous-pm pm-courant liste-calage-pm mat pm)
  (vl-load-com)
  
  (princ "\n=== VISUALISATION DES ZONES DE SÉLECTION ===")
  
  ;; Collecter tous les points
  (setq liste-calage (collect-blocks "_CALAGE_PT"))
  
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
  
  ;; Visualiser chaque zone
  (foreach pm-courant tous-pm
    (princ (strcat "\n\n--- Zone PM " pm-courant " ---"))
    
    ;; Filtrer les points pour cette coupe
    (setq liste-calage-pm '())
    (foreach item liste-calage
      (if (wcmatch (car item) (strcat "*_" pm-courant))
        (setq liste-calage-pm (cons item liste-calage-pm))
      )
    )
    
    (if (>= (length liste-calage-pm) 3)
      (select-in-bounds-debug liste-calage-pm pm-courant)
      (princ (strcat "\nPas assez de points pour la coupe PM " pm-courant))
    )
  )
  
  (princ "\n\n=== VISUALISATION TERMINÉE ===")
  (princ)
)

;; Commande pour tester la sélection d'une zone spécifique
(defun c:TEST-ZONE ( / pt1 pt2 ss calques i ent layer cal)
  (princ "\n=== TEST DE SÉLECTION ===")
  (princ "\nCliquez le premier coin de la zone de test : ")
  (setq pt1 (getpoint))
  (princ "\nCliquez le coin opposé : ")
  (setq pt2 (getpoint pt1))
  
  ;; Sélectionner tout dans cette zone
  (setq ss (ssget "_W" pt1 pt2))
  
  (if ss
    (progn
      (princ (strcat "\n" (itoa (sslength ss)) " objets trouvés dans cette zone"))
      
      ;; Lister les calques
      (setq calques '())
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq layer (cdr (assoc 8 (entget ent))))
        (if (not (member layer calques))
          (setq calques (cons layer calques))
        )
        (setq i (1+ i))
      )
      
      (princ "\nCalques trouvés :")
      (foreach cal calques
        (princ (strcat "\n  - " cal))
      )
    )
    (princ "\nAucun objet trouvé dans cette zone")
  )
  
  (princ)
)

(princ "\nCommandes chargées : CALAGE3D, CALAGE3D-INFO, CALAGE3D-AUTO, CALAGE3D-ZONES et TEST-ZONE")
(princ)