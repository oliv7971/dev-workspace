;;; Edit_bloc - Gilles Chanteau - version 3.6 - 04/05/07
;;;
;;; Redéfinit les blocs après modification des propriétés de leurs composants.
;;;
;;; Les modification affectent :
;;; - soit tous les blocs de la collection (insérés ou non)
;;; - soit tous les blocs insérés
;;; - soit une sélection de blocs faite dans le dessin.
;;;
;;; Il est possible de :
;;; - modifier l'échelle globale
;;; - changer l'unité d'insertion (versions postérieures à 2005)
;;; - mettre les objets composant les blocs sur le calque de son choix
;;; - changer la couleur, le type de ligne, l'épaisseur de ligne et le style
;;;   de tracé (STB uniquement) des composants en DuBloc ou DuCalque.
;;;
;;; Les blocs composant les blocs imbriqués sont traités.
;;; Les blocs insérés dans le dessin sont mis à jour en fonction
;;; des modifications effectuées.
;;;
;;; Les paramètres et propriétés des blocs dynamiques n'étant pas pris
;;; en compte par les changements d'échelle, une boite de dialogue demande
;;; confirmation ou infirmation pour les changements d'échelle du bloc.

(vl-load-com)

(defun c:edit_bloc (/
		    ;; Fonctions
		    e_b_err edit_prop	    scl_upd att_upd sub_upd
		    edit_bl
		    ;; Variables
		    AcDoc   dcl_id  loop    u_lst   l_lst   lt_lst
		    lw_lst  lay	    lay-p   col	    col-p   tl
		    tl-p    tl_n    el	    el-p    el_n    plt
		    plt-p   plt_n   e_scl   fact    unt	    i_unt
		    ss	    w	    h	    dis	    ind	    rgb
		    cnm	    tbl	    all	    sel
		   )


;;;******************************************************************* ;;;

  ;; Redéfinition de *error*

  (defun e_b_err (msg)
    (if	(or
	  (= msg "Fonction annulée")
	  (= msg "quitter / sortir abandon")
	)
      (princ)
      (princ (strcat "\nErreur: " msg))
    )
    (vla-endundomark
      (vla-get-ActiveDocument (vlax-get-acad-object))
    )
    (setq *error* m:err
	  m:err	nil
    )
    (princ)
  )

;;;******************************************************************* ;;;

  (defun alert_bloc (name / dcl_id)
    (setq dcl_id (load_dialog "Edit_bloc.dcl"))
    (if	(not (new_dialog "alert_bloc" dcl_id))
      (exit)
    )
    (set_tile "txt" name)
    (action_tile
      "mod"
      (strcat
	"(if (= \"1\" $value)"
	"(setq e_scl T)"
	"(setq e_scl nil))"
      )
    )
    (action_tile
      "anl"
      (strcat
	"(if (= \"1\" $value)"
	"(setq e_scl nil)"
	"(setq e_scl T))"
      )
    )
    (action_tile "accept" "(done_dialog)")
    (start_dialog)
    (unload_dialog dcl_id)
  )

;;;******************************************************************* ;;;

  ;; Modification des propriétés des entités composant le bloc

  (defun edit_prop (ent / acc)
    (if	lay-p
      (vla-put-Layer ent (nth lay l_lst))
    )
    (if	col-p
      (if (< (atoi (substr (getvar "ACADVER") 1 2)) 16)
	(vla-put-Color ent (cdar col))
	(progn
	  (setq	acc (vla-getInterfaceObject
		      (vlax-get-acad-object)
		      (strcat "AutoCAD.AcCmColor."
			      (substr (getvar "acadver") 1 2)
		      )
		    )
	  )
	  (cond
	    ((assoc 430 col)
	     (vla-setNames
	       acc
	       (substr cnm (+ 2 (vl-string-position 36 cnm)))
	       (substr cnm 1 (vl-string-position 36 cnm))
	     )
	     (vla-setRGB
	       acc
	       (lsh rgb -16)
	       (lsh (lsh rgb 16) -24)
	       (lsh (lsh rgb 24) -24)
	     )
	    )
	    ((assoc 420 col)
	     (vla-setRGB
	       acc
	       (lsh rgb -16)
	       (lsh (lsh rgb 16) -24)
	       (lsh (lsh rgb 24) -24)
	     )
	    )
	    (T
	     (vla-put-ColorIndex acc ind)
	    )
	  )
	  (vla-put-TrueColor ent acc)
	)
      )
    )
    (if	tl-p
      (vla-put-LineType
	ent
	(nth tl
	     (subst "ByLayer"
		    "DuCalque"
		    (subst "ByBlock" "DuBloc" lt_lst)
	     )
	)
      )
    )
    (if	el-p
      (vla-put-LineWeight
	ent
	(nth el
	     '(-1  -2  -3  0   5   9   13  15  18  20  25  30  35  40
	       45  50  53  60  70  80  90  100 106 120 140 158 200 211
	      )
	)
      )
    )
    (if	plt
      (if (= 1 plt_n)
	(vla-put-PlotStyleName ent "ByBlock")
	(vla-put-PlotStyleName ent "ByLayer")
      )
    )
  )

