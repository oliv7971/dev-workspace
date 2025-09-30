;; PLACE-TCPOINT.LSP v2.1 (enhanced 2025-09-08)
;; Placer des blocs TCPOINT aux extrémités des lignes/polylignes du côté du centre
;; Correctifs : 
;; - _safe-rtos pour éviter numberp:T/nil dans les affichages
;; - Conversion correcte des intersections (VARIANT/SAFEARRAY -> liste)
;; - Forçage de tolR en réel
;; - Garde sur c* (centre le plus proche)
;; - Nettoyage des doublons _collect-entities/_collect-centers
;; - Ajout _to-list et _is-pt2/_is-pt3 pour robustesse accrue
;; 
;; PRINCIPE :
;; 1. Détection automatique des centres (points sur calque _INTERSEC_AXE_2D)
;; 2. Sélection automatique ou manuelle des lignes/polylignes
;; 3. Calcul distance précise point-to-segment avec rayon de proximité
;; 4. Insertion des blocs TCPOINT aux bonnes extrémités

(vl-load-com)

;; ===== PARAMETRES A MODIFIER =====
(setq *NOM-BLOC-TCPOINT* "TCPOINT")     ;; Nom du bloc à insérer
(setq *SUFFIXE-CALQUE* "_tete")         ;; Suffixe ajouté au calque de la ligne
(setq *CALQUE-CENTRES* "_INTERSEC_AXE_2D")       ;; Calque des points centres
(setq *CALQUE-AXES* "INS_GC_GAL_Galeries_Axes") ;; Calque des axes pour intersection
(setq *RAYON-PROXIMITE* 10.0)           ;; Rayon de proximité par défaut (m)
(setq *AFFICHAGE-DEBUG* T)              ;; T = affiche détails, nil = silencieux
(setq *MODE-AUTO* T)                    ;; T = détection auto centres, nil = sélection manuelle

;; ===== FONCTIONS UTILITAIRES ROBUSTES =====
(defun _num (x) 
  (cond
    ((numberp x) x)
    ((= x T) (progn (princ "\nDEBUG: T converti en 0.0") 0.0))
    ((= x nil) (progn (princ "\nDEBUG: nil converti en 0.0") 0.0))
    (t (progn (princ (strcat "\nDEBUG: " (vl-princ-to-string x) " converti en 0.0")) 0.0))))

