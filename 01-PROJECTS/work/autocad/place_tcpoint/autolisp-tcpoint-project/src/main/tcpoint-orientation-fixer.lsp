;; TCPOINT-ORIENTATION-FIXER.LSP v1.0
;; =============================================================================
;; Script pour corriger l'orientation des blocs TCPOINT après transformations 3D
;; Résout les problèmes de représentation après changements SCU ou commandes 3DAlign
;; =============================================================================

(vl-load-com)

;; ======================= CONFIGURATION =======================

(setq *TCPOINT_BLOCKS* '("TCPOINT" "tcpoint" "POINT" "point" "PT" "pt"))
(setq *DEBUG_MODE* T)
(setq *USE_RECREATION_METHOD* T)  ; T = recréer les blocs, nil = rotation en place

;; ======================= UTILITAIRES =======================

(defun tcp:debug (msg)
  (if *DEBUG_MODE* (princ (strcat "\n[DEBUG] " msg))))

(defun tcp:safe-str (x)
  (cond 
    ((null x) "")
    ((= (type x) 'STR) x)
    (T (vl-princ-to-string x))))

(defun tcp:is-tcpoint-block? (ename / dxf blockname)
  "Vérifie si l'entité est un bloc TCPOINT"
  (setq dxf (entget ename))
  (if (and dxf (= (cdr (assoc 0 dxf)) "INSERT"))
    (progn
      (setq blockname (cdr (assoc 2 dxf)))
      (if (member (strcase blockname) 
                  (mapcar 'strcase *TCPOINT_BLOCKS*))
        T nil))
    nil))

;; ======================= DETECTION D'ORIENTATION =======================

(defun tcp:get-block-normal (ename / dxf normal)
  "Récupère la normale du bloc (vecteur Z local)"
  (setq dxf (entget ename))
  (setq normal (cdr (assoc 210 dxf)))
  (if normal normal '(0.0 0.0 1.0)))

(defun tcp:get-current-ucs-normal (/)
  "Récupère la normale du SCU courant"
  ; Méthode simple: transformer le vecteur Z du monde vers le SCU courant
  ; Le vecteur (0 0 1) dans le SCU correspond à la normale du plan XY du SCU
  (if (= 1 (getvar "WORLDUCS"))
    ; SCU monde
    '(0.0 0.0 1.0)
    ; SCU utilisateur - calculer le vecteur Z du SCU
    (let ((ucs-x (getvar "UCSXDIR"))
          (ucs-y (getvar "UCSYDIR")))
      (if (and ucs-x ucs-y)
        ; Produit vectoriel X × Y = Z
        (list (- (* (cadr ucs-x) (caddr ucs-y)) (* (caddr ucs-x) (cadr ucs-y)))
              (- (* (caddr ucs-x) (car ucs-y)) (* (car ucs-x) (caddr ucs-y)))
              (- (* (car ucs-x) (cadr ucs-y)) (* (cadr ucs-x) (car ucs-y))))
        ; Fallback si erreur
        '(0.0 0.0 1.0)))))

(defun tcp:vectors-parallel? (v1 v2 tolerance / dot-product mag1 mag2 cos-angle)
  "Vérifie si deux vecteurs sont parallèles (même direction ou opposée)"
  (setq tolerance (or tolerance 0.01))
  
  ; Vérifier que les vecteurs ont 3 composantes
  (if (and v1 v2 (>= (length v1) 3) (>= (length v2) 3))
    (progn
      (setq mag1 (sqrt (+ (* (car v1) (car v1)) 
                          (* (cadr v1) (cadr v1)) 
                          (* (caddr v1) (caddr v1)))))
      (setq mag2 (sqrt (+ (* (car v2) (car v2)) 
                          (* (cadr v2) (cadr v2)) 
                          (* (caddr v2) (caddr v2)))))
      
      (if (and (> mag1 tolerance) (> mag2 tolerance))
        (progn
          (setq dot-product (+ (* (car v1) (car v2))
                               (* (cadr v1) (cadr v2))
                               (* (caddr v1) (caddr v2))))
          (setq cos-angle (/ dot-product (* mag1 mag2)))
          ; Parallèle si cos(angle) proche de 1 ou -1
          (or (> cos-angle (- 1.0 tolerance))
              (< cos-angle (+ -1.0 tolerance))))
        nil))
    nil))

(defun tcp:block-orientation-ok? (ename / block-normal ucs-normal)
  "Vérifie si l'orientation du bloc correspond au SCU courant"
  (setq block-normal (tcp:get-block-normal ename))
  (setq ucs-normal (tcp:get-current-ucs-normal))
  
  (tcp:debug (strcat "Bloc normal: " (vl-princ-to-string block-normal)))
  (tcp:debug (strcat "SCU normal: " (vl-princ-to-string ucs-normal)))
  
  (tcp:vectors-parallel? block-normal ucs-normal 0.05))

;; ======================= SAUVEGARDE DES PROPRIETES =======================

(defun tcp:get-block-properties (ename / dxf vla-obj props attribs)
  "Sauvegarde toutes les propriétés importantes d'un bloc"
  (setq dxf (entget ename)
        vla-obj (vlax-ename->vla-object ename)
        props '())
  
  ; Propriétés de base
  (setq props (cons (cons 'blockname (cdr (assoc 2 dxf))) props))
  (setq props (cons (cons 'layer (cdr (assoc 8 dxf))) props))
  (setq props (cons (cons 'insertion-point (cdr (assoc 10 dxf))) props))
  (setq props (cons (cons 'scale-x (cdr (assoc 41 dxf))) props))
  (setq props (cons (cons 'scale-y (cdr (assoc 42 dxf))) props))
  (setq props (cons (cons 'scale-z (cdr (assoc 43 dxf))) props))
  (setq props (cons (cons 'rotation (cdr (assoc 50 dxf))) props))
  
  ; Couleur et propriétés graphiques
  (if (assoc 62 dxf) (setq props (cons (cons 'color (cdr (assoc 62 dxf))) props)))
  (if (assoc 6 dxf) (setq props (cons (cons 'linetype (cdr (assoc 6 dxf))) props)))
  
  ; Attributs
  (setq attribs (tcp:get-block-attributes ename))
  (if attribs (setq props (cons (cons 'attributes attribs) props)))
  
  props)

(defun tcp:get-block-attributes (ename / next-ent dxf attribs tag value)
  "Récupère tous les attributs d'un bloc"
  (setq next-ent (entnext ename)
        attribs '())
  
  (while (and next-ent
              (setq dxf (entget next-ent))
              (not (= (cdr (assoc 0 dxf)) "SEQEND")))
    (if (= (cdr (assoc 0 dxf)) "ATTRIB")
      (progn
        (setq tag (cdr (assoc 2 dxf))
              value (cdr (assoc 1 dxf)))
        (setq attribs (cons (cons tag value) attribs))))
    (setq next-ent (entnext next-ent)))
  
  (reverse attribs))

;; ======================= RECREATION DE BLOCS =======================

(defun tcp:recreate-block (ename props / doc mspace new-block attr-refs)
  "Recrée un bloc avec les propriétés sauvegardées"
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        mspace (vla-get-ModelSpace doc))
  
  ; Supprimer l'ancien bloc
  (entdel ename)
  
  ; Créer le nouveau bloc
  (setq new-block 
    (vla-InsertBlock 
      mspace
      (vlax-3d-point (cdr (assoc 'insertion-point props)))
      (cdr (assoc 'blockname props))
      (or (cdr (assoc 'scale-x props)) 1.0)
      (or (cdr (assoc 'scale-y props)) 1.0)
      (or (cdr (assoc 'scale-z props)) 1.0)
      (or (cdr (assoc 'rotation props)) 0.0)))
  
  ; Appliquer les propriétés
  (if (assoc 'layer props)
    (vla-put-Layer new-block (cdr (assoc 'layer props))))
  
  (if (assoc 'color props)
    (vla-put-Color new-block (cdr (assoc 'color props))))
  
  ; Appliquer les attributs
  (if (and (vla-get-HasAttributes new-block)
           (assoc 'attributes props))
    (progn
      (if (not (vl-catch-all-error-p 
                 (vl-catch-all-apply 'vla-GetAttributes (list new-block))))
        (progn
          (setq attr-refs (vlax-safearray->list 
                            (vlax-variant-value 
                              (vla-GetAttributes new-block))))
          (tcp:set-block-attributes attr-refs (cdr (assoc 'attributes props))))
        (tcp:debug "Erreur lors de la récupération des attributs"))))
  
  (tcp:debug "Bloc recréé avec succès")
  new-block)

(defun tcp:set-block-attributes (attr-refs saved-attrs / attr tag)
  "Applique les attributs sauvegardés au nouveau bloc"
  (foreach attr attr-refs
    (setq tag (strcase (vla-get-TagString attr)))
    (foreach saved-attr saved-attrs
      (if (= tag (strcase (car saved-attr)))
        (vla-put-TextString attr (cdr saved-attr))))))

;; ======================= CORRECTION PAR TRANSFORMATION =======================

(defun tcp:fix-block-orientation (ename / block-normal ucs-normal rotation-matrix)
  "Corrige l'orientation d'un bloc par transformation 3D"
  ; Cette méthode est plus complexe et sera implémentée si nécessaire
  (tcp:debug "Correction par transformation pas encore implémentée")
  nil)

;; ======================= COMMANDES PRINCIPALES =======================

(defun tcp:fix-selected-blocks (ss / i ename count-fixed count-total props)
  "Corrige l'orientation des blocs sélectionnés"
  (setq count-fixed 0 count-total 0)
  
  (if ss
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq ename (ssname ss i))
        (if (tcp:is-tcpoint-block? ename)
          (progn
            (setq count-total (1+ count-total))
            (tcp:debug (strcat "Vérification du bloc " (itoa count-total)))
            
            (if (not (tcp:block-orientation-ok? ename))
              (progn
                (tcp:debug "Orientation incorrecte détectée")
                (setq props (tcp:get-block-properties ename))
                
                (if *USE_RECREATION_METHOD*
                  (progn
                    (tcp:recreate-block ename props)
                    (setq count-fixed (1+ count-fixed))
                    (tcp:debug "Bloc corrigé par recréation"))
                  (if (tcp:fix-block-orientation ename)
                    (progn
                      (setq count-fixed (1+ count-fixed))
                      (tcp:debug "Bloc corrigé par transformation"))))
              (tcp:debug "Orientation correcte"))))
        (setq i (1+ i)))
      
      (princ (strcat "\nRésultat: " (itoa count-fixed) " blocs corrigés sur " 
                     (itoa count-total) " blocs TCPOINT trouvés.")))
    (princ "\nAucune sélection.")))

;; ======================= COMMANDES AUTOCAD =======================

(defun c:TCPOINT-FIX-SELECTION ()
  "Corrige l'orientation des blocs TCPOINT sélectionnés"
  (princ "\n=== CORRECTION D'ORIENTATION TCPOINT - SELECTION ===")
  (princ "\nSélectionnez les blocs TCPOINT à corriger...")
  
  (let ((ss (ssget '((0 . "INSERT")))))
    (tcp:fix-selected-blocks ss))
  (princ))

(defun c:TCPOINT-FIX-ALL ()
  "Corrige l'orientation de tous les blocs TCPOINT du dessin"
  (princ "\n=== CORRECTION D'ORIENTATION TCPOINT - TOUS ===")
  (princ "\nRecherche de tous les blocs TCPOINT...")
  
  (let ((ss (ssget "X" '((0 . "INSERT")))))
    (tcp:fix-selected-blocks ss))
  (princ))

(defun c:TCPOINT-FIX-LAYER ()
  "Corrige l'orientation des blocs TCPOINT sur un calque spécifique"
  (princ "\n=== CORRECTION D'ORIENTATION TCPOINT - CALQUE ===")
  
  (let ((layer-name (getstring "\nNom du calque (ou ENTREE pour calque courant): ")))
    (if (= layer-name "")
      (setq layer-name (getvar "CLAYER")))
    
    (princ (strcat "\nRecherche des blocs TCPOINT sur le calque: " layer-name))
    
    (let ((ss (ssget "X" (list '(0 . "INSERT") (cons 8 layer-name)))))
      (tcp:fix-selected-blocks ss)))
  (princ))

;; ======================= COMMANDE DE TEST =======================

(defun c:TCPOINT-CHECK-ORIENTATION ()
  "Vérifie l'orientation des blocs TCPOINT sans les corriger"
  (princ "\n=== VERIFICATION D'ORIENTATION TCPOINT ===")
  (princ "\nSélectionnez les blocs à vérifier...")
  
  (let ((ss (ssget '((0 . "INSERT"))))
        (count-ok 0) (count-bad 0) (i 0) ename)
    
    (if ss
      (progn
        (while (< i (sslength ss))
          (setq ename (ssname ss i))
          (if (tcp:is-tcpoint-block? ename)
            (if (tcp:block-orientation-ok? ename)
              (progn
                (setq count-ok (1+ count-ok))
                (princ (strcat "\nBloc " (itoa (1+ i)) ": OK")))
              (progn
                (setq count-bad (1+ count-bad))
                (princ (strcat "\nBloc " (itoa (1+ i)) ": MAUVAISE ORIENTATION")))))
          (setq i (1+ i)))
        
        (princ (strcat "\n\nRésumé: " (itoa count-ok) " blocs correctement orientés, " 
                       (itoa count-bad) " blocs mal orientés.")))
      (princ "\nAucune sélection.")))
  (princ))

;; ======================= CHARGEMENT =======================

(princ "\n=== TCPOINT-ORIENTATION-FIXER v1.0 chargé ===")
(princ "\nCommandes disponibles:")
(princ "\n- TCPOINT-FIX-SELECTION  : Corriger la sélection")
(princ "\n- TCPOINT-FIX-ALL        : Corriger tous les blocs")
(princ "\n- TCPOINT-FIX-LAYER      : Corriger un calque spécifique")
(princ "\n- TCPOINT-CHECK-ORIENTATION : Vérifier sans corriger")
(princ "\n")