;;;******************************************************************* ;;;

  ;; Mise à jour des attributs

  (defun att_upd (obj / att_lst)
    (if	(= :vlax-true (vla-get-HasAttributes obj))
      (if
	(listp (setq att_lst (vl-catch-all-apply
			       'vlax-invoke
			       (list obj 'getAttributes)
			     )
	       )
	)
	 (mapcar
	   '(lambda (x)
	      (if (and e_scl (/= fact 1.0))
		(vla-ScaleEntity
		  x
		  (vla-get-InsertionPoint obj)
		  fact
		)
	      )
	      (edit_prop x)
	    )
	   att_lst
	 )
      )
    )
  )


;;;******************************************************************* ;;;

  ;; Mise à jour de l'échelle en cas de changement d'unité

  (defun scl_upd (obj)
    (if	(and unt
	     (/= unt 0)
	     (/= i_unt unt)
	     (/= i_unt 0)
	)
      (vla-ScaleEntity
	obj
	(vla-get-InsertionPoint obj)
	(cvunit	1
		(nth unt u_lst)
		(nth i_unt u_lst)
	)
      )
    )
  )

;;;******************************************************************* ;;;

  ;; Mise à jour des blocs composant les blocs imbriqués

  (defun sub_upd (obj blc / org ins)
    (if	(and e_scl (/= fact 1.0))
      (progn
	(setq org (vlax-get blc 'origin)
	      ins (vlax-get ent 'InsertionPoint)
	)
	(vla-put-InsertionPoint
	  obj
	  (vlax-3d-point
	    (mapcar '+
		    org
		    (mapcar '(lambda (x)
			       (* x fact)
			     )
			    (mapcar '- ins org)
		    )
	    )
	  )
	)
      )
    )
    (edit_prop obj)
    (att_upd obj)
  )

;;;******************************************************************* ;;;

  ;; Modification des blocs

  (defun edit_bl (/ n obj lst n_lst name bloc i_unt nb)
    ;; Dévérouillage de tous les calques
    (vlax-for clq (vla-get-Layers AcDoc)
      (if (= :vlax-true
	     (vla-get-lock clq)
	  )
	(progn
	  (vla-put-lock clq :vlax-false)
	  (setq clq_lst (cons clq clq_lst))
	)
      )
    )
    ;; Création de la liste des blocs à modifier
    (if	ss
      ;; Si "Sélection" ou "Tous les blocs insérés"
      (progn
	(repeat	(setq n (sslength ss))
	  (setq
	    obj	(vlax-ename->vla-object (ssname ss (setq n (1- n))))
	  )
	  (if (vlax-property-available-p obj 'EffectiveName)
	    (setq name (vla-get-EffectiveName obj))
	    (setq name (vla-get-Name obj))
	  )
	  (if
	    (and
	      (not (member name lst))
	      (= :vlax-false
		 (vla-get-isXref
		   (vla-item (vla-get-Blocks AcDoc) name)
		 )
	      )
	    )
	     (setq lst (cons name lst))
	  )
	)
	;; Ajout des blocs dynamiques anonymes
	(and
	  (setq ss (ssget "_X" '((0 . "INSERT") (2 . "`*U*"))))
	  (repeat (setq n (sslength ss))
	    (setq
	      obj
	       (vlax-ename->vla-object (ssname ss (setq n (1- n))))
	    )
	    (if	(and (member (vla-get-EffectiveName obj) lst)
		     (not (member (vla-get-Name obj) lst))
		)
	      (setq lst (cons (vla-get-Name obj) lst))
	    )
	  )
	)
	;; Ajout des blocs composant les blocs imbriqués à la liste
	(setq n_lst 0)
	(while (setq name (nth n_lst lst))
	  (setq bloc (vla-item (vla-get-blocks acDoc) name))
	  (vlax-for ent	bloc
	    (if	(and (= (vla-get-ObjectName ent) "AcDbBlockReference")
		     (not (member (vla-get-name ent) lst))
		)
	      (setq
		lst (reverse (cons (vla-get-Name ent) (reverse lst)))
	      )
	    )
	  )
	  (setq n_lst (1+ n_lst))
	)
      )
      ;; Si "Toute la collection"
      (vlax-for	bl (vla-get-blocks AcDoc)
	(if (and (= :vlax-false (vla-get-isLayout bl))
		 (= :vlax-false (vla-get-isXref bl))
	    )
	  (setq lst (cons (vla-get-name bl) lst))
	)
      )
    )
    ;; Modification des blocs
    (mapcar
      '(lambda (name)
	 (setq bloc (vla-item (vla-get-blocks AcDoc) name))
	 (if (and e_scl
		  (< 16.1 (read (substr (getvar "ACADVER") 1 4)))
		  (= (vla-get-IsDynamicBlock bloc) :vlax-true)
		  (/= fact 1.0)
	     )
	   (progn
	     (setq e_scl nil)
	     (alert_bloc name)
	   )
	 )
	 (vlax-for ent bloc
	   (if (/= (vla-get-ObjectName ent) "AcDbZombieEntity")
	     (if (/= (vla-get-ObjectName ent) "AcDbBlockReference")
	       (progn
		 (if (and e_scl (/= fact 1.0)) ;_ Echelle
		   (vla-ScaleEntity ent (vla-get-origin bloc) fact)
		 )
		 (edit_prop ent)
	       )
	       (sub_upd ent bloc)
	     )
	   )
	 )
	 (if (< 16.1 (read (substr (getvar "acadver") 1 4))) ;_ Unités
	   (if (/= (setq i_unt (vla-get-units bloc)) unt)
	     (vla-put-Units bloc unt)
	   )
	 )
	 ;; Mise à jour des blocs insérés (attributs et unités)
	 (setq ss (ssget "_X" (list '(0 . "INSERT") (cons 2 name))))
	 (if ss
	   (repeat (setq n (sslength ss))
	     (setq obj (vlax-ename->vla-object
			 (ssname ss (setq n (1- n)))
		       )
	     )
	     (att_upd obj)
	     (scl_upd obj)
	   )
	 )
       )
      lst
    )
    ;; Mise à jour des blocs composant les blocs imbriqués insérés non sélectionnés
    (setq ss
	   (ssget "_X"
		  (cons	'(0 . "INSERT")
			(mapcar '(lambda (x) (cons 2 (strcat "~" x))) lst)
		  )
	   )
    )
    (if	ss
      (repeat (setq nb (sslength ss))
	(setq obj  (vlax-ename->vla-object (ssname ss (setq nb (1- nb))))
	      name (vla-get-Name obj)
	      bloc (vla-item (vla-get-blocks AcDoc) name)
	)
	(vlax-for ent bloc
	  (if (and (= (vla-get-ObjectName ent) "AcDbBlockReference")
		   (member (vla-get-Name ent) lst)
	      )
	    (progn
	      (sub_upd ent bloc)
	      (scl_upd ent)
	    )
	  )
	)
      )
    )
    ;; Revérouillage des calques vérouillés
    (if	clq_lst
      (mapcar '(lambda (x)
		 (vla-put-lock x :vlax-true)
	       )
	      clq_lst
      )
    )
    (vla-Regen AcDoc acAllViewports)
  )

;;;******************************************************************* ;;;

  ;; Boite de dialogue

  (setq	AcDoc	(vla-get-ActiveDocument (vlax-get-acad-object))
	m:err	*error*
	*error*	e_b_err
  )
  (vla-StartUndoMark AcDoc)
  (setq	dcl_id (load_dialog "Edit_bloc.dcl")
	loop   2
	u_lst  (list "Sans unités"     "Pouces"
		     "Pieds"	       "Miles"
		     "Millimètres"     "Centimètres"
		     "Mètres"	       "Kilomètres"
		     "Micropouces"     "Milles"
		     "Yards"	       "Angströms"
		     "Nanomètres"      "Microns"
		     "Décimètres"      "Décamètres"
		     "Hectomètres"     "Gigamètres"
		     "Unités astronomiques"
		     "Parsecs"
		    )
  )
  (vlax-for l (vla-get-Layers AcDoc)
    (or	(wcmatch (vla-get-Name l) "*|*")
	(setq l_lst (cons (vla-get-Name l) l_lst))
    )
  )
  (setq l_lst (acad_strlsort l_lst))
  (vlax-for lt (vla-get-LineTypes AcDoc)
    (setq lt_lst (cons (vla-get-Name lt) lt_lst))
  )
  (setq	lt_lst (reverse	(subst "DuBloc"
			       "ByBlock"
			       (subst "DuCalque" "ByLayer" lt_lst)
			)
	       )
  )
  (setq	lw_lst '("DuCalque"   "DuBloc"	     "Par_défaut"
		 "0.00 mm"     "0.05 mm"     "0.09 mm"
		 "0.13 mm"     "0.15 mm"     "0.18 mm"
		 "0.20 mm"     "0.25 mm"     "0.30 mm"
		 "0.35 mm"     "0.40 mm"     "0.45 mm"
		 "0.50 mm"     "0.53 mm"     "0.60 mm"
		 "0.70 mm"     "0.80 mm"     "0.90 mm"
		 "1.00 mm"     "1.06 mm"     "1.20 mm"
		 "1.40 mm"     "1.58 mm"     "2.00 mm"
		 "2.11 mm"
		)
  )
  (while (<= 2 loop)
    (if	(not (new_dialog "edit_bloc_3" dcl_id))
      (exit)
    )
    (start_list "unt")
    (mapcar 'add_list u_lst)
    (end_list)
    (start_list "lay_l")
    (mapcar 'add_list l_lst)
    (end_list)
    (start_list "tl_l")
    (mapcar 'add_list lt_lst)
    (end_list)
    (start_list "el_l")
    (mapcar 'add_list lw_lst)
    (end_list)
    (setq w (dimx_tile "i_col")
	  h (dimy_tile "i_col")
    )
    (or dis (setq dis 0))
    (start_image "i_col")
    (fill_image 0 0 w h dis)
    (vector_image 0 0 w 0 -18)
    (vector_image 0 0 0 h -18)
    (vector_image w h w 0 -18)
    (vector_image w h 0 h -18)
    (end_image)
    (or lay (setq lay 0))
    (or col (setq col '((62 . 0))))
    (or tl (setq tl 0))
    (or el (setq el 1))
    (or plt (setq plt 0))
    (setq ind (cdr (assoc 62 col))
	  rgb (cdr (assoc 420 col))
	  cnm (cdr (assoc 430 col))
    )
    (and tbl (set_tile "tbl" "1"))
    (and all (set_tile "all" "1"))
    (and sel (set_tile "sel" "1"))
    (set_tile "t_col"
	      (cond
		(cnm
		 (substr cnm (+ 2 (vl-string-position 36 cnm)))
		)
		(rgb
		 (strcat (itoa (lsh rgb -16))
			 ","
			 (itoa (lsh (lsh rgb 16) -24))
			 ","
			 (itoa (lsh (lsh rgb 24) -24))
		 )
		)
		(T
		 (cond
		   ((= ind 256) "DuCalque")
		   ((= ind 0) "DuBloc")
		   ((= ind 1) "Rouge")
		   ((= ind 2) "Jaune")
		   ((= ind 3) "Vert")
		   ((= ind 4) "Cyan")
		   ((= ind 5) "Bleu")
		   ((= ind 6) "Magenta")
		   ((= ind 7) "Blanc")
		   ((strcat "Couleur " (itoa ind)))
		 )
		)
	      )
    )
    (cond
      ((< 16.1 (read (substr (getvar "acadver") 1 4)))
       (mode_tile "unt" 0)
       (if (not unt)
	 (setq unt (getvar "INSUNITS"))
       )
      )
      (T
       (mode_tile "unt" 1)
       (setq unt nil)
      )
    )
    (if	unt
      (set_tile "unt" (itoa unt))
      (set_tile "unt" (itoa (getvar "INSUNITS")))
    )
    (if	(not (or ss tbl))
      (mode_tile "accept" 1)
    )
    (if	(zerop (getvar "PSTYLEMODE"))
      (mode_tile "plt" 0)
      (progn
	(mode_tile "plt" 1)
	(mode_tile "plt_db" 1)
	(mode_tile "plt_dc" 1)
	(setq plt nil)
      )
    )
    (if	e_scl
      (progn
	(set_tile "scl" "1")
	(mode_tile "fact" 0)
      )
      (progn
	(set_tile "scl" "0")
	(mode_tile "fact" 1)
      )
    )
    (if	fact
      (set_tile "fact" (rtos fact))
      (setq fact 1.0)
    )
    (if	lay-p
      (progn
	(mode_tile "lay_l" 0)
	(set_tile "lay" "1")
      )
      (progn
	(mode_tile "lay_l" 1)
	(set_tile "lay" "0")
      )
    )
    (set_tile "lay_l" (itoa lay))
    (if	(equal col '((62 . 0)))
      (set_tile "col_db" "1")
      (set_tile "col_db" "0")
    )
    (if	col-p
      (progn
	(set_tile "col" "1")
	(mode_tile "col_db" 0)
	(mode_tile "col_s" 0)
      )
      (progn
	(set_tile "col" "0")
	(mode_tile "col_db" 1)
	(mode_tile "col_s" 1)
      )
    )
    (if	tl-p
      (progn
	(mode_tile "tl_l" 0)
	(set_tile "tl" "1")
      )
      (progn
	(mode_tile "tl_l" 1)
	(set_tile "tl" "0")
      )
    )
    (set_tile "tl_l" (itoa tl))
    (if	el-p
      (progn
	(mode_tile "el_l" 0)
	(set_tile "el" "1")
      )
      (progn
	(mode_tile "el_l" 1)
	(set_tile "el" "0")
      )
    )
    (set_tile "el_l" (itoa el))
    (if	plt-p
      (progn
	(set_tile "plt" "1")
	(mode_tile "plt_r" 0)
      )
      (progn
	(set_tile "plt" "0")
	(mode_tile "plt_r" 1)
      )
    )
    (set_tile "plt_db" (itoa lay))
    (action_tile
      "tbl"
      "(if (= \"1\" $value)
	(progn (setq ss nil
	tbl T all nil sel nil)
	(mode_tile \"ss\" 1)
	(mode_tile \"accept\" 0)))"
    )
    (action_tile
      "all"
      "(if (= \"1\" $value)
	(progn
	(setq ss (ssget \"_X\" '((0 . \"INSERT\")))
	all T sel nil tbl nil)
	(mode_tile \"ss\" 1)
	(mode_tile \"accept\" 0)))"
    )
    (action_tile
      "sel"
      "(if (= \"1\" $value)
	(progn (mode_tile \"ss\" 0)
        (setq sel T all nil tbl nil)
	(mode_tile \"ss\" 2)
	(mode_tile \"accept\" 1))
	(mode_tile \"accept\" 0))"
    )
    (action_tile
      "ss"
      "(progn (done_dialog 3) (mode_tile \"accept\" 0))"
    )
    (action_tile
      "scl"
      "(if (= \"1\" $value)
      (progn (setq e_scl T)
      (mode_tile \"fact\" 0))
      (progn (setq e_scl nil)
      (mode_tile \"fact\" 1)))"
    )
    (action_tile
      "fact"
      "(if (< 0 (atof $value))
	(setq fact (atof $value))
	(progn (alert \"Entrée non valide\")
	(mode_tile \"fact\" 2)))"
    )
    (action_tile "unt" "(setq unt (atoi $value))")
    (action_tile
      "lay"
      "(if (= \"1\" $value)
	(progn
	(setq lay-p T)
	(setq lay (atoi (get_tile \"lay_l\")))
	(mode_tile \"lay_l\" 0))
	(progn (setq lay-p nil)
	(mode_tile \"lay_l\" 1)))"
    )
    (action_tile "lay_l" "(setq lay (atoi $value))")
    (action_tile
      "col"
      "(if (= \"1\" $value)
	(progn
	(setq col-p T)
	(mode_tile \"col_db\" 0)
	(mode_tile \"col_s\" 0))
	(progn
	(mode_tile \"col_db\" 1)
	(mode_tile \"col_s\" 1)))"
    )
    (action_tile
      "col_db"
      "(if (= \"1\" $value)
      (progn
      (setq col '((62 . 0)) dis 0)
      (set_tile\"col_db\" \"1\")
      (done_dialog 5))
      (done_dialog 4))"
    )
    (action_tile "col_s" "(done_dialog 4)")
    (action_tile
      "tl"
      "(if (= \"1\" $value)
	(progn
	(setq tl-p T)
	(setq tl (atoi (get_tile \"tl_l\")))
	(mode_tile \"tl_l\" 0))
	(progn (setq tl-p nil)
	(mode_tile \"tl_l\" 1)))"
    )
    (action_tile "tl_l" "(setq tl (atoi $value))")
    (action_tile
      "el"
      "(if (= \"1\" $value)
	(progn
	(setq el-p T)
	(setq el (atoi (get_tile \"el_l\")))
	(mode_tile \"el_l\" 0))
	(progn (setq el-p nil)
	(mode_tile \"el_l\" 1)))"
    )
    (action_tile "el_l" "(setq el (atoi $value))")
    (action_tile
      "plt"
      "(if (= \"1\" $value)
	(progn
	(setq plt T)
	(setq plt_n (atoi (get_tile \"plt_db\")))
	(mode_tile \"plt_r\" 0))
	(progn (setq plt nil)
	(mode_tile \"plt_r\" 1)))"
    )
    (action_tile
      "plt_r"
      "(setq plt_n (atoi (get_tile \"plt_db\")))"
    )
    (action_tile "accept" "(done_dialog 1)")
    (setq loop (start_dialog))
    (cond
      ((= loop 3)
       (or
	 (and (= (getvar "PICKFIRST") 1)
	      (setq ss (ssget "_I" '((0 . "INSERT"))))
	 )
	 (setq ss (ssget '((0 . "INSERT"))))
       )
      )
      ((= loop 4)
       (if (< (atoi (substr (getvar "ACADVER") 1 2)) 16)
	 (and (setq col (acad_colordlg 0))
	      (setq col (list (cons 62 col)))
	 )
	 (setq col (acad_truecolordlg '(62 . 0)))
       )
       (setq dis (cdr (assoc 62 col)))
      )
      ((= loop 1)
       (edit_bl)
      )
    )
  )
  (unload_dialog dcl_id)
  (vla-endundomark AcDoc)
  (setq	*error*	m:err
	m:err nil
  )
  (princ)
)