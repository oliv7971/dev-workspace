;; IDATA (gile) version 1.02 (26/12/2010)
;; Lier à chaque entité sélectionnée le texte multiligne entré (xdata)
;; ou modifier un texte multiligne déjà lié

(defun c:idata (/ *error* addDynDisplayData ent lastent pt mtxt)
  (vl-load-com)

  (defun *error* (msg)
    (and msg
         (/= msg "Fonction annulée")
	 (/= msg "Function cancelled")
         (princ (strcat "Error: " msg))
    )
    (and ent (redraw ent 4))
    (princ)
  )

  ;; Lier une xdata (mtext) à l'entité
  (defun addDynDisplayData (ent mtxt / elst)
    (setq elst (entget mtxt))
    (entmod
      (append (entget ent)
              (list
                (list
                  -3
                  (append
                    (list
                      "DynDisplayData"
                      (cons
                        1000
                        (if (< 16.0 (atof (substr (getvar 'acadver) 1 4)))
                          (vla-FieldCode (vlax-ename->vla-object mtxt))
                          (cdr (assoc 1 elst))
                        )
                      )
                      (cons 1000 (cdr (assoc 7 elst)))
                    )
                    (if (assoc 90 elst)
                      (list
                        (cons 1070 (cdr (assoc 90 elst)))
                        (cons 1071 (cdr (assoc 63 elst)))
                        (cons 1040 (cdr (assoc 45 elst)))
                      )
                    )
                  )
                )
              )
      )
    )
    (entdel mtxt)
  )

  (or (tblsearch "APPID" "DynDisplayData")
      (regapp "DynDisplayData")
  )
  (while (setq ent (entsel))
    (setq lastent (entlast)
          pt      (cadr ent)
          ent     (car ent)
    )
    (redraw ent 3)
    (if (setq data (cdadr (assoc -3 (entget ent '("DynDisplayData")))))
      (progn
        (entmake
          (append
            (list
              '(0 . "MTEXT")
              '(100 . "AcDbEntity")
              '(100 . "AcDbMText")
              (cons 10 (cadr (grread T)))
              (cons 40 (/ (getvar 'viewsize) 50.0))
              (cons 1 (cdr (assoc 1000 data)))
              (cons 7 (cdr (assoc 1000 (cdr (member (assoc 1000 data) data)))))
            )
            (if (assoc 1070 data)
              (list
                (cons 90 (cdr (assoc 1070 data)))
                (cons 63 (cdr (assoc 1071 data)))
                (cons 45 (cdr (assoc 1040 data)))
              )
            )
          )
        )
        (redraw ent 3)
        (setq mtxt (entlast))
        (vl-cmdf "_.mtedit" mtxt)
        (while (< 0 (getvar 'cmdactive)) (command pause))
        (addDynDisplayData ent mtxt)
      )
      (progn
        (initdia)
        (vl-cmdf "_.mtext" "_non" pt "_width" "0")
        (if (not (equal lastent (entlast)))
          (progn
            (setq mtxt (entlast))
            (addDynDisplayData ent mtxt)
          )
        )
      )
    )
  )
  (*error* nil)
)

;; RDATA (gile)
;; Supprimer le texte multiligne (xdata) liée à l'entité

(defun c:rdata (/ n ss ent)
  (if (setq n  -1
            ss (ssget '((-3 ("DynDisplayData"))))
      )
    (while (setq ent (ssname ss (setq n (1+ n))))
      (entmod
        (append
          (entget ent)
          ((lambda (l)
             (list (cons -3
                         (subst '("DynDisplayData")
                                (assoc "DynDisplayData" l)
                                l
                         )
                   )
             )
           )
            (cdr (assoc -3 (entget ent '("*"))))
          )
        )
      )
    )
  )
  (princ)
)

;; DDATA (gile)
;; Afficher le texte multiligne lié à l'entité qui se trouve sous le curseur

(defun c:ddata (/ *error* gr ent text ent str norm pt lst)
  (vl-load-com)

  (defun *error* (msg)
    (and msg
         (/= msg "Fonction annulée")
         (/= msg "Function cancelled")
         (princ (strcat "Error: " msg))
    )
    (and text (entdel text))
    (and ent (redraw ent 4))
    (princ)
  )

  (sssetfirst nil nil)
  (while (= (car (setq gr (grread T 14 2))) 5)
    (and text (entdel text) (setq text nil))
    (and ent (redraw ent 4))
    (setq pt (cadr gr))
    (if
      (and
        (setq ent (ssget pt '((-3 ("DynDisplayData")))))
        (setq ent (ssname ent 0))
        (setq lst (cdadr (assoc -3 (entget ent '("DynDisplayData")))))
      )
       (progn
         (redraw ent 3)
         (setq size (/ (getvar "VIEWSIZE") 40.) ; hauteur de texte
               norm (trans '(0 0 1) 2 0 t)
               text (entmakex
                      (append
                        (list
                          '(0 . "MTEXT")
                          '(100 . "AcDbEntity")
                          '(100 . "AcDbMText")
                          (cons 10
                                (trans
                                  (polar (trans pt 1 2) (* pi 1.75) size)
                                  2
                                  0
                                )
                          )
                          (cons 40 size)
                          '(41 . 0.)
                          (cons 1 "")
                          (cons 7 (cdr (assoc 1000 (cdr (member (assoc 1000 lst) lst)))))
                          (cons 210 norm)
                          (cons 11 (trans '(1 0 0) 2 0 T))
                        )
                        (if (assoc 1070 lst)
                          (list
                            (cons 90 (cdr (assoc 1070 lst)))
                            (cons 63 (cdr (assoc 1071 lst)))
                            (cons 45 (cdr (assoc 1040 lst)))
                          )
                        )
                      )
                    )
         )
         (vla-put-TextString (vlax-ename->vla-object text) (cdr (assoc 1000 lst)))
       )
    )
  )
  (*error* nil)
)