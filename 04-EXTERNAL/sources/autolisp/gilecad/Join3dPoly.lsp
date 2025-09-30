;; Join3dPoly (gile)
;; Joint les objets sélectionnés en une polyligne 3d s'ils sont jointifs
;; La polyligne est créée avec les propriétés courantes (calque, couleur, ...)

(defun c:Join3dPoly (/ Space ss lst plst olst n 3p)
  (vl-load-com)
  (or *acdoc*
      (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
  )
  (setq	Space (if (= (getvar "CVPORT") 1)
		(vla-get-PaperSpace *acdoc*)
		(vla-get-ModelSpace *acdoc*)
	      )
  )
  (while (not (ssget '((-4 . "<OR")
		       (0 . "LINE")
		       (-4 . "<AND")
		       (0 . "POLYLINE")
		       (70 . 8)
		       (-4 . "AND>")
		       (-4 . "<AND")
		       (0 . "LWPOLYLINE")
		       (70 . 0)
		       (-4 . "AND>")
		       (-4 . "OR>")
		      )
	      )
	 )
  )
  (vlax-for obj	(setq ss (vla-get-ActiveSelectionSet *acdoc*))
    (cond
      ((= (vla-get-ObjectName obj) "AcDbLine")
       (setq lst (cons
		   (cons obj
			 (list (vlax-get obj 'StartPoint)
			       (vlax-get obj 'EndPoint)
			 )
		   )
		   lst
		 )
       )
      )
      ((= (vla-get-ObjectName obj) "AcDbPolyline")
       (setq lst (cons (cons obj (PlinePoints obj)) lst))
      )
      ((= (vla-get-ObjectName obj) "AcDb3dPolyline")
       (setq lst
	      (cons
		(cons obj (3d-coord->pt-lst (vlax-get obj 'Coordinates)))
		lst
	      )
       )
      )
    )
  )
  (while (and lst (< (length olst) 2))
    (setq plst (cdar lst)
	  olst (list (caar lst))
	  lst  (cdr lst)
	  n    0
    )
    (while (and lst (< n (length lst)))
      (cond
	((equal (cadar lst) (last plst) 1e-9)
	 (setq plst (append plst (cddar lst))
	       olst (cons (caar lst) olst)
	       lst  (cdr lst)
	       n    0
	 )
	)
	((equal (last (cdar lst)) (car plst) 1e-9)
	 (setq plst (append (cdar lst) (cdr plst))
	       olst (cons (caar lst) olst)
	       lst  (cdr lst)
	       n    0
	 )
	)
	((equal (cadar lst) (car plst) 1e-9)
	 (setq plst (append (reverse (cdar lst)) (cdr plst))
	       olst (cons (caar lst) olst)
	       lst  (cdr lst)
	       n    0
	 )
	)
	((equal (last (cdar lst)) (last plst) 1e-9)
	 (setq plst (append plst (cdr (reverse (cdar lst))))
	       olst (cons (caar lst) olst)
	       lst  (cdr lst)
	       n    0
	 )
	)
	(T
	 (setq lst (append (cdr lst) (list (car lst)))
	       n   (1+ n)
	 )
	)
      )
    )
  )
  (if (and (= 1 (setq n (length olst))) (< 1 (vla-get-Count ss)))
    (princ "\nObjets non jointifs.")
    (progn
      (vla-StartUndoMark *acdoc*)
      (vlax-invoke Space 'add3dPoly (apply 'append plst))
      (if (= 1 n)
	(princ "\n1 objet a été transformé en polyligne 3d.")
	(princ (strcat "\n"
		       (itoa n)
		       " objets ont été joints en une polyligne 3d."
	       )
	)
      )
      (mapcar 'vla-delete olst)
      (vla-EndUndoMark *acdoc*)
    )
  )
  (vla-delete ss)
  (princ)
)

;;; 3d-coord->pt-lst
;;; Convertit une liste de coordonnées 3D en liste de points
;;; (3d-coord->pt-lst '(1.0 2.0 3.0 4.0 5.0 6.0)) -> ((1.0 2.0 3.0) (4.0 5.0 6.0))

(defun 3d-coord->pt-lst	(lst)
  (if lst
    (cons (list (car lst) (cadr lst) (caddr lst))
	  (3d-coord->pt-lst (cdddr lst))
    )
  )
)

;;; PlinePoints
;;; Retourne la liste des sommets (coordonnées SCG) de la polyligne (ename ou vla-object)

(defun PlinePoints (pl / sub)
  (vl-load-com)
  (or (= (type pl) 'VLA-OBJECT)
      (setq pl (vlax-ename->vla-object pl))
  )

  (defun sub (l e n)
    (if	l
      (cons (trans (list (car l) (cadr l) e) n 0)
	    (sub (cddr l) e n)
      )
    )
  )

  (sub (vlax-get pl 'Coordinates)
       (vla-get-Elevation pl)
       (vlax-get pl 'Normal)
  )
)