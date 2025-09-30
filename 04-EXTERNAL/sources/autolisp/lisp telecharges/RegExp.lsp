;;--------------------------------------------------------------------------------------------------------;;
;;                                         Expressions Régulières                                         ;;
;;--------------------------------------------------------------------------------------------------------;;
;;                                                                                                        ;;
;; Fonctions LISP pour émuler les propriétés et méthodes du type RegExp de vbscript.                      ;;
;;                                                                                                        ;;
;; Référence                                                                                              ;;
;; http://tahe.developpez.com/tutoriels-cours/vbscript/?page=page_4#LIV-B                                 ;;
;; https://msdn.microsoft.com/en-us/library/1400241x(VS.85).aspx                                          ;;
;;                                                                                                        ;;
;; Gilles Chanteau                                                                                        ;;
;;--------------------------------------------------------------------------------------------------------;;

(vl-load-com)

;; RegExpSet
;; Retourne l'instance de VBScript.RegExp courante après avoir défini ses propriétés.
;;
;; Arguments
;; pattern    : Motif à rechercher.
;; ignoreCase : Si non nil, la recherche est faite sans tenir compte de la casse.
;; global     : Si non nil, recherche toutes les occurrences du modèle ;
;;              si nil, recherche uniquement la première occurrence.

(defun RegExpSet (pattern ignoreCase global / regex)
  (setq regex
         (cond
           ((vl-bb-ref '*regexp*))
           ((vl-bb-set '*regexp* (vlax-create-object "VBScript.RegExp")))
         )
  )
  (vlax-put regex 'Pattern pattern)
  (if ignoreCase
    (vlax-put regex 'IgnoreCase acTrue)
    (vlax-put regex 'IgnoreCase acFalse)
  )
  (if global
    (vlax-put regex 'Global acTrue)
    (vlax-put regex 'Global acFalse)
  )
  regex
)

;; RegExpTest
;; Retourne T si une correspondance avec le motif a été trouvée dans la chaîne ; sinon, nil.
;;
;; Arguments
;; string     : Chaîne dans la quelle on recherche le motif.
;; pattern    : Motif à rechercher.
;; ignoreCase : Si non nil, la recherche est faite sans tenir compte de la casse.
;;
;; Exemples :
;; (RegexpTest "foo bar" "Ba" nil)  ; => nil
;; (RegexpTest "foo bar" "Ba" T)    ; => T
;; (RegExpTest "42C" "[0-9]+" nil)  ; => T

(defun RegExpTest (string pattern ignoreCase)
  (= (vlax-invoke (RegExpSet pattern ignoreCase nil) 'Test string) -1)
)

;; RegExpExecute
;; Retourne la liste des correspondances avec le motif trouvées dans la chaine.
;; Chaque correspondance est renvoyée sous la forme d'une sous-liste contenant :
;; - la valeur de la correspondance,
;; - l'index du premier caractère (base 0)
;; - une liste des sous groupes.
;;
;; Arguments
;; string     : Chaîne dans la quelle on recherche le motif.
;; pattern    : Motif à rechercher.
;; ignoreCase : Si non nil, la recherche est faite sans tenir compte de la casse.
;; global     : Si non nil, recherche toutes les occurrences du modèle ;
;;              si nil, recherche uniquement la première occurrence.
;;
;; Exemples
;; (RegExpExecute "foo bar baz" "ba" nil nil)               ; => (("ba" 4 nil))
;; (RegexpExecute "12B 4bis" "([0-9]+)([A-Z]+)" T T)        ; => (("12B" 0 ("12" "B")) ("4bis" 4 ("4" "bis")))
;; (RegexpExecute "-12 25.4" "(-?\\d+(?:\\.\\d+)?)" nil T)  ; => (("-12" 0 ("-12")) ("25.4" 4 ("25.4")))

(defun RegExpExecute (string pattern ignoreCase global / sublst lst)
  (vlax-for match (vlax-invoke (RegExpSet pattern ignoreCase global) 'Execute string)
    (setq sublst nil)
    (vl-catch-all-apply
      '(lambda ()
	 (vlax-for submatch (vlax-get match 'SubMatches)
	   (if submatch
	     (setq sublst (cons submatch sublst))
	   )
	 )
       )
    )
    (setq lst (cons (list (vlax-get match 'Value)
			  (vlax-get match 'FirstIndex)
			  (reverse sublst)
		    )
		    lst
	      )
    )
  )
  (reverse lst)
)

;; RegExpReplace
;; Retourne la chaîne après remplacement des correspondances avec le motif.
;;
;; Arguments
;; string     : Chaîne dans la quelle on recherche le motif.
;; pattern    : Motif à rechercher.
;; newStr     : Chaîne de remplacement.
;; ignoreCase : Si non nil, la recherche est faite sans tenir compte de la casse.
;; global     : Si non nil, recherche toutes les occurrences du modèle ;
;;              si nil, recherche uniquement la première occurrence.
;;
;; Exemples :
;; (RegExpReplace "foo bar baz" "a" "oo" nil T)                  ; => "foo boor booz"
;; (RegExpReplace "foo bar baz" "(\\w)\\w(\\w)" "$1_$2" nil T)   ; => "f_o b_r b_z"
;; (RegExpReplace "$ 3.25" "\\$ (\\d+(\\.\\d+)?)" "$1 €" nil T)  ; => "3.25 €"

(defun RegExpReplace (string pattern newStr ignoreCase global)
  (vlax-invoke (RegExpSet pattern ignoreCase global) 'Replace string newStr)
)