;; SSFILTER (gile)
;; Créer un filtre de sélection à partir d'objets sélectionnés et de proprietés cochées dans une boite de dialogue

(defun ssfilter_box (/ dcl_id lst)
  (setq dcl_id (load_dialog "ssfilter.dcl"))
  (if (not (new_dialog "ssfilter_box" dcl_id))
    (exit)
  )
  (action_tile
    "accept"
    "(and (= \"1\" (get_tile \"wid\"))
      (setq lst (cons 370 lst))
    )
    (and	(= \"1\" (get_tile \"typ\"))
	(setq lst (cons 6 lst))
    )
    (and (= \"1\" (get_tile \"col\"))
      (setq lst (cons 62 lst))
    )
    (and	(= \"1\" (get_tile \"lay\"))
      (setq lst (cons 8 lst))
    )
    (and (= \"1\" (get_tile \"ent\"))
      (setq lst (cons 0 lst))
    )
    (done_dialog)"
  )
  (action_tile "cancel" "(setq lst nil)")
  (start_dialog)
  (unload_dialog dcl_id)
  lst
)


(defun c:ssf (/ ss ent lst flst n elst)
  (and
    (or
      (setq ss (cadr (ssgetfirst)))
      (setq ss (ssget))
    )
    (repeat (setq n (sslength ss))
      (setq elst (cons (entget (ssname ss (setq n (1- n)))) elst))
    )
    (setq lst (ssfilter_box))
    (setq flst
	   (append
	     (cons
	       '(-4 . "<AND")
	       (apply 'append
		      (mapcar '(lambda (x)
				 (append (cons
					   '(-4 . "<OR")
					   (mapcar '(lambda (y)
						      (cond
							((member x '(0 8 370))
							 (assoc x y)
							)
							((= 6 x)
							 (cond
							   ((assoc x y))
							   (T '(6 . "BYLAYER"))
							 )
							)
							((= 62 x)
							 (cond
							   ((assoc x y))
							   (T '(62 . 256))
							 )
							)
						      )
						    )
						   elst
					   )
					 )
					 (list '(-4 . "OR>"))
				 )
			       )
			      lst
		      )
	       )
	     )
	     (list '(-4 . "AND>"))
	   )
    )
  )
  (sssetfirst nil (ssget "_X" flst))
  (princ)
)