;;; 3dPolyFillet -Gilles Chanteau- 21/01/07 -Version 1.5-
;;; Crée un "raccord" sur les polylignes 3D (succession de segments)
;;; Modifié le 24/07/2013

(defun c:3dPolyFillet (/	 *error* butlast   closest_vertices    MakeFillet	   fr	     cSpace    cnt
		       prec	 rad	   ent1	     elst      ent2	 vxlst	   plst	     param     obj
		       p1	 p2
		      )
  (vl-load-com)
  (or *acad* (setq *acad* (vlax-get-acad-object)))
  (or *acdoc* (setq *acdoc* (vla-get-ActiveDocument *acad*)))

;;;*************************************************************;;;

  (defun *error* (msg)
    (and
      msg
      (not (wcmatch (strcase msg) "CANCELLED,ANNULEE"))
      (princ (strcat (if fr "\nErreur: " "\nError: ") msg))
    )
    (vla-EndUndoMark *acdoc*)
    (princ)
  )

;;;*************************************************************;;;

  (defun butlast (lst)
    (reverse (cdr (reverse lst)))
  )

;;;*************************************************************;;;

  (defun closest_vertices (obj pt / par)
    (if	(setq par (vlax-curve-getParamAtPoint obj pt))
      (list (vlax-curve-getPointAtParam obj (fix par))
	    (vlax-curve-getPointAtParam obj (1+ (fix par)))
      )
    )
  )

;;;*************************************************************;;;

  (defun MakeFillet (obj par1 par2 / pts1 pts2 som p1 p2 ptlst norm pt0 pt1 pt2 pt3 pt4 cen ang inc n vlst nb1 nb2)
    (if	(and
	  (setq pts1 (closest_vertices obj par1))
	  (setq pts2 (closest_vertices obj par2))
	)
      (progn
	(setq som (inters (car pts1) (cadr pts1) (car pts2) (cadr pts2) nil))
	(if som
	  (if
	    (or	(equal (car pts1) som 1e-9)
		(equal (cadr pts1) som 1e-9)
		(equal (gc:GetUnitVector (car pts1) (cadr pts1))
		       (gc:GetUnitVector (car pts1) som)
		       1e-9
		)
	    )
	     (progn
	       (if (equal (car pts1) (cadr pts2))
		 (setq p1 (cadr pts1)
		       p2 (car pts2)
		 )
		 (setq p1 (car pts1)
		       p2 (cadr pts2)
		 )
	       )
	       (if (= rad 0)
		 (setq ptlst (list som))
		 (progn
		   (setq norm (gc:Normal3Pts som p2 p1)
			 pt0  (trans som 0 norm)
			 pt1  (trans p1 0 norm)
			 pt2  (trans p2 0 norm)
			 cen  (inters
				(polar pt0 (- (angle pt0 pt1) (/ pi 2)) rad)
				(polar pt1 (- (angle pt0 pt1) (/ pi 2)) rad)
				(polar pt0 (+ (angle pt0 pt2) (/ pi 2)) rad)
				(polar pt2 (+ (angle pt0 pt2) (/ pi 2)) rad)
				nil
			      )
			 pt3  (polar cen (- (angle pt1 pt0) (/ pi 2)) rad)
			 pt4  (polar cen (+ (angle pt2 pt0) (/ pi 2)) rad)
			 ang  (- (angle cen pt4) (angle cen pt3))
		   )
		   (if
		     (and (inters pt0 pt1 cen pt3 T) (inters pt0 pt2 cen pt4 T))
		      (progn
			(if (minusp ang)
			  (setq ang (+ (* 2 pi) ang))
			)
			(setq inc (/ ang prec)
			      n	  0
			)
			(repeat	(1+ prec)
			  (setq	ptlst (cons
					(polar cen (- (angle cen pt4) (* inc n)) rad)
					ptlst
				      )
				n     (1+ n)
			  )
			)
			(setq
			  ptlst	(mapcar	(function (lambda (p) (trans p norm 0)))
					ptlst
				)
			)
		      )
		   )
		 )
	       )
	       (setq vlst (gc:split3 (vlax-get obj 'Coordinates)))
	       (if ptlst
		 (progn
		   (setq nb1 (vl-position p1 vlst)
			 nb2 (1+ (vl-position (car pts2) vlst))
		   )
		   (setq vlst
			  (if (equal (car pts1) (cadr pts2))
			    (if	(= (vla-get-Closed obj) :vlax-true)
			      (append (reverse ptlst) (cdr vlst))
			      (append (reverse ptlst) (gc:sublist 1 (1- nb2) vlst) (list (last ptlst)))
			    )
			    (append (gc:take (1+ nb1) vlst) ptlst (gc:skip nb2 vlst))
			  )
		   )
		   (vlax-put obj 'Coordinates (apply 'append vlst))
		 )
		 (prompt
		   (if fr
		     "\nLe rayon spécifié est trop grand."
		     "\nThe specified radius is too large."
		   )
		 )
	       )
	     )
	     (prompt
	       (if fr
		 "\nLes segments sont divergents."
		 "\nThe segments are divergent"
	       )
	     )
	  )
	  (prompt
	    (if	fr
	      "\nLes segments ne sont pas concourants."
	      "\nThe segments are not intersecting."
	    )
	  )
	)
      )
      (prompt
	(if fr
	  "\nLe rayon spécifié est trop grand."
	  "\nThe specified radius is too large."
	)
      )
    )
  )


;;;*************************************************************;;;

  (setq	fr     (wcmatch (ver) "*(fr)")
	cSpace (vla-get-Block (vla-get-activeLayout *acdoc*))
  )
  (vla-StartUndoMark *acdoc*)
  (sssetfirst nil nil)

  ;; Saisie des données
  (if (not (vlax-ldata-get "3dFillet" "Prec"))
    (vlax-ldata-put "3dFillet" "Prec" 20)
  )
  (if (not (vlax-ldata-get "3dFillet" "Rad"))
    (vlax-ldata-put "3dFillet" "Rad" 10.0)
  )
  (prompt
    (if	fr
      (strcat "\nParamètres courants.\tSegments: "
	      (itoa (vlax-ldata-get "3dFillet" "Prec"))
	      "\tRayon: "
	      (rtos (vlax-ldata-get "3dFillet" "Rad"))
      )
      (strcat "\nCurrent settings.\tSegments: "
	      (itoa (vlax-ldata-get "3dFillet" "Prec"))
	      "\tRadius: "
	      (rtos (vlax-ldata-get "3dFillet" "Rad"))
      )
    )
  )
  (setq cnt 1)
  (while (= 1 cnt)
    (if	fr
      (progn
	(initget 1 "Segments Rayon")
	(setq ent1 (entsel "\nSélectionnez le premier segment ou [Segments/Rayon]: "))
      )
      (progn
	(initget 1 "Segments Radius")
	(setq ent1 (entsel "\nSelect the first segment or [Segments/Radius]: "))
      )
    )
    (cond
      ((not ent1)
       (prompt
	 (if fr
	   "\nAucun objet sélectionné."
	   "\nNone selected object."
	 )
       )
      )
      ((= ent1 "Segments")
       (initget 6)
       (if (setq prec
		  (getint
		    (if	fr
		      (strcat "\nSpécifiez le nombre de segments pour les arcs <"
			      (itoa (vlax-ldata-get "3dFillet" "Prec"))
			      ">: "
		      )
		      (strcat "\nSpecify the number segments per arc <"
			      (itoa (vlax-ldata-get "3dFillet" "Prec"))
			      ">: "
		      )
		    )
		  )
	   )
	 (vlax-ldata-put "3dFillet" "Prec" prec)
       )
      )
      ((or (= ent1 "Radius") (= ent1 "Rayon"))
       (initget 4)
       (if (setq rad
		  (getdist
		    (if	fr
		      (strcat "\nSpécifiez le rayon <"
			      (rtos (vlax-ldata-get "3dFillet" "Rad"))
			      ">: "
		      )
		      (strcat "\nSpecify the radius <"
			      (rtos (vlax-ldata-get "3dFillet" "Rad"))
			      ">: "
		      )
		    )
		  )
	   )
	 (vlax-ldata-put "3dFillet" "Rad" rad)
       )
      )
      ((and
	 (setq elst (entget (car ent1)))
	 (= (cdr (assoc 0 elst)) "POLYLINE")
	 (= (logand 8 (cdr (assoc 70 elst))) 8)
       )
       (if (< 0 (logand 4 (cdr (assoc 70 elst))))
	 (prompt
	   (if fr
	     "\nL'objet sélectionné est une polyligne 3D splinée."
	     "\nThe selected object is a splined 3D polyline."
	   )
	 )
	 (setq cnt 0)
       )
      )
      (T
       (prompt
	 (if fr
	   "\nL'objet sélectionné n'est pas une polyligne 3D."
	   "\nThe selected object is not a 3D polyline."
	 )
       )
      )
    )
  )
  (setq	prec (vlax-ldata-get "3dFillet" "Prec")
	rad  (vlax-ldata-get "3dFillet" "Rad")
  )
  (while
      (not
	(or
	  (and
	    (if	fr
	      (setq ent2 (entsel "\nSélectionnez le deuxième segment ou <Tous>: "))
	      (setq ent2 (entsel "\nSelect the second segment or <All>: "))
	    )
	    (eq (car ent1) (car ent2))
	  )
	  (= (getvar 'errno) 52)
	)
      )
     (prompt
       (if fr
	 "\nLe segment sélectionné n'est pas sur le même objet."
	 "\nThe selected segment in not on the same object."
       )
     )
     (setq ent2 nil)
  )
  (setq obj (vlax-ename->vla-object (car ent1)))
  (if (null ent2)
    (progn
      (setq vxlst (gc:split3 (vlax-get obj 'Coordinates))
	    param 0.6
      )
      (if (= (vla-get-closed obj) :vlax-true)
	(while (equal (car vxlst) (last vxlst))
	  (setq vxlst (butlast vxlst))
	  (vlax-put obj 'coordinates (apply 'append vxlst))
	)
      )
      (repeat (if (= (vla-get-closed obj) :vlax-true)
		(length vxlst)
		(1- (length vxlst))
	      )
	(setq plst  (append plst (list (vlax-curve-getPointAtParam obj param)))
	      param (1+ param)
	)
      )
      (mapcar '(lambda (p1 p2) (MakeFillet obj p1 p2)) plst (cdr plst))
      (if (or
	    (= (vla-get-closed obj) :vlax-true)
	    (equal (car vxlst) (last vxlst))
	  )
	(MakeFillet obj (vlax-curve-getPointAtParam obj 0.4) (last plst))
      )
    )
    (progn
      (setq p1 (trans (osnap (cadr ent1) "_nea") 1 0)
	    p2 (trans (osnap (cadr ent2) "_nea") 1 0)
      )
      (if (< (vlax-curve-getParamAtPoint obj p1) (vlax-curve-getParamAtPoint obj p2))
	(MakeFillet obj p1 p2)
	(MakeFillet obj p2 p1)
      )
    )
  )
  (*error* nil)
)

;;;*************************************************************;;;
;;;                        SOUS ROUTINES                        ;;;
;;;*************************************************************;;;

;; gc:GetUnitVector
;; Retourne le vecteur unitaire de sens p1 p2
;;
;; Arguments
;; p1, p2 : 2 points

(defun gc:GetUnitVector	(p1 p2)
  ((lambda (d)
     (if (not (zerop d))
       (mapcar (function (lambda (x1 x2) (/ (- x2 x1) d))) p1 p2)
     )
   )
    (distance p1 p2)
  )
)

;;;*************************************************************;;;

;; gc:Normalize
;; Retourne le vecteur unitaire d'un vecteur
;;
;; Argument
;; v : un vecteur
(defun gc:Normalize (v)
  ((lambda (l)
     (if (/= 0 l)
       (mapcar (function (lambda (x) (/ x l))) v)
     )
   )
    (distance '(0. 0. 0.) v)
  )
)

;;;*************************************************************;;;

;; gc:Normal3Pts
;; Retourne le vecteur normal du plan défini par p1 p2 p3
;;
;; Arguments
;; p1, p2, p3 trois points 3d figurant un triangle dans l'espace

(defun gc:Normal3Pts (p1 p2 p3)
  (gc:Normalize
    (list
      (- (* (- (cadr p2) (cadr p1)) (- (caddr p3) (caddr p1)))
	 (* (- (caddr p2) (caddr p1)) (- (cadr p3) (cadr p1)))
      )
      (- (* (- (caddr p2) (caddr p1)) (- (car p3) (car p1)))
	 (* (- (car p2) (car p1)) (- (caddr p3) (caddr p1)))
      )
      (- (* (- (car p2) (car p1)) (- (cadr p3) (cadr p1)))
	 (* (- (cadr p2) (cadr p1)) (- (car p3) (car p1)))
      )
    )
  )
)

;;;*************************************************************;;;

;; gc:split3
;; Convertit une liste de coordonnées 3D en liste de points
;;
;; Argument
;; l : une liste

(defun gc:split3 (l)
  (if l
    (cons (list (car l) (cadr l) (caddr l))
	  (gc:split3 (cdddr l))
    )
  )
)

;;;*************************************************************;;;

;; gc:take
;; Retourne les n premiers éléments de la liste
;;
;; Arguments
;; n : le nombre d'éléments
;; l : une liste

(defun gc:take (n l)
  (if (and l (< 0 n))
    (cons (car l) (gc:take (1- n) (cdr l)))
  )
)

;;;*************************************************************;;;

;; gc:skip
;; Retourne la liste moins les n premiers éléments
;;
;; Arguments
;; n : le nombre d'éléments
;; l : une liste

(defun gc:skip (n l)
  (if (and l (< 0 n))
    (gc:skip (1- n) (cdr l))
    l
  )
)

;;;*************************************************************;;;

;; gc:gc:sublist
;; Retourne la sous liste de n éléments à partir de i
;;
;; Arguments
;; i : index du premier élément
;; n : nombre d'éléments
;; l : une liste

(defun gc:sublist (i n l)
  (gc:take n (gc:skip i l))
)

;;;*************************************************************;;;
