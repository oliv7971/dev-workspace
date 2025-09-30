;| TOTALPERIM version 4.1.0 (gile)
Définit les commandes PERIMBOX, TOTALPERIM, PERIMUPD, PERIMEDIT, PERIMSHOW
et les variables PERIMCONV, PERIMPREC

Bloc "TotalPerimeter"

Une définition bloc nommé "TotalPerimeter" doit être présente dans le dessin ou sous
forme de fichier "TotalPerimeter.dwg" dans un répertoire du chemin de recherche.

Ce bloc doit contenir au moins trois attributs ayant pour étiquettes "LABEL", "UNIT" et "PERIM"
Ce dernier sera automatiquement renseigné avec la somme des périmètres des objets qui lui sont liés.
(arc cercle ellipse ligne polyligne polyligne2d polyligne3d spline mpolygon region)

S'il contient un autre attribut ayant pour étiquette "NOBJ", celui sera aussi
automatiquement renseigné avec le nombre d'objets liés au bloc.

Le bloc "TotalPerimeter" peut être dynamique.

Format de l'affichage de l'attribut PERIM

Le nombre de décimales affichées dépend de la valeur de la variable PERIMPREC

Facteur de conversion

Il est possible d'affecter un facteur de conversion à la valeur de l'attribut.
Cette valeur est gérée avec une variable (PERIMCONV) qui peut être modifiée avec la
commande du même nom.
|;

