;;; FUSION -Gilles Chanteau- 01/01/06
;;; Crée une polyligne sur le contour de chaque groupe de polylignes fermées et contiguës sélectionnées.
;;; Mise à jour: 19/04/2011 (fonctionnement 3d)

(defun c:fusion (/ *error* ss lst erase cnt)
  (vl-load-com)

  (or *acad* (setq *acad* (vlax-get-acad-object)))
  (or *acdoc* (setq *acdoc* (vla-get-activeDocument *acad*)))

  (defun *error* (msg)
    (and msg
	 (or
	   (= msg "Fonction annulée")
	   (= msg "quitter / sortir abandon")
	 )
	 (princ (strcat "\nErreur: " msg))
    )
    (vla-endundomark *acdoc*)
    (princ)
  )

  (prompt "\nSélectionnez les polylignes à fusionner: ")
  (if (ssget '((0 . "LWPOLYLINE") (-4 . "&") (70 . 1)))
    (progn
      (initget "Oui Non")
      (setq erase (getkword "\nEffacer les polylignes source ? [Oui/Non] <Oui>: "))
      (vlax-for	obj (setq ss (vla-get-ActiveSelectionSet *acdoc*))
	(setq lst (cons obj lst))
      )
      (vla-Delete ss)
      (vla-StartUndoMark *acdoc*)
      (setq cnt (gc:MergePlines lst (/= erase "Non")))
      (vla-EndUndoMark *acdoc*)
      (princ (strcat "\n"
		     (itoa cnt)
		     (if (< 1 cnt)
		       " polylignes creees."
		       " polyligne creee."
		     )
	     )
      )
    )
  )
  (*error* nil)
)

;;;***************************************************************;;;

;; MergePlines
;; Unit les polylignes coplanaires et contigües, retourne le nombre de polylignes créées.
;;
;; Arguments
;; lst : liste des polylignes à traiter
;; erase : si non nil, les polylignes source sont effacées

(defun gc:MergePlines (lst erase / arcbulge space tmp source reg elev norm expl	objs regs olst blst
		       dlst plst tlst blg pline cnt)

  (or *acad* (setq *acad* (vlax-get-acad-object)))
  (or *acdoc* (setq *acdoc* (vla-get-activeDocument *acad*)))

  (defun arcbulge (arc)
    (/ (sin (/ (vla-get-TotalAngle arc) 4))
       (cos (/ (vla-get-TotalAngle arc) 4))
    )
  )

  (setq	space (if (= 1 (getvar "CVPORT"))
		(vla-get-PaperSpace *acdoc*)
		(vla-get-Modelspace *acdoc*)
	      )
	cnt 0
  )
  (while lst
    (setq tmp nil)
    (setq source (car lst)
	  elev	 (vla-get-Elevation source)
	  norm	 (vlax-get source 'Normal)
    )
    (foreach p lst
      (if (and (equal elev (vla-get-Elevation p) 1e-12)
	       (equal norm (vlax-get p 'Normal) 1e-2)
	  )
	(setq tmp (cons p tmp)
	      lst (vl-remove p lst)
	)
      )
    )
    (if	(and
	  (< 1 (length tmp))
	  (setq reg (vlax-invoke space 'addRegion tmp))
	)
      (progn
	(if erase
	  (mapcar 'vla-Delete tmp)
	)
	(while (cadr reg)
	  (vla-boolean (car reg) acUnion (cadr reg))
	  (setq reg (cons (car reg) (cddr reg)))
	)
	(setq reg  (car reg)
	      expl (vlax-invoke reg 'Explode)
	)
	(vla-delete reg)
	(while expl
	  (setq	objs (vl-remove-if-not
		       '(lambda	(x)
			  (or
			    (= (vla-get-ObjectName x) "AcDbLine")
			    (= (vla-get-ObjectName x) "AcDbArc")
			  )
			)
		       expl
		     )
		regs (vl-remove-if-not
		       '(lambda (x) (= (vla-get-ObjectName x) "AcDbRegion"))
		       expl
		     )
	  )
	  (if objs
	    (progn
	      (setq olst (mapcar '(lambda (x)
				    (list x
					  (vlax-get x 'StartPoint)
					  (vlax-get x 'EndPoint)
				    )
				  )
				 objs
			 )
	      )
	      (while olst
		(setq blst nil)
		(if (= (vla-get-ObjectName (caar olst)) "AcDbArc")
		  (setq blst (list (cons 0 (arcbulge (caar olst)))))
		)
		(setq plst (cdar olst)
		      dlst (list (caar olst))
		      olst (cdr olst)
		)
		(while
		  (setq
		    tlst (vl-member-if
			   '(lambda (x)
			      (or (equal (last plst) (cadr x) 1e-9)
				  (equal (last plst) (caddr x) 1e-9)
			      )
			    )
			   olst
			 )
		  )
		   (if (equal (last plst) (caddar tlst) 1e-9)
		     (setq blg -1)
		     (setq blg 1)
		   )
		   (if (= (vla-get-ObjectName (caar tlst)) "AcDbArc")
		     (setq
		       blst (cons (cons	(1- (length plst))
					(* blg (arcbulge (caar tlst)))
				  )
				  blst
			    )
		     )
		   )
		   (setq plst (append plst
				      (if (minusp blg)
					(list (cadar tlst))
					(list (caddar tlst))
				      )
			      )
			 dlst (cons (caar tlst) dlst)
			 olst (vl-remove (car tlst) olst)
		   )
		)
		(setq pline
		       (vlax-invoke
			 Space
			 'addLightWeightPolyline
			 (apply	'append
				(mapcar	'(lambda (x)
					   (setq x (trans x 0 Norm))
					   (list (car x) (cadr x))
					 )
					(reverse (cdr (reverse plst)))
				)
			 )
		       )
		)
		(vla-put-Closed pline :vlax-true)
		(mapcar
		  '(lambda (x) (vla-setBulge pline (car x) (cdr x)))
		  blst
		)
		(vla-put-Elevation pline elev)
		(vla-put-Normal pline (vlax-3d-point norm))
		(mapcar 'vla-delete dlst)
		(setq cnt (1+ cnt))
	      )
	    )
	  )
	  (if regs
	    (progn
	      (setq
		expl (append (vlax-invoke (car regs) 'Explode)
			     (cdr regs)
		     )
	      )
	      (vla-delete (car regs))
	    )
	    (setq expl nil)
	  )
	)
      )
    )
  )
  cnt
)

(defun c:upl() (c:fusion))