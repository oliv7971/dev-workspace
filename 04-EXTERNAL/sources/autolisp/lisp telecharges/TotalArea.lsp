;| TOTALAREA version 4.1.0 (gile)
Définit les commandes AREABOX, TOTALAREA, AREAEDIT, AREASHOW
et les variables AREACONV, AREAPREC

Bloc "TotalArea"

Une définition bloc nommé "TotalArea" doit être présente dans le dessin ou sous
forme de fichier "TotalArea.dwg" dans un répertoire du chemin de recherche.

Ce bloc doit contenir au moins trois attributs ayant pour étiquettes "LABEL", "UNIT" et "AREA".
Ce dernier sera automatiquement renseigné avec la somme des aires des objets qui lui sont liés.
(arc, cercle, ellipse, polyligne, spline, hachure, region, mpolygon)

S1 le bloc contient un autre attribut ayant pour étiquette "NOBJ", celui sera aussi
automatiquement renseigné avec le nombre d'objets liés au bloc.

Le bloc "TotalArea" peut être un bloc dynamique.

Format de l'affichage de l'attribut "AREA"

Le nombre de décimales affichées dépend de la valeur de la variable AREAPREC

Facteur de conversion

Il est possible d'affecter un facteur de conversion à la valeur de l'attribut.
Cette valeur est gérée avec une variable (AREACONV) qui peut être modifiée avec la
commande du même nom.
|;

;;;===============================================;;;

