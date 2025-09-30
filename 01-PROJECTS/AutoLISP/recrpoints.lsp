;;; RECRPOINTS — remplace les POINTs et blocs TCPOINT* par des DBPOINT AutoCAD,
;;; en conservant calque et coordonnées. Convertit OCS→WCS pour éviter les points "perdus".
;;; Les attributs des TCPOINT ne sont PAS recréés (on ne garde que la tête graphique).

(defun _rp:tcpoint-p (ename)
  ;; Vrai si INSERT dont le nom commence par "TCPOINT" (insensible à la casse)
  (and ename
       (eq (cdr (assoc 0 (entget ename))) "INSERT")
       (wcmatch (strcase (cdr (assoc 2 (entget ename)))) "TCPOINT*"))
)

(defun _rp:wcs-pt (ename dxfdata)
  ;; Renvoie le point 10 transformé en WCS (depuis l'OCS de l'entité)
  (trans (cdr (assoc 10 dxfdata)) ename 0)
)

(defun _rp:collect (/ res ss i n e d typ)
  ;; -> liste d’alistes: ((layer . "<calque>") (pt . (x y z)) (ename . <ename>))
  (setq res '())
  (setq ss (ssget "X" '((0 . "POINT,INSERT"))))
  (if ss
    (progn
      (setq n (sslength ss) i 0)
      (while (< i n)
        (setq e (ssname ss i)
              d (entget e)
              typ (cdr (assoc 0 d)))
        (cond
          ((eq typ "POINT")
           (setq res (cons (list (cons 'layer (cdr (assoc 8 d)))
                                 (cons 'pt    (_rp:wcs-pt e d))
                                 (cons 'ename e)) res)))
          ((and (eq typ "INSERT") (_rp:tcpoint-p e))
           (setq res (cons (list (cons 'layer (cdr (assoc 8 d)))
                                 (cons 'pt    (_rp:wcs-pt e d))
                                 (cons 'ename e)) res))))
        (setq i (1+ i))
      )
    )
  )
  res
)

(defun _rp:entmake-point (lay pt)
  ;; Crée un DBPOINT (normal Z) sur le calque lay aux coordonnées pt (en WCS)
  (entmakex (list
              (cons 0   "POINT")
              (cons 8   lay)
              (cons 10  pt)
              (cons 210 (list 0.0 0.0 1.0))
            ))
)

(defun _rp:count-by-layer (items / out it lay pair)
  ;; Petit récap par calque, sans COM
  (setq out '())
  (foreach it items
    (setq lay (cdr (assoc 'layer it)))
    (setq pair (assoc lay out))
    (if pair
      (setq out (subst (cons lay (1+ (cdr pair))) pair out))
      (setq out (cons (cons lay 1) out)))
  )
  ;; tri alpha (avec gestion robuste des types)
  (vl-sort out (function (lambda (a b) 
    (< (strcase (if (stringp (car a)) (car a) (vl-princ-to-string (car a))))
       (strcase (if (stringp (car b)) (car b) (vl-princ-to-string (car b))))))))
)

(defun C:RECRPOINTS (/ olderr items ndel nnew bylay e)
  (vl-load-com)
  (setq olderr *error*)
  (defun *error* (msg)
    (if (wcmatch (strcase (getvar "UNDOCTL")) "*1*")
      (command "._UNDO" "_End"))
    (if (and msg (/= msg "Function cancelled"))
      (princ (strcat "\n[RECRPOINTS] Erreur: " msg)))
    (setq *error* olderr)
    (princ)
  )

  (setq items (_rp:collect))
  (if (null items)
    (progn (princ "\nAucun POINT ni bloc TCPOINT* trouvé.") (*error* nil))
  )

  (princ (strcat "\nÉléments à traiter : " (itoa (length items))))
  (command "._UNDO" "_Begin")

  ;; 1) supprimer sources
  (setq ndel 0)
  (foreach it items
    (setq e (cdr (assoc 'ename it)))
    (if (and e (entget e))
      (progn (entdel e) (setq ndel (1+ ndel)))))

  ;; 2) recréer DBPOINT sur même calque
  (setq nnew 0)
  (foreach it items
    (if (_rp:entmake-point (cdr (assoc 'layer it)) (cdr (assoc 'pt it)))
      (setq nnew (1+ nnew))))

  (command "._UNDO" "_End")

  ;; 3) récap
  (setq bylay (_rp:count-by-layer items))
  (princ (strcat "\nSupprimé : " (itoa ndel) "  |  Recréé : " (itoa nnew)))
  (princ "\nPar calque :")
  (foreach kv bylay
    (princ (strcat "\n  - " 
                   (if (stringp (car kv)) 
                       (car kv) 
                       (vl-princ-to-string (car kv))) 
                   " : " (itoa (cdr kv)) " point(s)")))

  ;; 4) aide visibilité
  (princ (strcat
    "\nNote : les nouveaux objets sont des DBPOINT. Affichage = PDMODE/PDSIZE."
    "\n       PDMODE actuel=" (itoa (getvar "PDMODE")) ", PDSIZE=" (rtos (getvar "PDSIZE") 2 3)
    "\n       Si vous ne voyez rien, essayez : PDMODE=35 (ou 3) puis REGEN."))
  (princ)
)
