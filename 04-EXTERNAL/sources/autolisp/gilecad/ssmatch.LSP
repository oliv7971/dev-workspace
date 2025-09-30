;; SSM & SSMM -Gilles Chanteau- 19/04/07
;; Sélectionne tous les objets ayant les mêmes propriétés que celles de l'objet sélectionné
;; et qui sont cochées dans la boite de dialogue.
;;
;; Modifié le 08/10/07
;; Ajout d'une case "Nom du bloc" dans la boite de dialogue.
;; Ajout de la commande SSMM qui permet des sélections filtées multiples.

;;;=====================================================================================;;;

;; Boite de dialogue

(defun ssmatch_box (ent / elst nam col lst dis dcl_id w h)
  (setq	elst   (entget ent)
	nam    (if (= (cdr (assoc 0 elst)) "INSERT")
		 (assoc 2 elst)
	       )
	col    (cond ((assoc 420 elst))
		     ((assoc 62 elst))
		     ('(62 . 256))
	       )
	lst    (list (assoc 0 elst)
		     col
		     (assoc 8 elst)
		     (cond
		       ((assoc 6 elst))
		       ('(6 . "BYLAYER"))
		     )
		     (cond
		       ((assoc 370 elst))
		       ('(370 . -1))
		     )
	       )
	col    (cdr col)
	dis    (cond
		 ((cdr (assoc 62 elst)))
		 ((cdr (assoc 62 (tblsearch "LAYER" (cdr (assoc 8 elst))))))
	       )
	dcl_id (load_dialog "ssmatch_box2.dcl")
  )
  (and nam (setq lst (cons nam lst)))
  (if (not (new_dialog "ssmatch_box" dcl_id))
    (exit)
  )
  (setq	w (dimx_tile "e_col")
	h (dimy_tile "e_col")
  )
  (start_image "e_col")
  (fill_image 0 0 w h dis)
  (end_image)
  (set_tile "e_ent" (cdr (assoc 0 elst)))
  (if nam
    (progn
      (set_tile "e_nam" (cdr (assoc 2 elst)))
      (mode_tile "nam" 0)
    )
    (mode_tile "nam" 1)
  )
  (set_tile "t_col"
	    (cond
	      ((= col 256) "DuCalque")
	      ((= col 0) "DuBloc")
	      ((< 256 col)
	       (strcat (itoa (lsh col -16))
		       ","
		       (itoa (lsh (lsh col 16) -24))
		       ","
		       (itoa (lsh (lsh col 24) -24))
	       )
	      )
	      ((itoa col))
	    )
  )
  (set_tile "e_lay" (cdr (assoc 8 elst)))
  (set_tile "e_typ"
	    (cond
	      ((or (null (cdr (assoc 6 elst)))
		   (= (strcase (cdr (assoc 6 elst))) "BYLAYER")
	       )
	       "DuCalque"
	      )
	      ((= (strcase (cdr (assoc 6 lst))) "BYBLOCK")
	       "DuBloc"
	      )
	      ((cdr (assoc 6 lst)))
	    )
  )
  (set_tile "e_wid"
	    (cond
	      ((null (cdr (assoc 370 elst))) "DuCalque")
	      ((= -1 (cdr (assoc 370 elst))) "DuCalque")
	      ((= -2 (cdr (assoc 370 elst))) "DuBlock")
	      ((= -3 (cdr (assoc 370 elst))) "Défaut")
	      ((rtos (/ (cdr (assoc 370 elst)) 100.0) 2 2))
	    )
  )
  (action_tile
    "accept"
    "(or (= \"1\" (get_tile \"ent\"))
      (setq lst (vl-remove (assoc 0 lst) lst))
    )
    (or (= \"1\" (get_tile \"nam\"))
      (setq lst (vl-remove (assoc 2 lst) lst))
    )
    (or (= \"1\" (get_tile \"col\"))
      (setq lst (vl-remove (assoc 420 lst)
      (vl-remove (assoc 62 lst) lst)))
    )
    (or	(= \"1\" (get_tile \"lay\"))
      (setq lst (vl-remove (assoc 8 lst) lst))
    )
    (or	(= \"1\" (get_tile \"typ\"))
	(setq lst (vl-remove (assoc 6 lst) lst))
    )
    (or	(= \"1\" (get_tile \"wid\"))
      (setq lst (vl-remove (assoc 370 lst) lst))
    )
    (done_dialog)"
  )
  (action_tile "cancel" "(setq lst nil)")
  (start_dialog)
  (unload_dialog dcl_id)
  lst
)

;;;=====================================================================================;;;

;; Fonctions d'appel

(defun c:ssm (/ ss ent lst)
  (and
    (or
      (and
	(setq ss (cadr (ssgetfirst)))
	(= 1 (sslength ss))
	(setq ent (ssname ss 0))
      )
      (and
	(sssetfirst nil nil)
	(setq ent (car (entsel)))
      )
    )
    (setq lst (ssmatch_box ent))
    (sssetfirst nil (ssget "_X" lst))
  )
  (princ)
)

(defun c:ssmm (/ ss ent lst n tmp elt)
  (setq ss (ssadd))
  (while (setq ent (car (entsel "\nSélectionnez l'objet source: ")))
    (setq lst (ssmatch_box ent)
	  n   0
    )
    (princ
      "\nSélectionnez les objes (ou Entrée pour \"Tout\"): "
    )
    (if (not (setq tmp (ssget lst)))
      (setq tmp (ssget "_X" lst))
    )
    (while (setq elt (ssname tmp n))
      (ssadd elt ss)
      (redraw elt 3)
      (setq  n (1+ n))
    )
      (setq tmp nil)
  )
  (sssetfirst nil ss)
  (princ)
)