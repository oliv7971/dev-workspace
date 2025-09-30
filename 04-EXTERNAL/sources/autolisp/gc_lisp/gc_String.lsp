;; gc:strinp
;; Evalue si l'expression est une chaine non vide
;;
;; Argument
;; expr : l'expression à évaluer
(defun gc:strinp (expr)
  (and (= 'STR (type expr))
       (/= expr "")
  )
)

;; gc:StringSubstAll
;; Substitue toutes les occurences d'une chaine par une autre dans une chaine
;;
;; Arguments
;; new : la chaîne à substituer
;; old : la chaîne à remplacer
;; str : la chaîne à traiter
(defun gc:StringSubstAll (new old str / pos)
  (while (setq pos (vl-string-search old str))
    (setq str (vl-string-subst new old str pos))
  )
  str
)

;; gc:str2lst
;; Transforme un chaine avec séparateur en liste de chaines
;;
;; Arguments
;; str : la chaîne
;; sep : le séparateur
(defun gc:str2lst (str sep / len lst)
  (setq len (strlen sep))
  (while (setq pos (vl-string-search sep str))
    (setq lst (cons (substr str 1 pos) lst)
	  str (substr str (+ len pos 1))
    )
  )
  (reverse (cons (substr str 1 pos) lst))
)

;; gc:lst2str
;; Concatène une liste de chaînes et un séparateur en une chaine
;;
;; Arguments
;; lst : la liste
;; sep : le séparateur
(defun gc:lst2str (lst sep)
  (apply 'strcat
	 (cons (car lst)
	       (mapcar (function (lambda (x) (strcat sep x))) (cdr lst))
	 )
  )
)

;; gc:str2pt
;; Transforme une chaine en point 3d (saisie clavier avec grread)
;;
;; Argument
;; str : la chaîne
(defun gc:str2pt (str)
  (setq str (mapcar 'read (gc:str2lst str ",")))
  (if (and (vl-every 'numberp str)
	   (< 1 (length str) 4)
      )
    (trans str 0 0)
  )
)

;; gc:StringPadLeft
;; Ajoute autant de caratères que nécessaire au début de la chaîne
;;
;; Arguments
;; str : la chaîne
;; len : la longueur de chaîne
;; char : le caractère à ajouter
(defun gc:StringPadLeft	(str len char)
  (if (< (strlen str) len)
    (gc:StringPadLeft (strcat char str) len char)
    str
  )
)

;; gc:StringPadRight
;; Ajoute autant de caratères que nécessaire à la fin de la chaîne
;;
;; Arguments
;; str : la chaîne
;; len : la longueur de chaîne
;; char : le caractère à ajouter
(defun gc:StringPadRight (str len char)
  (if (< (strlen str) len)
    (gc:StringPadRight (strcat str char) len char)
    str
  )
)

;; gc:NumStrSort
;; Retourne un liste de chaînes triés en tenant compte de la valeur
;; des chiffres placés au début
;;
;; Argument
;; lst : la liste de chaînes à trier
(defun gc:NumStrSort (lst / pref)

  (defun pref (str / l1 l2)
    (setq l1 (vl-string->list str))
    (while (< 47 (car l1) 58)
      (setq l2 (cons (car l1) l2)
	    l1 (cdr l1)
      )
    )
    (vl-list->string (reverse l2))
  )

  (vl-sort lst
	   '(lambda (x1 x2 / n1 n2)
	      (if (and (/= (setq n1 (pref x1)) "")
		       (/= (setq n2 (pref x2)) "")
		       (/= n1 n2)
		  )
		(< (atoi n1) (atoi n2))
		(< x1 x2)
	      )
	    )
  )
)

;; gc:IncrNumStr
;; Incrémente une chaine numéraire
;;
;; Argument
;; str : la chaîne
(defun gc:IncrNumStr (str / l)
  (gc:StringPadLeft "0" (strlen str) (itoa (1+ (atoi str))))
)

;; gc:IncSuff (version 1.0.0) -Gilles Chanteau- 09/03/10
;; Incrémente le suffixe d'une chaîne de caractères de la valeur spécifiée.
;; Est pris en compte comme suffixe, l'ensemble des caractères [0-9] et/ou [A-Z] et/ou [a-z]
;; plus le séparateur (optionnel) depuis la fin du texte, en fonction de la valeur de 'alpha'
;;
;; Arguments
;; str : la chaîne
;; alpha : drapeau indiquant le type de chaîne à incrémenter somme des code binaires suivant :
;;         - 1 nombres entiers
;;         - 2 majuscules
;;         - 4 minuscules
;; sep : caractère devant être considéré comme séparateur (ou nil)
(defun gc:IncSuff	(str	inc    alpha  sep    /	    number upper
		 lower	lst    crt    pas    ind    val	   quo
		 ret
		)
  (defun number (x) (and (< 47 x 58) (= 1 (logand 1 alpha))))
  (defun upper (x) (and (< 64 x 91) (= 2 (logand 2 alpha))))
  (defun lower (x) (and (< 96 x 123) (= 4 (logand 4 alpha))))
  (setq	lst (reverse (vl-string->list str))
	sep (if	sep
	      (ascii sep)
	      0
	    )
  )
  (while
    (and
      (setq crt (car lst))
      (if (= sep crt)
	(if (or
	      (setq num (number (cadr lst)))
	      (setq upr (upper (cadr lst)))
	      (setq lwr (lower (cadr lst)))
	    )
	  (setq	lst (cdr lst)
		crt (car lst)
		ret (cons sep ret)
	  )
	  T
	)
	(or
	  (setq num (number crt))
	  (setq upr (upper crt))
	  (setq lwr (lower crt))
	  T
	)
      )
      (cond
	(num
	 (setq pas 10
	       ind 48
	 )
	)
	(upr
	 (setq pas 26
	       ind 65
	 )
	)
	(lwr
	 (setq pas 26
	       ind 97
	 )
	)
	((< 0 quo)
	 (setq crt (if (= 10 pas)
		     ind
		     (1- ind)
		   )
	       lst (cons (car lst) lst)
	 )
	)
      )
    )
     (setq val (- crt ind)
	   quo (/ (+ val inc) pas)
	   ret (cons (+ ind (rem (+ val inc) pas)) ret)
     )
     (if (zerop quo)
       (setq ret (append (reverse (cdr lst)) ret)
	     lst nil
       )
       (if (cdr lst)
	 (setq lst (cdr lst)
	       inc quo
	 )
	 (setq lst (list ind)
	       inc (if (= 10 pas)
		     quo
		     (1- quo)
		   )
	 )
       )
     )
  )
  (if ret
    (vl-list->string ret)
  )
)

;; gc:Balanced
;; Evalue si les caractères ouvrant et fermant sont appariée dans une chaine
;;
;; Arguments
;; op : le caractère ouvrant
;; cl : le caractère fermant
;; str : la chaîne
(defun gc:Balanced (op cl str / n r)
  (setq	n   0
	r   T
	str (vl-string->list str)
  )
  (while (and r str)
    (cond
      ((= (car str) op) (setq n (1+ n)))
      ((= (car str) cl) (setq n (1- n)))
    )
    (setq r   (<= n 0)
	  str (cdr str)
    )
  )
  r
)

;; gc:Apaired
;; Retourne la liste des positions d'un caractère ouvrant et de son équivalent fermant
;;
;; Arguments
;; op : le caractère ouvrant
;; cl : le caractère fermant
;; str : la chaîne
;; pos : index de départ de la recherche
(defun gc:Apaired (op cl str pos / opened closed start tmp cnt)
  (and
    (setq opened (vl-string-search op str pos))
    (setq start	 (1+ opened)
	  closed T
	  cnt	 1
    )
    (while (and closed (< 0 cnt))
      (setq tmp	   (vl-string-search op str start)
	    closed (vl-string-search cl str start)
      )
      (if closed
	(if (and tmp (< tmp closed))
	  (setq	cnt   (1+ cnt)
		start (1+ tmp)
	  )
	  (setq	cnt   (1- cnt)
		start (1+ closed)
	  )
	)
      )
    )
  )
  (if (= 0 cnt)
    (list opened closed)
  )
)

;; gc:FieldCode (gile)
;; Retourne la chaîne de caractère d'un attribut, texte ou mtexte
;; avec le(s) code(s) de champ(s)
;;
;; Argument
;; ent : le nom d'entité du texte, mtexte ou attribut
(defun gc:FieldCode (ent / foo elst xdict dict field str)

  (defun foo (field str / pos fldID objID)
    (setq pos 0)
    (if (setq pos (vl-string-search "\\_FldIdx " str pos))
      (while (setq pos (vl-string-search "\\_FldIdx " str pos))
        (setq fldId (entget (cdr (assoc 360 field)))
              field (vl-remove (assoc 360 field) field)
              str   (strcat
                      (substr str 1 pos)
                      (if (setq objID (cdr (assoc 331 fldId)))
                        (vl-string-subst
                          (strcat "ObjId " (itoa (gc:EnameToObjectId objID)))
                          "ObjIdx"
                          (cdr (assoc 2 fldId))
                        )
                        (foo fldId (cdr (assoc 2 fldId)))
                      )
                      (substr str (1+ (vl-string-search ">%" str pos)))
                    )
        )
      )
      str
    )
  )
  
  (setq elst (entget ent))
  (if (and
	(member (cdr (assoc 0 elst)) '("ATTRIB" "MTEXT" "TEXT"))
	(setq xdict (cdr (assoc 360 elst)))
	(setq dict (dictsearch xdict "ACAD_FIELD"))
	(setq field (dictsearch (cdr (assoc -1 dict)) "TEXT"))
      )
    (setq str (foo field (cdr (assoc 2 field))))
  )
)

;; gc:EnameToObjectId (gile)
;; Retourne l'ObjectID correspondant à un ename
;;
;; Argument
;; ent : le nom d'entité
(defun gc:EnameToObjectId (ename)
  ((lambda (str)
     (gc:hex2dec
       (substr (vl-string-right-trim ">" str) (+ 3 (vl-string-search ":" str)))
     )
   )
    (vl-princ-to-string ename)
  )
)

;; gc:Rot13
;; Crypte la chaine avec la méthode ROT13
;;
;; Argument
;; s : la chaîne
(defun gc:Rot13 (s)
  (vl-list->string
    (mapcar
      (function
	(lambda	(x)
	  (cond
	    ((<= 65 x 90) (+ 65 (rem (- x 52) 26)))
	    ((<= 97 x 122) (+ 97 (rem (- x 84) 26)))
	    (x)
	  )
	)
      )
      (vl-string->list s)
    )
  )
)

;; gc:Rot47
;; Crypte la chaine avec la méthode ROT47
;;
;; Argument
;; s : la chaîne
(defun gc:Rot47 (s)
  (vl-list->string
    (mapcar
      (function
	(lambda	(x)
	  (if (<= 33 x 126)
	    (+ 33 (rem (+ x 14) 94))
	    x
	  )
	)
      )
      (vl-string->list s)
    )
  )
)

;; gc:hex2dec
;; Convertit un nombre hexadécimal (chaine) en un entier
;;
;; Argument
;; n : la chaîne figurant le nombre hexadécimal
(defun gc:hex2dec (n / r s)
  (setq r 0)
  (foreach s (vl-string->list (strcase n))
    (setq r (+
	      (* r 16)
	      (- s
		 (if (<= s 57)
		   48
		   55
		 )
	      )
	    )
    )
  )
)

;; gc:int2hex
;; Convertit un entier en un nombre hexadécimal (chaine)
;;
;; Argument
;; n : l'entier
(defun gc:int2hex	(n / r i)
  (setq r "")
  (while (> n 0)
    (setq i (fix (rem n 16))
	  n (/ (- n i) 16)
	  r (strcat (if	(< i 10)
		      (itoa i)
		      (chr (+ 55 i))
		    )
		    r
	    )
    )
  )
)

;; gc:hex2long
;; Convertit un nombre hexadécimal (chaine) en un entier long (chaine)
;;
;; Argument
;; n : la chaîne figurant le nombre hexadécimal
(defun gc:hex2long	(n / r s)
  (setq r 0.)
  (rtos
    (foreach s (vl-string->list (strcase n))
      (setq r (+
		(* r 16.)
		(- s
		   (if (<= s 57)
		     48.
		     55.
		   )
		)
	      )
      )
    )
    2
    0
  )
)

;; gc:long2hex
;; Convertit un entier long (chaine) en un nombre hexadécimal (chaine)
;;
;; Argument
;; n : la chaîne figurant l'entier long
(defun gc:long2hex	(n / r i)
  (setq	r ""
	n (atof n)
  )
  (while (> n 0)
    (setq i (fix (rem n 16))
	  n (/ (- n i) 16)
	  r (strcat (if	(< i 10)
		      (itoa i)
		      (chr (+ 55 i))
		    )
		    r
	    )
    )
  )
)

;; gc:num2alpha
;; Convertit un entier en caractères alphabétiques (majuscules)
;;
;; Argument
;; num : un nombre entier
(defun gc:num2alpha (num)
  (if (< num 27)
    (chr (+ 64 num))
    (if	(zerop (rem num 26))
      (strcat (gc:num2alpha (1- (/ num 26))) "Z")
      (strcat (gc:num2alpha (/ num 26))
	      (chr (+ 64 (rem num 26)))
      )
    )
  )
)

;; gc:alpha2num
;; Convertit une chaine en entier (insensible à la casse)
;;
;; Argument
;; str : la chaîne
(defun gc:alpha2num (str)
  (if (zerop (strlen str))
    0
    (+ (* (- (ascii (strcase (substr str 1 1))) 64)
	  (expt 26 (1- (strlen str)))
       )
       (gc:alpha2num (substr str 2))
    )
  )
)