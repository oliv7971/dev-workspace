;; =============================================================
;; PLACE-TCPOINT.LSP  v2.6  (robuste, parentheses verifiees)
;; =============================================================

(vl-load-com)
(if (not (boundp 'acExtendNone)) (setq acExtendNone 0))

;; ---------- Parametres ----------
(setq *NOM-BLOC-TCPOINT* "TCPOINT")
(setq *SUFFIXE-CALQUE* "_tete")
(setq *CALQUE-CENTRES* "_INTERSEC_AXE_2D")
(setq *CALQUE-AXES* "INS_GC_GAL_Galeries_Axes")
(setq *RAYON-PROXIMITE* 10.0)
(setq *AFFICHAGE-DEBUG* T)

;; ---------- Utils ----------
(defun _safe-rtos (x) (if (numberp x) (rtos x 2 3) (vl-princ-to-string x)))

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

(defun _sanitize-pt (v / l x y z)
  (setq l (_to-list v))
  (setq x (if (and l (numberp (nth 0 l))) (nth 0 l) 0.0))
  (setq y (if (and l (>= (length l) 2) (numberp (nth 1 l))) (nth 1 l) 0.0))
  (setq z (if (and l (>= (length l) 3) (numberp (nth 2 l))) (nth 2 l) 0.0))
  (list x y z))

(defun _pt3 (v) (_sanitize-pt v))

(defun _safe-dist2d (p q)
  (if (and (_is-pt2 p) (_is-pt2 q))
    (sqrt (+ (expt (- (car p) (car q)) 2)
             (expt (- (cadr p) (cadr q)) 2)))
    1e99))

(defun _dist2d-pt-seg (c a b / ax ay bx by cx cy abx aby acx acy ab2 t1 px py)
  (if (and (_is-pt2 c) (_is-pt2 a) (_is-pt2 b))
    (progn
      (setq ax (car a) ay (cadr a) bx (car b) by (cadr b) cx (car c) cy (cadr c))
      (setq abx (- bx ax) aby (- by ay) acx (- cx ax) acy (- cy ay))
      (setq ab2 (+ (* abx abx) (* aby aby)))
      (if (and (numberp ab2) (/= ab2 0.0))
        (progn
          (setq t1 (/ (+ (* acx abx) (* acy aby)) ab2))
          (cond
            ((and (numberp t1) (< t1 0.0)) (_safe-dist2d c a))
            ((and (numberp t1) (> t1 1.0)) (_safe-dist2d c b))
            (T (setq px (+ ax (* t1 abx)) py (+ ay (* t1 aby)))
               (_safe-dist2d c (list px py 0.0)))))
        (_safe-dist2d c a)))
    1e99))

(defun _has-block? (name) (if (tblsearch "BLOCK" name) T nil))

;; ---------- Geometrie entites ----------
(defun _ends-line (o / sp ep)
  (setq sp (_pt3 (vla-get-StartPoint o))
        ep (_pt3 (vla-get-EndPoint   o)))
  (list sp ep))

(defun _ends-lwpoly (o / coords n elev)
  (setq coords (_to-list (vla-get-Coordinates o)))
  (setq n (if coords (length coords) 0))
  (setq elev (or (vla-get-Elevation o) 0.0))
  (if (>= n 4)
    (list
      (list (nth 0 coords) (nth 1 coords) elev)
      (list (nth (- n 2) coords) (nth (- n 1) coords) elev))
    nil))

(defun _dist-center-line (c o / ends)
  (setq ends (_ends-line o))
  (if ends (_dist2d-pt-seg c (car ends) (cadr ends)) 1e99))

(defun _dist-center-lwpoly (c o / coords n i dmin a b d)
  (setq coords (_to-list (vla-get-Coordinates o)))
  (setq n (if coords (length coords) 0))
  (setq dmin 1e99 i 0)
  (while (< (+ i 3) n)
    (setq a (list (nth i coords) (nth (1+ i) coords) 0.0))
    (setq b (list (nth (+ i 2) coords) (nth (+ i 3) coords) 0.0))
    (setq d (_dist2d-pt-seg c a b))
    (if (and (numberp d) (< d dmin)) (setq dmin d))
    (setq i (+ i 2)))
  dmin)

;; ---------- Collecte ----------
(defun _collect-centers (/ ss n i en vo p lst)
  (setq ss (ssget "_ALL" (list '(0 . "POINT") (cons 8 *CALQUE-CENTRES*))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i))
        (setq vo (vlax-ename->vla-object en))
        (setq p (_sanitize-pt (vla-get-Coordinates vo)))
        (setq lst (cons p lst))
        (setq i (1+ i)))
      (reverse lst))
    nil))

(defun _collect-entities (/ ss n i en vo lst)
  (setq ss (ssget "_ALL" '((0 . "LINE,LWPOLYLINE"))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i))
        (setq vo (vlax-ename->vla-object en))
        (setq lst (cons vo lst))
        (setq i (1+ i)))
      (reverse lst))
    nil))

;; ---------- Layers / Insertions ----------
(defun _ensure-layer (doc name / layrs lyr)
  (setq layrs (vla-get-Layers doc))
  (if (not (tblsearch "LAYER" name))
    (setq lyr (vla-Add layrs name))
    (setq lyr (vla-Item layrs name)))
  lyr)

(defun _add-blockref-dynamic (space name pt calque-ligne / br calque-cible p3)
  (setq p3 (_sanitize-pt pt))
  (setq calque-cible (strcat calque-ligne *SUFFIXE-CALQUE*))
  (if (not (tblsearch "LAYER" calque-cible)) (command "._LAYER" "_M" calque-cible ""))
  (setq br (vla-InsertBlock space (vlax-3d-point p3) name 1.0 1.0 1.0 0.0))
  (if calque-cible (vla-put-Layer br calque-cible))
  br)

;; ---------- Commande principale ----------
(defun c:place-tcpoint (/ doc ms tolR centres liste-entites mode-choisi
                          ss-entites liste-lignes centre axes centres-crees)
  (princ "\n=== PLACE-TCPOINT v2.6 ===")
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq ms  (vla-get-ModelSpace doc))
  (setq tolR (getreal (strcat "\nRayon proximite (m) <" (_safe-rtos (float *RAYON-PROXIMITE*)) ">: ")))
  (if (not (and (numberp tolR) (> tolR 0.0))) (setq tolR (float *RAYON-PROXIMITE*)))
  (setq tolR (float tolR))
  (princ "\n1=Auto  2=Semi-auto  3=Manuel  4=Auto-creer centres")
  (setq mode-choisi (getint "\nChoisissez le mode (1/2/3/4) <1>: "))
  (if (not mode-choisi) (setq mode-choisi 1))
  (cond
    ((= mode-choisi 1)
     (setq centres (_collect-centers))
     (setq liste-entites (_collect-entities))
     (if (and centres liste-entites)
       (placer-tcpoints-auto liste-entites centres tolR)
       (progn
         (if (not centres) (princ (strcat "\nAucun centre sur " *CALQUE-CENTRES*)))
         (if (not liste-entites) (princ "\nAucune ligne/polyligne trouvee")))))
    ((= mode-choisi 2)
     (setq centres (_collect-centers))
     (if centres
       (progn
         (princ "\nSelectionnez les lignes/polylignes...")
         (setq ss-entites (ssget))
         (if ss-entites
           (progn
             (setq liste-entites (convertir-selection-en-vla ss-entites))
             (placer-tcpoints-auto liste-entites centres tolR))
           (princ "\nAucune selection.")))
       (princ (strcat "\nAucun centre sur " *CALQUE-CENTRES*))))
    ((= mode-choisi 3)
     (princ "\nSelectionnez les lignes et polylignes...")
     (setq ss-entites (ssget))
     (if ss-entites
       (progn
         (setq liste-lignes (filtrer-lignes-polylignes ss-entites))
         (if (> (length liste-lignes) 0)
           (progn
             (princ (strcat "\n" (itoa (length liste-lignes)) " entites trouvees"))
             (setq centre (getpoint "\nCentre de reference : "))
             (if centre (placer-tcpoints liste-lignes centre) (princ "\nAnnule.")))
           (princ "\nAucune ligne ou polyligne trouvee")))
       (princ "\nAucune selection.")))
    ((= mode-choisi 4)
     (setq axes (_collect-axes))
     (if axes
       (progn
         (setq centres-crees (_create-intersection-centers axes))
         (if (> (length centres-crees) 0)
           (progn
             (setq liste-entites (_collect-entities))
             (if liste-entites
               (placer-tcpoints-auto liste-entites centres-crees tolR)
               (princ "\nAucune ligne/polyligne pour placement TCPOINT.")))
           (princ "\nAucune intersection trouvee.")))
       (princ (strcat "\nAucun axe sur " *CALQUE-AXES*))))
    (T (princ "\nMode invalide.")))
  (princ))

;; ---------- Conversion selection ----------
(defun convertir-selection-en-vla (ss / liste i ent)
  (setq liste '() i 0)
  (repeat (sslength ss)
    (setq ent (vlax-ename->vla-object (ssname ss i)))
    (setq liste (cons ent liste))
    (setq i (1+ i)))
  (reverse liste))

;; ---------- Placement auto ----------
(defun placer-tcpoints-auto (liste-entites centres tolR / doc ms created scanned on ends dmin c* d* dc p1 p2 d1 d2 pin calque-ligne calques-crees calque-cible)
  (princ "\n=== Placement (rayon proximite) ===")
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq ms  (vla-get-ModelSpace doc))
  (setq calques-crees '() created 0 scanned 0)
  (if (not (_has-block? *NOM-BLOC-TCPOINT*)) (progn (princ (strcat "\nBloc manquant: " *NOM-BLOC-TCPOINT*)) (exit)))
  (vl-catch-all-apply 'vla-StartUndoMark (list doc))
  (foreach o liste-entites
    (setq scanned (1+ scanned) on (vla-get-ObjectName o) ends nil dmin 1e99 calque-ligne (vla-get-Layer o))
    (cond
      ((= on "AcDbLine")
       (setq ends (_ends-line o))
       (foreach c centres (setq dc (_dist-center-line c o)) (if (and (numberp dc) (< dc dmin)) (setq dmin dc))))
      ((= on "AcDbPolyline")
       (if (eq (vla-get-Closed o) :vlax-false)
         (progn
           (setq ends (_ends-lwpoly o))
           (foreach c centres (setq dc (_dist-center-lwpoly c o)) (if (and (numberp dc) (< dc dmin)) (setq dmin dc))))
         (setq ends nil))))
    (if (and ends (numberp dmin) (numberp tolR) (<= dmin tolR))
      (progn
        (setq c* nil d* 1e99)
        (foreach c centres
          (if (_is-pt2 c)
            (progn
              (setq dc (if (= on "AcDbLine") (_dist-center-line c o) (_dist-center-lwpoly c o)))
              (if (and (numberp dc) (< dc d*)) (setq d* dc c* c)))))
        (if (_is-pt2 c*)
          (progn
            (setq p1 (car ends) p2 (cadr ends))
            (setq d1 (_safe-dist2d p1 c*) d2 (_safe-dist2d p2 c*))
            (setq pin (if (< d1 d2) p1 p2))
            (_add-blockref-dynamic ms *NOM-BLOC-TCPOINT* pin calque-ligne)
            (setq created (1+ created))
            (setq calque-cible (strcat calque-ligne *SUFFIXE-CALQUE*))
            (if (not (member calque-cible calques-crees)) (setq calques-crees (cons calque-cible calques-crees))))
          (if *AFFICHAGE-DEBUG* (princ "\n  Centre invalide - ignore."))))
      (if *AFFICHAGE-DEBUG* (princ (strcat "\n  Ignore: dmin=" (_safe-rtos dmin) " > tolR=" (_safe-rtos tolR))))))
  (vl-catch-all-apply 'vla-EndUndoMark (list doc))
  (princ (strcat "\n-- Resume --  Entites: " (itoa scanned) " | Places: " (itoa created) " | Rayon: " (_safe-rtos tolR)))
  (if *AFFICHAGE-DEBUG*
    (progn
      (princ (strcat "\nCalques utilises (" (itoa (length calques-crees)) "):"))
      (foreach cal (reverse calques-crees) (princ (strcat "\n  - " cal)))))
  (princ "\nTermine !")
  (princ))

;; ---------- Manuel ----------
(defun filtrer-lignes-polylignes (ss-source / liste-lignes i ent data type-obj pt1 pt2 vertices)
  (setq liste-lignes '() i 0)
  (repeat (sslength ss-source)
    (setq ent (ssname ss-source i))
    (setq data (entget ent))
    (setq type-obj (cdr (assoc 0 data)))
    (cond
      ((= type-obj "LINE")
       (setq pt1 (cdr (assoc 10 data)))
       (setq pt2 (cdr (assoc 11 data)))
       (setq liste-lignes (cons (list ent "LINE" pt1 pt2) liste-lignes)))
      ((= type-obj "LWPOLYLINE")
       (setq vertices (extraire-vertices-polyligne data))
       (if vertices (setq liste-lignes (cons (list ent "LWPOLYLINE" (car vertices) (car (last vertices))) liste-lignes)))))
    (setq i (1+ i)))
  (reverse liste-lignes))

(defun extraire-vertices-polyligne (data / vertices)
  (setq vertices '())
  (foreach item data (if (= (car item) 10) (setq vertices (append vertices (list (cdr item))))))
  vertices)

(defun placer-tcpoints (liste-lignes centre / compteur nb-places ent type-ligne pt1 pt2 dist1 dist2 calque-ligne)
  (princ "\nPlacement manuel des blocs TCPOINT...")
  (if (not (_has-block? *NOM-BLOC-TCPOINT*)) (progn (princ (strcat "\nBloc manquant: " *NOM-BLOC-TCPOINT*)) (exit)))
  (setq compteur 0 nb-places 0)
  (foreach ligne liste-lignes
    (setq compteur (1+ compteur))
    (setq ent (car ligne) type-ligne (cadr ligne) pt1 (caddr ligne) pt2 (cadddr ligne))
    (setq calque-ligne (cdr (assoc 8 (entget ent))))
    (setq dist1 (distance pt1 centre) dist2 (distance pt2 centre))
    (if (< dist1 dist2) (placer-bloc-tcpoint-dynamique pt1 calque-ligne) (placer-bloc-tcpoint-dynamique pt2 calque-ligne))
    (setq nb-places (1+ nb-places)))
  (princ (strcat "\nLignes/polylignes : " (itoa compteur) " | Places : " (itoa nb-places)))
  (princ "\nTermine !")
  (princ))

(defun placer-bloc-tcpoint-dynamique (point calque-ligne / calque-actuel calque-cible p3)
  (setq calque-actuel (getvar "CLAYER"))
  (setq calque-cible (strcat calque-ligne *SUFFIXE-CALQUE*))
  (if (not (tblsearch "LAYER" calque-cible)) (command "._LAYER" "_M" calque-cible ""))
  (setq p3 (_sanitize-pt point))
  (setvar "CLAYER" calque-cible)
  (command "._INSERT" *NOM-BLOC-TCPOINT* p3 1 1 0)
  (setvar "CLAYER" calque-actuel))

;; ---------- Axes / Intersections ----------
(defun _collect-axes (/ ss n i en vo lst)
  (setq ss (ssget "_ALL" (list '(0 . "LINE,LWPOLYLINE") (cons 8 *CALQUE-AXES*))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i))
        (setq vo (vlax-ename->vla-object en))
        (setq lst (cons vo lst))
        (setq i (1+ i)))
      (reverse lst))
    nil))

(defun _get-intersections (ent1 ent2 / res)
  (setq res (vl-catch-all-apply 'vlax-invoke (list ent1 'IntersectWith ent2 acExtendNone)))
  (cond
    ((vl-catch-all-error-p res) nil)
    (T (_to-list res))))

(defun _add-point (space pt layer / p3 p)
  (setq p3 (_sanitize-pt pt))
  (setq p (vla-AddPoint space (vlax-3d-point p3)))
  (if layer (vla-put-Layer p layer))
  p)

(defun _point-exists? (pt liste tolerance / existe p)
  (setq existe nil)
  (foreach p liste
    (if (and (_is-pt2 pt) (_is-pt2 p) (numberp tolerance)
             (< (_safe-dist2d pt p) tolerance))
      (setq existe T)))
  existe)

(defun _create-intersection-centers (axes / doc ms centres-crees nb-axes i j ent1 ent2 intersections pt k)
  (princ "\n=== Creation centres d'intersection ===")
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq ms  (vla-get-ModelSpace doc))
  (setq centres-crees '())
  (setq nb-axes (length axes))
  (_ensure-layer doc *CALQUE-CENTRES*)
  (vl-catch-all-apply 'vla-StartUndoMark (list doc))
  (setq i 0)
  (while (< i nb-axes)
    (setq ent1 (nth i axes))
    (setq j (1+ i))
    (while (< j nb-axes)
      (setq ent2 (nth j axes))
      (setq intersections (_get-intersections ent1 ent2))
      (if intersections
        (progn
          (setq k 0)
          (while (< k (length intersections))
            (setq pt (list (nth k intersections) (nth (1+ k) intersections) (nth (+ k 2) intersections)))
            (if (not (_point-exists? pt centres-crees 0.001))
              (progn
                (_add-point ms pt *CALQUE-CENTRES*)
                (setq centres-crees (cons pt centres-crees))))
            (setq k (+ k 3)))))  ;; fin while k
      (setq j (1+ j)))           ;; fin while j
    (setq i (1+ i)))             ;; fin while i
  (vl-catch-all-apply 'vla-EndUndoMark (list doc))
  (princ (strcat "\nCentres crees : " (itoa (length centres-crees))))
  centres-crees)

;; ---------- Config & Test ----------
(defun c:config-tcpoint (/ v)
  (princ "\n=== CONFIG-TCPOINT ===")
  (princ (strcat "\nBloc          : " *NOM-BLOC-TCPOINT*))
  (princ (strcat "\nSuffixe calq. : " *SUFFIXE-CALQUE*))
  (princ (strcat "\nCalque centres: " *CALQUE-CENTRES*))
  (princ (strcat "\nCalque axes   : " *CALQUE-AXES*))
  (princ (strcat "\nRayon (m)     : " (_safe-rtos (float *RAYON-PROXIMITE*))))
  (setq v (getstring T "\nNouveau nom de bloc (Entree=Garder): ")) (if (> (strlen v) 0) (setq *NOM-BLOC-TCPOINT* v))
  (setq v (getstring T "\nNouveau suffixe calque (Entree=Garder): ")) (if (> (strlen v) 0) (setq *SUFFIXE-CALQUE* v))
  (setq v (getstring T "\nNouveau calque centres (Entree=Garder): ")) (if (> (strlen v) 0) (setq *CALQUE-CENTRES* v))
  (setq v (getstring T "\nNouveau calque axes (Entree=Garder): ")) (if (> (strlen v) 0) (setq *CALQUE-AXES* v))
  (setq v (getreal "\nNouveau rayon (Entree=Garder): ")) (if (and (numberp v) (> v 0.0)) (setq *RAYON-PROXIMITE* v))
  (princ "\nConfiguration mise a jour.")
  (princ))

(defun c:test-centres (/ centres i)
  (princ "\n=== TEST-CENTRES ===")
  (setq centres (_collect-centers))
  (if centres
    (progn
      (princ (strcat "\n" (itoa (length centres)) " centre(s) :"))
      (setq i 1)
      (foreach c centres
        (princ (strcat "\n  " (itoa i) ". (" (_safe-rtos (car c)) ", " (_safe-rtos (cadr c)) ")"))
        (setq i (1+ i))))
    (princ (strcat "\nAucun centre sur " *CALQUE-CENTRES*)))
  (princ))

(defun c:create-centres ()  ;; utilitaire autonome si besoin
  (setq axes (_collect-axes))
  (if axes
    (_create-intersection-centers axes)
    (princ (strcat "\nAucun axe sur " *CALQUE-AXES*)))
  (princ))

;; ---------- Message de chargement ----------
(princ "\n=== PLACE-TCPOINT v2.6 charge ===")
(princ "\nCommandes: PLACE-TCPOINT | CONFIG-TCPOINT | TEST-CENTRES | CREATE-CENTRES")
(princ)