;; Convertit proprement VARIANT/SAFEARRAY/LIST -> LIST ; sinon NIL
(defun _to-list (v / val)
  (cond
    ((= (type v) 'VARIANT)
     (setq val (vlax-variant-value v))
     (cond
       ((= (type val) 'SAFEARRAY) (vlax-safearray->list val))
       ((= (type val) 'LIST)      val)
       (T                         nil)))
    ((= (type v) 'SAFEARRAY) (vlax-safearray->list v))
    ((= (type v) 'LIST)      v)
    (T                       nil)))

(defun _is-pt2 (p) (and (listp p) (numberp (car p)) (numberp (cadr p))))
(defun _is-pt3 (p) (and (_is-pt2 p) (numberp (caddr p))))

;; Normalise en (x y z)
(defun _pt3 (v / l)
  (setq l (_to-list v))
  (cond
    ((and l (= (length l) 3)) l)
    ((and l (= (length l) 2)) (append l (list 0.0)))
    (T (list 0.0 0.0 0.0))))

(defun _safe-dist2d (p q)
  (if (and (listp p) (listp q) 
           (numberp (car p)) (numberp (cadr p))
           (numberp (car q)) (numberp (cadr q)))
    (sqrt (+ (expt (- (car p) (car q)) 2)
             (expt (- (cadr p) (cadr q)) 2)))
    (progn
      (princ (strcat "\nDEBUG _safe-dist2d: p=" (vl-princ-to-string p) " q=" (vl-princ-to-string q)))
      1e99)))

(defun _dist2d (p q)
  (_safe-dist2d p q))

(defun _safe-rtos (x /)
  (cond
    ((numberp x) (rtos x 2 3))
    ((= x T) "T")
    ((= x nil) "nil")
    (t (vl-princ-to-string x))))

;; Distance point->segment 2D (plus précise que distance aux extrémités)
(defun _dist2d-pt-seg (c a b / ax ay bx by cx cy abx aby acx acy ab2 t1 px py)
  ;; Vérifications de sécurité
  (if (not (and (listp c) (listp a) (listp b)
                (numberp (car c)) (numberp (cadr c))
                (numberp (car a)) (numberp (cadr a))
                (numberp (car b)) (numberp (cadr b))))
    (progn
      (princ (strcat "\nDEBUG _dist2d-pt-seg: c=" (vl-princ-to-string c) 
                     " a=" (vl-princ-to-string a) 
                     " b=" (vl-princ-to-string b)))
      1e99)
    (progn
      (setq ax (car a) ay (cadr a)
            bx (car b) by (cadr b)
            cx (car c) cy (cadr c))
      (setq abx (- bx ax) aby (- by ay)
            acx (- cx ax) acy (- cy ay)
            ab2 (+ (* abx abx) (* aby aby)))
      (if (= ab2 0.0)
        (_safe-dist2d c a) ; A==B
        (progn
          (setq t1 (/ (+ (* acx abx) (* acy aby)) ab2))
          (cond
            ((< t1 0.0) (_safe-dist2d c a))
            ((> t1 1.0) (_safe-dist2d c b))
            (T (setq px (+ ax (* t1 abx))
                     py (+ ay (* t1 aby)))
               (_safe-dist2d c (list px py 0.0))))))))))

(defun _ensure-layer (doc name / layrs lyr)
  (setq layrs (vla-get-Layers doc))
  (if (not (tblsearch "LAYER" name))
    (progn 
      (setq lyr (vla-Add layrs name)) 
      (vla-put-Color lyr 3)
      (princ (strcat "\nCalque '" name "' créé"))
    )
    (setq lyr (vla-Item layrs name)))
  lyr)

(defun _has-block? (name) (if (tblsearch "BLOCK" name) T nil))

;; Extrémités des entités
(defun _ends-line (o / sp ep)
  (setq sp (_pt3 (vla-get-StartPoint o))
        ep (_pt3 (vla-get-EndPoint   o)))
  (list sp ep))

(defun _ends-lwpoly (o / coords n elev)
  (setq coords (_to-list (vla-get-Coordinates o))
        n      (if coords (length coords) 0)
        elev   (or (vla-get-Elevation o) 0.0))
  (if (>= n 4)
    (list
      (list (nth 0 coords) (nth 1 coords) elev)
      (list (nth (- n 2) coords) (nth (- n 1) coords) elev))
    nil))

;; Distance centre -> entité (point-to-segment)
(defun _dist-center-line (c o / ends)
  (setq ends (_ends-line o))
  (if ends 
    (_dist2d-pt-seg c (car ends) (cadr ends)) 
    (progn
      (if *AFFICHAGE-DEBUG* (princ "\nDEBUG _dist-center-line: ends=nil"))
      1e99)))

(defun _dist-center-lwpoly (c o / coords n i dmin a b d)
  (setq coords (_to-list (vla-get-Coordinates o))
        n      (if coords (length coords) 0)
        dmin   1e99
        i      0)
  (while (< (+ i 3) n)
    (setq a (list (nth i coords)     (nth (+ i 1) coords) 0.0)
          b (list (nth (+ i 2) coords) (nth (+ i 3) coords) 0.0)
          d (_dist2d-pt-seg c a b))
    (if *AFFICHAGE-DEBUG*
      (princ (strcat "\n    DEBUG _dist-center-lwpoly: d=" (vl-princ-to-string d)))
    )
    (if (and (numberp d) (< d dmin)) (setq dmin d))
    (setq i (+ i 2)))
  dmin)

;; Collecte automatique des entités (respecte automatiquement les calques gelés)
(defun _collect-entities ( / ss n i en vo lst)
  (setq ss (ssget "_ALL" '((0 . "LINE,LWPOLYLINE"))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i)
              vo (vlax-ename->vla-object en))
        (setq lst (cons vo lst))
        (setq i (1+ i)))
      (reverse lst))
    nil))

;; Collecte automatique des centres (respecte automatiquement les calques gelés)
(defun _collect-centers ( / ss n i en vo p lst)
  (setq ss (ssget "_ALL" (list '(0 . "POINT") (cons 8 *CALQUE-CENTRES*))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i)
              vo (vlax-ename->vla-object en)
              p  (_to-list (vla-get-Coordinates vo)))
        (if (_is-pt2 p) 
          (progn
            (setq p (if (= (length p) 3) p (append p (list 0.0))))
            (setq lst (cons p lst))
            (if *AFFICHAGE-DEBUG*
              (princ (strcat "\n  DEBUG: Centre collecté: " (vl-princ-to-string p)))
            )
          )
        )
        (setq i (1+ i)))
      (reverse lst))
    nil))

;; Insertion de bloc avec calque dynamique
(defun _add-blockref-dynamic (space name pt calque-ligne / br calque-cible p3)
  (setq calque-cible (strcat calque-ligne *SUFFIXE-CALQUE*))
  
  ;; Vérifier que pt est valide
  (if (not (_is-pt2 pt))
    (progn
      (princ (strcat "\nERREUR: Point invalide reçu: " (vl-princ-to-string pt)))
      (exit)
    )
  )
  
  ;; Créer le calque s'il n'existe pas
  (if (not (tblsearch "LAYER" calque-cible))
    (progn
      (command "._LAYER" "_M" calque-cible "")
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n    Calque '" calque-cible "' créé"))
      )
    )
  )
  
  (setq p3 (if (_is-pt3 pt) pt (append pt (list 0.0))))
  (setq br (vla-InsertBlock space (vlax-3d-point p3) name 1.0 1.0 1.0 0.0))
  (if calque-cible (vla-put-Layer br calque-cible))
  
  (if *AFFICHAGE-DEBUG*
    (princ (strcat "\n    TCPOINT sur calque: " calque-cible))
  )
  
  br)
;; ===== COMMANDE PRINCIPALE =====
(defun c:place-tcpoint (/ doc ms tolR centres liste-entites mode-choisi)
  (princ "\n=== PLACEMENT AUTOMATIQUE DE BLOCS TCPOINT v2.0 ===")
  
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        ms  (vla-get-ModelSpace doc))
  
  ;; Configuration du rayon de proximité
  (setq tolR (getreal (strcat "\nRayon de proximité au centre (m) <" (_safe-rtos (float *RAYON-PROXIMITE*)) ">: ")))
  (if (not (and tolR (> tolR 0.0))) (setq tolR (float *RAYON-PROXIMITE*)))
  (setq tolR (float tolR)) ;; force réel
  
  ;; Choix du mode
  (princ "\n")
  (princ "\nMODES DISPONIBLES :")
  (princ "\n1. Automatique : Détection auto des centres + toutes les lignes/polylignes")
  (princ "\n2. Semi-auto   : Centres auto + sélection manuelle des entités")
  (princ "\n3. Manuel      : Centre manuel + sélection manuelle")
  (princ "\n4. Auto-Créer  : Créer centres d'intersection + placement automatique")
  (princ "\n")
  
  (setq mode-choisi (getint "\nChoisissez le mode (1/2/3/4) <1>: "))
  (if (not mode-choisi) (setq mode-choisi 1))
  
  (cond
    ;; Mode 1 : Tout automatique
    ((= mode-choisi 1)
     (princ "\n=== MODE AUTOMATIQUE ===")
     (setq centres (_collect-centers))
     (if centres
       (progn
         (princ (strcat "\n" (itoa (length centres)) " centres trouvés sur calque '" *CALQUE-CENTRES* "'"))
         (setq liste-entites (_collect-entities))
         (if liste-entites
           (progn
             (princ (strcat "\n" (itoa (length liste-entites)) " lignes/polylignes trouvées"))
             (placer-tcpoints-auto liste-entites centres tolR)
           )
           (princ "\nAucune ligne/polyligne trouvée dans le dessin")
         )
       )
       (princ (strcat "\nAucun centre trouvé sur le calque '" *CALQUE-CENTRES* "'"))
     )
    )
    
    ;; Mode 2 : Semi-automatique
    ((= mode-choisi 2)
     (princ "\n=== MODE SEMI-AUTOMATIQUE ===")
     (setq centres (_collect-centers))
     (if centres
       (progn
         (princ (strcat "\n" (itoa (length centres)) " centres trouvés sur calque '" *CALQUE-CENTRES* "'"))
         (princ "\nSélectionnez les lignes et polylignes...")
         (setq ss-entites (ssget))
         (if ss-entites
           (progn
             (setq liste-entites (convertir-selection-en-vla ss-entites))
             (placer-tcpoints-auto liste-entites centres tolR)
           )
           (princ "\nAucune sélection.")
         )
       )
       (princ (strcat "\nAucun centre trouvé sur le calque '" *CALQUE-CENTRES* "'"))
     )
    )
    
    ;; Mode 3 : Manuel (ancien mode)
    ((= mode-choisi 3)
     (princ "\n=== MODE MANUEL ===")
     (princ "\nSélectionnez les lignes et polylignes...")
     (setq ss-entites (ssget))
     (if ss-entites
       (progn
         (setq liste-lignes (filtrer-lignes-polylignes ss-entites))
         (if (> (length liste-lignes) 0)
           (progn
             (princ (strcat "\n" (itoa (length liste-lignes)) " lignes/polylignes trouvées"))
             (princ "\nCliquez pour définir le centre de référence...")
             (setq centre (getpoint "\nCentre de référence : "))
             (if centre
               (placer-tcpoints liste-lignes centre)
               (princ "\nAnnulé.")
             )
           )
           (princ "\nAucune ligne ou polyligne trouvée")
         )
       )
       (princ "\nAucune sélection.")
     )
    )
    
    ;; Mode 4 : Auto-création des centres + placement
    ((= mode-choisi 4)
     (princ "\n=== MODE AUTO-CRÉATION DES CENTRES ===")
     
     ;; Collecter les axes pour intersection
     (setq axes (_collect-axes))
     (if axes
       (progn
         (princ (strcat "\n" (itoa (length axes)) " axes trouvés sur calque '" *CALQUE-AXES* "'"))
         
         ;; Créer automatiquement les centres d'intersection
         (setq centres-crees (_create-intersection-centers axes))
         
         (if (> (length centres-crees) 0)
           (progn
             ;; Maintenant utiliser ces centres pour placer les TCPOINT
             (setq liste-entites (_collect-entities))
             (if liste-entites
               (progn
                 (princ (strcat "\n" (itoa (length liste-entites)) " lignes/polylignes trouvées"))
                 (placer-tcpoints-auto liste-entites centres-crees tolR)
               )
               (princ "\nAucune ligne/polyligne trouvée pour placement TCPOINT")
             )
           )
           (princ "\nAucune intersection trouvée entre les axes")
         )
       )
       (princ (strcat "\nAucun axe trouvé sur le calque '" *CALQUE-AXES* "'"))
     )
    )
    
    (T (princ "\nMode invalide."))
  )
  
  (princ)
)

;; ===== CONVERSION SELECTION EN VLA OBJECTS =====
(defun convertir-selection-en-vla (ss / liste i ent)
  (setq liste '()
        i 0)
  (repeat (sslength ss)
    (setq ent (vlax-ename->vla-object (ssname ss i)))
    (setq liste (cons ent liste))
    (setq i (1+ i))
  )
  (reverse liste)
)

;; ===== PLACEMENT AUTOMATIQUE AVEC RAYON DE PROXIMITE =====
(defun placer-tcpoints-auto (liste-entites centres tolR / doc ms created scanned on ends dmin c* d* dc p1 p2 d1 d2 pin calque-ligne calques-crees calque-cible)
  (princ "\n=== PLACEMENT AVEC RAYON DE PROXIMITÉ ===")
  
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        ms  (vla-get-ModelSpace doc)
        calques-crees '())
  
  ;; Vérifier que le bloc TCPOINT existe
  (if (not (_has-block? *NOM-BLOC-TCPOINT*))
    (progn
      (princ (strcat "\nATTENTION : Le bloc '" *NOM-BLOC-TCPOINT* "' n'existe pas !"))
      (princ "\nVeuillez créer ou charger le bloc TCPOINT avant d'utiliser cette commande.")
      (exit)
    )
  )
  
  (setq created 0 scanned 0)
  
  (vl-catch-all-apply 'vla-StartUndoMark (list doc))
  
  ;; Traitement de chaque entité
  (foreach o liste-entites
    (setq scanned (1+ scanned)
          on      (vla-get-ObjectName o)
          ends    nil
          dmin    1e99
          calque-ligne (vla-get-Layer o))  ;; Récupérer le calque de la ligne
    
    (if *AFFICHAGE-DEBUG*
      (princ (strcat "\n--- Entité " (itoa scanned) " : " on " (calque: " calque-ligne ") ---"))
    )
    
    (cond
      ;; Ligne
      ((= on "AcDbLine")
       (setq ends (_ends-line o))
       (foreach c centres
         (setq dc (_dist-center-line c o))
         (if (and (numberp dc) (< dc dmin)) (setq dmin dc)))
      )
      ;; Polyligne
      ((= on "AcDbPolyline")
       (if (eq (vla-get-Closed o) :vlax-false)  ;; Seulement les polylignes ouvertes
         (progn
           (setq ends (_ends-lwpoly o))
           (foreach c centres
             (setq dc (_dist-center-lwpoly c o))
             (if (and (numberp dc) (< dc dmin)) (setq dmin dc)))
         )
         (if *AFFICHAGE-DEBUG*
           (princ "\n  Polyligne fermée ignorée")
         )
       )
      )
    )
    
    ;; Si l'entité est assez proche d'au moins un centre
    (if (and ends (<= dmin tolR))
      (progn
        (if *AFFICHAGE-DEBUG*
          (princ (strcat "\n  Distance min aux centres: " (_safe-rtos dmin) " ≤ " (_safe-rtos tolR) " → OK"))
        )
        
        ;; Trouver le centre le plus proche pour décider de l'extrémité
        (setq c* nil d* 1e99)
        (foreach c centres
          (if (_is-pt2 c)  ;; Validation du centre avant utilisation
            (progn
              (if *AFFICHAGE-DEBUG*
                (princ (strcat "\n    DEBUG: Centre testé: " (vl-princ-to-string c)))
              )
              (setq dc (cond
                         ((= on "AcDbLine")    (_dist-center-line c o))
                         (T                    (_dist-center-lwpoly c o))))
              (if *AFFICHAGE-DEBUG*
                (princ (strcat "\n    DEBUG: Distance centre: " (_safe-rtos dc)))
              )
              (if (and (numberp dc) (< dc d*)) 
                (progn
                  (setq d* dc c* c)
                  (if *AFFICHAGE-DEBUG*
                    (princ (strcat "\n    DEBUG: Nouveau centre le plus proche: " (vl-princ-to-string c*)))
                  )
                )
              )
            )
          )
        )
        
        ;; Choisir l'extrémité la plus proche du centre le plus proche
        (setq p1 (car ends) p2 (cadr ends))
        (if (_is-pt2 c*)  ;; Validation du centre avant utilisation
          (progn
            (setq d1 (_dist2d p1 c*) d2 (_dist2d p2 c*))
            (if *AFFICHAGE-DEBUG*
              (princ (strcat "\n    DEBUG: d1=" (vl-princ-to-string d1) " d2=" (vl-princ-to-string d2)))
            )
            (setq pin (if (and (numberp d1) (numberp d2) (< d1 d2)) p1 p2))
            
            ;; Insérer le bloc TCPOINT sur le calque dynamique
            (_add-blockref-dynamic ms *NOM-BLOC-TCPOINT* pin calque-ligne)
            (setq created (1+ created))
            
            ;; Ajouter le calque à la liste des calques créés
            (setq calque-cible (strcat calque-ligne *SUFFIXE-CALQUE*))
            (if (not (member calque-cible calques-crees))
              (setq calques-crees (cons calque-cible calques-crees))
            )
            
            (if *AFFICHAGE-DEBUG*
              (progn
                (princ (strcat "\n  Centre le plus proche: (" (_safe-rtos (car c*)) "," (_safe-rtos (cadr c*)) ")"))
                (princ (strcat "\n  ✓ TCPOINT placé à (" (_safe-rtos (car pin)) "," (_safe-rtos (cadr pin)) ")"))
              )
            )
          )
          (if *AFFICHAGE-DEBUG* (princ "\n  Centre le plus proche: indisponible (aucun centre valide)"))
        )
      )
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n  Distance min aux centres: " (_safe-rtos dmin) " > " (_safe-rtos tolR) " → Ignoré"))
      )
    )
  )
  
  (vl-catch-all-apply 'vla-EndUndoMark (list doc))
  
  (princ "\n")
  (princ (strcat "\nRÉSULTAT FINAL :"))
  (princ (strcat "\n- Entités scannées       : " (itoa scanned)))
  (princ (strcat "\n- Blocs TCPOINT placés   : " (itoa created)))
  (princ (strcat "\n- Rayon proximité (m)    : " (_safe-rtos tolR)))
  (princ (strcat "\n- Suffixe calques        : " *SUFFIXE-CALQUE*))
  
  (if (> (length calques-crees) 0)
    (progn
      (princ (strcat "\n- Calques créés/utilisés : " (itoa (length calques-crees))))
      (if *AFFICHAGE-DEBUG*
        (progn
          (princ "\n  Liste des calques :")
          (foreach cal (reverse calques-crees)
            (princ (strcat "\n    • " cal))
          )
        )
      )
    )
  )
  
  (princ "\nTerminé !")
)

;; ===== FILTRAGE DES LIGNES ET POLYLIGNES =====
(defun filtrer-lignes-polylignes (ss-source / liste-lignes i ent data type-obj pt1 pt2 vertices)
  (setq liste-lignes '())
  (setq i 0)
  
  (if *AFFICHAGE-DEBUG* (princ "\nFiltrage des entités..."))
  
  (repeat (sslength ss-source)
    (setq ent (ssname ss-source i))
    (setq data (entget ent))
    (setq type-obj (cdr (assoc 0 data)))
    
    ;; Garder seulement les LINE et LWPOLYLINE
    (cond
      ((= type-obj "LINE")
       (setq pt1 (cdr (assoc 10 data)))
       (setq pt2 (cdr (assoc 11 data)))
       (setq liste-lignes (cons (list ent "LINE" pt1 pt2) liste-lignes))
       (if *AFFICHAGE-DEBUG* 
         (princ (strcat "\n  Gardé : LINE de (" (_safe-rtos (car pt1)) "," (_safe-rtos (cadr pt1)) ") à (" (_safe-rtos (car pt2)) "," (_safe-rtos (cadr pt2)) ")"))
       )
      )
      ((= type-obj "LWPOLYLINE")
       (setq vertices (extraire-vertices-polyligne data))
       (if vertices
         (progn
           (setq pt1 (car vertices))
           (setq pt2 (last vertices))
           (setq liste-lignes (cons (list ent "LWPOLYLINE" pt1 pt2) liste-lignes))
           (if *AFFICHAGE-DEBUG* 
             (princ (strcat "\n  Gardé : POLYLIGNE de (" (_safe-rtos (car pt1)) "," (_safe-rtos (cadr pt1)) ") à (" (_safe-rtos (car pt2)) "," (_safe-rtos (cadr pt2)) ")"))
           )
         )
       )
      )
      (T
       (if *AFFICHAGE-DEBUG*
         (princ (strcat "\n  Ignoré : " type-obj))
       )
      )
    )
    (setq i (1+ i))
  )
  
  liste-lignes
)

;; ===== EXTRACTION DES VERTICES D'UNE POLYLIGNE =====
(defun extraire-vertices-polyligne (data / vertices)
  (setq vertices '())
  (foreach item data
    (if (= (car item) 10)  ;; Code 10 = vertex
      (setq vertices (append vertices (list (cdr item))))
    )
  )
  vertices
)

;; ===== PLACEMENT TCPOINTS MODE MANUEL (avec calques dynamiques) =====
(defun placer-tcpoints (liste-lignes centre / compteur nb-places ent type-ligne pt1 pt2 dist1 dist2 calque-ligne)
  (princ "\nPlacement des blocs TCPOINT...")
  
  ;; Vérifier que le bloc TCPOINT existe
  (if (not (tblsearch "BLOCK" *NOM-BLOC-TCPOINT*))
    (progn
      (princ (strcat "\nATTENTION : Le bloc '" *NOM-BLOC-TCPOINT* "' n'existe pas !"))
      (princ "\nVeuillez créer ou charger le bloc TCPOINT avant d'utiliser cette commande.")
      (exit)
    )
  )
  
  (setq compteur 0
        nb-places 0)
  
  (foreach ligne liste-lignes
    (setq compteur (1+ compteur))
    (setq ent (car ligne))
    (setq type-ligne (cadr ligne))
    (setq pt1 (caddr ligne))
    (setq pt2 (cadddr ligne))
    (setq calque-ligne (cdr (assoc 8 (entget ent))))  ;; Récupérer le calque de la ligne
    
    (if *AFFICHAGE-DEBUG*
      (princ (strcat "\n--- Traitement " type-ligne " " (itoa compteur) " (calque: " calque-ligne ") ---"))
    )
    
    ;; Calculer les distances au centre pour chaque extrémité
    (setq dist1 (distance pt1 centre))
    (setq dist2 (distance pt2 centre))
    
    (if *AFFICHAGE-DEBUG*
      (progn
        (princ (strcat "\n  Pt1: (" (_safe-rtos (car pt1)) "," (_safe-rtos (cadr pt1)) ") - Distance au centre: " (_safe-rtos dist1)))
        (princ (strcat "\n  Pt2: (" (_safe-rtos (car pt2)) "," (_safe-rtos (cadr pt2)) ") - Distance au centre: " (_safe-rtos dist2)))
      )
    )
    
    ;; Placer le TCPOINT à l'extrémité la plus proche du centre
    (if (< dist1 dist2)
      (progn
        ;; pt1 est plus proche du centre
        (placer-bloc-tcpoint-dynamique pt1 calque-ligne)
        (setq nb-places (1+ nb-places))
        (if *AFFICHAGE-DEBUG*
          (princ (strcat "\n  ✓ TCPOINT placé à Pt1 (plus proche du centre)"))
        )
      )
      (progn
        ;; pt2 est plus proche du centre
        (placer-bloc-tcpoint-dynamique pt2 calque-ligne)
        (setq nb-places (1+ nb-places))
        (if *AFFICHAGE-DEBUG*
          (princ (strcat "\n  ✓ TCPOINT placé à Pt2 (plus proche du centre)"))
        )
      )
    )
  )
  
  (princ "\n")
  (princ (strcat "\nRÉSULTAT FINAL :"))
  (princ (strcat "\n- Lignes/polylignes traitées : " (itoa compteur)))
  (princ (strcat "\n- Blocs TCPOINT placés : " (itoa nb-places)))
  (princ (strcat "\n- Suffixe calques : " *SUFFIXE-CALQUE*))
  (princ "\nTerminé !")
)

;; ===== PLACEMENT D'UN BLOC TCPOINT AVEC CALQUE DYNAMIQUE =====
(defun placer-bloc-tcpoint-dynamique (point calque-ligne / calque-actuel calque-cible)
  ;; Sauvegarder le calque actuel
  (setq calque-actuel (getvar "CLAYER"))
  
  ;; Créer le nom du calque cible
  (setq calque-cible (strcat calque-ligne *SUFFIXE-CALQUE*))
  
  ;; Créer le calque s'il n'existe pas
  (if (not (tblsearch "LAYER" calque-cible))
    (progn
      (command "._LAYER" "_M" calque-cible "")
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n    Calque '" calque-cible "' créé"))
      )
    )
  )
  
  ;; Changer vers le calque TCPOINT
  (setvar "CLAYER" calque-cible)
  
  ;; Insérer le bloc TCPOINT
  (command "._INSERT" *NOM-BLOC-TCPOINT* point 1 1 0)
  
  (if *AFFICHAGE-DEBUG*
    (princ (strcat "\n    TCPOINT sur calque: " calque-cible))
  )
  
  ;; Restaurer le calque actuel
  (setvar "CLAYER" calque-actuel)
)

;; ===== COMMANDE POUR CHANGER LES PARAMÈTRES =====
(defun c:config-tcpoint ()
  (princ "\n=== CONFIGURATION TCPOINT v2.1 ===")
  (princ (strcat "\nBloc actuel          : " *NOM-BLOC-TCPOINT*))
  (princ (strcat "\nSuffixe calque       : " *SUFFIXE-CALQUE*))
  (princ (strcat "\nCalque centres       : " *CALQUE-CENTRES*))
  (princ (strcat "\nCalque axes          : " *CALQUE-AXES*))
  (princ (strcat "\nRayon proximité (m)  : " (_safe-rtos (float *RAYON-PROXIMITE*))))
  
  (setq nouveau-bloc (getstring T "\nNouveau nom de bloc (Entrée pour garder) : "))
  (if (and nouveau-bloc (> (strlen nouveau-bloc) 0))
    (setq *NOM-BLOC-TCPOINT* nouveau-bloc)
  )
  
  (setq nouveau-suffixe (getstring T "\nNouveau suffixe calque (Entrée pour garder) : "))
  (if (and nouveau-suffixe (> (strlen nouveau-suffixe) 0))
    (setq *SUFFIXE-CALQUE* nouveau-suffixe)
  )
  
  (setq nouveau-calque-centres (getstring T "\nNouveau calque centres (Entrée pour garder) : "))
  (if (and nouveau-calque-centres (> (strlen nouveau-calque-centres) 0))
    (setq *CALQUE-CENTRES* nouveau-calque-centres)
  )
  
  (setq nouveau-calque-axes (getstring T "\nNouveau calque axes (Entrée pour garder) : "))
  (if (and nouveau-calque-axes (> (strlen nouveau-calque-axes) 0))
    (setq *CALQUE-AXES* nouveau-calque-axes)
  )
  
  (setq nouveau-rayon (getreal "\nNouveau rayon proximité (Entrée pour garder) : "))
  (if (and nouveau-rayon (> nouveau-rayon 0.0))
    (setq *RAYON-PROXIMITE* nouveau-rayon)
  )
  
  (princ "\n--- Configuration mise à jour ---")
  (princ (strcat "\nBloc          : " *NOM-BLOC-TCPOINT*))
  (princ (strcat "\nSuffixe       : " *SUFFIXE-CALQUE*))
  (princ (strcat "\nCalque centres: " *CALQUE-CENTRES*))
  (princ (strcat "\nCalque axes   : " *CALQUE-AXES*))
  (princ (strcat "\nRayon (m)     : " (_safe-rtos (float *RAYON-PROXIMITE*))))
  
  (princ "\n\nEXEMPLE DE CALQUES TCPOINT :")
  (princ (strcat "\n- Ligne sur 'CONTOUR'    → TCPOINT sur 'CONTOUR" *SUFFIXE-CALQUE* "'"))
  (princ (strcat "\n- Ligne sur 'AXE_ROUTE'  → TCPOINT sur 'AXE_ROUTE" *SUFFIXE-CALQUE* "'"))
  (princ (strcat "\n- Ligne sur '0'          → TCPOINT sur '0" *SUFFIXE-CALQUE* "'"))
  (princ)
)

;; ===== COMMANDE SIMPLE POUR TESTER LES CENTRES =====
(defun c:test-centres ()
  (princ "\n=== TEST DES CENTRES ===")
  (setq centres (_collect-centers))
  (if centres
    (progn
      (princ (strcat "\n" (itoa (length centres)) " centres trouvés sur calque '" *CALQUE-CENTRES* "' :"))
      (setq i 1)
      (foreach c centres
        (princ (strcat "\n  " (itoa i) ". (" (_safe-rtos (car c)) ", " (_safe-rtos (cadr c)) ")"))
        (setq i (1+ i))
      )
    )
    (princ (strcat "\nAucun centre trouvé sur le calque '" *CALQUE-CENTRES* "'"))
  )
  (princ)
)

;; ===== FONCTIONS POUR CRÉATION AUTOMATIQUE DES CENTRES =====

;; Collecte des axes pour intersection
(defun _collect-axes ( / ss n i en vo lst)
  (setq ss (ssget "_ALL" (list '(0 . "LINE,LWPOLYLINE") (cons 8 *CALQUE-AXES*))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i)
              vo (vlax-ename->vla-object en))
        (setq lst (cons vo lst))
        (setq i (1+ i)))
      (reverse lst))
    nil))

;; Calcul des intersections entre deux entités -> retourne une LISTE (x1 y1 z1 x2 y2 z2 ...)
(defun _get-intersections (ent1 ent2 / res)
  (setq res (vl-catch-all-apply 'vlax-invoke (list ent1 'IntersectWith ent2 acExtendNone)))
  (cond
    ((vl-catch-all-error-p res) nil)
    (T (_to-list res))))  ;; _to-list gère VARIANT/SAFEARRAY/LIST/NIL

;; Création automatique des centres d'intersection
(defun _create-intersection-centers (axes / doc ms centres-crees nb-axes i j ent1 ent2 intersections pt k)
  (princ "\n=== CRÉATION DES CENTRES D'INTERSECTION ===")
  
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        ms  (vla-get-ModelSpace doc)
        centres-crees '()
        nb-axes (length axes))
  
  (if *AFFICHAGE-DEBUG*
    (princ (strcat "\n" (itoa nb-axes) " axes trouvés sur calque '" *CALQUE-AXES* "'"))
  )
  
  ;; Créer/vérifier le calque des centres
  (_ensure-layer doc *CALQUE-CENTRES*)
  
  (vl-catch-all-apply 'vla-StartUndoMark (list doc))
  
  ;; Tester toutes les combinaisons d'axes
  (setq i 0)
  (while (< i nb-axes)
    (setq ent1 (nth i axes))
    (setq j (1+ i))
    (while (< j nb-axes)
      (setq ent2 (nth j axes))
      
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n  Test intersection " (itoa (1+ i)) " × " (itoa (1+ j))))
      )
      
      ;; Calculer les intersections -> liste plate (x y z ...)
      (setq intersections (_get-intersections ent1 ent2))
      
      (if intersections
        (progn
          ;; Traiter chaque point d'intersection
          (setq k 0)
          (while (< k (length intersections))
            (setq pt (list (nth k intersections) (nth (1+ k) intersections) (nth (+ k 2) intersections)))
            
            ;; Vérifier que ce point n'existe pas déjà (éviter les doublons)
            (if (not (_point-exists? pt centres-crees 0.001))
              (progn
                ;; Créer le point centre
                (_add-point ms pt *CALQUE-CENTRES*)
                (setq centres-crees (cons pt centres-crees))
                
                (if *AFFICHAGE-DEBUG*
                  (princ (strcat "\n    ✓ Centre créé à (" (_safe-rtos (car pt)) "," (_safe-rtos (cadr pt)) ")"))
                )
              )
              (if *AFFICHAGE-DEBUG*
                (princ "\n    - Point déjà existant (ignoré)")
              )
            )
            (setq k (+ k 3))  ;; Passer au point suivant (x,y,z)
          )
        )
        (if *AFFICHAGE-DEBUG*
          (princ "\n    - Aucune intersection")
        )
      )
      (setq j (1+ j))
    )
    (setq i (1+ i))
  )
  
  (vl-catch-all-apply 'vla-EndUndoMark (list doc))
  
  (princ (strcat "\n" (itoa (length centres-crees)) " centres d'intersection créés sur calque '" *CALQUE-CENTRES* "'"))
  centres-crees
)

;; Vérifier si un point existe déjà dans une liste (avec tolerance)
(defun _point-exists? (pt liste tolerance / existe p)
  (setq existe nil)
  (foreach p liste
    (if (< (_dist2d pt p) tolerance)
      (setq existe T)
    )
  )
  existe
)

;; Créer un point
(defun _add-point (space pt layer / p p3)
  (setq p3 (if (_is-pt3 pt) pt (append pt (list 0.0))))
  (setq p (vla-AddPoint space (vlax-3d-point p3)))
  (if layer (vla-put-Layer p layer))
  p)

;; ===== COMMANDE POUR CRÉER LES CENTRES D'INTERSECTION =====
(defun c:create-centres ()
  (princ "\n=== CRÉATION AUTOMATIQUE DES CENTRES ===")
  
  ;; Collecter les axes
  (setq axes (_collect-axes))
  
  (if axes
    (progn
      (princ (strcat "\n" (itoa (length axes)) " axes trouvés sur calque '" *CALQUE-AXES* "'"))
      
      ;; Créer les centres d'intersection
      (setq centres-crees (_create-intersection-centers axes))
      
      (if (> (length centres-crees) 0)
        (princ "\n✓ Centres créés avec succès !")
        (princ "\nAucune intersection trouvée.")
      )
    )
    (princ (strcat "\nAucun axe trouvé sur le calque '" *CALQUE-AXES* "'"))
  )
  
  (princ)
)

;; ===== MESSAGES DE CHARGEMENT =====
(princ "\n=== PLACE-TCPOINT.LSP v2.1 (patched) chargé ===")
(princ "\n")
(princ "\nCOMMANDES DISPONIBLES :")
(princ "\n- PLACE-TCPOINT   : Placer blocs TCPOINT aux extrémités (4 modes)")
(princ "\n- CONFIG-TCPOINT  : Configurer paramètres")
(princ "\n- TEST-CENTRES    : Tester détection des centres")
(princ "\n- CREATE-CENTRES  : Créer centres d'intersection uniquement")
(princ "\n")
(princ "\nMODES DE PLACEMENT :")
(princ "\n1. AUTOMATIQUE   : Centres existants + toutes les lignes")
(princ "\n2. SEMI-AUTO     : Centres existants + sélection manuelle")
(princ "\n3. MANUEL        : Centre manuel + sélection manuelle")
(princ "\n4. AUTO-CRÉER    : Créer centres d'intersection + placement auto")
(princ "\n")
(princ "\nCALQUES DYNAMIQUES :")
(princ (strcat "\n- Les TCPOINT sont placés sur : [CalqueLigne]" *SUFFIXE-CALQUE*))
(princ "\n- Exemple : ligne sur 'CONTOUR' → TCPOINT sur 'CONTOUR_tete'")
(princ "\n")
(princ (strcat "\nPARAMÈTRES ACTUELS :"))
(princ (strcat "\n- Bloc TCPOINT    : " *NOM-BLOC-TCPOINT*))
(princ (strcat "\n- Suffixe calque  : " *SUFFIXE-CALQUE*))
(princ (strcat "\n- Calque centres  : " *CALQUE-CENTRES*))
(princ (strcat "\n- Calque axes     : " *CALQUE-AXES*))
(princ (strcat "\n- Rayon proximité : " (_safe-rtos (float *RAYON-PROXIMITE*)) " m"))
(princ (strcat "\n- Debug           : " (if *AFFICHAGE-DEBUG* "ACTIVÉ" "DÉSACTIVÉ")))
(princ "\n")
(princ "\nUSAGE : Tapez PLACE-TCPOINT dans AutoCAD")
(princ)
