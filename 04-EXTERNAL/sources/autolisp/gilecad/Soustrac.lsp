;; SOUSTRAC (gile)
;; Effectue une soustraction de régions ou solides 3d sans faire d'union
;; Propose de supprimer ou de conserver les objets soustraits
(defun c:soustrac (/ *error* ss1 ss2 n lst)
  (vl-load-com)
  (or *acdoc*
      (setq *acdoc* (vla-get-activeDocument (vlax-get-acad-object)))
  )
  (defun *error* (msg)
    (and
      msg
      (/= msg "Fonction annulée")
      (princ (strcat "\nErreur: " msg))
    )
    (vla-EndUndoMark *acdoc*)
    (princ)
  )
  (princ
    "\nSélectionnez les solides et les régions à enlever de .."
  )
  (if
    (setq ss1 (ssget '((0 . "REGION,3DSOLID"))))
     (if (and
	   (princ
	     "\nSélectionnez les solides et les régions à soustraire .."
	   )
	   (setq ss2 (ssget '((0 . "REGION,3DSOLID"))))
	 )
       (progn
	 (vla-StartUndoMark *acdoc*)
	 (repeat (setq n (sslength ss2))
	   (setq
	     lst
	      (cons
		(vlax-ename->vla-object (ssname ss2 (setq n (1- n))))
		lst
	      )
	   )
	 )
	 (repeat (setq n (sslength ss1))
	   (setq
	     obj (vlax-ename->vla-object (ssname ss1 (setq n (1- n))))
	   )
	   (foreach o lst
	     (and (= (vla-get-ObjectName obj) (vla-get-ObjectName o))
		  (vla-Boolean obj acSubtraction (vla-copy o))
	     )
	   )
	 )
	 (initget "Oui Non")
	 (if (= "Oui" (getkword "\nSupprimer les objets soustraits [Oui/Non] <N>: "))
	      (mapcar 'vla-delete lst)
	 )
	 (*error* nil)
       )
     )
  )
)