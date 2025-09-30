;;; ARCEDIT (gile) 25/11/2005
;;; Convertit un cercle ou une ellipse en arc ou modifie le départ et la fin
;;; d'un arc d'après les angles spécifiés, l'option "Fermer" permet la conversion d'un
;;; arc de cercle en cercle ou d'un arc elliptique en ellipse fermée.

(defun c:arcedit (/ ucszdir getang ang->param set1 ent lst ang1	ang2 opt
		  echo)

  ;; ucszdir Retourne la direction d'extrusion du SCU courant (vecteur)
  (defun ucszdir ()
    (trans '(0 0 1) 1 0 T)
  )

  ;; Saisie des angles de départ et de fin de l'arc (option "Fermer")
  (defun getang	()
    (if	(or (= (cdr (assoc 0 lst)) "CIRCLE")
	    (and (= (cdr (assoc 0 lst)) "ELLIPSE")
		 (= (cdr (assoc 41 lst)) 0.0)
		 (= (cdr (assoc 42 lst)) (* 2 pi))
	    )
	)
      (progn (setq opt "") (initget 1))
      (progn (setq opt " ou [Fermer] <f>:") (initget "Fermer"))
    )
    (if	(numberp (setq ang1
			(getangle (trans (cdr (assoc 10 lst)) ent 1)
				  (strcat "\nSpécifiez l'angle de départ de l'arc"
					  opt
					  ": "
				  )
			)
		 )
	)
      (progn
	(initget 1)
	(setq ang2
	       (getangle (trans (cdr (assoc 10 lst)) ent 1)
			 "\nSpécifiez l'angle de fin de l'arc: "
	       )
	)
	(foreach ang '(ang1 ang2)
	  (set ang
	       (+ (eval ang)
		  (angle '(0 0) (trans (getvar "UCSXDIR") 0 (ucszdir)))
		  (getvar "ANGBASE")
	       )
	  )
	)
      )
    )
  )

  ;; Convertit l'angle saisi en "paramètre" de l'ellipse (code dxf 41 et 42)
  (defun ang->param (ang)
    (setq
      ang (- ang
	     (angle '(0 0) (trans (cdr (assoc 11 lst)) 0 (ucszdir)))
	  )
    )
    (atan (sin ang) (* (cos ang) (cdr (assoc 40 lst))))
  )

  ;; Fonction principale
  (if (and (= 1 (getvar "PICKFIRST"))
	   (setq set1 (ssget "_i" '((0 . "ARC,CIRCLE,ELLIPSE"))))
	   (eq 1 (sslength set1))
      )
    (progn
      (setq ent	(ssname set1 0)
	    lst	(entget ent)
      )
      (sssetfirst nil nil)
    )
    (progn
      (sssetfirst nil nil)
      (while
	(not
	  (and
	    (setq ent
		   (car	(entsel
			  "\nSélectionnez un arc, un cercle, ou une ellipse: "
			)
		   )
	    )
	    (setq lst (entget ent))
	    (member (cdr (assoc 0 lst)) '("ARC" "CIRCLE" "ELLIPSE"))
	  )
	)
      )
    )
  )
  (if (equal (ucszdir) (cdr (assoc 210 lst)) 1e-9)
    (progn
      (getang)
      (cond
	((= (cdr (assoc 0 lst)) "ARC")
	 (if (numberp ang1)
	   (setq lst (subst (cons 50 ang1)
			    (assoc 50 lst)
			    (subst (cons 51 ang2) (assoc 51 lst) lst)
		     )
	   )
	   (setq
	     lst (cons '(0 . "CIRCLE")
		       (vl-remove-if
			 '(lambda (x)
			    (member (car x) '(-1 0 330 5 100 50 51))
			  )
			 lst
		       )
		 )
	   )
	 )
	)
	((= (cdr (assoc 0 lst)) "CIRCLE")
	 (setq lst
		(cons
		  '(0 . "ARC")
		  (cons
		    (cons 50 ang1)
		    (cons
		      (cons 51 ang2)
		      (vl-remove-if
			'(lambda (x) (member (car x) '(-1 0 330 5 100)))
			lst
		      )
		    )
		  )
		)
	 )
	)
	((= (cdr (assoc 0 lst)) "ELLIPSE")
	 (if (numberp ang1)
	   (foreach ang	'(ang1 ang2)
	     (set ang (ang->param (eval ang)))
	   )
	   (setq ang1 0.0
		 ang2 (* 2 pi)
	   )
	 )
	 (setq lst (subst (cons 41 ang1)
			  (assoc 41 lst)
			  (subst (cons 42 ang2) (assoc 42 lst) lst)
		   )
	 )
	)
      )
      (setq echo (getvar "CMDECHO"))
      (setvar "CMDECHO" 0)
      (command "_undo" "_begin")
      (entmake lst)
      (entdel ent)
      (command "_undo" "_end")
      (setvar "CMDECHO" echo)
    )
    (princ
      "\nErreur: Le SCU courant et le SCO de l'objet ne sont pas parallèles."
    )
  )
  (princ)
)