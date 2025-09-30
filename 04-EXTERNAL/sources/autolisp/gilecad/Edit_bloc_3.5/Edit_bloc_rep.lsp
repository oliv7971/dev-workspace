;;; EDIT_BLOC_REP -Gilles Chanteau- 11/06/06

;;; Pour lancer Edit_bloc sur tout un répertoire de wblocs
;;; À utiliser dans un dessin vierge (brouillon)
;;; Choisir l'option "Toute la collection"

(defun c:edit_bloc_rep (/ App AcDoc ModSp n lst file dir f_lst ss)
  (vl-load-com)
  (setq	App   (vlax-get-acad-object)
	AcDoc (vla-get-ActiveDocument App)
	ModSp (vla-get-ModelSpace acDoc)
  )

  ;; Teste la présence d'entités graphiques dans le dessin
  (if (< 0 (vla-get-Count ModSp))
    (progn
      (alert
	"Le dessin contient des entités.
      \nCe programme doit être lancé à partir d'un dessin vierge."
      )
      (exit)
    )
  )

  ;; Teste la présence de définitions de blocs dans le dessin
  (repeat (setq n (vla-get-Count (vla-get-Blocks AcDoc)))
    (setq
      lst (cons	(vla-get-Name
		  (vla-item (vla-get-Blocks AcDoc) (setq n (1- n)))
		)
		lst
	  )
    )
  )
  (if (vl-remove-if '(lambda (x) (wcmatch x "*Space*")) lst)
    (progn
      (alert
	"Le dessin contient des définitions de blocs.
    \nCe programme doit être lancé à partir d'un dessin vierge."
      )
      (exit)
    )
  )

  (setq
    file (getfiled "Choisir un fichier dans le répertoire à modifier"
		   ""
		   "dwg"
		   0
	 )
  )
  (if file
    (progn
      (setq dir	  (vl-filename-directory file)
	    f_lst (vl-directory-files dir "*.dwg")
      )
      (foreach f f_lst
	(setq bl
	       (vl-catch-all-apply
		 'vla-InsertBlock
		 (list
		   ModSp
		   (vlax-3d-point '(0. 0. 0.))
		   (strcat dir "\\" f)
		   1.
		   1.
		   1.
		   0.
		 )
	       )
	)
	(if (vl-catch-all-error-p bl)
	  (progn
	    (princ (strcat "\nErreur de chargement du bloc : " f "\n"))
	    (vl-remove f f_lst)
	  )
	  (vla-Erase bl)
	)
      )
      (c:edit_bloc)
      (mapcar
	'(lambda (x)
	   (setq bl (vla-InsertBlock
		      ModSp
		      (vlax-3d-point '(0 0 0))
		      (vl-filename-base x)
		      1
		      1
		      1
		      0
		    )
	   )
	   (vla-ZoomExtents App)
	   (vla-ZoomScaled App 0.9 1)
	   (setq ss (vla-add (vla-get-SelectionSets AcDoc) "wbloc_ss"))
	   (vla-addItems ss (vla-explode bl))
	   (vla-wblock AcDoc (strcat dir "\\" x) ss)
	   (vla-erase ss)
	   (vla-delete ss)
	   (vla-delete (vlax-ename->vla-object (entlast)))
	 )
	f_lst
      )
    )
  )
  (princ)
)
