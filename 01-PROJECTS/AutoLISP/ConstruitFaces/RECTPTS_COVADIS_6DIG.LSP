;; RECTPTS_CONTOURS_ONLY.LSP — version autonome minimale
(vl-load-com)

;; ====== Options minimales (si pas déjà définies ailleurs) ======
(if (not (boundp '*RP_LAYER_EDGES*)) (setq *RP_LAYER_EDGES* "REMBLAIS-COUPES-ARETES"))

;; ====== Helpers couche & 3D plines ======
(defun rp:ensure-layer (name / doc lays)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        lays (vla-get-Layers doc))
  (if (not (tblsearch "LAYER" name)) (vla-add lays name))
  name)

(defun rp:ensure-3d (pt)
  (if (and (= (type pt) 'LIST) (= (length pt) 2))
    (list (car pt) (cadr pt) 0.0)
    pt))

;; POLYLINE 3D valide : entête (70 . 8), VERTEX (70 . 32)
(defun rp:mk-pline3d (pts)
  (if (and pts (> (length pts) 1))
    (progn
      (entmake (list (cons 0 "POLYLINE") (cons 8 *RP_LAYER_EDGES*) (cons 66 1) (cons 70 8)))
      (foreach p pts
        (entmake (list (cons 0 "VERTEX") (cons 8 *RP_LAYER_EDGES*) (cons 10 (rp:ensure-3d p)) (cons 70 32))))
      (entmake (list (cons 0 "SEQEND") (cons 8 *RP_LAYER_EDGES*))))))

(defun rp:mk-pline3d-closed (pts)
  (if (and pts (> (length pts) 2))
    (rp:mk-pline3d (append pts (list (car pts))))))

(defun rp:outline-quad (p1 p2 p3 p4)
  (rp:mk-pline3d-closed (list p1 p2 p3 p4)))

;; ====== Lecture ATTRIB / point d’insertion ======
(defun rp:trim (s) (if (and s (= (type s) 'STR)) (vl-string-trim " \t\r\n" s) nil))
(defun rp:uc   (s) (if (and s (= (type s) 'STR)) (strcase s) nil))

(defun rp:get-attrib-text (insEnt tag / e txt tg dxf)
  (setq tag (rp:uc tag) e (entnext insEnt) txt nil)
  (while (and e (not txt))
    (setq dxf (entget e))
    (cond
      ((= (cdr (assoc 0 dxf)) "SEQEND") (setq e nil))
      ((= (cdr (assoc 0 dxf)) "ATTRIB")
       (setq tg (rp:uc (cdr (assoc 2 dxf))))
       (if (= tg tag) (setq txt (rp:trim (cdr (assoc 1 dxf)))))
       (setq e (entnext e)))
      (t (setq e (entnext e)))))
  txt)

(defun rp:pt-of-entity (e / d p ztxt zval)
  (setq d (entget e) p (cdr (assoc 10 d)))
  (if p
    (progn
      (setq p (trans p 0 1)) ; UCS→WCS
      (setq ztxt (or (rp:get-attrib-text e "ALT")
                     (rp:get-attrib-text e "Z")
                     (rp:get-attrib-text e "ELEV")))
      (if (and ztxt (= (type ztxt) 'STR))
        (progn (setq zval (atof ztxt))
               (if (numberp zval) (list (car p) (cadr p) zval) p))
        p))
    nil))

;; ====== Parsing matricules (formats 6ch & décimaux & 4+1) ======
(defun rp:parse-mat (s / S dashPos idpart idlen id4 tval side)
  (if s
    (progn
      (setq S (rp:uc (rp:trim s)))
      (setq dashPos (vl-string-search "-" S))
      (if (and dashPos (>= (strlen S) (+ dashPos 2)))
        (progn
          (setq idpart (rp:trim (substr S 1 dashPos))
                idlen  (strlen idpart)
                side   (substr S (+ dashPos 2) 1))
          (if (and (wcmatch side "[GAD]") (wcmatch idpart "#*"))
            (cond
              ((= idlen 5)
               (setq id4  (substr idpart 1 4)
                     tval (substr idpart 5 1))
               (if (and (wcmatch id4 "####") (wcmatch tval "[01]")) (list id4 tval side)))
              ((= idlen 4)
               (if (wcmatch idpart "####") (list idpart nil side))))))))))
(defun rp:parse-mat-extended (s / S dashPos idpart side dotPos beforeDot)
  (if s
    (progn
      (setq S (rp:uc (rp:trim s))
            S (vl-string-translate " " "" S))
      (if (wcmatch S "######-[GAD]*")
        (progn (setq idpart (substr S 1 6) side (substr S 8 1))
               (list idpart nil side))
        (if (and (setq dotPos (vl-string-search "." S))
                 (setq dashPos (vl-string-search "-" S))
                 (> dashPos dotPos))
          (progn (setq beforeDot (substr S 1 dashPos)
                       side      (substr S (+ dashPos 2) 1))
                 (if (wcmatch side "[GAD]") (list beforeDot nil side) nil))
          (rp:parse-mat S))))))

(defun rp:normalize-id (rawid / s codes p4)
  (setq s (rp:uc (rp:trim rawid)))
  (if (not s) nil
    (progn
      ;; regrouper par 4 chiffres si possible
      (setq s (vl-string-translate ". " "" s)
            codes (vl-string->list s)
            p4 '())
      (foreach c codes
        (if (and (numberp c) (wcmatch (chr c) "#") (< (length p4) 4))
          (setq p4 (append p4 (list c)))))
      (if (= (length p4) 4) (vl-list->string p4) rawid))))

(defun rp:guess-matricule (e / v d next txt parsed)
  (setq next (entnext e) v nil)
  (while (and next
              (setq d (entget next))
              (not (= (cdr (assoc 0 d)) "SEQEND"))
              (not v))
    (if (= (cdr (assoc 0 d)) "ATTRIB")
      (progn
        (setq txt (rp:trim (cdr (assoc 1 d))))
        (if (and txt (= (type txt) 'STR))
          (progn (setq parsed (rp:parse-mat-extended txt))
                 (if parsed (setq v txt))))))
    (setq next (entnext next)))
  (if (not v)
    (progn
      (setq v (cdr (assoc 2 (entget e)))) ; nom du bloc comme dernier recours
      (if (and v (= (type v) 'STR) (not (rp:parse-mat-extended v))) (setq v nil))))
  v)

;; ====== Maps simples par id4 ======
(defun rp:byid-put (by k tag pt / rec newby)
  (setq rec (cdr (assoc k by)))
  (if (not (and rec (= (type rec) 'LIST))) (setq rec '()))
  (if (assoc tag rec)
    (setq rec (subst (cons tag pt) (assoc tag rec) rec))
    (setq rec (cons (cons tag pt) rec)))
  (setq newby (vl-remove (assoc k by) by))
  (cons (cons k rec) newby))

(defun rp:byid-get (by k tag)
  (cdr (assoc tag (cdr (assoc k by)))))

(defun rp:sort-keys-numeric (alist-or-keys)
  (vl-sort
    (if (and alist-or-keys (listp (car alist-or-keys)))
      (mapcar 'car alist-or-keys) alist-or-keys)
    (function (lambda (a b) (< (atoi a) (atoi b))))))

(defun rp:collect-points (ss / i e mat parsed id4 tval side pt by)
  (setq i 0 by '())
  (while (< i (sslength ss))
    (setq e (ssname ss i)
          mat (rp:guess-matricule e)
          pt  (rp:pt-of-entity e))
    (if (and mat pt (setq parsed (rp:parse-mat-extended mat)))
      (progn
        (setq id4  (rp:normalize-id (nth 0 parsed))
              tval (nth 1 parsed)
              side (rp:uc (nth 2 parsed)))
        (if (and side (> (strlen side) 1)) (setq side (substr side 1 1)))
        (if (and id4 (wcmatch side "[GAD]") (wcmatch tval "[01]"))
          (setq by (rp:byid-put by id4 (strcat side tval) pt)))))
    (setq i (1+ i)))
  by)

;; ====== COMMANDE : RECTPTS_CONTOURS ======
(defun c:RECTPTS_CONTOURS (/ ss by keys len idx
                             k1 k2 G0i G1i A0i A1i D0i D1i
                             G0j G1j A0j A1j D0j D1j
                             nclosed nlisses)
  (prompt "\n[RECTPTS_CONTOURS] Contours fermés (quads) + lisses verticales…")
  (rp:ensure-layer *RP_LAYER_EDGES*)
  (setq ss (ssget '((0 . "INSERT"))))
  (if (not ss) (setq ss (ssget "X" '((0 . "INSERT")))))
  (if (not ss)
    (prompt "\nAucun bloc d'insertion trouvé.")
    (progn
      (setq by (rp:collect-points ss)
            keys (rp:sort-keys-numeric by)
            len (length keys)
            idx 0
            nclosed 0 nlisses 0)
      ;; contours entre profils consécutifs
      (while (< idx (1- len))
        (setq k1 (nth idx keys)    k2 (nth (1+ idx) keys))
        (setq G0i (rp:byid-get by k1 "G0")  G1i (rp:byid-get by k1 "G1")
              A0i (rp:byid-get by k1 "A0")  A1i (rp:byid-get by k1 "A1")
              D0i (rp:byid-get by k1 "D0")  D1i (rp:byid-get by k1 "D1"))
        (setq G0j (rp:byid-get by k2 "G0")  G1j (rp:byid-get by k2 "G1")
              A0j (rp:byid-get by k2 "A0")  A1j (rp:byid-get by k2 "A1")
              D0j (rp:byid-get by k2 "D0")  D1j (rp:byid-get by k2 "D1"))
        (if (and A0i A1i A0j A1j) (progn (rp:outline-quad A0i A1i A1j A0j) (setq nclosed (1+ nclosed))))
        (if (and G0i G1i G0j G1j) (progn (rp:outline-quad G0i G1i G1j G0j) (setq nclosed (1+ nclosed))))
        (if (and D0i D1i D0j D1j) (progn (rp:outline-quad D0i D1i D1j D0j) (setq nclosed (1+ nclosed))))
        (if (and G0i A0i G0j A0j) (progn (rp:outline-quad G0i A0i A0j G0j) (setq nclosed (1+ nclosed))))
        (if (and A0i D0i A0j D0j) (progn (rp:outline-quad A0i D0i D0j A0j) (setq nclosed (1+ nclosed))))
        (if (and G1i A1i G1j A1j) (progn (rp:outline-quad G1i A1i A1j G1j) (setq nclosed (1+ nclosed))))
        (if (and A1i D1i A1j D1j) (progn (rp:outline-quad A1i D1i D1j A1j) (setq nclosed (1+ nclosed))))
        (setq idx (1+ idx)))
      ;; lisses verticales par profil
      (foreach k1 keys
        (if (and (rp:byid-get by k1 "G0") (rp:byid-get by k1 "G1"))
          (progn (rp:mk-pline3d (list (rp:byid-get by k1 "G0") (rp:byid-get by k1 "G1"))) (setq nlisses (1+ nlisses))))
        (if (and (rp:byid-get by k1 "A0") (rp:byid-get by k1 "A1"))
          (progn (rp:mk-pline3d (list (rp:byid-get by k1 "A0") (rp:byid-get by k1 "A1"))) (setq nlisses (1+ nlisses))))
        (if (and (rp:byid-get by k1 "D0") (rp:byid-get by k1 "D1"))
          (progn (rp:mk-pline3d (list (rp:byid-get by k1 "D0") (rp:byid-get by k1 "D1"))) (setq nlisses (1+ nlisses)))))
      (prompt (strcat
        "\n[RECTPTS_CONTOURS] RÉSUMÉ : Contours=" (itoa nclosed)
        "  |  Lisses=" (itoa nlisses)
        "  |  Calque=" *RP_LAYER_EDGES*))))
  (princ))

(princ "\nRECTPTS_CONTOURS_ONLY chargé. Commande : RECTPTS_CONTOURS")
(princ)
