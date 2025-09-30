;;; Vue prédéfinies depuis le pavé numérique (gile)
;;; 0 = Bas
;;; 1 = Isométrie sud Ouest
;;; 2 = Avant
;;; 3 = Isométrie sud Est
;;; 4 = Gauche
;;; 5 = Haut
;;; 6 = Droite
;;; 7 = Isométrie Nord Ouest
;;; 8 = Arrière
;;; 9 = Isométrie Nord Est

(mapcar
  '(lambda (f v)
     (eval (list 'defun
		 f
		 nil
		 (list 'command "_.view" v)
		 '(princ)
	   )
     )
   )
  '(c:0 c:1 c:2 c:3 c:4 c:5 c:6 c:7 c:8 c:9)
  '("_bottom"	"_swiso"    "_front"	"_seiso"    "_left"
    "_top"	"_right"    "_nwiso"	"_back"	    "_neiso"
   )
)