;; CT & MT (Gilles Chanteau) 21/11/07
;; Fonctionnent avec textes simples et multilignes
;; Les paramètres (couleur et la distance de décalage)
;; sont conservées dans le dessin pendant la session

;; CT Encadre les textes sélectionnés
;; Le cadre (polyligne) est placé sur le calque du texte
;; Le décalage, la couleur et la largeur sont paramétrables

(defun c:ct (/ of col wid opt par wo n ss n tx elst plst)
  (vl-load-com)
  (or *acad* (setq *acad* (vlax-get-acad-object)))
  (or *acdoc* (setq *acdoc* (vla-get-ActiveDocument *acad*)))
  (or *TextFrameOffset*
      (setq *TextFrameOffset* (/ (getvar "TEXTSIZE") 5.0))
  )
  (or *TextFrameColor*
      (setq *TextFrameColor* (list '(62 . 256)))
  )
  (or *TextFrameWidth*
      (setq *TextFrameWidth* 0.0)
  )
  (setq	of  *TextFrameOffset*
	col *TextFrameColor*
	wid *TextFrameWidth*
  )
  (while
    (and (princ	(strcat	"\nDécalage: "
			(rtos of)
			"\tCouleur: "
			(TrueColor2String col)
			"\tLargeur: "
			(rtos wid)
			"\nSélectionnez les textes ou <Paramètres>."
		)
	 )
	 (not (setq ss (ssget '((0 . "MTEXT,TEXT")))))
    )
     (initget 1 "Décalage Couleur Largeur")
     (setq par (getkword
		 "\nChoix de l'option [Décalage/Couleur/Largeur]: "
	       )
     )
     (cond
       ((= par "Couleur")
	(if (< 15 (atoi (substr (getvar "ACADVER") 1 2)))
	  (if (setq col	(acad_truecolordlg
			  (cond
			    ((assoc 420 col))
			    ((assoc 62 col))
			  )
			)
	      )
	    (setq *TextFrameColor* col)
	    (setq col *TextFrameColor*)
	  )
	  (if (setq col (acad_colordlg (cdr (assoc 62 col))))
	    (setq *TextFrameColor* (setq col (list (cons 62 col))))
	    (setq col *TextFrameColor*)
	  )
	)
       )
       ((= par "Décalage")
	(if (setq of (getdist (strcat "\nSpécifiez le décalage du cadre <"
				      (rtos of)
				      ">: "
			      )
		     )
	    )
	  (setq *TextFrameOffset* of)
	  (setq of *TextFrameOffset*)
	)
       )
       (T
	(if (setq wid (getdist (strcat "\nSpécifiez la largeur du cadre <"
				       (rtos wid)
				       ">: "
			       )
		      )
	    )
	  (setq *TextFrameWidth* wid)
	  (setq wid *TextFrameWidth*)
	)
       )
     )
  )
  (setq n -1)
  (vla-StartUndoMark *acdoc*)
  (while (setq tx (ssname ss (setq n (1+ n))))
    (setq elst (entget tx)
	  plst (text2box-plst elst of)
    )
    (make-frame elst col wid plst)
  )
  (vla-EndUndoMark *acdoc*)
  (princ)
)

;; ==========================================================;;

;; MT Place un masque derrière les textes sélectionnés
;; Le masque (hachure SOLID ou wipeout) est placé sur le calque du texte
;; Le décalage , la couleur et le type de masque sont paramétrables

(defun c:mt (/ of col par n ss tx elst plst olst space sort)
  (vl-load-com)
  (or *acad* (setq *acad* (vlax-get-acad-object)))
  (or *acdoc* (setq *acdoc* (vla-get-ActiveDocument *acad*)))
  (or *TextMaskOffset*
      (setq *TextMaskOffset* (/ (getvar "TEXTSIZE") 5.0))
  )
  (or *TextMaskColor*
      (setq *TextMaskColor* (list '(62 . 1)))
  )
  (setq	of  *TextMaskOffset*
	col *TextMaskColor*
  )
  (while
    (and (princ	(strcat	"\nDécalage: "
			(rtos of)
			"\tCouleur: "
			(TrueColor2String col)
			"\nSélectionnez les textes ou <Paramètres>."
		)
	 )
	 (not (setq ss (ssget '((0 . "MTEXT,TEXT")))))
    )
     (initget 1 "Décalage Couleur Wipeout")
     (setq par (getkword
		 "\nChoix de l'option [Décalage/Couleur/Wipeout]: "
	       )
     )
     (cond
       ((= par "Wipeout")
	(setq *TextMaskColor* (setq col (list (cons 430 "Wipeout"))))
       )
       ((= par "Couleur")
	(if (< 15 (atoi (substr (getvar "ACADVER") 1 2)))
	  (if (setq col	(acad_truecolordlg
			  (cond
			    ((assoc 420 col))
			    ((assoc 62 col))
			    (T '(62 . 1))
			  )
			)
	      )
	    (setq *TextMaskColor* col)
	    (setq col *TextMaskColor*)
	  )
	  (if (setq col	(acad_colordlg
			  (cond	((cdr (assoc 62 col)))
				(T 1)
			  )
			)
	      )
	    (setq *TextMaskColor* (setq col (list (cons 62 col))))
	    (setq col *TextMaskColor*)
	  )
	)
       )
       (T
	(setq of (getdist (strcat "\nSpécifiez le décalage du cadre <"
				  (rtos of)
				  ">: "
			  )
		 )
	)
	(setq *TextMaskOffset* of)
	(setq of *TextMaskOffset*)
       )
     )
  )
  (setq n -1)
  (vla-StartundoMark *acdoc*)
  (while (setq tx (ssname ss (setq n (1+ n))))
    (setq elst (entget tx)
	  plst (text2box-plst elst of)
	  olst (cons (vlax-ename->vla-object tx) olst)
    )
    (make-mask elst col plst)
  )
  (setq	space (if (= (getvar "CVPORT") 1)
		(vla-get-PaperSpace *acdoc*)
		(vla-get-ModelSpace *acdoc*)
	      )
  )
  (if (vl-catch-all-error-p
	(setq sort (vl-catch-all-apply
		     'vla-item
		     (list (vla-getExtensionDictionary
			     space
			   )
			   "ACAD_SORTENTS"
		     )
		   )
	)
      )
    (setq sort (vla-addObject
		 (vla-getExtensionDictionary
		   space
		 )
		 "ACAD_SORTENTS"
		 "AcDbSortentsTable"
	       )
    )
  )
  (vlax-invoke sort 'MoveToTop olst)
  (vla-EndUndoMark *acdoc*)
  (princ)
)

;; ==========================================================;;

;; Text2Box-plst (gile)
;; Retourne la liste des sommets (coordonnées SCO) de la boite
;; englobant le texte après décalage
;;
;; Arguments
;; elst : liste DXF de l'entité
;; of : distance de décalage

(defun Text2box-plst (elst of / nor ref rot wid hgt jus org box plst)
  (if (= "MTEXT" (cdr (assoc 0 elst)))
    (setq nor  (cdr (assoc 210 elst))
	  ref  (trans (cdr (assoc 10 elst)) 0 nor)
	  rot  (angle '(0 0 0) (trans (cdr (assoc 11 elst)) 0 nor))
	  wid  (cdr (assoc 42 elst))
	  hgt  (cdr (assoc 43 elst))
	  jus  (cdr (assoc 71 elst))
	  org  (list
		 (cond
		   ((member jus '(2 5 8)) (/ wid -2))
		   ((member jus '(3 6 9)) (- wid))
		   (T 0.0)
		 )
		 (cond
		   ((member jus '(1 2 3)) (- hgt))
		   ((member jus '(4 5 6)) (/ hgt -2))
		   (T 0.0)
		 )
	       )
	  plst (mapcar
		 (function
		   (lambda (p)
		     (mapcar '+ org p)
		   )
		 )
		 (list
		   (list (- of) (- of))
		   (list (+ wid of) (- of))
		   (list (+ wid of) (+ hgt of))
		   (list (- of) (+ hgt of))
		 )
	       )
    )
    (setq box  (textbox elst)
	  ref  (cdr (assoc 10 elst))
	  rot  (cdr (assoc 50 elst))
	  plst (list
		 (list (- (caar box) of) (- (cadar box) of))
		 (list (+ (caadr box) of) (- (cadar box) of))
		 (list (+ (caadr box) of) (+ (cadadr box) of))
		 (list (- (caar box) of) (+ (cadadr box) of))
	       )
    )
  )
  (setq	mat  (list (list (cos rot) (- (sin rot)) 0)
		   (list (sin rot) (cos rot) 0)
		   '(0 0 1)
	     )
	plst (mapcar
	       (function
		 (lambda (p)
		   (mapcar '+ (mxv mat p) (list (car ref) (cadr ref)))
		 )
	       )
	       plst
	     )
  )
)

;; ==========================================================;;

;; Make-Frame (gile)
;; Crée une polyligne encadrant le texte
;;
;; Arguments
;; elst : liste DXF de l'entité
;; col : couleur de la polyligne
;; plst : liste des sommets

(defun make-frame (elst col wid plst / nor elv)
  (setq nor (cdr (assoc 210 elst)))
  (if (= "MTEXT" (cdr (assoc 0 elst)))
    (setq elv (caddr (trans (cdr (assoc 10 elst)) 0 nor)))
    (setq elv (caddr (cdr (assoc 10 elst))))
  )
  (entmake
    (append
      (list '(0 . "LWPOLYLINE")
	    '(100 . "AcDbEntity")
	    (assoc 8 elst)
	    (if	(and (< 15 (atoi (substr (getvar "ACADVER") 1 2)))
		     (assoc 420 col)
		)
	      (assoc 420 col)
	      (assoc 62 col)
	    )
	    '(100 . "AcDbPolyline")
	    '(90 . 4)
	    '(70 . 1)
	    (cons 43 wid)
	    (cons 38 elv)
	    (cons 210 nor)
      )
      (mapcar (function (lambda (x) (cons 10 x))) plst)
    )
  )
)

;; ==========================================================;;

;; Make-Mask (gile)
;; Crée une hachure SOLID figurant un masque d'arrière plan
;;
;; Arguments
;; elst : liste DXF de l'entité texte
;; col : couleur de la hachure
;; plst : liste des sommets

(defun make-mask (elst col plst / nor elv)
  (setq nor (cdr (assoc 210 elst)))
  (if (= "MTEXT" (cdr (assoc 0 elst)))
    (setq elv (caddr (trans (cdr (assoc 10 elst)) 0 nor)))
    (setq elv (caddr (cdr (assoc 10 elst))))
  )
  (if (= (cdr (assoc 430 col)) "Wipeout")
    (MakeWipeout
      (mapcar
	(function
	  (lambda (p)
	    (list (car p) (cadr p) elv)
	  )
	)
	plst
      )
      nor
      (cdr (assoc 8 elst))
    )
    (entmake
      (list
	'(0 . "HATCH")
	'(100 . "AcDbEntity")
	(assoc 8 elst)
	(if (and (< 15 (atoi (substr (getvar "ACADVER") 1 2)))
		 (assoc 420 col)
	    )
	  (assoc 420 col)
	  (assoc 62 col)
	)
	'(100 . "AcDbHatch")
	(list 10 0.0 0.0 elv)
	(cons 210 nor)
	'(2 . "SOLID")
	'(70 . 1)
	'(71 . 0)
	'(91 . 1)
	'(92 . 1)
	'(93 . 4)
	'(72 . 1)
	(cons 10 (car plst))
	(cons 11 (cadr plst))
	'(72 . 1)
	(cons 10 (cadr plst))
	(cons 11 (caddr plst))
	'(72 . 1)
	(cons 10 (caddr plst))
	(cons 11 (cadddr plst))
	'(72 . 1)
	(cons 10 (cadddr plst))
	(cons 11 (car plst))
	'(97 . 0)
	'(75 . 0)
	'(76 . 1)
	'(98 . 1)
	'(10 0.0 0.0 0.0)
      )
    )
  )
)




;; ==========================================================;;

;; MakeWipeout (gile)
;; crée un objet "wipeout" à partir d'une liste de points et du vecteur normal de l'objet

(defun MakeWipeout (pt_lst nor lay / echo dxf10 max_dist cen dxf_14)
  (if (> (atoi (getvar 'acadver)) 18)
    (or
      (dictsearch (namedobjdict) "ACAD_WIPEOUT_VARS")
      (not (setq echo (getvar 'cmdecho)))
      (not (setvar 'cmdecho 0))
      (command "_wipeout")
      (command)
      (not (setvar 'cmdecho 1))
      (dictadd
	(namedobjdict)
	"ACAD_WIPEOUT_VARS"
	(entmakex
	  '((0 . "WIPEOUTVARIABLES") (100 . "AcDbWipeoutVariables") (70 . 1))
	)
      )
    )
    (or
      (member "acwipeout.arx" (arx))
      (arxload "acwipeout.arx")
    )
  )
  (setq	dxf10 (list (apply 'min (mapcar 'car pt_lst))
		    (apply 'min (mapcar 'cadr pt_lst))
		    (caddar pt_lst)
	      )
  )
  (setq
    max_dist
     (float
       (apply 'max
	      (mapcar '- (apply 'mapcar (cons 'max pt_lst)) dxf10)
       )
     )
  )
  (setq cen (mapcar '+ dxf10 (list (/ max_dist 2) (/ max_dist 2) 0.0)))
  (setq
    dxf14 (mapcar
	    '(lambda (p)
	       (mapcar '/
		       (mapcar '- p cen)
		       (list max_dist (- max_dist) 1.0)
	       )
	     )
	    pt_lst
	  )
  )
  (setq dxf14 (reverse (cons (car dxf14) (reverse dxf14))))
  (entmake
    (append (list '(0 . "WIPEOUT")
		  '(100 . "AcDbEntity")
		  (cons 8 lay)
		  '(100 . "AcDbWipeout")
		  '(90 . 0)
		  (cons 10 (trans dxf10 nor 0))
		  (cons 11 (trans (list max_dist 0.0 0.0) nor 0))
		  (cons 12 (trans (list 0.0 max_dist 0.0) nor 0))
		  '(13 1.0 1.0 0.0)
		  '(70 . 7)
		  '(280 . 1)
		  '(71 . 2)
		  (cons 91 (length dxf14))
	    )
	    (mapcar '(lambda (p) (cons 14 p)) dxf14)
    )
  )
)

;; ==========================================================;;

;; Applique une matrice de transformation à un vecteur (Vladimir Nesterovsky)
(defun mxv (m v)
  (mapcar (function (lambda (r) (apply '+ (mapcar '* r v))))
	  m
  )
)

;; ==========================================================;;

;; TrueColor2String (gile)
;; Retourne une chaîne indiquant l'index de la couleur ou les valeurs RVB
(defun TrueColor2String	(lst / ind)
  (setq	ind (cond ((cdr (assoc 430 lst)))
		  ((cdr (assoc 420 lst)))
		  ((cdr (assoc 62 lst)))
		  (T 256)
	    )
  )
  (cond
    ((= (type ind) 'STR) ind)
    ((= ind 256) "DuCalque")
    ((= ind 0) "DuBloc")
    ((< 256 ind)
     (strcat (itoa (lsh ind -16))
	     ","
	     (itoa (lsh (lsh ind 16) -24))
	     ","
	     (itoa (lsh (lsh ind 24) -24))
     )
    )
    ((itoa ind))
  )
)