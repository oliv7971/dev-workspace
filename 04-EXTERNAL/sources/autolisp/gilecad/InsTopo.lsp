;;; INSTOPO (gile)
;;; Insère le bloc "PointBloc" sur les points décrit dans un fichier ascii (.txt .csv ou autre)
;;;
;;; Modification : possibilité d'insérer un point 02/12/2009

(defun c:instopo (/	   *error*  makeblock	      filename tmp	file	 layers	  clay
		  ptlay	   blklay   data-sep dec-sep  mat-p    mat	alt	 scl	  point
		  bloc	   dcl_id   status   space    line     coords	matric	 insert	  matp
		  altp	   bname    status   cnt
		 )

  (vl-load-com)
  (or *acdoc*
      (setq *acdoc* (vla-get-ActiveDocument (vlax-get-acad-object)))
  )
  (or *blocks* (setq *blocks* (vla-get-Blocks *acdoc*)))
  (or *layers* (setq *layers* (vla-get-Layers *acdoc*)))

  ;;---------------------------------------------------;;

  (defun *error* (msg)
    (or	(= msg "Fonction annulée")
	(princ (strcat "Erreur: " msg))
    )
    (and file (close file))
    (vla-EndUndoMark *acdoc*)
    (princ)
  )

  ;;---------------------------------------------------;;

  ;; MakeBlock
  ;; Crée le bloc TCPOINT
  (defun makeblock (/ block pt att)
    (vl-load-com)
    (vla-Add *layers* "TopoMat")
    (vla-Add *layers* "TopoAlt")
    (setq block	(vla-add *blocks*
			 (vlax-3d-point '(0. 0. 0.))
			 "TCPOINT"
		)
    )
    (setq pt (vla-addPoint block (vlax-3d-point '(0. 0. 0.))))
    (vla-put-Layer pt "0")
    (vla-put-Color pt acByblock)
    (setq att
	   (vla-addAttribute
	     block
	     0.3
	     acAttributeModePreset
	     ""
	     (vlax-3d-point '(0.1 0.1 0.))
	     "MAT"
	     ""
	   )
    )
    (vla-put-Layer att "TopoMat")
    (setq att
	   (vla-addAttribute
	     block
	     0.3
	     acAttributeModePreset
	     ""
	     (vlax-3d-point '(1. -3. 0.))
	     "ALT"
	     ""
	   )
    )
    (vla-put-Alignment att acAlignmentTopLeft)
    (vla-put-TextAlignmentPoint
      att
      (vlax-3d-point '(0.1 -0.1 0.0))
    )
    (vla-put-Layer att "TopoAlt")
  )

  ;;---------------------------------------------------;;

  (if (setq filename (getfiled "Sélectionner un fichier point"
			       ""
			       "txt;csv;*"
			       0
		     )
      )
    (progn
      ;; Création du fichier DCL temporaire
      (setq tmp	 (vl-filename-mktemp "Tmp.dcl")
	    file (open tmp "w")
      )
      (write-line
	"InsTopo
	:dialog{label=\"InsTopo\";
	:boxed_row{label=\"Format du fichier\";
	:column{
	:button{label=\"Ouvrir le ficher\";key=\"open\";fixed_width=true;}
	:boxed_radio_column{label=\"Séparateur de données\";key=\"data-sep\";
	:radio_button{label=\"Virgule\";key=\"44\";value =\"1\";}
	:radio_button{label=\"Point-virgule\";key =\"59\";}
	:radio_button{label=\"Espace\";key=\"32\";}
	:radio_button{label=\"Tabulation\";key =\"9\";}}
	}
	:column{
	:boxed_radio_column{label=\"Séparateur décimal\";key=\"dec-sep\";
	:radio_button{label=\"Virgule\";key =\"com\";}
	:radio_button{label=\"Point\";key=\"dot\";value=\"1\";}}
	:boxed_radio_column{label=\"Matricule\";key=\"mat-p\";
	:radio_button{label=\"Présent\";key=\"present\";value=\"1\";}
	:radio_button{label=\"Absent\";key=\"absent\";}}}}
	
	:boxed_column{label=\"Points\";
	:toggle{label=\"Insérer des points\";key=\"point\";value=\"1\";}
	:row{
	:spacer{width=18;}
	spacer;
	:popup_list{label=\"Calque\";key =\"ptlay\";edit_width = 24;alignment=right;}}
	spacer;}
	
	:boxed_column{label=\"Blocs\";
	:row{
	:toggle{label=\"Insérer des blocs :\";key=\"bloc\";value=\"1\";width=16;}
	:text{value=\"TCPOINT\";key=\"bname\";width=36;}
	}
	:row{
	:boxed_column{label=\"Choix du bloc\";key=\"choice\";
	:toggle{label=\"TCPOINT\";key=\"tcpt\";value=\"1\";}
	:button{label=\"Autre...\";key=\"other\";fixed_width=true;width=14;}}
	spacer;
	:boxed_column{label=\"Attributs\";key=\"atts\";
	:toggle{label=\"Matricule\";key=\"mat\";value=\"1\";}
	:toggle{label=\"Altitude\";key=\"alt\";value=\"1\";}}}
	spacer;
	:row{
	:edit_box{label=\"Echelle  \";key=\"scl\";value=\"1.0\";fixed_width=true;}
	:spacer{width=4;}
	:popup_list{label=\"Calque\";key =\"blklay\";edit_width = 24;}}
	spacer;}
	spacer;ok_cancel_help;}"
	file
      )
      (close file)

      (vlax-for	l (vla-get-Layers *acdoc*)
	(setq layers (cons (vla-get-Name l) layers))
      )
      (setq layers   (vl-sort layers '<)
	    clay     (getvar "CLAYER")
	    ptlay    clay
	    blklay   clay
	    data-sep "44"
	    dec-sep  "dot"
	    mat-p    "present"
	    mat	     "0"
	    alt	     "0"
	    scl	     1.0
	    point    T
	    bloc     nil
	    bname    ""
	    altp     nil
	    matp     nil
	    dcl_id   (load_dialog tmp)
	    status   2
      )
      (while (< 1 status)
	(if (not (new_dialog "InsTopo" dcl_id))
	  (exit)
	)
	(start_list "ptlay")
	(mapcar 'add_list layers)
	(end_list)
	(start_list "blklay")
	(mapcar 'add_list layers)
	(end_list)
	(set_tile "ptlay" (itoa (vl-position ptlay layers)))
	(set_tile "blklay" (itoa (vl-position blklay layers)))
	(foreach k (list "data-sep" "dec-sep" "mat-p" "mat" "alt")
	  (set_tile k (eval (read k)))
	)
	(set_tile "point"
		  (if point
		    "1"
		    "0"
		  )
	)
	(set_tile "bloc"
		  (if bloc
		    "1"
		    "0"
		  )
	)
	(set_tile "bname" bname)
	(set_tile "scl" (rtos scl))
	(if point
	  (mode_tile "ptlay" 0)
	  (mode_tile "ptlay" 1)
	)
	(if bloc
	  (progn
	    (mode_tile "blklay" 0)
	    (mode_tile "scl" 0)
	    (mode_tile "choice" 0)
	    (mode_tile "atts" 0)
	  )
	  (progn
	    (mode_tile "blklay" 1)
	    (mode_tile "scl" 1)
	    (mode_tile "choice" 1)
	    (mode_tile "atts" 1)
	  )
	)
	(if (= bname "TCPOINT")
	  (progn
	    (set_tile "tcpt" "1")
	  )
	  (progn
	    (set_tile "tcpt" "0")
	  )
	)
	(if altp
	  (mode_tile "alt" 0)
	  (mode_tile "alt" 1)
	)
	(if matp
	  (mode_tile "mat" 0)
	  (mode_tile "mat" 1)
	)
	(action_tile "open" "(startapp \"notepad\" filename)")
	(foreach k (list "data-sep" "dec-sep" "mat-p")
	  (action_tile k "(set (read $key) $value)")
	)
	(action_tile
	  "mat-p"
	  "(if (= \"absent\" $value)
	    (progn
	      (mode_tile \"mat\" 1)
	      (set_tile \"mat\" \"0\")
	    )
	    (mode_tile \"mat\" 0)
	  )"
	)
	(action_tile
	  "point"
	  "(if (= \"1\" $value)
            (progn
              (setq point T)
              (mode_tile \"ptlay\" 0)
            )
            (progn
              (setq point nil)
              (mode_tile \"ptlay\" 1)
            )
          )"
	)
	(action_tile
	  "bloc"
	  "(if (= \"1\" $value)
          (progn
            (setq bloc T)
            (mode_tile \"blklay\" 0)
            (mode_tile \"scl\" 0)
            (mode_tile \"choice\" 0)
            (mode_tile \"atts\" 0)
          )
          (progn
            (setq bloc nil)
            (mode_tile \"blklay\" 1)
            (mode_tile \"scl\" 1)
            (mode_tile \"choice\" 1)
            (mode_tile \"atts\" 1)
          )
        )"
	)
	(action_tile
	  "tcpt"
	  "(if (= \"1\" $value)
	    (progn (setq bname \"TCPOINT\") (mode_tile \"atts\" 0))
	    (setq bname \"\")
          )
          (set_tile \"bname\" bname)"
	)
	(action_tile "alt" "(setq alt $value altp (= \"1\" $value))")
	(action_tile "mat" "(setq mat $value matp (= \"1\" $value))")
	(action_tile "other" "(done_dialog 3)")
	(action_tile
	  "ptlay"
	  "(setq ptlay (nth (atoi $value) layers))"
	)
	(action_tile
	  "blklay"
	  "(setq blklay (nth (atoi $value) layers))"
	)
	(action_tile
	  "scl"
	  "(setq scl (distof $value))
	(while (or (not scl) (<= scl 0))
	(alert \"Nécessite un nombre réel strictement positif\")
	(setq scl 1.0)
	(set_tile \"scl\" \"1.0\")
	(mode_tile \"scl\" 2))"
	)
	(action_tile "cancel" "(setq data-sep nil) (done_dialog 0)")
	(action_tile
	  "accept"
	  "(if (and bloc (= bname \"\"))
	    (alert \"Aucun bloc spécifié\")
	    (done_dialog 1)
	  )"
	)
	(setq status (start_dialog))
	(cond
	  ((= status 3)
	   (setq altp nil
		 matp nil
		 alt  "0"
		 mat  "0"
	   )
	   (if (setq bname (gc:Getblock nil))
	     (progn
	       (if (vl-filename-extension bname)
		 (progn
		   (vla-Delete
		     (vla-InsertBlock
		       (vla-get-ModelSpace *acdoc*)
		       (vlax-3d-point '(0. 0. 0.))
		       bname
		       1.
		       1.
		       1.
		       0.
		     )
		   )
		   (setq bname (vl-filename-base bname))
		 )
	       )
	       (vlax-for o (vla-Item *Blocks* bname)
		 (if
		   (= (vla-get-ObjectName o) "AcDbAttributeDefinition")
		    (cond
		      ((= (strcase (vla-get-TagString o)) "ALT")
		       (setq altp T)
		      )
		      ((= (strcase (vla-get-TagString o)) "MAT")
		       (setq matp T)
		      )
		    )
		 )
	       )
	     )
	     (setq bname ""
		   bloc	nil
	     )
	   )
	  )
	)
      )
      (unload_dialog dcl_id)
      (vl-file-delete tmp)
      (if (= 1 status)
	(progn
	  (vla-StartUndoMark *acdoc*)
	  (and (= bname "TCPOINT")
	       (vl-catch-all-error-p
		 (vl-catch-all-apply
		   'vla-item
		   (list *blocks* "TCPOINT")
		 )
	       )
	       (makeblock)
	  )
	  (setq	space (vla-get-ModelSpace *acdoc*)
		file  (open filename "r")
		cnt   0
	  )
	  (while (setq line (read-line file))
	    (setq coords (gc:str2lst line (chr (atoi data-sep))))
	    (if	(= mat-p "present")
	      (setq matric (car coords)
		    coords (cdr coords)
	      )
	      (setq matric nil)
	    )
	    (if	(= dec-sep "com")
	      (setq
		coords (mapcar
			 '(lambda (x)
			    (read (vl-string-translate "," "." x))
			  )
			 coords
		       )
	      )
	      (setq coords (mapcar 'read coords))
	    )
	    (setq coords (list (car coords)
			       (cadr coords)
			       (cond ((caddr coords))
				     (T 0.0)
			       )
			 )
	    )
	    (if	(vl-every 'numberp coords)
	      (progn
		(setq cnt (1+ cnt))
		(if point
		  (vla-put-Layer
		    (vla-AddPoint space (vlax-3d-point coords))
		    ptlay
		  )
		)
		(if (and bloc (/= bname ""))
		  (progn
		    (setq
		      insert
		       (vla-InsertBlock
			 space
			 (vlax-3d-point coords)
			 bname
			 scl
			 scl
			 scl
			 0.0
		       )
		    )
		    (vla-put-Layer insert blklay)
		    (if	(or altp matp)
		      (foreach att (vlax-invoke insert 'getAttributes)
			(if
			  (and
			    (= (vla-get-TagString att) "MAT")
			    matp
			    matric
			    (= mat "1")
			  )
			   (vla-put-TextString att matric)
			)
			(if
			  (and
			    (= (vla-get-TagString att) "ALT")
			    altp
			    (= alt "1")
			  )
			   (vla-put-TextString att (rtos (caddr coords)))
			)
		      )
		    )
		  )
		)
	      )
	    )
	  )
	  (close file)
	  (vla-EndUndoMark *acdoc*)
	  (princ (strcat
		   "\n"
		   (itoa cnt)
		   (cond
		     ((and point bloc)
		      (if (< 2 cnt)
			" points et blocs insérés"
			" point et bloc inséré"
		      )
		     )
		     (point
		      (if (< 2 cnt)
			" points insérés"
			" point inséré"
		      )
		     )
		     (bloc
		      (if (< 2 cnt)
			" blocs insérés"
			" bloc inséré"
		      )
		     )
		   )
		 )
	  )
	)
      )
    )
  )
  (princ)
)

;; gc:str2lst
;; Transforme un chaine avec séparateur en liste de chaines
;;
;; Arguments
;; str : la chaine à transformer en liste
;; sep : le séparateur
;;
;; Exemples
;; (gc:str2lst "a b c" " ") -> ("a" "b" "c")
;; (gc:str2lst "1,2,3" ",") -> ("1" "2" "3")
;; (mapcar 'read (gc:str2lst "1,2,3" ",")) -> (1 2 3)

(defun gc:str2lst (str sep / pos)
  (if (setq pos (vl-string-search sep str))
    (cons (substr str 1 pos)
	  (gc:str2lst (substr str (+ (strlen sep) pos 1)) sep)
    )
    (list str)
  )
)

(princ "\nEntrez INSTOPO pour ouvrir la boite de dialogue")
(princ)

;;; gc:Getblock (gile) 03/11/07
;;; Retourne le nom du bloc entré ou choisi par l'utilisateur 
;;; dans une liste déroulante de la boite de dialogue ou depuis la boite
;;; de dialogue standard d'AutoCAD
;;; Argument : le titre (string) ou nil (défaut : "Choisir un bloc")

(defun gc:Getblock (titre / bloc n lst tmp file what_next dcl_id nom)
  (while (setq bloc (tblnext "BLOCK" (not bloc)))
    (setq lst (cons (cdr (assoc 2 bloc)) lst)
    )
  )
  (setq	lst  (acad_strlsort
	       (vl-remove-if
		 (function (lambda (n) (= (substr n 1 1) "*")))
		 lst
	       )
	     )
	tmp  (vl-filename-mktemp "Tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    (strcat
      "getblock:dialog{label="
      (cond (titre (vl-prin1-to-string titre))
	    ("\"Choisir un bloc\"")
      )
      ";initial_focus=\"bl\";:boxed_column{
      :row{:text{label=\"Sélectionner\";alignment=left;}
      :button{label=\">>\";key=\"sel\";alignment=right;fixed_width=true;}}
      spacer;
      :column{:button{label=\"Parcourir...\";key=\"wbl\";alignment=right;fixed_width=true;}}
      :column{:text{label=\"Nom :\";alignment=left;}}
      :edit_box{key=\"tp\";edit_width=25;}
      :popup_list{key=\"bl\";edit_width=25;}spacer;}
      spacer;
      ok_cancel;}"
    )
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (setq what_next 2)
  (while (>= what_next 2)
    (if	(not (new_dialog "getblock" dcl_id))
      (exit)
    )
    (start_list "bl")
    (mapcar 'add_list lst)
    (end_list)
    (if	(setq n	(vl-position
		  (strcase (getvar "INSNAME"))
		  (mapcar 'strcase lst)
		)
	)
      (setq nom (nth n lst))
      (setq nom	(car lst)
	    n	0
      )
    )
    (set_tile "bl" (itoa n))
    (action_tile "sel" "(done_dialog 5)")
    (action_tile "bl" "(setq nom (nth (atoi $value) lst))")
    (action_tile "wbl" "(done_dialog 3)")
    (action_tile "tp" "(setq nom $value) (done_dialog 4)")
    (action_tile
      "accept"
      "(setq nom (nth (atoi (get_tile \"bl\")) lst)) (done_dialog 1)"
    )
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3)
       (if (setq nom (getfiled "Sélectionner un fichier" "" "dwg" 0))
	 (setq what_next 1)
	 (setq what_next 2)
       )
      )
      ((= what_next 4)
       (cond
	 ((not (read nom))
	  (setq what_next 2)
	 )
	 ((tblsearch "BLOCK" nom)
	  (setq what_next 1)
	 )
	 ((findfile (setq nom (strcat nom ".dwg")))
	  (setq what_next 1)
	 )
	 (T
	  (alert (strcat "Le fichier \"" nom "\" est introuvable."))
	  (setq	nom nil
		what_next 2
	  )
	 )
       )
      )
      ((= what_next 5)
       (if (and	(setq ent (car (entsel)))
		(= "INSERT" (cdr (assoc 0 (entget ent))))
	   )
	 (setq nom	 (cdr (assoc 2 (entget ent)))
	       what_next 1
	 )
	 (setq what_next 2)
       )
      )
      ((= what_next 0)
       (setq nom nil)
      )
    )
  )
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  nom
)