(vl-load-com)
(or *acdoc*
    (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
)

(setq *gc:TotalAreaModified*
       nil
      *gc:TotalAreaLispReactor*
       nil
      *gc:TotalAreaCommandReactor*
       nil
)

;;; AREABOX (gile)
;;; Boite de dialogue d'appel des commandes

(defun c:Areabox (/ tmp file what_next dcl_id result)
  (or (getenv "AreaConv") (setenv "AreaConv" "1"))
  (or (getenv "AreaPrec")
      (setenv "AreaPrec" (itoa (getvar "LUPREC")))
  )
  (setq	tmp  (vl-filename-mktemp "Tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    "AreaBox:dialog{label=\"Surfaces cumulées\";
    :boxed_column{label=\"Commandes\";:row{
    :button{label=\"TotalArea\";key=\"(c:totalarea)\";width=16;}
    spacer;:text{label=\"Insérer et lier\";width= 20;}}
    :row{
    :button{label=\"AreaEdit\";key=\"(c:areaedit)\";width=16;}
    spacer;:text{label=\"Modifier\";width= 20;}}
    :row{
    :button{label=\"AreaShow\";key=\"(c:areashow)\";width=16;}
    spacer;:text{label=\"Visualiser\";width= 20;}}}
    :boxed_column{label=\"Variables\";:row{
    :text{key=\"ConvValue\";width= 20;}
    :button{label=\"AreaConv\";key=\"areaconv\";width=16;}}
    :row{:text{key=\"PrecValue\";width= 20;}
    :button{label=\"AreaPrec\";key=\"areaprec\";width=16;}}}
    spacer;cancel_button;}"
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (setq what_next 2)
  (while (>= what_next 2)
    (if	(not (new_dialog "AreaBox" dcl_id))
      (exit)
    )
    (set_tile "ConvValue"
	      (strcat "AREACONV = " (getenv "AreaConv"))
    )
    (set_tile "PrecValue"
	      (strcat "AREAPREC = " (getenv "AreaPrec"))
    )
    (foreach k '("(c:totalarea)"
		 "(c:areaedit)"
		 "(c:areashow)"
		)
      (action_tile k "(setq result $key) (done_dialog)")
    )
    (action_tile "areaconv" "(done_dialog 3)")
    (action_tile "areaprec" "(done_dialog 4)")
    (action_tile "cancel" "(done_dialog 0)")
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3) (c:areaconv))
      ((= what_next 4) (c:areaprec))
    )
  )
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  (and result (eval (read result)))
  (princ)
)

;;;===============================================;;;

;; TotalAreaBox
;; Boite de dialgue de la commande TotalArea

(defun TotalAreaBox (/	     lbl     unt     scl     lay     lst
		     tmp     file    what_next	     dcl_id  data
		     result
		    )
  (or (getenv "AreaConv") (setenv "AreaConv" "1"))
  (or (getenv "AreaPrec")
      (setenv "AreaPrec" (itoa (getvar "LUPREC")))
  )
  (or (setq lbl (vlax-ldata-get "TotalArea" "lbl"))
      (setq lbl (vlax-ldata-put "TotalArea" "lbl" "Aire totale"))
  )
  (or (setq unt (vlax-ldata-get "TotalArea" "unt"))
      (setq unt (vlax-ldata-put "TotalArea" "unt" "m²"))
  )
  (or (setq scl (vlax-ldata-get "TotalArea" "scl"))
      (setq scl (vlax-ldata-put "TotalArea" "scl" 1))
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
    "AreaBox:dialog{label=\"TotalArea\";
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
    :button{label=\"AreaConv\";key=\"areaconv\";width=16;}}
    :row{:text{key=\"PrecValue\";width= 20;}
    :button{label=\"AreaPrec\";key=\"areaprec\";width=16;}}}
    spacer;ok_cancel_help;}"
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (setq what_next 2)
  (while (>= what_next 2)
    (if	(not (new_dialog "AreaBox" dcl_id))
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
	      (strcat "AREACONV = " (getenv "AreaConv"))
    )
    (set_tile "PrecValue"
	      (strcat "AREAPREC = " (getenv "AreaPrec"))
    )
    (action_tile "lbl" "(setq lbl $value)")
    (action_tile "unt" "(setq unt $value)")
    (action_tile
      "scl"
      "(if (< 0 (distof $value))
	(setq scl (distof $value))
	(progn (alert \"Nécessite une échelle valide.\")
	  (setq scl (vlax-ldata-get \"TotalArea\" \"scl\"))
	  (set_tile \"scl\" (rtos scl))
	  (mode_tile \"scl\" 2)))"
    )
    (action_tile "lay" "(setq lay (nth (atoi $value) lst))")
    (action_tile "areaconv" "(done_dialog 3)")
    (action_tile "areaprec" "(done_dialog 4)")
    (action_tile "help" "(done_dialog 5)")
    (action_tile "cancel" "(done_dialog 0)")
    (action_tile
      "accept"
      "(setq result (list lbl unt scl lay))
      (vlax-ldata-put \"TotalArea\" \"lbl\" lbl)
      (vlax-ldata-put \"TotalArea\" \"unt\" unt)
      (vlax-ldata-put \"TotalArea\" \"scl\" scl)
      (done_dialog 1)"
    )
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3) (c:areaconv))
      ((= what_next 4) (c:areaprec))
      ((= what_next 5) (help "TotalArea"))
    )
  )
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  result
)

;;;===============================================;;;

;;; TOTALAREA (gile)
;;; Insère le bloc "TotalArea" dont la valeur de l'attribut "AREA" est égale à
;;; l'aire totale des objets sélectionnés

(defun c:TotalArea
       (/ *error* space dz bloc data tot ss lst ins scl blk)

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "\Erreur: " msg))
    )
    (setvar "DIMZIN" dz)
    (vla-EndUndoMark *acdoc*)
    (princ)
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
	  (setq bloc "TotalArea")
	)
	(findfile (setq bloc "TotalArea.dwg"))
      )
    (if	(setq data (TotalAreaBox))
      (if
	(ssget
	  '((-4 . "<OR")
	    (0 . "ARC,CIRCLE,ELLIPSE,LWPOLYLINE,HATCH,MPOLYGON,REGION")
	    (-4 . "<AND")
	    (0 . "POLYLINE")
	    (-4 . "<NOT")
	    (-4 . "&")
	    (70 . 120)
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
	 (progn
	   (setq tot 0.0)
	   (vla-StartUndoMark *acdoc*)
	   (vlax-for obj (setq ss (vla-get-ActiveSelectionset *acdoc*))
	     (setq tot (+ tot (vla-get-Area obj))
		   lst (cons obj lst)
	     )
	   )
	   (vla-delete ss)
	   (initget 1)
	   (setq ins (getpoint "\nSpécifiez le point d'insertion: ")
		 scl (caddr data)
		 blk
		     (vla-insertBlock
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
	   (setvar "DIMZIN" (Boole 2 (getvar "DIMZIN") 8))
	   (foreach att	(vlax-invoke blk 'GetAttributes)
	     (cond
	       ((= (vla-get-TagString att) "LABEL")
		(vla-put-TextString att (car data))
	       )
	       ((= (vla-get-TagString att) "UNIT")
		(vla-put-TextString att (cadr data))
	       )
	       ((= (vla-get-TagString att) "AREA")
		(vla-put-Textstring
		  att
		  (rtos	(/ tot (distof (getenv "areaConv")))
			2
			(atoi (getenv "AreaPrec"))
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
	     "TotalArea"
	     (mapcar 'vla-get-Handle lst)
	   )
	   (setvar "DIMZIN" dz)

	   ;;------------------------------------------------------------------;;
	   ;; Création des réacteurs
	   (foreach obj	lst
	     (vlr-object-reactor
	       (list obj)
	       (vla-get-Handle blk)
	       '((:vlr-erased . GC:AREAOBJECTERASED)
		 (:vlr-unerased . GC:AREAOBJECTUNERASED)
		 (:vlr-modified . GC:AREAOBJECTMODIFIED)
		)
	     )
	   )
	   ;;------------------------------------------------------------------;;

	   (vla-EndUndoMark *acdoc*)
	 )
      )
    )
    (princ "\nLe bloc \"TotalArea\" est introuvable.")
  )
  (princ)
)

;;;===============================================;;;

;;; AREAEDIT (gile)
;;; Lie ou délie les objets sélectionnés au bloc "TotalArea"

(defun c:AreaEdit (/ *error* lst blk obj elst rea)

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
  (if (setq lst (gc:AreaGet "\nSélectionnez le bloc à modifier: "))
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
	(setq elst (entget obj))
	(if (or
	      (member (cdr (assoc 0 elst))
		      '("ARC"	      "CIRCLE"	    "ELLIPSE"
			"LWPOLYLINE"  "HATCH"	    "MPOLYGON"
			"REGION"
		       )
	      )
	      (and (= (cdr (assoc 0 elst)) "POLYLINE")
		   (zerop (logand 120 (cdr (assoc 70 elst))))
	      )
	      (and (= (cdr (assoc 0 elst)) "SPLINE")
		   (= 8 (logand 8 (cdr (assoc 70 elst))))
	      )
	    )
	  (if (member (setq obj (vlax-ename->vla-object obj)) lst)
	    (progn
	      (setq lst (vl-remove obj lst))
	      (vla-highlight obj :vlax-false)
	      (if (setq rea (gc:GetAreaObjectReactor obj blk))
		(vlr-remove rea)
	      )
	    )
	    (progn
	      (setq lst (cons obj lst))
	      (vla-highlight obj :vlax-true)
	      (vlr-object-reactor
		(list obj)
		(vla-get-Handle blk)
		'((:vlr-erased . GC:AREAOBJECTERASED)
		  (:vlr-unerased . GC:AREAOBJECTUNERASED)
		  (:vlr-modified . GC:AREAOBJECTMODIFIED)
		 )
	      )
	    )
	  )
	)
	(gc:TotalAreaUpd blk lst)
      )
      (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	      lst
      )
    )
    (vla-EndUndoMark *acdoc*)
  )
  (princ)
)

;;;===============================================;;;

;;; AREASHOW (gile)
;;; Met en surbrillance les objets liés au bloc sur lequel passe le curseur

(defun c:AreaShow (/ lst)
  (and (setq lst (gc:AreaGet ""))
       (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	       (cadr lst)
       )
  )
  (princ)
)

;;;===============================================;;;

;;; AREACONV (gile)
;;; Modifier la valeur de la variable AREACONV
;;; Cette variable, enregistrée dans la base de registre gère le facteur
;;; de conversion pour les unités de surface.
;;; exemple : 10000 pour cm² -> m², 1000000 (ou 1e6) pour m² -> km²

(defun c:AreaConv ()
  (or (getenv "AreaConv") (setenv "AreaConv" "1"))
  (while
    (not
      ((lambda (r)
	 (or (= r "")
	     (< 0 (distof r))
	 )
       )
	(setq
	  r (getstring
	      (strcat "\nEntrez une nouvelle valeur pour AREACONV <"
		      (getenv "AreaConv")
		      ">: "
	      )
	    )
	)
      )
    )
     (princ "\nNécessite un nombre strictement positif")
  )
  (or (= r "")
      (and (setenv "AreaConv" r) (gc:AreaUpdAll))
  )
  (princ)
)

;;;===============================================;;;

;;; AREAPREC (gile)
;;; Modifier la valeur de la variable AREAPREC
;;; Cette variable, enregistrée dans la base de registre, gère le nombre de
;;; décimales affichées.

(defun c:AreaPrec ()
  (or (getenv "AreaPrec")
      (setenv "AreaPrec" (itoa (getvar "LUPREC")))
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
	      (strcat "\nEntrez une nouvelle valeur pour AREAPREC <"
		      (getenv "AreaPrec")
		      ">: "
	      )
	    )
	)
      )
    )
     (princ "\nNécessite un nombre entier positif")
  )
  (or (= r "")
      (and (setenv "AreaPrec" r) (gc:AreaUpdAll))
  )
  (princ)
)

;;;===============================================;;;

;;; AreaHelp (gile)
;;; Ouvre l'aide

(defun c:areahelp ()
  (help "TotalArea")
  (princ)
)

(foreach cmd '("c:TotalArea" "c:AreaEdit" "c:AreaShow" "c:AreaConv"
	       "c:AreaPrec")
  (setfunhelp cmd "TotalArea.chm")
)

;;;================== SOUS ROUTINES ==================;;;

;;; gc:TotalAreaUpd (gile)
;;; Mise à jour les attribus d'un bloc "TotalArea"

(defun gc:TotalAreaUpd (blk lst / *error* dz tot new)
  (vl-load-com)

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "\Erreur: " msg))
    )
    (setvar "DIMZIN" dz)
    (princ)
  )

  (setq dz (getvar "DIMZIN"))
  (setvar "DIMZIN" (Boole 2 (getvar "DIMZIN") 8))
  (if lst
    (progn
      (setq tot 0.0)
      (foreach obj lst
	(if obj
	  (setq	tot (+ tot (vla-get-Area obj))
		new (cons (vla-get-Handle obj) new)
	  )
	)
      )
      (foreach att (vlax-invoke blk 'GetAttributes)
	(cond
	  ((= (vla-get-TagString att) "AREA")
	   (vla-put-Textstring
	     att
	     (rtos (/ tot (distof (getenv "areaConv")))
		   2
		   (atoi (getenv "AreaPrec"))
	     )
	   )
	  )
	  ((= (vla-get-TagString att) "NOBJ")
	   (vla-put-TextString att (itoa (length new)))
	  )
	)
      )
    )
    (foreach att (vlax-invoke blk 'GetAttributes)
      (cond
	((= (vla-get-TagString att) "AREA")
	 (vla-put-Textstring
	   att
	   (rtos 0.0 2 (atoi (getenv "AreaPrec")))
	 )
	)
	((= (vla-get-TagString att) "NOBJ")
	 (vla-put-TextString att "0")
	)
      )
    )
  )
  (vlax-ldata-put blk "TotalArea" new)
  (setvar "DIMZIN" dz)
)

;;;===============================================;;;

;;; gc:AreaGet (gile)
;;; Retourne un liste contenant un bloc "TotalArea" et la liste des objets liés
;;; Les objets liés à un bloc sont mises en surbrillance quand le curseur est sur ce bloc

(defun gc:AreaGet (msg / *error* gr ent l1 found blk obj l2)

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
	       (= (vla-get-EffectiveName blk) "TotalArea")
	  )
	(progn
	  (setq	found T
		l1    (vlax-ldata-get ent "TotalArea")
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
    (list blk l2)
    (mapcar (function (lambda (x) (vla-highlight x :vlax-false)))
	    l2
    )
  )
)

;;;===============================================;;;

;;; gc:AreaUpdAll
;;; Met à jour tous les blocs "ToTalArea"

(defun gc:AreaUpdAll (/ ss)
  (if (ssget "_X" '((0 . "INSERT") (2 . "TotalArea,`*U*")))
    (progn
      (vlax-for	blk (setq ss (vla-get-activeSelectionSet *acdoc*))
	(if (= (vla-get-EffectiveName blk) "TotalArea")
	  (gc:TotalAreaUpd
	    blk
	    (mapcar 'gc:HandleToObject
		    (vlax-ldata-get blk "TotalArea")
	    )
	  )
	)
      )
      (vla-delete ss)
    )
  )
)

;;;===============================================;;;

;;; gc:GetAreaObjectReactor
;;; Retourne le réacteur de l'objet lié au bloc
;;; Arguments
;;; obj : l'objet propriétaire (vla-object)
;;; blk : le bloc lié à l'objet (vla-object)
;;;
;;; Retour : le reacteur ou nil

(defun gc:GetAreaObjectReactor (obj blk / lst rea loop)
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

;;; gc:HandleToObject (gile)
;;; Retourne le VLA-OBJECT d'après son handle
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

;;;================== RETRO APPELS ==================;;;

(defun GC:AREAOBJECTERASED (own rea lst)
  (vlr-remove rea)
)

;;;===============================================;;;

(defun GC:AREAOBJECTUNERASED (own rea lst / blk)
  (if (setq blk (gc:HandleToObject (vlr-data rea)))
    (vlr-add rea)
    (vlr-remove rea)
  )
)

;;;===============================================;;;

;;;(defun GC:AREAOBJECTMODIFIED (own rea lst / blk data)
;;;  (if (setq blk (gc:HandleToObject (vlr-data rea)))
;;;    (if	(setq data (vlax-ldata-get blk "TotalArea"))
;;;      (gc:TotalAreaUpd blk (mapcar 'gc:HandleToObject data))
;;;    )
;;;    (vlr-remove rea)
;;;  )
;;;)
(defun GC:AREAOBJECTMODIFIED (own rea lst)
  (setq *gc:TotalAreaModified* (cons rea *gc:TotalAreaModified*))
  (if (zerop (getvar 'cmdactive))
    (or	*gc:TotalAreaLispReactor*
	(setq *gc:TotalAreaLispReactor*
	       (vlr-lisp-reactor
		 nil
		 '((:VLR-lispEnded . GC:TOTALAREALISPENDED))
	       )
	)
    )
    (or	*gc:TotalAreaCommandReactor*
	(setq *gc:TotalAreaCommandReactor*
	       (vlr-command-reactor
		 nil
		 '((:VLR-commandEnded . GC:TOTALAREACOMMANDENDED))
	       )
	)
    )
  )
)

;;;===============================================;;;

(defun GC:TOTALAREACOMMANDENDED	(rea cmd / blk data)
  (foreach r *gc:TotalAreaModified*
    (if	(setq blk (gc:HandleToObject (vlr-data r)))
      (if (setq data (vlax-ldata-get blk "TotalArea"))
	(gc:TotalAreaUpd blk (mapcar 'gc:HandleToObject data))
      )
      (vlr-remove r)
    )
  )
  (vlr-remove *gc:TotalAreaCommandReactor*)
  (setq	*gc:TotalAreaCommandReactor*
	 nil
	*gc:TotalAreaModified*
	 nil
  )
)

;;;===============================================;;;

(defun GC:TOTALAREALISPENDED (rea cmd / blk data)
  (foreach r *gc:TotalAreaModified*
    (if	(setq blk (gc:HandleToObject (vlr-data r)))
      (if (setq data (vlax-ldata-get blk "TotalArea"))
	(gc:TotalAreaUpd blk (mapcar 'gc:HandleToObject data))
      )
      (vlr-remove r)
    )
  )
  (vlr-remove *gc:TotalAreaLispReactor*)
  (setq	*gc:TotalAreaLispReactor*
	 nil
	*gc:TotalAreaModified*
	 nil
  )
)

;;;==================== CREATION DES REACTEURS AU CHARGEMENT ====================;;;

((lambda (/ ss obj)
   (foreach r (cdr (assoc :VLR-Object-Reactor (vlr-reactors)))
     (if (member '(:VLR-erased . GC:AREAOBJECTERASED)
		 (vlr-reactions r)
	 )
       (vlr-remove r)
     )
   )
   (if (ssget "_X" '((0 . "INSERT") (2 . "TotalArea,`*U*")))
     (progn
       (vlax-for blk (setq ss (vla-get-ActiveSelectionSet *acdoc*))
	 (if (and
	       (vlax-property-available-p blk 'EffectiveName)
	       (= (strcase (vla-get-EffectiveName blk)) "TOTALAREA")
	     )
	   (progn
	     (foreach hand (vlax-ldata-get blk "TotalArea")
	       (if (setq obj (gc:HandleToObject hand))
		 (vlr-object-reactor
		   (list obj)
		   (vla-get-Handle blk)
		   '((:vlr-erased . GC:AREAOBJECTERASED)
		     (:vlr-unerased . GC:AREAOBJECTUNERASED)
		     (:vlr-objectClosed . GC:AREAOBJECTMODIFIED)
		    )
		 )
	       )
	     )
	     (gc:TotalAreaUpd
	       blk
	       (mapcar 'gc:HandleToObject
		       (vlax-ldata-get blk "TotalArea")
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