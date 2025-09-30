;;; RES_HEL (Gilles Chanteau)
;;;  Crée un réseau hélicoïdal (-RES_HEL -> ligne de commande) -04/07/06-

;;;============================== Sous routines ==============================;;;

;;; ANG2STR Convertit une valeur d'angle en radians en chaine de caractère
;;; représentant l'angle dans l'unité spécifiée
;;; (ANG2STR (* 3 pi) 2 2) -> "600.00g"
;;; (ANG2STR (* 3 pi) nil nil) -> "540.00" pour AUNITS=0 et AUPREC=2

(defun ang2str (ang unt prec / d m s)
  (if (numberp ang)
    (progn
      (if (not unt)
	(setq unt (getvar "AUNITS"))
      )
      (if (not prec)
	(setq prec (getvar "AUPREC"))
      )
      (cond
	((= unt 0)
	 (rtos (* (/ ang pi) 180) 2 prec)
	)
	((= unt 1)
	 (setq d (* (/ ang pi) 180)
	       m (* 60 (- d (setq d (fix d))))
	       s (* 60 (- m (setq m (fix m))))
	 )
	 (if (equal (abs s) 60 1e-009)
	   (progn
	     (setq s 0.0)
	     (if (minusp m)
	       (setq m (1- m))
	       (setq m (1+ m))
	     )
	   )
	 )
	 (if (= (abs m) 60)
	   (progn
	     (setq m 0)
	     (if (minusp m)
	       (setq d (1- d))
	       (setq d (1+ d))
	     )
	   )
	 )
	 (strcat (itoa d)
		 "d"
		 (if (< 0 prec)
		   (strcat (itoa m) "'")
		   ""
		 )
		 (if (< 2 prec)
		   (if (< prec 4)
		     (strcat (itoa (fix s)) "\"")
		     (strcat (rtos s 2 (- prec 4)) "\"")
		   )
		   ""
		 )
	 )
	)
	((= unt 2)
	 (strcat (rtos (* (/ ang pi) 200) 2 prec) "g")
	)
	((= unt 3)
	 (strcat (rtos ang 2 prec) "r")
	)
	((= unt 4)
	 (if (= (getvar "ANGDIR") 1)
	   (setq ang (- ang))
	 )
	 (angtos (+ (getvar "ANGBASE") ang) 4 prec)
	)
      )
    )
    (princ "\n; erreur: type d'argument incorrect: numberp: nil"
    )
  )
)

;;; STR2ANG Convertit une chaine de caractères représentant un angle
;;; en sa valeur en radians (nombre réel)
;;; (STR2ANG "540" 0) ou (STR2ANG "600g" nil) retournent 9.42478 soit 3*pi radians

