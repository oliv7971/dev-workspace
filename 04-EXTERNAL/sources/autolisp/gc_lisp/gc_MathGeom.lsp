;;-------------------------------------------------;;
;;-------------------- NOMBRES --------------------;;
;;-------------------------------------------------;;

;; gc:binList
;; Retourne la liste des codes binaires contenus dans un entier
;;
;; Argument
;; n : un nombre entier
(defun bin-list	(n / b l)
  (while (/= 0 n)
    (setq b (expt 2 (fix (/ (log n) (log 2))))
	  n (- n b)
	  l (cons b l)
    )
  )
)

;; gc:hex2dec
;; Convertit un hexadécimal (string) en décimal (int)
;;
;; Argument
;; s : une chaîne représentant un nombre hexadécimal
(defun gc:hex2dec (s / f)
  (defun f (l a / c)
    (if	(setq c (car l))
      (f (cdr l)
	 (+ (cond
	      ((< 96 c 103) (- c 87))
	      ((< 64 c 71) (- c 55))
	      ((< 47 c 58) (- c 48))
	    )
	    (lsh a 4)
	 )
      )
      a
    )
  )
  (f (vl-string->list s) 0)
)

;; gc:dec2hex
;; Convertit un décimal (int) en hexadécimal (string)
;;
;; Argument
;; n : un nombre entier
(defun gc:dec2hex (n)
  (cond
    ((< 15 n)
     (strcat (gc:dec2hex (lsh n -4)) (gc:dec2hex (rem n 16)))
    )
    ((< n 10) (itoa n))
    (T (chr (+ n 55)))
  )
)

;; gc:round
;; Arrondit à la valeur entière la plus proche
;;
;; Arguments
;; num : le nombre à arrondir
(defun gc:round	(num)
  (if (minusp num)
    (fix (- num 0.5))
    (fix (+ num 0.5))
  )
)

;; gc:roundTo
;; Arrondit à la valeur la plus proche en fonction de prec
;;
;; Arguments
;; prec : le nombre spécifiant la précision de l'arrondi
;; num : le nombre à arrondir
(defun gc:roundTo (prec num)
  (if (zerop (setq prec (abs prec)))
    num
    (* prec (gc:round (/ num prec)))
  )
)

