;;; ARC2SEG (gile) 06/03/09
;;; Transforme les arcs, cercles et polyarcs en polylignes constituées de segments droits
;;; Les Xdatas sont copiées dans les nouveaux objet ainsi que les données d'objet MAP
;;; (copy_data.lsp doit être chargée)

(defun c:Arc2Seg (/ arc2pol pol2pol seg del org ss n ent elst)

  ;; Retourne la liste dxf de la polyligne (d'après un arc ou un cercle)
  (defun arc2pol
	 (elst seg org / closed alpha delta cen elv rad lay nlst)
    (and (= (cdr (assoc 0 elst)) "CIRCLE") (setq closed T))
    (setq alpha	(if closed
		  (* pi 2)
		  (cdr (assoc 51 elst))
		)
	  delta	(if closed
		  (/ alpha seg)
		  (/ (ang<2pi (- alpha (cdr (assoc 50 elst)))) seg)
		)
	  cen	(cdr (assoc 10 elst))
	  elv	(caddr cen)
	  cen	(list (car cen) (cadr cen))
	  rad	(cdr (assoc 40 elst))
	  lay	(if org
		  (assoc 8 elst)
		  (cons 8 (getvar "CLAYER"))
		)
	  nlst	(vl-remove-if-not
		  (function (lambda (x) (member (car x) '(210 -3))))
		  elst
		)
	  nlst	(cons (cons 10 (polar cen alpha rad)) nlst)
    )
    (repeat (if	closed
	      (1- seg)
	      seg
	    )
      (setq
	nlst (cons (cons 10
			 (polar cen (setq alpha (- alpha delta)) rad)
		   )
		   nlst
	     )
      )
    )
    (setq nlst
	   (cons '(0 . "LWPOLYLINE")
		 (cons '(100 . "AcDbEntity")
		       (cons (cons 410 (getvar "CTAB"))
			     (cons lay
				   (cons '(100 . "AcDbPolyline")
					 (cons (cons 90
						     (if closed
						       seg
						       (1+ seg)
						     )
					       )
					       (cons (cons 70
							   (if closed
							     1
							     0
							   )
						     )
						     (cons (cons 38 elv) nlst)
					       )
					 )
				   )
			     )
		       )
		 )
	   )
    )
  )

  ;; Retourne la liste dxf de la polyligne modifiée (d'après une polyligne)

  (defun pol2pol (elst	seg   org   /	  cnt	closed	    nlst  p0
		  p1	p2    bu    larg  inc	bdata delta cen	  rad
		  alpha	n
		 )
    (setq closed (logand 1 (cdr (assoc 70 elst)))
	  cnt	 0
    )
    (and (= closed 1) (setq p0 (cdr (assoc 10 elst))))
    (while elst
      (if (= (caar elst) 10)
	(progn
	  (setq	p1 (cdar elst)
		p2 (cdr (assoc 10 (cdr elst)))
		bu (cdr (assoc 42 elst))
	  )
	  (if (or (= 0 bu)
		  (and (zerop closed) (null p2))
	      )
	    (setq nlst (cons (cadddr elst)
			     (cons (caddr elst)
				   (cons (cadr elst)
					 (cons (car elst) nlst)
				   )
			     )
		       )
		  elst (cddddr elst)
	    )
	    (progn
	      (and (not p2) (= closed 1) (setq p2 p0))
	      (setq larg  (cdr (assoc 40 elst))
		    inc	  (/ (- (cdr (assoc 41 elst)) larg) seg)
		    bdata (BulgeData bu p1 p2)
		    delta (/ (car bdata) seg)
		    rad	  (abs (cadr bdata))
		    cen	  (caddr bdata)
		    alpha (angle cen p1)
		    n	  0
		    cnt	  (+ cnt seg -1)
	      )
	      (while (< n seg)
		(setq nlst (cons
			     (cons 10
				   (polar cen
					  (+ alpha (* delta n))
					  rad
				   )
			     )
			     nlst
			   )
		      nlst (cons (cons 40 larg) nlst)
		      nlst (cons (cons 41 (setq larg (+ larg inc))) nlst)
		      nlst (cons '(42 . 0.0) nlst)
		      n	   (1+ n)
		)
	      )
	      (setq elst (cddddr elst))
	    )
	  )
	)
	(setq nlst (cons (car elst) nlst)
	      elst (cdr elst)
	)
      )
    )
    (or	org
	(setq nlst (subst (cons 8 (getvar "CLAYER")) (assoc 8 nlst) nlst))
    )
    ((lambda (dxf90)
       (subst (cons 90 (+ (cdr dxf90) cnt))
	      dxf90
	      (reverse (subst '(42 . 0.0) (assoc 42 nlst) nlst))
       )
     )
      (assoc 90 nlst)
    )
  )

  ;; Fonction principale

  (or (getenv "SegmentsNumberPerCircle")
      (setenv "SegmentsNumberPerCircle" "64")
  )
  (initget 6)
  (if
    (setq seg (getint
		(strcat	"\nNombre de segments par arc <"
			(getenv "SegmentsNumberPerCircle")
			">: "

		)
	      )
    )
     (setenv "SegmentsNumberPerCircle" (itoa seg))
     (setq seg (atoi (getenv "SegmentsNumberPerCircle")))
  )
  (initget "Oui Non")
  (if (= "Oui"
	 (getkword "\nEffacer les objets source [Oui/Non] ? <N>: ")
      )
    (setq del T)
  )
  (initget "Courant Origine")
  (if (= "Origine"
	 (getkword
	   "\nCalque des nouveaux objets [Courant/Origine] ? <C>: "
	 )
      )
    (setq org T)
  )
  (prompt
    "\nSélectionner les objets à traiter ou <tous>."
  )
  (and
    (or	(setq ss (ssget '((0 . "ARC,CIRCLE,LWPOLYLINE"))))
	(setq ss (ssget "_X" '((0 . "ARC,CIRCLE,LWPOLYLINE"))))
    )
    (setq n 0)
    (while (setq ent (ssname ss n))
      (setq elst (entget ent '("*")))
      (if (= (cdr (assoc 0 elst)) "LWPOLYLINE")
	(if del
	  (entmod (pol2pol elst seg org))
	  (progn
	    (entmake (pol2pol elst seg org))
	    (and
	      ade_odgettables
	      ade_odrecordqty
	      ade_oddelrecord
	      ade_odtabledefn
	      ade_odgetfield
	      ade_odaddrecord
              copy_data
	      (copy_data ent (entlast) nil)
	    )
	  )
	)
	(progn
	  (entmake (arc2pol elst seg org))
	  (and
	    ade_odgettables
	    ade_odrecordqty
	    ade_oddelrecord
	    ade_odtabledefn
	    ade_odgetfield
	    ade_odaddrecord
            copy_data
	    (copy_data ent (entlast) nil)
	  )
	  (and del (entdel ent))
	)
      )
      (setq n (1+ n))
    )
  )
  (princ)
)

;; BulgeData
;; Retourne les données d'un polyarc (angle rayon centre)
(defun BulgeData (bu p1 p2 / alpha rad cen)
  (setq	alpha (* 2 (atan bu))
	rad   (/ (distance p1 p2)
		 (* 2 (sin alpha))
	      )
	cen   (polar p1
		     (+ (angle p1 p2) (- (/ pi 2) alpha))
		     rad
	      )
  )
  (list (* alpha 2.0) rad cen)
)

;;; Ang<2pi
;;; Retourne l'angle, à 2*k*pi près, compris entre 0 et 2*pi

(defun ang<2pi (ang)
  (if (and (<= 0 ang) (< ang (* 2 pi)))
    ang
    (ang<2pi (rem (+ ang (* 2 pi)) (* 2 pi)))
  )
)