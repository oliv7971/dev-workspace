;; gc:DictDataPut
;;
;; Stocke une liste de données dans un dictionnaire
;;
;; Arguments :
;; dict : le nom du dictionnaire (chaine) ou de l'object (ename)
;; key : la clé de l'entée du dictionnaire (chaine)
;; data : la liste de données (chaine, entier, réel, point)

(defun gc:DictDataPut (name key data / dict lst xrec typ)
  (if
    (or
      (and
	(= (type name) 'STR)
	(snvalid name)
	(or
	  (and
	    (dictsearch (namedobjdict) name)
	    (setq
	      dict (cdr (assoc -1 (dictsearch (namedobjdict) name)))
	    )
	  )
	  (setq	dict
		 (dictadd
		   (namedobjdict)
		   name
		   (entmakex '((0 . "DICTIONARY") (100 . "AcDbDictionary")))
		 )
	  )
	)
      )
      (and
	(or
	  (= (type name) 'ENAME)
	  (and
	    (= (type name) 'VLA-OBJECT)
	    (setq name (vlax-vla-object->ename name))
	  )
	)
	(or (setq
	      dict (cdr	(assoc 360
			       (member '(102 . "{ACAD_XDICTIONARY")
				       (entget name)
			       )
			)
		   )
	    )
	    (and
	      (setq
		dict (entmakex
		       '((0 . "DICTIONARY") (100 . "AcDbDictionary"))
		     )
	      )
	      (entmod (append (entget name)
			      (list '(102 . "{ACAD_XDICTIONARY")
				    (cons 360 dict)
				    '(102 . "}")
			      )
		      )
	      )
	    )
	)
      )
    )
     (if (snvalid key)
       (progn
	 (or (listp data) (setq data (list data)))
	 (foreach d data
	   (setq typ (type d))
	   (cond
	     ((= typ 'STR) (setq lst (cons (cons 1 d) lst)))
	     ((= typ 'INT) (setq lst (cons (cons 70 d) lst)))
	     ((= typ 'REAL) (setq lst (cons (cons 40 d) lst)))
	     ((and (listp d) (<= 2 (length d) 3) (vl-every 'numberp d))
	      (setq lst (cons (cons 10 d) lst))
	     )
	   )
	 )
	 (and (setq xrec (dictsearch dict key))
	      (entdel (cdr (assoc -1 xrec)))
	 )
	 (if lst
	   (progn
	     (dictadd
	       dict
	       key
	       (entmakex
		 (append
		   (list '(0 . "XRECORD")
			 '(100 . "AcDbXrecord")
		   )
		   (reverse lst)
		 )
	       )
	     )
	     (reverse (mapcar 'cdr lst))
	   )
	 )
       )
       (princ (strcat "\nClé non valide: " key))
     )
     (princ "\nNom ou objet non valide.")
  )
)


;; gc:DictDataList
;;
;; Liste les données des entrées d'un dictionnaire
;; Arguments :
;; dict : le nom du dictionnaire (chaine) ou de l'object (ename)

(defun gc:DictDataList (name / dict elst lst)
  (if (or
	(and
	  (= (type name) 'STR)
	  (dictsearch (namedobjdict) name)
	  (setq dict (dictsearch (namedobjdict) name))
	)
	(and
	  (or
	    (= (type name) 'ENAME)
	    (and
	      (= (type name) 'VLA-OBJECT)
	      (setq name (vlax-vla-object->ename name))
	    )
	  )
	  (setq
	    dict (entget
		   (cdr	(assoc 360
			       (member '(102 . "{ACAD_XDICTIONARY")
				       (entget name)
			       )
			)
		   )
		 )
	  )
	)
      )
    (progn
      (setq elst (vl-member-if
		   (function (lambda (x) (= (car x) 3)))
		   dict
		 )
      )
      (while elst
	(setq lst  (cons
		     (cons (cdar elst)
			   (mapcar
			     'cdr
			     (cdr
			       (vl-member-if
				 (function (lambda (x) (= (car x) 280)))
				 (entget (cdadr elst))
			       )
			     )
			   )
		     )
		     lst
		   )
	      elst (cddr elst)
	)
      )
      (reverse lst)
    )
  )
)


;; gc:DictDataDelete
;;
;; Supprime une entée dans un dictionnaire
;; Arguments :
;; dict : le nom du dictionnaire (chaine) ou de l'object (ename)
;; key : la clé de l'entée du dictionnaire (chaine)

(defun gc:DictDataDelete (name key / dict xrec)
  (if (or
	(and
	  (= (type name) 'STR)
	  (dictsearch (namedobjdict) name)
	  (setq dict (cdr (assoc -1 (dictsearch (namedobjdict) name))))
	)
	(and
	  (or
	    (= (type name) 'ENAME)
	    (and
	      (= (type name) 'VLA-OBJECT)
	      (setq name (vlax-vla-object->ename name))
	    )
	  )
	  (setq
	    dict (cdr (assoc 360
			     (member '(102 . "{ACAD_XDICTIONARY")
				     (entget name)
			     )
		      )
		 )
	  )
	)
      )
    (if	(setq xrec (dictsearch dict key))
      (entdel (cdr (assoc -1 xrec)))
    )
  )
)


;; gc:DictDataGet
;;
;; Retorune la liste de données de l'entrée du dictionnaire
;; Arguments :
;; dict : le nom du dictionnaire (chaine) ou de l'object (ename)
;; key : la clé de l'entée du dictionnaire (chaine)

(defun gc:DictDataGet (name key / dict xrec)
  (if (or
	(and
	  (= (type name) 'STR)
	  (dictsearch (namedobjdict) name)
	  (setq dict (cdr (assoc -1 (dictsearch (namedobjdict) name))))
	)
	(and
	  (or
	    (= (type name) 'ENAME)
	    (and
	      (= (type name) 'VLA-OBJECT)
	      (setq name (vlax-vla-object->ename name))
	    )
	  )
	  (setq
	    dict (cdr (assoc 360
			     (member '(102 . "{ACAD_XDICTIONARY")
				     (entget name)
			     )
		      )
		 )
	  )
	)
      )
    (if	(setq xrec (dictsearch dict key))
      (mapcar
	'cdr
	(cdr
	  (vl-member-if (function (lambda (x) (= (car x) 280))) xrec)
	)
      )
    )
  )
)

;; gc:GetExtDict (gile)
;; Retourne le dictionnaire d'extension de l'entité (ou nil)
;;
;; Argument : ent (ENAME)

(defun gc:GetExtDict (ent)
  (cdadr (member '(102 . "{ACAD_XDICTIONARY") (entget ent)))
)

;; gc:GetOrCreateExtDict (gile)
;; Retourne le dictionnaire d'extension de l'entité
;; Le dictionnaire est créé s'il n'existe pas
;;
;; Argument : ent (ENAME)

(defun gc:GetOrCreateExtDict (ent / dict)
  (cond
    ((cdadr (member '(102 . "{ACAD_XDICTIONARY") (entget ent))))
    ((setq dict	(entmakex
		  '((0 . "DICTIONARY") (100 . "AcDbDictionary"))
		)
     )
     (entmod
       (vl-list*
         (assoc -1 elst)
         (assoc 0 elst)
         (assoc 5 elst)
         (cons 102 "{ACAD_XDICTIONARY")
         (cons 360 dict)
         (cons 102 "}")
         (vl-remove-if (function (lambda (x) (member (car x) '(-1 0 5)))) elst)
       )
     )
     dict
    )
  )
)

;;;============================================================;;;

;; gc:GetDictEntries
;; Retourne la liste des entrées du dictionnaire
;; sous forme de paires pointées (Nom . ENAME)
;;
;; Argument : dict le dictionnaire (ENAME ou liste DXF)

(defun gc:GetDictEntries (dict / result)
  (and (= (type dict) 'ENAME) (setq dict (entget dict)))
  (while
    (setq dict (vl-member-if (function (lambda (x) (= (car x) 3))) (cdr dict)))
     (setq result (cons (cons (cdar dict) (cdadr dict)) result))
  )
  (reverse result)
)

;; gc:NestedDictSearch
;; Retourne la liste DXF du dernier dictionnaire enfant de la liste (ou nil)
;;
;; Argument
;; lst : la liste des noms des dictionnaires dans l'ordre de parenté

(defun gc:NestedDictSearch (lst / dict)
  (if (setq dict (dictsearch (namedobjdict) (car lst)))
    (while
      (and (setq lst (cdr lst))
	   (setq dict (dictsearch (cdr (assoc -1 dict)) (car lst)))
      )
    )
  )
  dict
)

;; gc:GetOrCreateDict
;; Retourne le ENAME du dictionnaire trouvé ou créé s'il n'exstait pas
;;
;; Arguments
;; dict : ENAME du dictionnaire parent
;; name : nom du dictionnaire à chercher ou créer

(defun gc:GetOrCreateDict (dict name)
  (if (snvalid name)
    (cond
      ((cdr (assoc -1 (dictsearch dict name))))
      ((dictadd	dict
		name
		(entmakex '((0 . "DICTIONARY") (100 . "AcDbDictionary")))
       )
      )
    )
  )
)

;; gc:GetOrCreateNestedDict
;; Retourne le ENAME du dernier dictionnaire enfant de la liste
;; S'ils n'existent pas déjà les dictionnaires sont créés
;;
;; Argument
;; lst : la liste des noms des dictionnaires dans l'ordre de parenté

(defun gc:GetOrCreateNestedDict	(lst)
  (setq dict (namedobjdict))
  (foreach n lst (setq dict (gc:GetOrCreateDict dict n)))
  dict
)

;; gc:NestedDictRemove
;; Retourne le ENAME du dictionnaire supprimé (ou nil)
;;
;; Arguments
;; lst : la liste des noms des dictionnaires dans l'ordre de parenté
;; key : le nom du dictionnaire à supprimer

(defun gc:NestedDictRemove (lst key / dict)
  (if (setq dict (gc:NestedDictSearch lst))
    (dictremove (cdr (assoc -1 dict)) key)
  )
)

;; gc:GetXrecData
;; Retourne la liste des données affectées au Xrecord (liste de paires pointées)
;;
;; Arguments
;; dict : ENAME du dictionnaire parent
;; key : nom du Xrecord

(defun gc:GetXrecData (dict key / xrec)
  (if (and
	(setq xrec (dictsearch dict key))
	(= (cdr (assoc 0 xrec)) "XRECORD")
      )
    (cdr (member (assoc 280 xrec) xrec))
  )
)

;; gc:SetXrecData
;; Retourne le ENAME du xrecord auquel sont affectées mes données
;;
;; Arguments
;; dict : ENAME du dictionnaire parent
;; key : nom du Xrecord
;; data : liste de paires pointées contenant les données

(defun gc:SetXrecData (dict key data / xrec)
  (if (snvalid key)
    (progn
      (and (setq xrec (dictsearch dict key))
	   (entdel (cdr (assoc -1 xrec)))
      )
      (dictadd
	dict
	key
	(entmakex
	  (append
	    (list '(0 . "XRECORD")
		  '(100 . "AcDbXrecord")
	    )
	    data
	  )
	)
      )
    )
  )
)

;; gc:GetNestedXrecData
;; Retourne la liste des données affectées au Xrecord du dernier dictionnaire enfant
;;
;; Arguments
;; lst : la liste des noms des dictionnaires dans l'ordre de parenté
;; key : nom du Xrecord

(defun gc:GetNestedXrecData (lst key / dict)
  (if (setq dict (gc:NestedDictSearch lst))
    (gc:GetXrecData (cdr (assoc -1 dict)) key)
  )
)

;; gc:SetNestedXrecData
;; Retourne le ENAME du xrecord auquel sont affectées les données
;;
;; Arguments
;; lst : la liste des noms des dictionnaires dans l'ordre de parenté
;; key : nom du Xrecord
;; val : liste de paires pointées

(defun gc:SetNestedXrecData (lst key val / dict)
  (if (setq dict (gc:NestedDictSearch lst))
    (gc:SetXrecData (cdr (assoc -1 dict)) key val)
  )
)