;;; gc:RoundRec
;; Arrondit les nombres dans les points, listes de points, etc
;;
;; Arguments
;; lst : une liste de nombres et/ou de sous-listes de nombres
;; prec : le nombre spécifiant la précision de l'arrondi
(defun gc:RoundRec (lst prec)
  (if (listp lst)
    (mapcar '(lambda (x) (gc:RoundRec x prec)) lst)
    (gc:roundTo lst prec)
  )
)

;; gc:FixZero
;; Arrondit à 0 les nombres compris entre -fuzz et fuzz
;; Fonctionne avec les nombres et les listes de nombres (même imbriquées)
;;
;; Arguments
;; num : le nombre à arrondir
;; fuzz : la tolérance
(defun gc:FixZero (num fuzz)
  (if (listp num)
    (mapcar '(lambda (x) (gc:FixZero x fuzz)) num)
    (if	(equal num 0. fuzz)
      0.
      num
    )
  )
)

;; gc:Log10
;; Retourne le logarithme décimal du nombre
;;
;; Argument
;; x : un nombre strictement positif
(defun gc:Log10 (x)
  (/ (log x) (log 10))
)

;; gc:Fuzz
;; Retourne la tolérance utilisable pour comparaison en fonction
;; du nombre de chiffres significatifs de x
;;
;; Argument
;; x : le nombre
(defun gc:Fuzz (x)
  (if (zerop x)
    1e-15
    (expt 10.0 (fix (- (gc:Log10 (abs x)) 15)))
  )
)

;; gc:EqualNumbers
;; Evalue si deux nombres sont égaux en utilisant une tolérance calculée
;; en fonction du nombre de chiffres significatifs de x et y
;;
;; Argument
;; x et y : les nombres à comparer
(defun gc:EqualNumbers (x y)
  (or (= x y) (equal x y (max (gc:Fuzz x) (gc:Fuzz y))))
)

;; gc:random
;; Retourne un nombre "pseudo-aléatoire" entre 0 et 1
(defun gc:random ()
  (or *seed* (setq *seed* (getvar "DATE")))
  (setq *seed* (rem (1+ (* 1664525 *seed*)) 4294967296.))
  (/ *seed* 4294967296.)
)

;; gc:StepRandom
;; Retourne un nombre "pseudo-aléatoire" entre mini et maxi arrondi au pas spécifié
;;
;; Arguments
;; mini : le nombre minimum
;; maxi : le nombre maximum
;; step : le pas
(defun gc:StepRandom (mini maxi step)
  (+ mini (gc:round (* (- maxi mini) (rng)) step))
)

;; gc:int2bin
;; Retourne une chaine qui est la représentation binaire de num
;;
;; Argument
;; num : un nombre entier
(defun gc:int2bin (num / n s)
  (setq	n 1
	s (itoa (rem num 2))
  )
  (while (< 0 (/ num (expt 2 n)))
    (if	(/= 0 (logand num (expt 2 n)))
      (setq s (strcat "1" s))
      (setq s (strcat "0" s))
    )
    (setq n (1+ n))
  )
  s
)

;; gc:bin2int
;; Retourne l'entier auquel correspond la représentation binare bin
;;
;; Argument
;; bin : chaîne uniquement composée de 0 et de 1
(defun b2d (bin / n s)
  (setq	n (strlen bin)
	s 0
  )
  (repeat n
    (setq n (1- n))
    (if	(= "1" (substr bin 1 1))
      (setq s (+ s (expt 2 n)))
    )
    (setq bin (substr bin 2))
  )
  s
)

;; gc:isPrime
;; Evalue si un nombre est premier
;;
;; Argument
;; n : un nombre entier
(defun gc:isPrime (n / f)
  (defun f (i)
    (or
      (> (* i i) n)
      (and
	(/= 0 (rem n i))
	(f (i + 2))
      )
    )
  )
  (or
    (< n 4)
    (and
      (/= 0 (rem n 2))
      (f 3)
    )
  )
)

;;------------------------------------------------;;
;;-------------------- POINTS --------------------;;
;;------------------------------------------------;;

;; gc:PointP
;; Évalue si p est un point valide
;;
;; Argument
;; p : l'expression à évaluer
(defun gc:PointP (p)
  (and
    (listp p)
    (<= 2 (length p) 3)
    (vl-every 'numberp p)
  )
)

;; gc:EqualPoints
;; Evalue si deux points sont égaux en utilisant une tolérance calculée
;; en fonction du nombre de chiffres significatifs des coordonnées
;;
;; Argument
;; p1 et p2 : les points à comparer
(defun gc:EqualPoints (p1 p2)
  (vl-every 'gc:EqualNumbers p1 p2)
)

;; gc:MidPoint
;; Retourne le milieu de p1 p2
;;
;; Arguments
;; p1 : un point
;; p2 : un point
(defun gc:MidPoint (p1 p2)
  (mapcar (function (lambda (x1 x2) (/ (+ x1 x2) 2.))) p1 p2)
)

;; gc:BetweenP
;; Evalue si pt est entre p1 et p2
;;
;; Arguments
;; p1 : un point
;; p2 : un point
					;  pt : le point à évaluer
(defun gc:BetweenP (p1 p2 pt)
  (or (equal p1 pt 1e-9)
      (equal p2 pt 1e-9)
      (equal (gc:GetUnitVector p1 pt)
	     (gc:GetUnitVector pt p2)
	     1e-9
      )
  )
)

;; gc:DistanceTo
;; Retourne la distance du point pt à la droite p1 p2
;;
;; Arguments
;; pt : le point extérieur à la droite
;; p1 : un point sur la droite
;; p2 : un point sur la droite
(defun gc:DistanceTo (pt p1 p2)
  ((lambda (v)
     (/
       (distance '(0. 0. 0.) (gc:CrossProduct (mapcar '- pt p1) v))
       (distance '(0. 0. 0.) v)
     )
   )
    (mapcar '- p2 p1)
  )
)

;; gc:DivSeg
;; Retourne la liste des points qui divisent le segment p1 p2 en n segments égaux
;;
;; Arguments
;; p1 : le point à une extrémité du segment
;; p2 : le point à l'autre extrémité du segment
;; n  : le nombre de divisions
(defun gc:DivSeg (p1 p2 n / v l)
  (setq	v (mapcar (function (lambda (x1 x2) (/ (- x2 x1) n))) p1 p2)
	l (cons p2 l)
  )
  (while (< 0 (setq n (1- n)))
    (setq l
	   (cons
	     (mapcar (function (lambda (x1 x2) (+ x1 (* x2 n)))) p1 v)
	     l
	   )
    )
  )
  (cons p1 l)
)

;; gc:ConvHull
;; Retourne la liste des points formant l'envloppe convexe
;;
;; Argument
;; pts : la liste des points
(defun gc:ConvHull (pts / p0)
  (setq	pts (vl-sort pts
		     '(lambda (p1 p2)
			(if (= (cadr p1) (cadr p2))
			  (< (car p1) (car p2))
			  (< (cadr p1) (cadr p2))
			)
		      )
	    )
	p0  (car pts)
	pts (vl-sort (cdr pts)
		     '(lambda (p1 p2 / d1 d2 c1 c2)
			(setq d1 (distance p0 p1)
			      d2 (distance p0 p2)
			)
			(if (equal (setq c1 (/ (- (car p0) (car p1)) d1))
				   (setq c2 (/ (- (car p0) (car p2)) d2))
				   1e-9
			    )
			  (< d1 d2)
			  (< c1 c2)
			)
		      )
	    )
	acc (list (car pts) p0)
	pts (cdr pts)
  )
  (foreach p pts
    (while (and (cdr acc) (gc:clockwise (cadr acc) (car acc) p))
      (setq acc (cdr acc))
    )
    (setq acc (cons p acc))
  )
  (reverse acc)
)

;;------------------------------------------------;;
;;-------------------- ANGLES --------------------;;
;;------------------------------------------------;;

;; gc:EqualK*Pi
;; Évalue si un angle est égal à k*pi radians à 0.000000001 près.
;;
;; Argument
;; a : la valeur de l'angle en radians
(defun gc:EqualK*Pi (a)
  (or
    (equal (rem a pi) 0. 1e-009)
    (equal (abs (rem a pi)) pi 1e-009)
  )
)

;; gc:tan
;; Retourne la tangente de l'angle
;;
;; Argument
;; a : la valeur de l'angle en radians
(defun gc:Tan (a) (/ (sin a) (cos a)))

;; gc:asin
;; Retourne l'arc sinus du nombre
;;
;; Argument
;; x : le sinus de l'angle
(defun gc:asin (x)
  (cond
    ((equal x 1. 1e-9) (/ pi 2.))
    ((equal x -1. 1e-9) (/ pi -2.))
    ((< -1. x 1.)
     (atan x (sqrt (- 1 (* x x))))
    )
  )
)

;; gc:acos
;; Retourne l'arc cosinus du nombre
;;
;; Argument
;; x : le cosinus de l'angle
(defun gc:acos (x)
  (cond
    ((equal x 1. 1e-9) 0.)
    ((equal x -1. 1e-9) pi)
    ((< -1. x 1.)
     (atan (sqrt (- 1. (* x x))) x)
    )
  )
)

;; gc:Ang<2pi
;; Retourne l'angle, à 2*k*pi près, compris entre 0 et 2*pi
;;
;; Argument
;; a : la valeur de l'angle en radians
(defun gc:Ang<2pi (a)
  (if (and (<= 0. a) (< a (* 2. pi)))
    a
    (gc:Ang<2pi (rem (+ a (* 2. pi)) (* 2. pi)))
  )
)

;; gc:cosh
;; Retourne le cosinus hyperbolique du nombre
;;
;; Argument
;; x : un nombre
(defun gc:cosh (x)
  (/ (+ (exp x) (exp (- x))) 2.)
)			

;; gc:sinh
;; Retourne le sinus hyperbolique du nombre
;;
;; Argument
;; x : un nombre
(defun gc:sinh (x)
  (/ (- (exp x) (exp (- x))) 2.)
)

;; gc:tanh
;; Retourne la tangente hyperbolique du nombre
;;
;; Argument
;; x : un nombre
(defun gc:tanh (x)
  (/ (- (exp x) (exp (- x))) (+ (exp x) (exp (- x))))
)

;; gc:asinh
;; Retourne l'argument sinus hyperbolique du nombre
;;
;; Argument
;; x : un nombre
(defun gc:asinh	(x)
  (log (+ x (sqrt (+ (* x x) 1.))))
)

;; gc:acosh
;; Retourne l'argument cosinus hyperbolique du nombre
;;
;; Argument
;; x : un nombre compris supérieur ou égal à 1.0
(defun gc:acosh	(x)
  (if (<= 1. x)
    (log (+ x (sqrt (- (* x x) 1.))))
  )
)

;; gc:acosh
;; Retourne l'argument tangente hyperbolique du nombre
;;
;; Argument
;; x : un nombre strictement compris entre -1.0 et 1.0
(defun gc:atanh	(x)
  (if (< -1. x 1.)
    (/ (log (/ (+ 1. x) (- 1. x))) 2.)
  )
)

;;-----------------------------------------------;;
;;------------------ TRIANGLES ------------------;;
;;-----------------------------------------------;;

;; gc:Normal3Pts
;; Retourne le vecteur normal du plan défini par p1 p2 p3
;;
;; Arguments
;; p1, p2, p3 trois points 3d figurant un triangle dans l'espace
(defun gc:Normal3Pts (p1 p2 p3)
  (list
    (- (* (- (cadr p2) (cadr p1)) (- (caddr p3) (caddr p1)))
       (* (- (caddr p2) (caddr p1)) (- (cadr p3) (cadr p1)))
    )
    (- (* (- (caddr p2) (caddr p1)) (- (car p3) (car p1)))
       (* (- (car p2) (car p1)) (- (caddr p3) (caddr p1)))
    )
    (- (* (- (car p2) (car p1)) (- (cadr p3) (cadr p1)))
       (* (- (cadr p2) (cadr p1)) (- (car p3) (car p1)))
    )
  )
)

;; gc:Clockwise
;; Evalue si les points p1 p2 et p3 tournent dans le sens horaire
;;
;; Arguments
;; p1, p2, p3 trois points 2d figurant un triangle dans le plan XY
(defun gc:Clockwise (p1 p2 p3)
  (<
    (- (* (- (car p2) (car p1)) (- (cadr p3) (cadr p2)))
       (* (- (cadr p2) (cadr p1)) (- (car p3) (car p2)))
    )
    1e-12
  )
)

;; gc:Angle3Pts
;; Retourne l'angle défini par son sommet (p0) et deux points (p1 et p2)
;; L'angle retourné est toujours positif et inférieur à pi radians.
;;
;; Arguments
;; p0 : le point au sommet de l'angle
;; p1 : un point délimitant le secteur angulaire
;; p2 : un point délimitant le secteur angulaire
(defun gc:Angle3Pts (p0 p1 p2)
  ((lambda (v1 v2)
     (gc:acos (/ (gc:DotProduct v1 v2)
		 (* (gc:VecLength v1) (gc:VecLength v2))
	      )
     )
   )
    (mapcar '- p1 p0)
    (mapcar '- p2 p0)
  )
)

;; gc:Inscribe
;; Retourne le centre, le rayon et la normale du cercle inscrit dans le triangle p1 p2 p3
;;
;; Arguments
;; p1, p3, p3 : 3 points décrivant un triangle dans l'espace
(defun gc:Inscribe (p1 p2 p3 / v1 v2 n c)
  (setq	v1 (gc:GetNormal (mapcar '- p2 p1))
	v2 (gc:GetNormal (mapcar '- p3 p1))
	n  (gc:GetNormal (gc:CrossProduct v1 v2))
  )
  (list
    (setq c (inters
	      p1
	      (mapcar '+ p1 v1 v2)
	      p2
	      (mapcar '+ p2 v1 (gc:GetNormal (mapcar '- p2 p3)))
	      nil
	    )
    )
    (distance '(0. 0. 0.) (gc:CrossProduct (mapcar '- c p1) v1))
    n
  )
)

;; gc:Circumscribe
;; Retourne le centre, le rayon et la normale du cercle circonscrit au le triangle p1 p2 p3
;;
;; Arguments
;; p1, p3, p3 : 3 points décrivant un triangle dans l'espace
(defun gc:Circumscribe (p1 p2 p3 / v1 v2 n m1 m2 c)
  (setq	v1 (mapcar '- p2 p1)
	v2 (mapcar '- p3 p1)
	n  (gc:CrossProduct v1 v2)
	m1 (gc:MidPoint p1 p2)
	m2 (gc:MidPoint p1 p3)
  )
  (list
    (setq c (inters
	      m1
	      (mapcar '+ m1 (gc:CrossProduct v1 n))
	      m2
	      (mapcar '+ m2 (gc:CrossProduct v2 n))
	      nil
	    )
    )
    (distance c p1)
    (gc:GetNormal n)
  )
)

;; gc:AlgebraicArea
;; Retourne l'aire algébrique (signée) du triangle p1, p2, p3
;;
;; Arguments
;; p1, p3, p3 : 3 points 2d décrivant un triangle dans le plan XY
(defun gc:AlgebraicArea	(p1 p2 p3)
  (/ (-	(* (- (car p2) (car p1))
	   (- (cadr p3) (cadr p1))
	)
	(* (- (car p3) (car p1))
	   (- (cadr p2) (cadr p1))
	)
     )
     2.0
  )
)

;;------------------------------------------------;;
;;------------------- VECTEURS -------------------;;
;;------------------------------------------------;;

;; gc:GetVector
;; Retourne le vecteur de p1 à p2
;;
;; Arguments
;; p1, p2 : 2 points
(defun gc:GetVector (p1 p2) (mapcar '- p2 p1))

;; gc:VecLength
;; retourne la norme (longueur) du vecteur
;;
;; Argument
;; v : un vecteur
(defun gc:VecLength (v) (distance '(0. 0. 0.) v))

;; gc:ScaleVector
;; Multiplie le vecteur par un scalaire
;;
;; Arguments
;; v : un vecteur
;; s : un nombre
(defun gc:ScaleVector (v s)
  (mapcar (function (lambda (x) (* x s))) v)
)

;; gc:DotProduct
;; Retourne le produit scalaire de deux vecteurs
;; Arguments
;; v1, v2 : deux vecteurs
(defun gc:DotProduct (v1 v2) (apply '+ (mapcar '* v1 v2)))

;; gc:CrossProduct
;; Retourne le produit vectoriel (vecteur) de deux vecteurs
;; Arguments
;; v1, v2 : deux vecteurs
(defun gc:CrossProduct (v1 v2)
  (list	(- (* (cadr v1) (caddr v2)) (* (caddr v1) (cadr v2)))
	(- (* (caddr v1) (car v2)) (* (car v1) (caddr v2)))
	(- (* (car v1) (cadr v2)) (* (cadr v1) (car v2)))
  )
)

;; gc:GetNormal
;; Retourne le vecteur unitaire d'un vecteur
;;
;; Argument
;; v : un vecteur
(defun gc:GetNormal (v / l)
  (if (/= 0. (setq l (gc:VecLength v)))
    (gc:ScaleVector v (/ 1. l))
  )
)

;; gc:GetUnitVector
;; Retourne le vecteur unitaire de sens p1 p2
;;
;; Arguments
;; p1, p2 : 2 points
(defun gc:GetUnitVector	(p1 p2)
  ((lambda (d)
     (if (not (zerop d))
       (mapcar (function (lambda (x1 x2) (/ (- x2 x1) d))) p1 p2)
     )
   )
    (distance p1 p2)
  )
)

;; gc:Rotate3d
;; Retourne le point après rotation sur l'axe défini par p1 p2
;;
;; Arguments
;; pt : le point devant subir la rotation
;; p1 : l'origine de l'axe de rotation
;; p2 : un point sur l'axe de rotation
;; ang : l'angle en radians
(defun gc:Rotate3d (pt p1 p2 ang)
  ((lambda (v)
     (mapcar '+
	     p1
	     (trans
	       (mxv
		 (list (list (cos ang) (- (sin ang)) 0.)
		       (list (sin ang) (cos ang) 0.)
		       '(0. 0. 1.)
		 )
		 (trans (mapcar '- pt p1) 0 v)
	       )
	       v
	       0
	     )
     )
   )
    (gc:GetVector p1 p2)
  )
)

;; gc:Rotate
;; Retourne le vecteur après rotation sur l'axe défini par le vecteur axis
;;
;; Arguments
;; vec : le vecteur devant subir la rotation
;; axis : l'axe de rotation (vecteur)
;; ang : l'angle en radians
(defun gc:rotate (vec axis ang)
  (trans
    (mxv
      (list (list (cos ang) (- (sin ang)) 0.)
	    (list (sin ang) (cos ang) 0.)
	    '(0. 0. 1.)
      )
      (trans vec 0 axis)
    )
    axis
    0
  )
)

;; gc:MirrorVector
;; retourne le vecteur après un miroir suivant le plan dont axis est la normale
;;
;; Arguments
;; vec : le vecteur devant subir la rotation
;; axis : le vecteur normal du plan
(defun gc:MirrorVector (vec axis)
  ((lambda (v)
     (trans (list (car v) (cadr v) (- (caddr v))) axis 0)
   )
    (trans vec 0 axis)
  )
)

;; gc:ColinearP
;; Evalue si tous les points de la liste sont colinéiares
;;
;; Arguments
;; pts : une liste de points
(defun gc:ColinearP (pts / p0)
  (setq p0 (car pts))
  (vl-every
    (function
      (lambda (p1 p2)
	(equal
	  (gc:CrossProduct (gc:GetVector p0 p1) (gc:GetVector p0 p2))
	  '(0. 0. 0.)
	  1e-9
	)
      )
    )
    (cdr pts)
    (cddr pts)
  )
)

;; gc:Parallelp
;; Evalue si les segments p1 p2 et p3 p4 sont parallèles
;;
;; Arguments
;; p1 : un point sur le premier segment
;; p2 : un autre point sur le premier segment
;; p3 : un point sur le second segment
;; p4 : un autre point sur le second segment
(defun gc:Parallelp (p1 p2 p3 p4)
  (equal '(0. 0. 0.)
	 (gc:CrossProduct (gc:GetVector p1 p2) (gc:GetVector p3 p4))
	 1e-9
  )
)

;; gc:Penpendicularp
;; Evalue si les segments p1 p2 et p3 p4 sont perpendiculaires
;;
;; Arguments
;; p1 : un point sur le premier segment
;; p2 : un autre point sur le premier segment
;; p3 : un point sur le second segment
;; p4 : un autre point sur le second segment
(defun gc:Penpendicularp (p1 p2 p3 p4)
  (equal (gc:DotProduct (gc:GetVector p1 p2) (gc:GetVector p3 p4))
	 0
	 1e-9
  )
)

;; gc:Coplanarp
;; Evalue si tous les points de la liste sont coplanaires
;;
;; Arguments
;; pts : une liste de points
(defun gc:Coplanarp (pts / norm zlst)
  (or
    (null (cdddr pts))
    (and
      (setq norm (gc:Normal3Pts (car pts) (cadr pts) (caddr pts))
	    zlst (mapcar (function (lambda (p) (caddr (trans p 0 norm))))
			 pts
		 )
      )
      (vl-every	(function (lambda (z) (equal z (car zlst) 1e-9)))
		(cdr zlst)
      )
    )
  )
)

;; gc:elevation
;; Retourne l'élévation du point par rapport au plan
;;
;; Arguments
;; pt : le point dont on cherche l'élévation
;; norm : la normale du plan
;; org : un point sur le plan
(defun gc:elevation (pt norm org)
  (- (caddr (trans pt 0 norm)) (caddr (trans org 0 norm)))
)

;; gc:ProjectOnLine
;; Retourne la projection de pt sur la droite p1 p2
;;
;; Arguments
;; pt : le point à projeter
;; p1 : un point sur la droite
;; p2 : un point sur la droite
(defun gc:ProjectOnLine (pt p1 p2)
  ((lambda (u v)
     (mapcar '+ p1 (gc:ScaleVector u (gc:DotProduct u v)))
   )
    (gc:GetUnitVector p1 p2)
    (gc:GetVector p1 pt)
  )
)

;; gc:ProjectOnPlane
;; Retourne la projection de pt sur le plan
;;
;; Arguments
;; pt : le point à projeter
;; norm : la normale du plan
;; org : un point sur le plan
(defun gc:ProjectOnPlane (pt norm org)
  ((lambda (p o)
     (trans (list (car p) (cadr p) (caddr o)) norm 0)
   )
    (trans pt 0 norm)
    (trans org 0 norm)
  )
)

;; gc:IntersLinePlane
;; Retourne le point d'intersection de la droite définie par p1 p2
;; avec le plan défini pas un point et sa normale
;;
;; Arguments
;; p1 : un point sur la droite
;; p2 : un autre point sur la droite
;; norm : la normale du plan de projection
;; org : un point sur le plan de projection
;; onSeg : si T, le point d'intersection doit être sur le segment p1, p2
;;         si nil, le segment est prolongé
(defun gc:IntersLinePlane (p1 p2 norm org onSeg / scl)
  (if
    (and
      (/= 0. (setq scl (gc:DotProduct norm (gc:GetVector p1 p2))))
      (or
	(<= 0.
	    (setq scl (/ (gc:DotProduct norm (gc:GetVector p1 org)) scl))
	    1.
	)
	(not onSeg)
      )
    )
     (mapcar '+ p1 (gc:ScaleVector (gc:GetVector p1 p2) scl))
  )
)

;; gc:GetPointAboutPlane
;; Retourne le point d'intersection de la perpendiculaire à la vue courante passant
;; par le point saisi par l'utilsateur et le plan défini par sa normale et un point.
;;
;; Arguments
;; nor : la normale du plan de projection
;; org : un point sur le plan de projection
;; msg : le message affiché pour la saisie du point
(defun gc:GetPointAboutPlane (nor org msg / p1 p2 sc)
  (if (and (setq p1 (getpoint msg))
	   (setq p1 (trans p1 1 0)
		 p2 (trans p1 0 2)
		 p2 (trans (list (car p2) (cadr p2) (1+ (caddr p2))) 2 0)
	   )
	   (/= 0
	       (setq sc (apply '+ (mapcar '* nor (gc:GetVector p1 p2))))
	   )
      )
    (mapcar
      (function
	(lambda	(x1 x2)
	  (+ (*	(/ (apply '+ (mapcar '* nor (gc:GetVector org p1))) sc)
		(- x1 x2)
	     )
	     x1
	  )
	)
      )
      p1
      p2
    )
  )
)

;; gc:GreatestSlope
;; Retourne le vecteur de plus grande pente d'un plan dont n est la normale
;;
;; Argument
;; n : la normale du plan
(defun gc:GreatestSlope	(n)
  (gc:GetNormal
    (gc:CrossProduct (list (- (cadr n)) (car n) 0.) n)
  )
)

;; gc:SlopePercent
;; Retourne l'expression en pourcentage de la pente d'un plan dont n est la normale
;;
;; Argument
;; n : la normale du plan
(defun gc:SlopePercent (n)
  (if (= 0. (caddr n))
    1e99
    (abs
      (/
	(* 100 (sqrt (+ (* (car n) (car n)) (* (cadr n) (cadr n)))))
	(caddr n)
      )
    )
  )
)

;;------------------------------------------------;;
;;------------------- MATRICES -------------------;;
;;------------------------------------------------;;

;; TRP
;; Transpose une matrice -Doug Wilson-
;;
;; Argument
;; m : une matrice
(defun trp (m) (apply 'mapcar (cons 'list m)))

;; MXV
;; Applique une matrice de transformation à un vecteur -Vladimir Nesterovsky-
;;
;; Arguments-
;; m : une matrice
;; v : un vecteur
(defun mxv (m v)
  (mapcar (function (lambda (r) (apply '+ (mapcar '* r v))))
	  m
  )
)

;; MXM
;; Multiplie (combine) deux matrices -Vladimir Nesterovsky-
;;
;; Arguments
;; m : une matrice
;; v : une matrice
(defun mxm (m q)
  (mapcar (function (lambda (r) (mxv (trp q) r))) m)
)

;; gc:SquareP
;; Evalue si une matrice est carrée
;;
;; Argument
;; m : une matrice
(defun gc:SquareP (m)
  (vl-every (function (lambda (v) (= (length v) (length m))))
	    m
  )
)

;; gc:UniformP
;; Evalue si une matrice de transformation (3X3 ou 4X4) a un échelle uniforme
;;
;; Argument
;; m : une matrice
(defun gc:UniformP (m)
  (and (or (= 3 (length m)) (setq m (mapcar 'butlast (butlast m))))
       (vl-every
	 (function
	   (lambda (v)
	     (equal (distance '(0. 0. 0.) (car m))
		    (distance '(0. 0. 0.) v)
		    1e-12
	     )
	   )
	 )
	 m
       )
  )
)

;; gc:TmatrixValid
;; Evalue si une matrice est valide pour une utilisation avec vlax-tmatrix
;;
;; Argument
;; m : une matrice
(defun gc:TmatrixValid (m)
  (and (= 4 (setq l (length m)))
       (gc:SquareP m)
       (gc:UniformP m)
  )
)

;; gc:Indentity
;; Crée une matrice d'identité de dimension n
;;
;; Argument
;; d : la dimension de la matrice
(defun gc:Indentity (d / i n r m)
  (setq i d)
  (while (<= 0 (setq i (1- i)))
    (setq n d
	  r nil
    )
    (while (<= 0 (setq n (1- n)))
      (setq r (cons (if	(= i n)
		      1.
		      0.
		    )
		    r
	      )
      )
    )
    (setq m (cons r m))
  )
)

;; gc:IsOrtho
;; Évalue si la matrice est orthogonale
;;
;; Argument
;; mat : une matrice
(defun gc:IsOrtho (mat)
  (equal (mxm (trp mat) mat)
	 (gc:Indentity (length mat))
	 1e-14
  )
)

;; gc:Inv3x3
;; Retourne la matrice de transformation (3X3) inverse
;;
;; Argument
;; mat : une matrice 3x3
(defun gc:Inv3x3 (mat / a b c d e f g h i det)
  (mapcar 'set
	  '(a b c d e f g h i)
	  (mapcar 'float (apply 'append mat))
  )
  (setq	det (+ (* a e i)
	       (* b f g)
	       (* c d h)
	       (- (* c e g))
	       (- (* b d i))
	       (- (* a f h))
	    )
  )
  (if (and (/= 0 det) (setq det (/ 1 det)))
    (mapcar
      '(lambda (v)
	 (mapcar '(lambda (x) (* x det)) v)
       )
      (list
	(list (- (* e i) (* f h))
	      (- (* c h) (* b i))
	      (- (* b f) (* c e))
	)
	(list (- (* f g) (* d i))
	      (- (* a i) (* c g))
	      (- (* c d) (* a f))
	)
	(list (- (* d h) (* e g))
	      (- (* b g) (* a h))
	      (- (* a e) (* b d))
	)
      )
    )
  )
)

;; gc:GaussJordan
;; Applique la méthode de Gauss-Jordan à deux matrices
;;
;; Arguments
;; m1 : une matrice
;; m2 : une matrice
(defun gc:GaussJordan (m1 m2 / len mat todo cnt row col piv new)
  (setq len (length m1))
  (if (= len (length m2))
    (progn
      (setq mat	 (mapcar (function (lambda (x1 x2) (append x1 x2))) m1 m2)
	    todo mat
	    cnt	 0
      )
      (while todo
	(setq row (nth cnt mat)
	      col (mapcar (function (lambda (x) (abs (car x)))) todo)
	)
	(repeat	(vl-position (apply 'max col) col)
	  (setq	mat (append (vl-remove row mat) (list row))
		row (nth cnt mat)
	  )
	)
	(if (equal (setq piv (car row)) 0. 1e-14)
	  (setq	mat  nil
		todo nil
	  )
	  (setq	piv  (/ 1.0 piv)
		new  (mapcar (function (lambda (x) (* x piv))) row)
		mat  (mapcar
		       (function
			 (lambda (r / e)
			   (setq e (car r))
			   (if (equal r row)
			     (cdr new)
			     (cdr (mapcar
				    (function (lambda (x n) (- x (* n e))))
				    r
				    new
				  )
			     )
			   )
			 )
		       )
		       mat
		     )
		todo mat
		cnt  (1+ cnt)
	  )
	)
	(and todo (repeat cnt (setq todo (cdr todo))))
      )
      mat
    )
  )
)

;; gc:Inverse
;; Inverse une matrice carrée (méthode Gauss-Jordan)
;;
;; Argument
;; mat : une matrice
(defun gc:Inverse (mat / col piv row res)
  (setq	mat (mapcar '(lambda (x1 x2) (append x1 x2))
		    mat
		    (gc:Indentity (length mat))
	    )
  )
  (while mat
    (setq col (mapcar '(lambda (x) (abs (car x))) mat))
    (repeat (vl-position (apply 'max col) col)
      (setq mat (append (cdr mat) (list (car mat))))
    )
    (if	(equal (setq piv (caar mat)) 0. 1e-14)
      (setq mat	nil
	    res	nil
      )
      (setq piv	(/ 1.0 piv)
	    row	(mapcar '(lambda (x) (* x piv)) (car mat))
	    mat	(mapcar
		  '(lambda (r / e)
		     (setq e (car r))
		     (cdr (mapcar '(lambda (x n) (- x (* n e))) r row))
		   )
		  (cdr mat)
		)
	    res	(cons
		  (cdr row)
		  (mapcar
		    '(lambda (r / e)
		       (setq e (car r))
		       (cdr (mapcar '(lambda (x n) (- x (* n e))) r row))
		     )
		    res
		  )
		)
      )
    )
  )
  (reverse res)
)

;; gc:Cofactor
;; Retourne le cofacteur associé à l'élément (i,j) d'une matrice (m)
;;
;; Arguments
;; i : index de rangée
;; j : index de colonne
;; m : une matrice
;;
;; Fonction requise
;; - gc:RemoveAt (gc_List.lsp)
(defun gc:Cofactor (i j m)
  (* (gc:Determ
       (gc:RemoveAt
	 (1- i)
	 (mapcar (function (lambda (x) (gc:RemoveAt (1- j) x))) m)
       )
     )
     (expt -1 (+ i j))
  )
)

;; gc:Determ
;; Retourne le déterminant d'une matrice carré
;;
;; Argument
;; m : une matrice
(defun gc:Determ (m)
  (if (= 2 (length m))
    (- (* (caar m) (cadadr m)) (* (caadr m) (cadar m)))
    ((lambda (r n)
       (apply '+
	      (mapcar
		(function
		  (lambda (x) (* x (gc:Cofactor 1 (setq n (1+ n)) m)))
		)
		r
	      )
       )
     )
      (car m)
      0
    )
  )
)

;; gc:AdjMat
;; Retourne la matrice adjointe d'une matrice
;;
;; Argument
;; m : une matrice
(defun gc:AdjMat (m / i)
  (setq i 0)
  (trp
    (mapcar
      (function
	(lambda	(v / j)
	  (setq	i (1+ i)
		j 0
	  )
	  (mapcar
	    (function (lambda (x) (gc:Cofactor i (setq j (1+ j)) m)))
	    v
	  )
	)
      )
      m
    )
  )
)

;; gc:InvMat
;; Retourne la matrice inverse d'une matrice
;;
;; Argument
;; m : une matrice
(defun gc:InvMat (m / d)
  (if (/= 0 (setq d (determ m)))
    (mxs (adj-mat m) (/ 1.0 d))
  )
)

;; gc:TransformBy
;; Applique la matrice de transformation (4x4) au point
;;
;; Arguments
;; pt : un point
;; mat : une matrice 4x4
(defun gc:TransformBy (pt mat)
  ((lambda (m d)
     (mapcar '+ (mxv m pt) d)
   )
    (list
      (list (caar mat) (cadar mat) (caddar mat))
      (list (caadr mat) (cadadr mat) (caddr (cadr mat)))
      (list (caaddr mat) (cadr (caddr mat)) (caddr (caddr mat)))
    )
    (list (cadddr (car mat))
	  (cadddr (cadr mat))
	  (cadddr (caddr mat))
    )
  )
)

;; gc:TMatrixFromTo
;; Retourne la matrice de transformation (4x4) d'un système de coordonnées
;; vers un autre (mêmes types d'arguments que trans)
;;
;; Arguments
;; from : système de coordonnées de départ (entier, vecteur ou ename)
;; to : système de coordonnées de destination (entier, vecteur ou ename)
(defun gc:TMatrixFromTo	(from to)
  (append
    (mapcar
      (function
	(lambda	(v o)
	  (append (trans v from to T) (list o))
	)
      )
      '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
      (trans '(0. 0. 0.) to from)
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:ProjectionMatrix
;; Retourne la matrice de transformation de la projection sur le plan
;; défini par origin et normal suivant la direction du vecteur projectDir
;;
;; Arguments
;; origin : un point sur le plan de projection
;; normal : la normale du plan de projection
;; projectDir : le vecteur décrivant la direction de projection
(defun gc:ProjectionMatrix (origin normal projectDir / scl mat)
  (if (/= (setq scl (gc:DotProduct normal projectDir)) 0.)
    (append
      (mapcar
	(function (lambda (v x) (append v (list x))))
	(setq mat
	       (mapcar
		 (function (lambda (v1 v2) (mapcar '- v1 v2)))
		 '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
		 (mapcar
		   (function (lambda (s) (gc:ScaleVector normal s)))
		   (gc:ScaleVector projectDir (/ 1. scl))
		 )
	       )
	)
	(mapcar '- origin (mxv mat origin))
      )
      '((0. 0. 0. 1.))
    )
  )
)

;; gc:ScaleMatrix
;; Retourne un matrice (4x4) de mise à l'échelle
;;
;; Arguments
;; base : le point de base
;; scl : le facteur d'échelle
(defun gc:ScaleMatrix (base scl)
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append (mapcar '(lambda (x) (* x scl)) v1)
		  (list v2)
	  )
	)
      )
      '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
      (mapcar '(lambda (x) (- x (* x scl))) base)
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:MoveMatrix
;; Retourne un matrice (4x4) de déplacement
;;
;; Argument
;; dep : le vecteur décrivant le déplacement
(defun gc:MoveMatrix (dep)
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append v1 (list v2))
	)
      )
      '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
      dep
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:2dRotationMatrix
;; Retourne un matrice (4x4) de rotation sur l'axe Z
;;
;; Arguments
;; base : le point de base
;; ang : l'angle en radians
(defun gc:2dRotationMatrix (base ang / mat)
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append v1 (list v2))
	)
      )
      (setq mat	(list (list (cos ang) (- (sin ang)) 0.)
		      (list (sin ang) (cos ang) 0.)
		      '(0. 0. 1.)
		)
      )
      (mapcar '- base (mxv mat base))
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:3dRotationMatrix
;; Retourne un matrice (4x4) de rotation suivant un axe
;;
;; Arguments
;; org : origine de l'axe
;; axis : vecteur directeur de l'axe
;; ang : l'angle en radians

(defun gc:3dRotationMatrix (org axis ang)
  (mxm
    (gc:TMatrixFromTo 0 axis)
    (mxm
      (gc:2dRotationMatrix (trans org 0 axis) ang)
      (gc:TMatrixFromTo axis 0)
    )
  )
)

;; gc:XRotateMatrix
;; Retourne un matrice (4x4) de rotation sur l'axe X
;;
;; Arguments
;; base : le point de base
;; ang : l'angle en radians
(defun gc:XRotateMatrix	(base ang / mat)
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append v1 (list v2))
	)
      )
      (setq mat	(list '(1. 0. 0.)
		      (list 0. (cos ang) (- (sin ang)))
		      (list 0. (sin ang) (cos ang))
		)
      )
      (mapcar '- base (mxv mat base))
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:YRotateMatrix
;; Retourne un matrice (4x4) de rotation sur l'axe Y
;;
;; Arguments
;; base : le point de base
;; ang : l'angle en radians
(defun gc:YRotateMatrix	(base ang / mat)
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append v1 (list v2))
	)
      )
      (setq mat	(list (list (cos ang) 0 (sin ang))
		      '(0. 1. 0.)
		      (list (- (sin ang)) 0 (cos ang))
		)
      )
      (mapcar '- base (mxv mat base))
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:WCS2PCS
;; Traduit les coordonnées d'un point du SCG dans le SC de l'espace
;; papier correspondant à la fenêtre spécifiée
;; (WCS2PCS pt vp) est équivalent à (trans (trans pt 0 2) 2 3) avec vp active
;;
;; Arguments
;; pt : un point
;; vp : la fenêtre (ename ou vla-object)
(defun gc:WCS2PCS (pt vp / elst ang nor scl mat)
  (vl-load-com)
  (and (= (type vp) 'VLA-OBJECT)
       (setq vp (vlax-vla-object->ename vp))
  )
  (setq	pt   (trans pt 0 0)
	elst (entget vp)
	ang  (cdr (assoc 51 elst))
	nor  (cdr (assoc 16 elst))
	scl  (/ (cdr (assoc 41 elst)) (cdr (assoc 45 elst)))
	mat  (mxm
	       (list (list (cos ang) (- (sin ang)) 0.)
		     (list (sin ang) (cos ang) 0.)
		     '(0. 0. 1.)
	       )
	       (mapcar (function (lambda (v) (trans v nor 0 T)))
		       '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
	       )
	     )
  )
  (mapcar '+
	  (vxs (mxv mat (mapcar '- pt (cdr (assoc 17 elst)))) scl)
	  (vxs (cdr (assoc 12 elst)) (- scl))
	  (cdr (assoc 10 elst))
  )
)

;; gc:PCS2WCS
;; Traduit les coordonnées d'un point de l'espace papier dans le
;; SCG correspondant à la fenêtre spécifiée
;; (PCS2WCS pt vp) est équivalent à (trans (trans pt 3 2) 2 0) avec vp active
;;
;; Arguments
;; pt : un point
;; vp : la fenêtre (ename ou vla-object)
(defun gc:PCS2WCS (pt vp / ang nor scl mat)
  (vl-load-com)
  (and (= (type vp) 'VLA-OBJECT)
       (setq vp (vlax-vla-object->ename vp))
  )
  (setq	pt   (trans pt 0 0)
	elst (entget vp)
	ang  (- (cdr (assoc 51 elst)))
	nor  (cdr (assoc 16 elst))
	scl  (/ (cdr (assoc 45 elst)) (cdr (assoc 41 elst)))
	mat  (mxm
	       (mapcar (function (lambda (v) (trans v 0 nor T)))
		       '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
	       )
	       (list (list (cos ang) (- (sin ang)) 0.)
		     (list (sin ang) (cos ang) 0.)
		     '(0. 0. 1.)
	       )
	     )
  )
  (mapcar '+
	  (mxv mat
	       (mapcar '+
		       (vxs pt scl)
		       (vxs (cdr (assoc 10 elst)) (- scl))
		       (cdr (assoc 12 elst))
	       )
	  )
	  (cdr (assoc 17 elst))
  )
)

;; gc:RCS2WCS
;; Traduit les coordonnées du Système de Coordonnées Reference (bloc ou xref) vers le SCG
;;
;; Arguments :
;; pt : un point dans le RCS
;; mat : une matrice de transformation, retournée par (caddr (nentsel)) ou (caddr (nentselp))
(defun gc:RCS2WCS (pt mat)
  (setq pt (trans pt 0 0))
  (if (= 3 (length (car mat)))
    (mapcar '+ (mxv (trp (gc:butlast mat)) pt) (last mat))
    (mapcar '+
	    (mxv (mapcar 'gc:butlast (gc:butlast mat)) pt)
	    (gc:butlast (mapcar 'last mat))
    )
  )
)

;; gc:WCS2RCS
;; Traduit les coordonnées du SCG vers le Système de Coordonnées Reference (bloc ou xref)
;;
;; Arguments :
;; pt : un point dans le SCG
;; mat : une matrice de transformation, retournée par (caddr (nentsel)) ou (caddr (nentselp))
(defun gc:WCS2RCS (pt mat)
  (setq pt (trans pt 0 0))
  (if (= 3 (length (car mat)))
    (setq mat (append (trp mat) (list '(0. 0. 0. 1.))))
  )
  (setq mat (inversematrix mat))
  (mapcar '+ (mxv mat pt) (gc:butlast (mapcar 'last mat)))
)

;; gc:BlockTransform
;; Retourne la matrice de transformation d'une référence de bloc.
;; Matrice 4x4 telle que renvoyée par nentsel.
;;
;; Argument
;; ename : lenom d'entité de la référence de bloc
(defun gc:BlockTransform (ename / elst ang norm)
  (setq	elst (entget ename)
	ang  (cdr (assoc 50 elst))
	norm (cdr (assoc 210 elst))
  )
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append v1 (list v2))
	)
      )
      (setq mat
	     (mxm
	       (mapcar (function (lambda (v) (trans v 0 norm T)))
		       '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
	       )
	       (mxm
		 (list (list (cos ang) (- (sin ang)) 0.)
		       (list (sin ang) (cos ang) 0.)
		       '(0. 0. 1.)
		 )
		 (list (list (cdr (assoc 41 elst)) 0. 0.)
		       (list 0. (cdr (assoc 42 elst)) 0.)
		       (list 0. 0. (cdr (assoc 43 elst)))
		 )
	       )
	     )
      )
      (mapcar
	'-
	(trans (cdr (assoc 10 elst)) norm 0)
	(mxv mat
	     (cdr (assoc 10 (tblsearch "BLOCK" (cdr (assoc 2 elst)))))
	)
      )
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:BlockTransformInverse
;; Retourne la matrice inverse de celle retournée par gc:BlockTransform
;;
;; Argument
;; ename : le nom d'entité
(defun gc:BlockTransformInverse (ename / elst ang norm mat)
  (setq	elst (entget ename)
	ang  (- (cdr (assoc 50 elst)))
	norm (cdr (assoc 210 elst))
  )
  (append
    (mapcar
      (function
	(lambda	(v1 v2)
	  (append v1 (list v2))
	)
      )
      (setq mat
	     (mxm
	       (list (list (/ 1. (cdr (assoc 41 elst))) 0. 0.)
		     (list 0. (/ 1. (cdr (assoc 42 elst))) 0.)
		     (list 0. 0. (/ 1. (cdr (assoc 43 elst))))
	       )
	       (mxm
		 (list (list (cos ang) (- (sin ang)) 0.)
		       (list (sin ang) (cos ang) 0.)
		       '(0. 0. 1.)
		 )
		 (mapcar (function (lambda (v) (trans v norm 0 T)))
			 '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
		 )
	       )
	     )
      )
      (mapcar
	'-
	(cdr (assoc 10 (tblsearch "BLOCK" (cdr (assoc 2 elst)))))
	(mxv mat (trans (cdr (assoc 10 elst)) norm 0))
      )
    )
    '((0. 0. 0. 1.))
  )
)

;; gc:TransNested
;; Convertit les coordonnées d'un point entre le SCG ou le SCU  et le SCR -systéme de
;; coordonées d'une référence (xref ou bloc) quelque soit son niveau d'imbrication-
;;
;; Arguments
;; pt : le point à convertir
;; rlst : la liste des entités "parents" de la plus imbriqué à celle insérée dans
;;        l'espace courant -indentique à (last (nentsel)) ou (last (nentselp))
;; from to : comme avec trans : 0 pour le SCG, 1 pour le SCU courant, 2 pour le SCR
(defun gc:TransNested (pt rlst from to)
  (and (= 1 from) (setq pt (trans pt 1 0)))
  (and (= 2 to) (setq rlst (reverse rlst)))
  (and (or (= 2 from) (= 2 to))
       (while rlst
	 (setq geom (if	(= 2 to)
		      (gc:RevRefGeom (car rlst))
		      (gc:RefGeom (car rlst))
		    )
	       rlst (cdr rlst)
	       pt   (mapcar '+ (mxv (car geom) pt) (cadr geom))
	 )
       )
  )
  (if (= 1 to)
    (trans pt 0 1)
    pt
  )
)

;; gc:RefGeom
;; Retourne une liste dont le premier élément est une matrice de transformation
;; (rotation, échelles, normale) de dimension 3X3 et le second le point
;; d'insertion de l'objet dans son "parent" (xref, bloc ou espace)
;;
;; Argument
;; ename : le nom d'entité
(defun gc:RefGeom (ename / elst ang norm mat)
  (setq	elst (entget ename)
	ang  (cdr (assoc 50 elst))
	norm (cdr (assoc 210 elst))
  )
  (list
    (setq mat
	   (mxm
	     (mapcar (function (lambda (v) (trans v 0 norm T)))
		     '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
	     )
	     (mxm
	       (list (list (cos ang) (- (sin ang)) 0.)
		     (list (sin ang) (cos ang) 0.)
		     '(0. 0. 1.)
	       )
	       (list (list (cdr (assoc 41 elst)) 0. 0.)
		     (list 0. (cdr (assoc 42 elst)) 0.)
		     (list 0. 0. (cdr (assoc 43 elst)))
	       )
	     )
	   )
    )
    (mapcar
      '-
      (trans (cdr (assoc 10 elst)) norm 0)
      (mxv mat
	   (cdr (assoc 10 (tblsearch "BLOCK" (cdr (assoc 2 elst)))))
      )
    )
  )
)

;; gc:RevRefGeom
;; Fonction inverse de RefGeom
;;
;; Argument
;; ename : le nom d'entité
(defun gc:RevRefGeom (ename / elst ang norm mat)
  (setq	elst (entget ename)
	ang  (- (cdr (assoc 50 elst)))
	norm (cdr (assoc 210 elst))
  )
  (list
    (setq mat
	   (mxm
	     (list (list (/ 1 (cdr (assoc 41 elst))) 0. 0.)
		   (list 0. (/ 1 (cdr (assoc 42 elst))) 0.)
		   (list 0. 0. (/ 1 (cdr (assoc 43 elst))))
	     )
	     (mxm
	       (list (list (cos ang) (- (sin ang)) 0.)
		     (list (sin ang) (cos ang) 0.)
		     '(0. 0. 1.)
	       )
	       (mapcar (function (lambda (v) (trans v norm 0 T)))
		       '((1. 0. 0.) (0. 1. 0.) (0. 0. 1.))
	       )
	     )
	   )
    )
    (mapcar '-
	    (cdr (assoc 10 (tblsearch "BLOCK" (cdr (assoc 2 elst)))))
	    (mxv mat (trans (cdr (assoc 10 elst)) norm 0))
    )
  )
)

;; gc:GetTMatrix
;; Retourne une matrice de transformation (4X4) identique à celle retournée par nentselp
;;
;; Argument
;; lst : la liste des entités "parents" de la plus imbriqué à celle insérée dans
;;       l'espace courant -indentique à (last (nentsel)) ou (last (nentselp))
(defun gc:GetTMatrix (lst / mat pt geom)
  (setq	mat (gc:Indentity 3)
	pt  '(0. 0. 0.)
  )
  (while lst
    (setq geom (gc:refgeom (car lst))
	  mat  (mxm (car geom) mat)
	  pt   (mapcar '+ (mxv (car geom) pt) (cadr geom))
	  lst  (cdr lst)
    )
  )
  (append
    (mapcar '(lambda (v x) (append v (list x))) mat pt)
    (list '(0. 0. 0. 1.))
  )
)

;; gc:UcsBoundingBox
;; Retourne les coordonnées SCU de l'emprise (bounding box) de l'entité
;; par rapport au SCU courant.
;;
;; Arguments
;; obj: une entité (ENAME ou VLA-OBJCET)
;; _OutputMinPtSym: un symbole quoté (output)
;; _OutputMaxPtSym: un symbole quoté (output)

(defun gc:UcsBoundingBox (obj _OutputMinPtSym _OutputMaxPtSym)
  (vl-load-com)
  (and (= (type obj) 'ENAME)
       (setq obj (vlax-ename->vla-object obj))
  )
  (vla-TransformBy obj (vlax-tmatrix (gc:TMatrixFromTo 1 0)))
  (vla-GetBoundingBox obj _OutputMinPtSym _OutputMaxPtSym)
  (vla-TransformBy obj (vlax-tmatrix (gc:TMatrixFromTo 0 1)))
  (set _OutputMinPtSym
       (vlax-safearray->list (eval _OutputMinPtSym))
  )
  (set _OutputMaxPtSym
       (vlax-safearray->list (eval _OutputMaxPtSym))
  )
)

;; gc:SelSetUcsBBox
;; Retourne les coordonnées SCU de l'emprise (bounding box) des entités
;; contenues dans le jeu de sélection, par rapport au SCU courant.
;;
;; Arguments
;; ss: a selection set
;; _OutputMinPtSym: un symbole quoté (output)
;; _OutputMaxPtSym: un symbole quoté (output)

(defun gc:SelSetUcsBBox	(ss _OutputMinPtSym _OutputMaxPtSym / n l1 l2)
  (repeat (setq n (sslength ss))
    (gc:UcsBoundingBox
      (ssname ss (setq n (1- n)))
      _OutputMinPtSym
      _OutputMaxPtSym
    )
    (setq l1 (cons (eval _OutputMinPtSym) l1)
	  l2 (cons (eval _OutputMaxPtSym) l2)
    )
  )
  (set _OutputMinPtSym (apply 'mapcar (cons 'min l1)))
  (set _OutputMaxPtSym (apply 'mapcar (cons 'max l2)))
)