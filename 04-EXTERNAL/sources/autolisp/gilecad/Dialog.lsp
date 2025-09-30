;; GETLAYERS (gile) 02/12/07
;; Retourne la liste des calques cochés dans la boite de dialogue
;;
;; arguments
;; titre : le titre de la boite de dialogue ou nil (defaut = Choisir les calques)
;; lst1 : la liste des calques à pré-cochés ou nil
;; lst2 : la liste des calques non cochables (grisés) ou nil

(defun getlayers (titre	   lst1	    lst2     /	      sublist
		  toggle_column	    tmp	     file     lay      layers
		  len	   dcl_id   lst
		 )

  (defun sublist (lst start leng / n r)
    (if	(or (not leng) (< (- (length lst) start) leng))
      (setq leng (- (length lst) start))
    )
    (setq n (+ start leng))
    (repeat leng
      (setq r (cons (nth (setq n (1- n)) lst) r))
    )
  )

  (defun toggle_column (lst)
    (apply 'strcat
	   (mapcar
	     (function
	       (lambda (x)
		 (strcat ":toggle{key="
			 (vl-prin1-to-string x)
			 ";label="
			 (vl-prin1-to-string x)
			 ";}"
		 )
	       )
	     )
	     lst
	   )
    )
  )

  (setq	tmp  (vl-filename-mktemp "tmp.dcl")
	file (open tmp "w")
  )
  (while (setq lay (tblnext "LAYER" (not lay)))
    (setq layers (cons (cdr (assoc 2 lay)) layers))
  )
  (setq	layers (vl-sort layers '<)
	len    (length layers)
  )
  (write-line
    (strcat
      "GetLayers:dialog{label="
      (cond (titre (vl-prin1-to-string titre))
	    ("\"Choisir les calques\"")
      )
      ";:boxed_row{:column{"
      (cond
	((< len 12) (toggle_column layers))
	((< len 24)
	 (strcat (toggle_column (sublist layers 0 (/ len 2)))
		 "}:column{"
		 (toggle_column (sublist layers (/ len 2) nil))
	 )
	)
	((< len 45)
	 (strcat (toggle_column (sublist layers 0 (/ len 3)))
		 "}:column{"
		 (toggle_column (sublist layers (/ len 3) (/ len 3)))
		 "}:column{"
		 (toggle_column (sublist layers (* (/ len 3) 2) nil))
	 )
	)
	(T
	 (strcat (toggle_column (sublist layers 0 (/ len 4)))
		 "}:column{"
		 (toggle_column (sublist layers (/ len 4) (/ len 4)))
		 "}:column{"
		 (toggle_column (sublist layers (/ len 2) (/ len 4)))
		 "}:column{"
		 (toggle_column (sublist layers (* (/ len 4) 3) nil))
	 )
	)
      )
      "}}spacer;ok_cancel;}"
    )
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (if (not (new_dialog "GetLayers" dcl_id))
    (exit)
  )
  (foreach n lst1
    (set_tile n "1")
  )
  (foreach n lst2
    (mode_tile n 1)
  )
  (action_tile
    "accept"
    "(setq lst nil)
    (foreach n layers
    (if (= (get_tile n) \"1\")
    (setq lst (cons n lst))))
    (done_dialog)"
  )
  (start_dialog)
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  lst
)

;;============================================================================;;

;;; Getblock (gile) 03/11/07
;;; Retourne le nom du bloc entré ou choisi par l'utilisateur 
;;; dans une liste déroulante de la boite de dialogue ou depuis la boite
;;; de dialogue standard d'AutoCAD
;;; Argument : le titre (string) ou nil (défaut : "Choisir un bloc")

(defun getblock	(titre / bloc n lst tmp file what_next dcl_id nom)
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

;;============================================================================;;

;;; GetLayer (gile) 03/11/07
;;; Retourne le nom du calque entré ou choisi par l'utilisateur 
;;; dans une liste déroulante de la boite de dialogue ou en sélectionnant
;;; un objet à l'écran.
;;; Argument : le titre (string) ou nil (défaut : "Choisir un calque")

(defun getlayer	(titre / lay lst tmp file what_next dcl_id nom)
  (while (setq lay (tblnext "LAYER" (not lay)))
    (setq lst (cons (cdr (assoc 2 lay)) lst))
  )
  (setq	lst  (acad_strlsort lst)
	tmp  (vl-filename-mktemp "Tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    (strcat
      "getlayer:dialog{label="
      (cond (titre (vl-prin1-to-string titre))
	    ("\"Choisir un calque\"")
      )
      ";initial_focus=\"tp\";
      :boxed_column{:row{
      :column{:text{label=\"Sélectionner un objet\";alignment=left;}}
      :column{:button{label=\">>\";key=\"obj\";alignment=right;fixed_width=true;}
      spacer;}}
      :edit_box{key=\"tp\";edit_width=25;allow_accept=true;}
      :popup_list{key=\"lay\";edit_width=25;}
      spacer;}ok_cancel;}"
    )
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (setq what_next 2)
  (while (>= what_next 2)
    (if	(not (new_dialog "getlayer" dcl_id))
      (exit)
    )
    (start_list "lay")
    (mapcar 'add_list lst)
    (end_list)
    (or	nom
	(setq nom (vlax-ldata-get "getLayer" "n"))
	(setq nom (vlax-ldata-put "getLayer" "n" "0"))
    )
    (if	(member nom lst)
      (set_tile	"lay"
		(itoa (- (length lst) (length (member nom lst))))
      )
      (set_tile "lay" "0")
    )
    (set_tile "tp" nom)
    (action_tile "obj" "(done_dialog 3)")
    (action_tile "tp" "(setq nom $value)")
    (action_tile
      "lay"
      (strcat
	"(if (or (= $reason 1) (= $reason 4))"
	"(progn"
	"(setq nom (nth (atoi $value) lst))"
	"(set_tile \"tp\" (nth (atoi $value) lst))"
	"(mode_tile \"tp\" 2)))"
       )
    )
    (action_tile
      "accept"
      (strcat
	"(if (tblsearch \"LAYER\" nom)"
	"(progn (done_dialog 1)"
	"(vlax-ldata-put \"getLayer\" \"n\" nom))"
	"(progn"
	"(alert (strcat \"Le calque \" nom \" est introuvable.\"))"
	"(setq nom nil) (set_tile \"tp\" (vlax-ldata-get \"getLayer\" \"n\"))"
	"(mode_tile \"tp\" 2)))"
       )
    )
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3)
       (if (setq nom (car (entsel)))
	 (setq nom (cdr (assoc 8 (entget nom))))
	 (setq nom nil)
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

;;============================================================================;;

;; GETLAYOUTS (gile) 03/12/07
;; Retourne la liste des présentations choisies dans la boite de dialogue
;;
;; arguments
;; titre : titre de la boite de dialogue ou nil, défauts = Choisir la (ou les) présentation(s)
;; mult : T ou nil (pour choix multiple ou unique)

(defun GetLayouts (titre mult / str2lst lay tmp file ret)

  (defun str2lst (str sep / pos)
    (if	(setq pos (vl-string-search sep str))
      (cons (substr str 1 pos)
	    (str2lst (substr str (+ (strlen sep) pos 1)) sep)
      )
      (list str)
    )
  )

  (defun TabOrder (name / dict lay)
    (setq dict (dictsearch (namedobjdict) "ACAD_LAYOUT"))
    (if	(setq lay (cdr (assoc 350 (member (cons 3 name) dict))))
      (cdr (assoc 71 (entget lay)))
    )
  )

  (setq	lay  (vl-sort (layoutlist)
		      (function
			(lambda	(x1 x2)
			  (< (TabOrder x1)
			     (TabOrder x2)
			  )
			)
		      )
	     )
	tmp  (vl-filename-mktemp "tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    (strcat
      "GetLayouts:dialog{label="
      (if titre
	(vl-prin1-to-string titre)
	(if mult
	  "\"Choisir les présentations\""
	  "\"Choisir une présentation\""
	)
      )
      ";:list_box{key=\"lst\";multiple_select="
      (if mult
	"true;}:row{:retirement_button{label=\"Toutes\";key=\"all\";}
ok_button;cancel_button;}}"
	"false;}ok_cancel;}"
      )
    )
    file
  )
  (close file)
  (setq dcl_id (load_dialog tmp))
  (if (not (new_dialog "GetLayouts" dcl_id))
    (exit)
  )
  (start_list "lst")
  (mapcar 'add_list lay)
  (end_list)
  (action_tile "all" "(setq ret (reverse lay)) (done_dialog)")
  (action_tile
    "accept"
    "(or (= (get_tile \"lst\") \"\")
(foreach n (str2lst (get_tile \"lst\") \" \")
(setq ret (cons (nth (atoi n) lay) ret))))
(done_dialog)"
  )
  (start_dialog)
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  (reverse ret)
)

;;============================================================================;;

;; InputBox (gile)
;; Ouvre une boite de dialogue pour récupérer une valeur
;; sous forme de chaine de caractère
;;
;; Arguments
;; tous les arguments sont de chaines de caractère (ou "")
;; box : titre de la boite de dialogue
;; msg : message d'invite
;; val : valeur par défaut
;;
;; Retour
;; une chaine ("" si annulation)

(defun InputBox	(box msg val / subr temp file dcl_id ret)

  ;; Retour chariot automatique à 50 caractères
  (defun subr (str / pos)
    (if	(and
	  (< 36 (strlen str))
	  (setq pos (vl-string-position 32 (substr str 1 36) nil T))
	)
      (strcat ":text_part{label=\""
	      (substr str 1 pos)
	      "\";}"
	      (subr (substr str (+ 2 pos)))
      )
      (strcat ":text_part{label=\"" str "\";}")
    )
  )

  ;; Créer un fichier DCL temporaire
  (setq	temp (vl-filename-mktemp "Tmp.dcl")
	file (open temp "w")
	ret  ""
  )

  ;; Ecrire le fichier
  (write-line
    (strcat
      "InputBox:dialog{key=\"box\";initial_focus=\"val\";spacer;:paragraph{"
      (subr msg)
      "}spacer;:edit_box{key=\"val\";edit_width=36;allow_accept=true;}spacer;ok_cancel;}"
    )
    file
  )
  (close file)

  ;; Ouvrir la boite de dialogue
  (setq dcl_id (load_dialog temp))
  (if (not (new_dialog "InputBox" dcl_id))
    (exit)
  )
  (set_tile "box" box)
  (set_tile "val" val)
  (action_tile
    "accept"
    "(setq ret (get_tile \"val\")) (done_dialog)"
  )
  (start_dialog)
  (unload_dialog dcl_id)

  ;;Supprimer le fichier
  (vl-file-delete temp)
  ret
)

;;============================================================================;;

;; DoubleInputBox (gile)
;; Ouvre une boite de dialogue pour récupérer deux valeurs
;; sous forme de chaine de caractère
;;
;; Arguments
;; tous les arguments sont de chaines de caractère (ou "")
;; box : titre de la boite de dialogue
;; msg1 : message pour la première entrée
;; msg1 : message pour la seconde entrée
;; val1 : valeur par défaut de la première entrée
;; val1 : valeur par défaut de la seconde entrée
;;
;; Retour
;; une liste (valeur1 valeur2) ou nil

(defun DoubleInputBox (box msg1 msg2 val1 val2 / temp file dcl_id lst)

  (defun subr (str / pos)
    (if	(and
	  (< 36 (strlen str))
	  (setq pos (vl-string-position 32 (substr str 1 36) nil T))
	)
      (strcat ":text_part{label=\""
	      (substr str 1 pos)
	      "\";}"
	      (subr (substr str (+ 2 pos)))
      )
      (strcat ":text_part{label=\"" str "\";}")
    )
  )

  (setq	temp (vl-filename-mktemp "Tmp.dcl")
	file (open temp "w")
  )
  (write-line
    (strcat
      "DoubleInputBox:dialog{key=\"box\";initial_focus=\"val1\";:paragraph{"
      (subr msg1)
      "}:edit_box{key=\"val1\";edit_width=36;allow_accept=true;}spacer;:paragraph {"
      (subr msg2)
      "}:edit_box{key=\"val2\";edit_width=36;allow_accept=true;}spacer;ok_cancel; }"
    )
    file
  )
  (close file)
  (setq dcl_id (load_dialog temp))
  (if (not (new_dialog "DoubleInputBox" dcl_id))
    (exit)
  )
  (foreach n '("box" "val1" "val2")
    (set_tile n (eval (read n)))
  )
  (action_tile
    "accept"
    "(setq lst (list (get_tile \"val1\") (get_tile \"val2\")))
(done_dialog)"
  )
  (start_dialog)
  (unload_dialog dcl_id)
  (vl-file-delete temp)
  lst
)

;;============================================================================;;

;; OptionBox (gile)
;; Boite de dialogue permettant de choisir une ou plusieurs options
;;
;; Arguments
;; title : le titre de la boite de dialogue (chaîne)
;; msg ; message (chaîne), "" ou nil por aucun
;; keylab : une liste d'association du type ((key1 . label1) (key2 . label2) ...)
;; mult : T (choix multiple) ou nil (choix unique)
;;
;; Retour : la clé de l'option (mult = nil) ou la liste des clés des options (mult = T)
;;
;; Exemples d'utilisations
;; (OptionBox "Type de fichier"  nil '(("lin" . "Type de ligne") ("pat" . "Motif de hachure")) nil)
;; (OptionBox "Types d'entités" "Choisir les types d'entité" '(("LINE" . "Lignes") ("CIRCLE" . "Cercles")) T)

(defun OptionBox (title msg keylab mult / tmp file dcl_id choice)
  (setq	tmp  (vl-filename-mktemp "tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    (strcat "OptionBox:dialog{label=\"" title "\";")
    file
  )
  (write-line
    (strcat (if	mult
	      ":boxed_column{"
	      ":boxed_radio_column{key=\"choice\";"
	    )
    )
    file
  )
  (if (and msg (/= msg ""))
    (write-line (strcat "label=\"" msg "\";") file)
  )
  (mapcar
    (function
      (lambda (p)
	(write-line
	  (strcat (if mult
		    ":toggle{key=\""
		    ":radio_button{key=\""
		  )
		  (car p)
		  "\";label=\""
		  (cdr p)
		  "\";}"
	  )
	  file
	)
      )
    )
    keylab
  )
  (if mult
    (write-line
      "spacer;:button{label=\"Tout sélectionner\";
      key=\"all\";fixed_width=true;alignment=centered;}"
      file
    )
  )
  (write-line "}spacer;ok_cancel;}" file)
  (close file)
  (setq dcl_id (load_dialog tmp))
  (if (not (new_dialog "OptionBox" dcl_id))
    (exit)
  )
  (if mult
    (progn
      (action_tile
	"all"
	"(foreach k (mapcar 'car keylab)
        (set_tile k\"1\"))"
      )
      (action_tile
	"none"
	"(foreach k (mapcar 'car keylab)
        (set_tile k\"0\"))"
      )
      (action_tile
	"accept"
	"(foreach k (mapcar 'car keylab)
        (if (= \"1\" (get_tile k))
        (setq choice (cons k choice))))
        (setq choice (reverse choice))
        (done_dialog)"
      )
    )
    (progn
      (set_tile "choice" (caar keylab))
      (action_tile
	"accept"
	"(setq choice (get_tile \"choice\")) (done_dialog)"
      )
    )
  )
  (start_dialog)
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  choice
)

;;============================================================================;;

;; ListBox (gile)
;; Boite de dialogue permettant un ou plusieurs choix dans une liste
;;
;; Arguments
;; title : le titre de la boite de dialogue (chaîne)
;; msg ; message (chaîne), "" ou nil pour aucun
;; keylab : une liste d'association du type ((key1 . label1) (key2 . label2) ...)
;; flag : 0 = liste déroulante
;;        1 = liste choix unique
;;        2 = liste choix multipes
;;
;; Retour : la clé de l'option (flag = 0 ou 1) ou la liste des clés des options (flag = 2)
;;
;; Exemple d'utilisation
;; (listbox "Présentation" "Choisir une présentation" (mapcar 'cons (layoutlist) (layoutlist)) 1)

(defun ListBox (title msg keylab flag / str2lst tmp file dcl_id choice)

  (defun str2lst (str sep / pos)
    (if	(setq pos (vl-string-search sep str))
      (cons (substr str 1 pos)
	    (str2lst (substr str (+ (strlen sep) pos 1)) sep)
      )
      (list str)
    )
  )
  (setq	tmp  (vl-filename-mktemp "tmp.dcl")
	file (open tmp "w")
  )
  (write-line
    (strcat "ListBox:dialog{label=\"" title "\";")
    file
  )
  (if (and msg (/= msg ""))
    (write-line (strcat ":text{label=\"" msg "\";}") file)
  )
  (write-line
    (cond
      ((= 0 flag) "spacer;:popup_list{key=\"lst\";")
      ((= 1 flag) "spacer;:list_box{key=\"lst\";")
      (T "spacer;:list_box{key=\"lst\";multiple_select=true;")
    )
    file
  )
  (write-line "}spacer;ok_cancel;}" file)
  (close file)
  (setq dcl_id (load_dialog tmp))
  (if (not (new_dialog "ListBox" dcl_id))
    (exit)
  )
  (start_list "lst")
  (mapcar 'add_list (mapcar 'cdr keylab))
  (end_list)
  (action_tile
    "accept"
    "(or (= (get_tile \"lst\") \"\")
    (if (= 2 flag) (progn
    (foreach n (str2lst (get_tile \"lst\") \" \")
    (setq choice (cons (nth (atoi n) (mapcar 'car keylab)) choice)))
    (setq choice (reverse choice)))
    (setq choice (nth (atoi (get_tile \"lst\")) (mapcar 'car keylab)))))
    (done_dialog)"
  )
  (start_dialog)
  (unload_dialog dcl_id)
  (vl-file-delete tmp)
  choice
)

;;============================================================================;;

;; MsgBox
;; Boite de dialogue pour afficher un message et, éventuellement poser une question.
;; Renvoie : 1, si fermée par 'OK' ou 'Oui' ; 0, sinon.
;;
;; Arguments
;; title : titre de la boite de dialogue (chaîne)
;; msg   : message à afficher (chaîne ou liste de chaînes)
;; flag  : drapeau pour le type de boutons (entier):
;;	   - 0 => OK
;;	   - 1 => OK | Annuler
;;         - 2 => Oui | Non

(defun MsgBox (title msg flag / temp file dcl_id status try)
  ;; Créer un fichier DCL temporaire
  (setq	temp (vl-filename-mktemp "Tmp.dcl")
	file (open temp "w")
  )

  (vl-catch-all-apply
    '(lambda ()
       ;; Ecrire le fichier
       ;; boutons Oui / Non
       (if (= flag 2)
	 (write-line
	   "yes_button : retirement_button {
              label = \"  Oui  \";
              key = \"accept\";
              is_default = true;
            }
            no_button : retirement_button {
              label = \"  Non  \";
              key = \"cancel\";
              is_cancel = true;
           }
           yes_no : column {
             : row {
               fixed_width = true;
               alignment = centered;
               yes_button;
               : spacer { width = 2; }
               no_button;
             }
           }"
	   file
	 )
       )

       ;; boite de dialogue principale
       (write-line "msgbox : dialog { key = \"titre\"; spacer;" file)
       (if (vl-consp msg)
	 (progn
	   (write-line ": paragraph {" file)
	   (foreach l msg
	     (write-line (strcat ": text_part{ label = \"" l "\";}") file)
	   )
	   (write-line "}" file)
	 )
	 (write-line (strcat ": text { label = \"" msg "\"; }") file)
       )
       (write-line "spacer;" file)
       (cond
	 ((= flag 1) (write-line "ok_cancel; }" file))
	 ((= flag 2) (write-line "yes_no; }" file))
	 ((= flag 0) (write-line "ok_only; }" file))
	 (T (exit))
       )
       (close file)

       ;; Ouvrir la boite de dialogue
       (setq dcl_id (load_dialog temp))
       (if (not (new_dialog "msgbox" dcl_id))
	 (exit)
       )
       (set_tile "titre" title)
       (action_tile "accept" "(done_dialog 1)")
       (setq status (start_dialog))
       (unload_dialog dcl_id)
     )
  )

  
  ;; Supprimer le fichier
  (vl-file-delete temp)

  ;; Renvoyer le résultat (Oui = 1 , Non = 0) 
  status
)

;;============================================================================;;

;; D'après Patrick_35
;;
;; Arguments
;; default : chemin du répertoitre initial
;; fltr : filtre d'extensions
;; flag : somme des code binaires ci-dessous
;;       1 OFN_READONLY &H1 La case 'Lecture seule' est cochée à la création de la fenêtre.
;;       2 OFN_OVERWRITEPROMPT &H2 Afficher un message de confirmation d'écrasement de fichier si celui-ci existe déjà.
;;       4 OFN_HIDEREADONLY &H4 Case à cocher 'Lecture seule' invisible.
;;       8 OFN_NOCHANGEDIR &H8 Conserve le répertoire d'origine à la fermeture de la fenêtre.
;;      16 OFN_SHOWHELP &H10 Afficher le bouton 'Aide' dans la boîte de dialogue.
;;     256 OFN_NOVALIDATE &H100 Ne vérifie pas la validité de la saisie (validité du nom de fichier).
;;     512 OFN_ALLOWMULTISELECT &H200 Autoriser la sélection multiple de fichiers.
;;    1024 OFN_EXTENSIONDIFFERENT &H400 Indique que l'utilisateur a choisi une extension différente de celle par défaut.
;;    2048 OFN_PATHMUSTEXIST &H800 Les chemins et fichiers saisis doivent exister.
;;    4096 OFN_FILEMUSTEXIST &H1000 Seuls des fichiers existants peuvent être saisis.
;;    8192 OFN_CREATEPROMPT &H2000 Afficher une fenêtre de confirmation de création de fichier.
;;   16384 OFN_SHAREAWARE &H4000 Ignorer les erreurs de partage réseau.
;;   32768 OFN_NOREADONLYRETURN &H8000 Ne sélectionne pas la case à cocher 'Lecture seule'.
;;   65536 OFN_NOTESTFILECREATE &H10000 Le fichier ne sera pas créé avant la fermeture de la fenêtre.
;;  131072 OFN_NONETWORKBUTTON &H20000 Cache (désactive) le bouton 'Réseau'.
;;  262144 OFN_NOLONGNAMES &H40000 Utilise les noms courts de fichier (sans effet dans le cas des fenêtres du type 'Explorer').
;;  524288 OFN_EXPLORER &H80000 Donne un style 'Explorer' à la boîte de dialogue (par défaut).
;;         Qui ne fonctionne apparement pas sous XP
;; 1048576 OFN_NODEREFERENCELINKS &H100000 La boîte de dialogue prendra le nom et le chemin du raccourci sélectionné.
;; 2097152 OFN_LONGNAMES &H200000 Gestion des noms longs pour les boîtes de dialogue n'ayant pas le style 'Explorer'.

;; exemple d'utilisation
;|
(FileBox
  (getvar "DWGPREFIX")
  "Fichiers dessins (*.dwg)|*.dwg|Fichiers DXF (*.dxf)|*.dxf|Tous les fichiers (*.*)|*.*"
   (+ 4 8 512 2048 4096 131072 524288 2097152)
)
|;

(defun FileBox (default fltr flag / cdl f)
  (setq cdl (vlax-create-object "userAccounts.CommonDialog"))
  (vlax-put-property cdl 'filter (vlax-make-variant fltr))
  (vlax-put-property cdl 'filterindex 1)
  (vlax-put-property cdl 'flags flag)
  (vlax-put-property cdl 'initialdir default)
  (if (eq (vlax-invoke cdl 'showopen) -1)
    (setq f (vlax-get-property cdl 'filename))
    (setq f nil)
  )
  (vlax-release-object cdl)
  f
)

;;============================================================================;;

;; getfolderdialog
;; Boite de dialogue pour choisir un dossier
;;
;; Arguments
;; msg : message à afficher dans la boite
;; newFolder : affiche le bouton "Créer un nouveau dossier" si non nil

(defun getfolderdlg (msg newFolder / shell folder self path)
  (or *acad* (setq *acad* (vlax-get-acad-object)))
  (vl-catch-all-apply
    '(lambda (flag)
       (and
         (setq shell (vla-getinterfaceobject *acad* "shell.application"))
         (setq folder (vlax-invoke-method shell 'browseforfolder (vla-get-HWND *acad*) msg flag))
         (setq self (vlax-get-property folder 'self))
         (setq path (vlax-get-property self 'path))
       )
     )
    (if newFolder
      '(0)
      '(512)
    )
  )
  (foreach obj (list self folder shell)
    (and obj (vlax-release-object obj))
  )
  path
)