(defun STR2ANG (str unt / ang)
  (if (= (type str) 'STR)
    (progn
      (if (not unt)
	(setq unt (getvar "AUNITS"))
      )
      (cond
	((numberp (read str))
	 (setq ang (float (read str)))
	 (cond
	   ((or (= unt 0) (= unt 1) (= unt 4))
	    (* (/ ang 180) pi)
	   )
	   ((= unt 2)
	    (* (/ ang 200) pi)
	   )
	   ((= unt 3)
	    ang
	   )
	 )
	)
	((and (= unt 4) (angtof str))
	 (if (= (getvar "ANGDIR") 1)
	   (- (getvar "angbase") (angtof str))
	   (- (angtof str) (getvar "angbase"))
	 )
	)
	((angtof str)
	 (if (not (member "geomcal.arx" (arx)))
	   (arxload "geomcal")
	 )
	 (* (/ (cal str) 180) pi)
	)
      )
    )
    (princ "\n; erreur: type d'argument incorrect: stringp nil")
  )
)

;;; VL-CREAT_RES_HEL Création du réseau

(defun VL-CREAT_RES_HEL	(ss nb cen ang ht / AcDoc ModSp)
  (vl-load-com)
  (setq	AcDoc (vla-get-activedocument (vlax-get-acad-object))
	ModSp (vla-get-ModelSpace AcDoc)
  )
  (vla-startUndoMark AcDoc)
  (setq cen (trans cen 1 0))
  (repeat (1- nb)
    (repeat (setq n (sslength ss))
      (setq obj (vlax-ename->vla-object (ssname ss (setq n (1- n)))))
      (vla-Copy obj)
      (vla-Rotate obj (vlax-3d-point cen) ang)
      (vla-Move	obj
		(vlax-3d-point '(0 0))
		(vlax-3d-point
		  (trans (list 0 0 ht) (trans '(0 0 1) 1 0 T) 0)
		)
      )
    )
  )
  (vla-endUndoMark AcDoc)
)

;;;============================ Fonctions d'appel ============================;;;

;;; C:-RES_HEL Ligne de commande

(defun C:-RES_HEL (/ ss nb ang ht cen)
  (while (not (setq ss (ssget))))
  (initget 7)
  (setq nb (getint "\nEntrez le nombre d'éléments du réseau: "))
  (initget 1)
  (setq cen (getpoint "\nSpécifiez le centre du réseau: "))
  (if (not
	(setq ht
	       (getdist
		 "\nSpécifiez le décalage en hauteur ou < Hauteur totale >: "
	       )
	)
      )
    (progn
      (initget 1)
      (setq ht (/ (getdist "\nSpécifiez la hauteur totale: ") nb))
    )
  )
  (initget "Décrit Elément")
  (if
    (=
      (getkword
	"\nPrécisez : angle décrit ou angle entre les éléments [Décrit/Elément] < Décrit >: "
      )
      "Elément"
    )
     (setq ang_t "angle entre les éléments")
     (setq ang_t "angle décrit")
  )
  (while (not (numberp ang))
    (if	(= (setq ang
		  (getstring
		    (strcat "\nEntrez l'" ang_t " ou < Saisie graphique >: ")
		  )
	   )
	   ""
	)
      (progn
	(initget "Référence")
	(if (= "Référence"
	       (setq ang
		      (getangle cen "\nSpécifiez l'angle ou [Référence]: ")
	       )
	    )
	  (setq
	    ang
	     (+	(- (getangle cen "\nSpécifiez l'angle de référence: ")
		)
		(getangle cen "\nSpécifiez le nouvel angle: ")
	     )
	  )
	)
	(if (= 1 (getvar "ANGDIR"))
	  (setq ang (- ang))
	)
	(if (minusp ang)
	  (setq ang (+ (* 2 pi) ang))
	)
      )
      (setq ang (STR2ANG ang nil))
    )
  )
  (if (= ang_t "angle décrit")
    (setq ang (/ ang nb))
  )
  (initget "Horaire Trigonométrique")
  (if
    (=
      (getkword
	"\nSpécifiez le sens de rotation [Horaire/Trigonométrique] < T >: "
      )
      "Horaire"
    )
     (setq ang (- ang))
  )
  (VL-CREAT_RES_HEL ss nb cen ang ht)
  (princ)
)


;;; C:RES_HEL Boite  de dialogue

(defun C:RES_HEL (/ ss ang ht)
  (setq dcl_id (load_dialog "res_hel.dcl"))
  (setq what_next 2)
  (while (<= 2 what_next)
    (if	(not (new_dialog "res_hel" dcl_id))
      (exit)
    )
    (start_list "ang_typ")
    (mapcar 'add_list
	    '("Angle décrit" "Angle entre les éléments")
    )
    (end_list)
    (start_list "dec_ht")
    (mapcar 'add_list
	    '("Entre les éléments" "Hauteur totale")
    )
    (end_list)
    (if	(not *nb_res_hel*)
      (setq *nb_res_hel* 4)
    )
    (if	(null *cen_res_hel*)
      (setq *cen_res_hel* '(0.0 0.0))
    )
    (if	(not *dec_res_hel*)
      (setq *dec_res_hel* 0)
    )
    (if	(not *ht_res_hel*)
      (setq *ht_res_hel* 1.0)
    )
    (setq ht *ht_res_hel*)
    (if	(not *tot_res_hel*)
      (setq *tot_res_hel* 0)
    )
    (if	(not *sens_res_hel*)
      (setq *sens_res_hel* 1)
    )
    (if	(not *ang_res_hel*)
      (setq *ang_res_hel* (* 2 pi))
    )
    (setq ang *ang_res_hel*)
    (if	ss
      (mode_tile "accept" 0)
      (mode_tile "accept" 1)
    )
    (if	(zerop *tot_res_hel*)
      (set_tile "ang_typ" "0")
      (set_tile "ang_typ" "1")
    )
    (if	(zerop *dec_res_hel*)
      (set_tile "dec_ht" "0")
      (set_tile "dec_ht" "1")
    )
    (if	(minusp *sens_res_hel*)
      (set_tile "hor" "1")
      (set_tile "tri" "1")
    )
    (set_tile "nbre" (itoa *nb_res_hel*))
    (set_tile "ang_clv" (ANG2STR ang nil nil))
    (set_tile "ht_clv" (rtos ht))
    (set_tile "x_coord" (rtos (car *cen_res_hel*)))
    (set_tile "y_coord" (rtos (cadr *cen_res_hel*)))
    (action_tile
      "nbre"
      (strcat
	"(if (and (numberp (read $value))"
	"(< 0 (atoi $value)))"
	"(progn (setq *nb_res_hel* (atoi $value))"
	"(set_tile \"nbre\" (itoa *nb_res_hel*)))"
	"(progn (alert \"Entrée non valide\")"
	"(mode_tile \"nbre\" 2)))"
       )
    )
    (action_tile
      "x_coord"
      (strcat
	"(if (numberp (read $value))"
	"(setq *cen_res_hel* (list (atof $value) (cadr *cen_res_hel*)))"
	"(progn (alert \"Entrée non valide\")"
	"(mode_tile \"x_coord\" 2)))"
      )
    )
    (action_tile
      "y_coord"
      (strcat
	"(if (numberp (read $value))"
	"(setq *cen_res_hel* (list (car *cen_res_hel*) (atof $value)))"
	"(progn (alert \"Entrée non valide\")"
	"(mode_tile \"y_coord\" 2)))"
      )
    )
    (action_tile
      "ht_clv"
      (strcat
	"(if (numberp (read $value))"
	"(progn (setq ht (atof $value))"
	"(setq *ht_res_hel* ht)"
	"(set_tile \"ht_clv\" (rtos ht)))"
	"(progn (alert \"Entrée non valide\")"
	"(mode_tile \"ht_clv\" 2)))"
       )
    )
    (action_tile
      "dec_ht"
      (strcat
	"(if (= $value \"0\")"
	"(setq *dec_res_hel* 0)"
	"(setq *dec_res_hel* 1))"
      )
    )
    (action_tile
      "ang_typ"
      (strcat
	"(if (= $value \"0\")"
	"(setq *tot_res_hel* 0)"
	"(setq *tot_res_hel* 1))"
      )
    )
    (action_tile
      "hor"
      (strcat
	"(if (= $value \"0\")"
	"(setq *sens_res_hel* 1)"
	"(setq *sens_res_hel* -1))"
      )
    )
    (action_tile
      "tri"
      (strcat
	"(if (= $value \"1\")"
	"(setq *sens_res_hel* 1)"
	"(setq *sens_res_hel* -1))"
      )
    )
    (action_tile
      "ang_clv"
      (strcat
	"(if (angtof $value)"
	"(progn (setq ang (STR2ANG $value nil))"
	"(setq *ang_res_hel* ang)"
	"(set_tile \"ang_clv\" (ANG2STR ang nil nil)))"
	"(progn (alert \"Entrée non valide\")"
	"(mode_tile \"ang_clv\" 2)))"
       )
    )
    (action_tile "jeu_sel" "(done_dialog 3)")
    (action_tile "ht_sel" "(done_dialog 4)")
    (action_tile "cen_sel" "(done_dialog 5)")
    (action_tile "ang_sel" "(done_dialog 6)")
    (action_tile "accept" "(done_dialog 1)")
    (setq what_next (start_dialog))
    (cond
      ((= what_next 3)
       (setq ss (ssget))
      )
      ((= what_next 4)
       (setq ht (getdist "\nSpécifiez le premier point: "))
       (setq *ht_res_hel* ht)
      )
      ((= what_next 5)
       (setq *cen_res_hel* (getpoint "\nSpécifiez le centre: "))
      )
      ((= what_next 6)
       (initget "Référence")
       (if (= "Référence"
	      (setq ang	(getangle *cen_res_hel*
				  "\nSpécifiez l'angle ou [Référence]: "
			)
	      )
	   )
	 (setq
	   ang (+ (- (getangle *cen_res_hel*
			       "\nSpécifiez l'angle de référence: "
		     )
		  )
		  (getangle *cen_res_hel*
			    "\nSpécifiez le nouvel angle: "
		  )
	       )
	 )
       )
       (if (= 1 (getvar "ANGDIR"))
	 (setq ang (- ang))
       )
       (if (minusp ang)
	 (setq ang (+ (* 2 pi) ang))
       )
       (setq *ang_res_hel* ang)
      )
      ((= what_next 1)
       (setq ang (* ang *sens_res_hel*))
       (if (zerop *tot_res_hel*)
	 (setq ang (/ ang *nb_res_hel*))
       )
       (if (not (zerop *dec_res_hel*))
	 (setq ht (/ ht *nb_res_hel*))
       )
       (VL-CREAT_RES_HEL ss *nb_res_hel* *cen_res_hel* ang ht)
      )
    )
  )
  (unload_dialog dcl_id)
  (princ)
)