(vl-load-com)
(or *acdoc*
    (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
)
(or *blocks* (setq *blocks* (vla-get-Blocks *acdoc*)))
(setq *gc:TotalPerimModified*
       nil
      *gc:TotalPerimLispReactor*
       nil
      *gc:TotalPerimCommandReactor*
       nil
)

;;;===============================================;;;

;;; PERIMBOX (gile)
;;; Boite de dialogue d'appel des commandes

(defun c:Perimbox (/ tmp file what_next dcl_id result)
  (or (getenv "PerimConv") (setenv "PerimConv" "1"))
  (or (getenv "PerimPrec")
      (setenv "PerimPrec" (itoa (getvar "LUPREC")))
  )
  (setq	tmp  (vl-filename-mktemp "Tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    "PerimBox:dialog{label=\"Longueurs cumulées\";
    :boxed_column{label=\"Commandes\";:row{
    :button{label=\"TotalPerim\";key=\"(c:totalperim)\";width=16;}
    spacer;:text{label=\"Insérer et lier\";width= 20;}}
    :row{
    :button{label=\"PerimEdit\";key=\"(c:perimedit)\";width=16;}
    spacer;:text{label=\"Modifier\";width= 20;}}
    :row{
    :button{label=\"PerimShow\";key=\"(c:perimshow)\";width=16;}
    spacer;:text{label=\"Visualiser\";width= 20;}}}
    :boxed_column{label=\"Variables\";:row{
    :text{key=\"ConvValue\";width= 20;}
    :button{label=\"PerimConv\";key=\"perimconv\";width=16;}}
    :row{:text{key=\"PrecValue\";width= 20;}
    :button{label=\"PerimPrec\";key=\"perimprec\";width=16;}}}
    spacer;cancel_button;}"
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (setq what_next 2)
  (while (>= what_next 2)
    (if	(not (new_dialog "PerimBox" dcl_id))
      (exit)
    )
    (set_tile "ConvValue"
	      (strcat "PERIMCONV = " (getenv "PerimConv"))
    )
    (set_tile "PrecValue"
	      (strcat "PERIMPREC = " (getenv "PerimPrec"))
    )
    (foreach k '("(c:totalperim)"
		 "(c:perimedit)"
		 "(c:perimshow)"
		)
      (action_tile k "(setq result $key) (done_dialog)")
    )
    (action_tile "perimconv" "(done_dialog 3)")
    (action_tile "perimprec" "(done_dialog 4)")
    (action_tile "help" "(done_dialog 5)")
    (action_tile "cancel" "(done_dialog 0)")
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3) (c:perimconv))
      ((= what_next 4) (c:perimprec))
    )
  )
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  (and result (eval (read result)))
  (princ)
)

;;;===============================================;;;

;; TotalPerimBox
;; Boite de dialgue de la commande TotalPerim

(defun TotalPerimBox (/	      lbl     unt     scl     lay     lst
		      tmp     file    what_next	      dcl_id  data
		      result
		     )
  (or (getenv "PerimConv") (setenv "PerimConv" "1"))
  (or (getenv "PerimPrec")
      (setenv "PerimPrec" (itoa (getvar "LUPREC")))
  )
  (or (setq lbl (vlax-ldata-get "TotalPerimeter" "lbl"))
      (setq lbl (vlax-ldata-put "TotalPerimeter" "lbl" "Longueur totale"))
  )
  (or (setq unt (vlax-ldata-get "TotalPerimeter" "unt"))
      (setq unt (vlax-ldata-put "TotalPerimeter" "unt" "m"))
  )
  (or (setq scl (vlax-ldata-get "TotalPerimeter" "scl"))
      (setq scl (vlax-ldata-put "TotalPerimeter" "scl" 1))
  )
  (while (setq lay (tblnext "LAYER" (not lay)))
    (setq lst (cons (cdr (assoc 2 lay)) lst))
  )
  (setq lst (vl-sort lst '<))
  (setq lay (getvar "CLAYER"))
  (setq	tmp  (vl-filename-mktemp "Tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    "PerimBox:dialog{label=\"TotalPerim\";
    :boxed_column{label=\"Attributs\";
    :row{:text{label=\"Libellé\";}
    :edit_box{key=\"lbl\";width=24;}}
    :row{:text{label=\"Unités\";}
    :edit_box{key=\"unt\";fixed_width=true;}}}
    :boxed_column{label=\"Propriétés\";
    :row{:text{label=\"Echelle\";}
    :edit_box{key=\"scl\";fixed_width=true;}}
    :popup_list{label=\"Calque\";key=\"lay\";}}
    :boxed_column{label=\"Variables\";:row{
    :text{key=\"ConvValue\";width= 20;}
    :button{label=\"PerimConv\";key=\"perimconv\";width=16;}}
    :row{:text{key=\"PrecValue\";width= 20;}
    :button{label=\"PerimPrec\";key=\"perimprec\";width=16;}}}
    spacer;ok_cancel_help;}"
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (setq what_next 2)
  (while (>= what_next 2)
    (if	(not (new_dialog "PerimBox" dcl_id))
      (exit)
    )
    (start_list "lay")
    (mapcar 'add_list lst)
    (end_list)
    (set_tile "lbl" lbl)
    (set_tile "unt" unt)
    (set_tile "scl" (rtos scl))
    (set_tile "lay" (itoa (vl-position lay lst)))
    (set_tile "ConvValue"
	      (strcat "PERIMCONV = " (getenv "PerimConv"))
    )
    (set_tile "PrecValue"
	      (strcat "PERIMPREC = " (getenv "PerimPrec"))
    )
    (action_tile "lbl" "(setq lbl $value)")
    (action_tile "unt" "(setq unt $value)")
    (action_tile
      "scl"
      "(if (< 0 (distof $value))
	(setq scl (distof $value))
	(progn (alert \"Nécessite une échelle valide.\")
	  (setq scl (vlax-ldata-get \"TotalPerimeter\" \"scl\"))
	  (set_tile \"scl\" (rtos scl))
	  (mode_tile \"scl\" 2)))"
    )
    (action_tile "lay" "(setq lay (nth (atoi $value) lst))")
    (action_tile "perimconv" "(done_dialog 3)")
    (action_tile "perimprec" "(done_dialog 4)")
    (action_tile "help" "(done_dialog 5)")
    (action_tile "cancel" "(done_dialog 0)")
    (action_tile
      "accept"
      "(setq result (list lbl unt scl lay))
      (vlax-ldata-put \"TotalPerimeter\" \"lbl\" lbl)
      (vlax-ldata-put \"TotalPerimeter\" \"unt\" unt)
      (vlax-ldata-put \"TotalPerimeter\" \"scl\" scl)
      (done_dialog 1)"
    )
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3) (c:perimconv))
      ((= what_next 4) (c:perimprec))
      ((= what_next 5) (help "TotalPerim"))
    )
  )
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  result
)

;;;===============================================;;;

;;; TOTALPERIM (gile)
;;; Insère le bloc "TotalPerimeter" dont la valeur de l'attribut "PERIM" est égale à
;;; l'aire totale des objets sélectionnés

(defun c:TotalPerim
       (/ *error* space dz bloc data tot ss lst ins scl blk)
  (vl-load-com)
  (or *acdoc*
      (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
  )

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "\Erreur: " msg))
    )
    (setvar "DIMZIN" dz)
    (vla-EndUndoMark *acdoc*)
    (princ)
  )

  (or (getenv "PerimConv") (setenv "PerimConv" "1"))
  (or (getenv "PerimPrec")
      (setenv "PerimPrec" (itoa (getvar "LUPREC")))
  )
  (princ (strcat "\nParamètres courants : PERIMCONV = "
		 (getenv "PerimConv")
		 " PERIMPREC = "
		 (getenv "PerimPrec")
		 "\n"
	 )
  )
  (setq	Space (if (= (getvar "CVPORT") 1)
		(vla-get-PaperSpace *acdoc*)
		(vla-get-ModelSpace *acdoc*)
	      )
	dz    (getvar "DIMZIN")
  )
  (if (or
	(gc:GetItem
	  (vla-get-Blocks *acdoc*)
	  (setq bloc "TotalPerimeter")
	)
	(findfile (setq bloc "TotalPerimeter.dwg"))
      )
    (if	(setq data (TotalPerimBox))
      (if
	(ssget
	  '((-4 . "<OR")
	    (0
	     .
	     "ARC,CIRCLE,ELLIPSE,LINE,LWPOLYLINE,SPLINE,REGION,MPOLYGON"
	    )
	    (-4 . "<AND")
	    (0 . "POLYLINE")
	    (-4 . "<NOT")
	    (-4 . "&")
	    (70 . 112)
	    (-4 . "NOT>")
	    (-4 . "AND>")
	    (-4 . "OR>")
	   )
	)
	 (progn
	   (setq tot 0.0)
	   (vla-StartUndoMark *acdoc*)
	   (vlax-for obj (setq ss (vla-get-ActiveSelectionset *acdoc*))
	     (if (member (vla-get-ObjectName obj)
			 '("AcDbMPolygon" "AcDbRegion")
		 )
	       (setq tot (+ tot (vla-get-Perimeter obj)))
	       (setq tot (+ tot
			    (vlax-curve-getDistAtParam
			      obj
			      (vlax-curve-getEndParam obj)
			    )
			 )
	       )
	     )
	     (setq lst (cons obj lst))
	   )
	   (vla-delete ss)
	   (initget 1)
	   (setq ins (getpoint "\nSpécifiez le point d'insertion: ")
		 scl (caddr data)
		 blk (vla-insertBlock
		       Space
		       (vlax-3d-point (trans ins 1 0))
		       bloc
		       scl
		       scl
		       scl
		       0.0
		     )
	   )
	   (vla-put-layer blk (cadddr data))

	   ;;------------------------------------------------------------------;;
	   ;; Forcer l'affichage des zéros de fin dand les décimales
	   ;; Mettre un point-virgule devant la ligne pour supprimer cette option
	   (setvar "DIMZIN" (Boole 2 (getvar "DIMZIN") 8))
	   ;;------------------------------------------------------------------;;

	   (foreach att	(vlax-invoke blk 'GetAttributes)
	     (cond
	       ((= (vla-get-TagString att) "LABEL")
		(vla-put-TextString att (car data))
	       )
	       ((= (vla-get-TagString att) "UNIT")
		(vla-put-TextString att (cadr data))
	       )
	       ((= (vla-get-TagString att) "PERIM")
		(vla-put-Textstring
		  att
		  (rtos	(/ tot (distof (getenv "PerimConv")))
			2
			(atoi (getenv "PerimPrec"))
		  )
		)
	       )
	       ((= (vla-get-TagString att) "NOBJ")
		(vla-put-TextString att (itoa (length lst)))
	       )
	     )
	   )

	   (vlax-ldata-put
	     blk
	     "TotalPerimeter"
	     (mapcar 'vla-get-Handle lst)
	   )
	   (setvar "DIMZIN" dz)

	   ;;------------------------------------------------------------------;;
	   ;; Création des réacteurs
	   (foreach obj	lst
	     (vlr-object-reactor
	       (list obj)
	       (vla-get-Handle blk)
	       '((:vlr-erased . GC:PERIMOBJECTERASED)
		 (:vlr-unerased . GC:PERIMOBJECTUNERASED)
		 (:vlr-modified . GC:PERIMOBJECTMODIFIED)
		)
	     )
	   )
	   ;;------------------------------------------------------------------;;

	   (vla-EndUndoMark *acdoc*)
	 )
      )
    )
    (princ "\nLe bloc \"TotalPerimeter\" est introuvable.")
  )
  (princ)
)

;;;===============================================;;;

;;; PERIMEDIT (gile)
;;; Lie ou délie les objets sélectionnés au bloc "TotalPerimeter"

(defun c:PerimEdit (/ *error* lst blk obj rea)
  (vl-load-com)
  (or *acdoc*
      (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
  )

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "\Erreur: " msg))
    )
    (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	    lst
    )
    (vla-EndUndoMark *acdoc*)
    (princ)
  )

  (sssetfirst nil nil)
  (if (setq lst (gc:PerimGet "\nSélectionnez le bloc à modifier: "))
    (progn
      (setq blk	(car lst)
	    lst	(cadr lst)
      )
      (vla-StartUndoMark *acdoc*)
      (while (setq obj
		    (car
		      (entsel
			"\nSélectionnez un objet à ajouter ou supprimer: "
		      )
		    )
	     )
	(if
	  (or
	    (gc:IsCurveObject obj)
	    (member (cdr (assoc 0 (entget obj))) '("MPOLYGON" "REGION"))
	  )
	   (if (member (setq obj (vlax-ename->vla-object obj)) lst)
	     (progn
	       (setq lst (vl-remove obj lst))
	       (vla-highlight obj :vlax-false)
	       (if (setq rea (gc:GetPerimObjectReactor obj blk))
		 (vlr-remove rea)
	       )
	     )
	     (progn
	       (setq lst (cons obj lst))
	       (vla-highlight obj :vlax-true)
	       (vlr-object-reactor
		 (list obj)
		 (vla-get-Handle blk)
		 '((:vlr-erased . GC:PERIMOBJECTERASED)
		   (:vlr-unerased . GC:PERIMOBJECTUNERASED)
		   (:vlr-modified . GC:PERIMOBJECTMODIFIED)
		  )
	       )
	     )
	   )
	)
	(gc:TotalPerimUpd blk lst)
      )
      (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	      lst
      )
      (vla-EndUndoMark *acdoc*)
    )
  )
  (princ)
)

;;;===============================================;;;

;;; PERIMSHOW (gile)
;;; Met en surbrillance les objets liés au bloc sur lequel passe le curseur

(defun c:PerimShow (/ blk lst)
  (and (setq lst (gc:PerimGet ""))
       (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	       (cadr lst)
       )
  )
  (princ)
)

;;;===============================================;;;

;;; PERIMCONV (gile)
;;; Modifier la valeur de la variable PERIMCONV
;;; Cette variable, enregistrée dans la base de registre gère le facteur
;;; de conversion pour les unités de surface.
;;; exemple : 100 pour cm -> m, 1000 pour m -> km

(defun c:PerimConv ()
  (or (getenv "PerimConv") (setenv "PerimConv" "1"))
  (while
    (not
      ((lambda (r)
	 (or (= r "")
	     (< 0 (distof r))
	 )
       )
	(setq
	  r (getstring
	      (strcat "\nEntrez une nouvelle valeur pour PERIMCONV <"
		      (getenv "PerimConv")
		      ">: "
	      )
	    )
	)
      )
    )
     (princ "\nNécessite un nombre strictement positif")
  )
  (or (= r "")
      (and (setenv "PerimConv" r) (gc:PerimUpdAll))
  )
  (princ)
)

;;;===============================================;;;

;;; PERIMPREC (gile)
;;; Modifier la valeur de la variable PERIMPREC
;;; Cette variable, enregistrée dans la base de registre, gère le nombre de
;;; décimales affichées.

(defun c:PerimPrec ()
  (or (getenv "PerimPrec")
      (setenv "PerimPrec" (itoa (getvar "LUPREC")))
  )
  (while
    (not
      ((lambda (r)
	 (or (= r "")
	     (and
	       (= 'INT (type (read r)))
	       (<= 0 (atoi r))
	     )
	 )
       )
	(setq
	  r (getstring
	      (strcat "\nEntrez une nouvelle valeur pour PERIMPREC <"
		      (getenv "PerimPrec")
		      ">: "
	      )
	    )
	)
      )
    )
     (princ "\nNécessite un nombre entier positif")
  )
  (or (= r "")
      (and (setenv "PerimPrec" r) (gc:PerimUpdAll))
  )
  (princ)
)

;;;===============================================;;;

;;; PerimHelp (gile)
;;; Ouvre l'aide

(defun c:perimhelp ()
  (help "TotalPerim")
  (princ)
)

(foreach cmd '("c:TotalPerim"	   "c:PerimEdit"
	       "c:PerimShow"	   "c:PerimConv"
	       "c:PerimPrec"
	      )
  (setfunhelp cmd "TotalPerim.chm")
)

;;;================== SOUS ROUTINES ==================;;;

;;; gc:TotalPerimUpd (gile)
;;; Mise à jour les attributs d'un bloc "TotalPerimeter"

(defun gc:TotalPerimUpd	(blk lst / *error* dz tot new)
  (vl-load-com)

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "\Erreur: " msg))
    )
    (setvar "DIMZIN" dz)
    (princ)
  )

  (setq dz (getvar "DIMZIN"))

  ;;------------------------------------------------------------------;;
  ;; Forcer l'affichage des zéros de fin dand les décimales
  ;; Mettre un point-virgule devant la ligne pour supprimer cette option
  (setvar "DIMZIN" (Boole 2 (getvar "DIMZIN") 8))
  ;;------------------------------------------------------------------;;

  (if lst
    (progn
      (setq tot 0.0)
      (foreach obj lst
	(if obj
	  (progn
	    (if	(member	(vla-get-ObjectName obj)
			'("AcDbMPolygon" "AcDbRegion")
		)
	      (setq tot (+ tot (vla-get-Perimeter obj)))
	      (setq tot	(+ tot
			   (vlax-curve-getDistAtParam
			     obj
			     (vlax-curve-getEndParam obj)
			   )
			)
	      )
	    )
	    (setq new (cons (vla-get-Handle obj) new))
	  )
	)
      )
      (foreach att (vlax-invoke blk 'GetAttributes)
	(cond
	  ((= (vla-get-TagString att) "PERIM")
	   (vla-put-Textstring
	     att
	     (rtos (/ tot (distof (getenv "PerimConv")))
		   2
		   (atoi (getenv "PerimPrec"))
	     )
	   )
	  )
	  ((= (vla-get-TagString att) "NOBJ")
	   (vla-put-TextString att (itoa (length lst)))
	  )
	)
      )
    )
    (foreach att (vlax-invoke blk 'GetAttributes)
      (cond
	((= (vla-get-TagString att) "PERIM")
	 (vla-put-Textstring
	   att
	   (rtos 0.0 2 (atoi (getenv "PerimPrec")))
	 )
	)
	((= (vla-get-TagString att) "NOBJ")
	 (vla-put-TextString att "0")
	)
      )
    )
  )
  (vlax-ldata-put blk "TotalPerimeter" new)
  (setvar "DIMZIN" dz)
)

;;;===============================================;;;

;;; gc:PerimGet (gile)
;;; Retourne un liste contenant un bloc "TotalPerimeter" et la liste d'objets liés
;;; Les objets liés à un bloc sont mis en surbrillance quand le curseur est sur ce bloc

(defun gc:PerimGet (msg / *error* gr ent l1 found blk obj l2)

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "\nErreur: " msg))
    )
    (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	    l2
    )
    (princ)
  )

  (princ msg)
  (while (and (setq gr (grread T 4 2)) (= (car gr) 5))
    (if	(and (setq ent (nentselp (cadr gr)))
	     (or
	       (and
		 (caddr ent)
		 (setq ent (last (last ent)))
	       )
	       (setq ent (cdr (assoc 330 (entget (car ent)))))
	     )
	)
      (if (and (setq blk (vlax-ename->vla-object ent))
	       (= (vla-get-ObjectName blk) "AcDbBlockReference")
	       (= (vla-get-EffectiveName blk) "TotalPerimeter")
	  )
	(progn
	  (setq	found T
		l1    (vlax-ldata-get ent "TotalPerimeter")
	  )
	  (foreach h l1
	    (if	(setq obj (gc:HandleToObject h))
	      (progn
		(vla-highlight obj :vlax-true)
		(or (member obj l2) (setq l2 (cons obj l2)))
	      )
	    )
	  )
	)
      )
      (progn
	(mapcar	(function (lambda (x) (vla-highlight x :vlax-false)))
		l2
	)
	(setq l2 nil
	      found nil
	)
      )
    )
  )
  (if (and (= (car gr) 3) found)
    (list (vlax-ename->vla-object ent) l2)
    (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	    l2
    )
  )
)

;;;===============================================;;;

;;; gc:PerimUpdAll
;;; Met à jour tous les blocs "ToTalPerimeter"

(defun gc:PerimUpdAll (/ ss)
  (if (ssget "_X" '((0 . "INSERT") (2 . "TotalPerimeter,`*U*")))
    (progn
      (vlax-for	blk (setq ss (vla-get-activeSelectionSet *acdoc*))
	(if (= (vla-get-EffectiveName blk) "TotalPerimeter")
	  (gc:TotalPerimUpd
	    blk
	    (mapcar 'gc:HandleToObject
		    (vlax-ldata-get blk "TotalPerimeter")
	    )
	  )
	)
      )
      (vla-delete ss)
    )
  )
)

;;;===============================================;;;

;;; gc:GetPerimObjectReactor
;;; Retourne le réacteur de l'objet lié au bloc
;;; Arguments
;;; obj : l'objet propriétaire (vla-object)
;;; blk : le bloc lié à l'objet (vla-object)
;;;
;;; Retour : le reacteur ou nil

(defun gc:GetPerimObjectReactor	(obj blk / lst rea loop)
  (setq	lst  (cdr (assoc :VLR-Object-Reactor (vlr-reactors)))
	loop T
  )
  (while (and lst loop)
    (setq rea (car lst)
	  lst (cdr lst)
    )
    (if	(and
	  (equal (vlr-owners rea) (list obj))
	  (= (vlr-data rea) (vla-get-Handle blk))
	)
      (setq loop nil)
      (setq rea nil)
    )
  )
  rea
)

;;;===============================================;;;

;;; gc:GetItem (gile)
;;; Retourne le vla-object de l'item s'il est présent dans la collection
;;;
;;; Arguments
;;; col : la collection (vla-object)
;;; name : le nom de l'objet (string) ou son indice (entier)
;;;
;;; Retour : le vla-object ou nil

(defun gc:GetItem (col name / obj)
  (vl-catch-all-apply
    (function (lambda () (setq obj (vla-item col name))))
  )
  obj
)

;;;===============================================;;;

;; gc:HandleToObject (gile)
;; Retourne le VLA-OBJECT d'après son handle
;;; Argument
;;; handle : le handle de l'objet
;;;
;;; Retour : le vla-object ou nil

(defun gc:HandleToObject (handle / obj)
  (vl-catch-all-apply
    (function
      (lambda ()
	(setq obj (vla-HandleToObject
		    (vla-get-ActiveDocument (vlax-get-acad-object))
		    handle
		  )
	)
      )
    )
  )
  obj
)

;;;===============================================;;;

;;; gc:IsCurveObject (gile)
;;; Evalue si un objet (ename ou vla-object) est un "CurveObject"

(defun gc:IsCurveObject	(obj)
  (and
    (or	(= (type obj) 'VLA-OBJECT)
	(setq obj (vlax-ename->vla-object obj))
    )
    (member (vla-get-ObjectName obj)
	    '("AcDbArc"		  "AcDbCircle"
	      "AcDbEllipse"	  "AcDbLine"
	      "AcDbPolyline"	  "AcDb2dPolyline"
	      "AcDb3dPolyline"	  "AcDbSpline"
	     )
    )
  )
)

;;;================== RETRO APPELS ==================;;;

(defun GC:PERIMOBJECTERASED (own rea lst)
  (vlr-remove rea)
)

;;;===============================================;;;

(defun GC:PERIMOBJECTUNERASED (own rea lst / blk)
  (if (setq blk (gc:HandleToObject (vlr-data rea)))
    (vlr-add rea)
    (vlr-remove rea)
  )
)

;;;===============================================;;;

(defun GC:PERIMOBJECTMODIFIED (own rea lst)
  (setq *gc:TotalPerimModified* (cons rea *gc:TotalPerimModified*))
  (if (zerop (getvar 'cmdactive))
    (or	*gc:TotalPerimLispReactor*
	(setq *gc:TotalPerimLispReactor*
	       (vlr-lisp-reactor
		 nil
		 '((:VLR-lispEnded . GC:TOTALPERIMLISPENDED))
	       )
	)
    )
    (or	*gc:TotalPerimCommandReactor*
	(setq *gc:TotalPerimCommandReactor*
	       (vlr-command-reactor
		 nil
		 '((:VLR-commandEnded . GC:TOTALPERIMCOMMANDENDED))
	       )
	)
    )
  )
)

(defun GC:TOTALPERIMCOMMANDENDED (rea cmd / blk data)
  (foreach r *gc:TotalPerimModified*
    (if	(setq blk (gc:HandleToObject (vlr-data r)))
      (if (setq data (vlax-ldata-get blk "TotalPerimeter"))
	(gc:TotalPerimUpd blk (mapcar 'gc:HandleToObject data))
      )
      (vlr-remove r)
    )
  )
  (vlr-remove *gc:TotalPerimCommandReactor*)
  (setq	*gc:TotalPerimCommandReactor*
	 nil
	*gc:TotalPerimModified*
	 nil
  )
)

;;;===============================================;;;

(defun GC:TOTALPERIMLISPENDED (rea cmd / blk data)
  (foreach r *gc:TotalPerimModified*
    (if	(setq blk (gc:HandleToObject (vlr-data r)))
      (if (setq data (vlax-ldata-get blk "TotalPerimeter"))
	(gc:TotalPerimUpd blk (mapcar 'gc:HandleToObject data))
      )
      (vlr-remove r)
    )
  )
  (vlr-remove *gc:TotalPerimLispReactor*)
  (setq	*gc:TotalPerimLispReactor*
	 nil
	*gc:TotalPerimModified*
	 nil
  )
)

;;;==================== CREATION DES REACTEURS AU CHARGEMENT ====================;;;

((lambda (/ ss obj)
   (foreach r (cdr (assoc :VLR-Object-Reactor (vlr-reactors)))
     (if (member '(:VLR-erased . GC:PERIMOBJECTERASED)
		 (vlr-reactions r)
	 )
       (vlr-remove r)
     )
   )
   (if (ssget "_X" '((0 . "INSERT") (2 . "TotalPerimeter,`*U*")))
     (progn
       (vlax-for blk (setq ss (vla-get-ActiveSelectionSet *acdoc*))
	 (if
	   (and
	     (vlax-property-available-p blk 'EffectiveName)
	     (= (strcase (vla-get-EffectiveName blk)) "TOTALPERIMETER")
	   )
	    (progn
	      (foreach hand
			    (vlax-ldata-get blk "TotalPerimeter")
		(if (setq obj (gc:HandleToObject hand))
		  (vlr-object-reactor
		    (list obj)
		    (vla-get-Handle blk)
		    '((:vlr-erased . GC:PERIMOBJECTERASED)
		      (:vlr-unerased . GC:PERIMOBJECTUNERASED)
		      (:vlr-modified . GC:PERIMOBJECTMODIFIED)
		     )
		  )
		)
	      )
	      (gc:TotalPerimUpd
		blk
		(mapcar	'gc:HandleToObject
			(vlax-ldata-get blk "TotalPerimeter")
		)
	      )
	    )
	 )
       )
       (vla-delete ss)
     )
   )
 )
)

(princ)