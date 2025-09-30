;;; CURVE2PIPE -Gilles Chanteau- (gile) 07/04/07
;;; Extrude un anneau (région) suivant le(s) chemin(s) spécifié(s).
;;; (arc, cercle, ellipse, ligne, polyligne 2D 3D ou lw, spline plane)
;;; Spécifier les diamètres extérieurs et intérieurs et sélectionner le(s) chemin(s)
;;; Si la variable DELOBJ est supérieure à 0 les chemins sont supprimés.
;;;
;;; Révision 20/12/07
;;; conservation des dernières valeurs entrées dans le dessin
;;; ajout d'un raccourci : C2P
;;; Révision 01/07/2016
;;; correction d'une faute de frappe

(defun c:curve2pipe (/	       Space	 ext_rad   int_rad   ss
		     obj       start	 ext_circ  int_circ  ext_reg
		     int_reg   norm
		    )

  (vl-load-com)

  (or *acdoc*
      (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
  )
  (or (vlax-ldata-get "Curve2Pipe" "dia")
      (vlax-ldata-put "Curve2Pipe" "dia" 50.0)
  )
  (or (vlax-ldata-get "Curve2Pipe" "ep")
      (vlax-ldata-put "Curve2Pipe" "ep" 2.0)
  )
  (setq	Space
	 (if (= 1 (getvar "CVPORT"))
	   (vla-get-PaperSpace *acdoc*)
	   (vla-get-ModelSpace *acdoc*)
	 )
  )
  (if (setq ext_rad (getdist (strcat "\nDiamètre extérieur <"
				     (rtos (vlax-ldata-get "Curve2Pipe" "dia"))
				     ">: "
			     )
		    )
      )
    (vlax-ldata-put "Curve2Pipe" "dia" ext_rad)
    (setq ext_rad (vlax-ldata-get "Curve2Pipe" "dia"))
  )
  (setq	ext_rad	(/ ext_rad 2.0)
	int_rad	ext_rad
  )
  (while (<= ext_rad int_rad)
    (if	(setq int_rad (getdist (strcat "\nÉpaisseur <"
				       (rtos (vlax-ldata-get "Curve2Pipe" "ep"))
				       ">: "
			       )
		      )
	)
      (vlax-ldata-put "Curve2Pipe" "ep" int_rad)
      (setq int_rad (vlax-ldata-get "Curve2Pipe" "ep"))
    )
  )
  (if (setq ss
	     (ssget
	       '((-4 . "<OR")
		 (0 . "ARC,CIRCLE,ELLIPSE,LINE,LWPOLYLINE")
		 (-4 . "<AND")
		 (0 . "POLYLINE")
		 (-4 . "<NOT")
		 (-4 . "&")
		 (70 . 112)
		 (-4 . "NOT>")
		 (-4 . "AND>")
		 (-4 . "<AND")
		 (0 . "SPLINE")
		 (-4 . "&")
		 (70 . 8)
		 (-4 . "AND>")
		 (-4 . "OR>")
		)
	     )
      )
    (progn
      (vla-StartUndoMark *acdoc*)
      (foreach path (vl-remove-if 'listp (mapcar 'cadr (ssnamex ss)))
	(setq obj (vlax-ename->vla-object path))
	(setq start (vlax-curve-getPointAtParam
		      obj
		      (vlax-curve-getStartParam obj)
		    )
	)
	(setq ext_circ (vla-addCircle
			 Space
			 (vlax-3d-Point start)
			 ext_rad
		       )
	)
	(setq int_circ (vla-addCircle
			 Space
			 (vlax-3d-Point start)
			 (- ext_rad int_rad)
		       )
	)
	(setq norm (vunit (vlax-curve-getFirstDeriv
			    obj
			    (vlax-curve-getStartParam obj)
			  )
		   )
	)
	(vla-put-Normal ext_circ (vlax-3d-point norm))
	(vla-put-Normal int_circ (vlax-3d-point norm))
	(setq
	  ext_reg (car (vlax-invoke Space 'addRegion (list ext_circ)))
	)
	(setq
	  int_reg (car (vlax-invoke Space 'addRegion (list int_circ)))
	)
	(vla-Boolean ext_reg acSubtraction int_reg)
	(vla-addExtrudedSolidAlongPath Space ext_reg obj)
	(mapcar 'vla-delete (list ext_circ int_circ ext_reg))
	(if (< 0 (getvar "DELOBJ"))
	  (vla-delete obj)
	)
      )
      (vla-EndUndoMark *acdoc*)
    )
    (princ "\nEntrée non valide.")
  )
  (princ)
)

(defun c:c2p () (c:curve2pipe))

;;; VUNIT (gile)
;;; Retourne le vecteur unitaire d'un vecteur
(defun vunit (v)
  ((lambda (l)
     (if (/= 0 l)
       (mapcar '(lambda (x) (/ x l)) v)
     )
   )
    (sqrt (apply '+ (mapcar '* v v)))
  )
)