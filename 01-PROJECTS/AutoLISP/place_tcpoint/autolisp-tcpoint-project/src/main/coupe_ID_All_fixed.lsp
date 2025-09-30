;; COUPE_ID_ALL.lsp — v1.1 (2025-09-08)
;; - Traite toutes les coupes d'un coup
;; - Sélection circulaire autour de A_suffixe (rayon 9.5 m par défaut)
;; - Exclut A_/B_/C_ de la sélection (on ne transfère pas les points de calage)
;; - Conserve les calques d'origine ; ajoute XDATA + GROUP "COUPE_<suffixe>"
;; VERSION CORRIGÉE

(vl-load-com)

;;; ------------------ Helpers génériques ------------------

(defun _is-vla (x) (and x (eq (type x) 'VLA-OBJECT)))
(defun _ename->vla (e) (if (and e (= (type e) 'ENAME)) (vlax-ename->vla-object e)))
(defun _vla->ename (o) (if (_is-vla o) (vlax-vla-object->ename o)))
(defun _safe-str (x) (cond ((null x) "") ((= (type x) 'STR) x) (T (vl-princ-to-string x))))
(defun _lower (s) (vl-string-translate "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" s))
(defun _trim (s) (vl-string-trim " \t\r\n" (_safe-str s)))

(defun _dist (p q)
  (if (and (= (type p) 'LIST) (= (type q) 'LIST))
    (distance p q) 0.0))

(defun _add-appid (appid / doc dict exist)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq dict (vla-get-RegisteredApplications (vla-get-Database doc)))
  (if (not (vl-catch-all-error-p
             (vl-catch-all-apply 'vla-Item (list dict appid))))
    T
    (progn (vla-Add dict appid) T)))

(defun _set-xdata (ename appid key)
  (if (and ename appid key)
    (progn
      (_add-appid appid)
      (regapp appid)
      (entmod (append (entget ename)
                      (list (list -3 (list appid (list 1000 key))))))
      T)))

(defun _make-group (gname enames / doc groups g)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq groups (vla-get-Groups doc))
  (if (not (vl-catch-all-error-p (vl-catch-all-apply 'vla-Item (list groups gname))))
    (progn ;; déjà existe -> on le vide
      (setq g (vla-Item groups gname))
      (vla-RemoveAll g))
    (setq g (vla-Add groups gname)))
  ;; Ajouter les enames
  (foreach e enames
    (if (= (type e) 'ENAME)
      (vla-AppendItem g (vlax-ename->vla-object e))))
  g)

;;; ------------------ Extraction nom A_/B_/C_ ------------------

(defun _block-name (vla)
  (if (_is-vla vla)
    (cond
      ((vlax-property-available-p vla 'EffectiveName) (vla-get-EffectiveName vla))
      ((vlax-property-available-p vla 'Name) (vla-get-Name vla))
      (T ""))
    ""))

(defun _collect-attributes (vla / atts res i att)
  (setq res '())
  (if (and (_is-vla vla)
           (vlax-property-available-p vla 'HasAttributes)
           (vla-get-HasAttributes vla))
    (progn
      (setq atts (vlax-safearray->list (vlax-variant-value (vla-GetAttributes vla))))
      (foreach att atts
        (setq res (cons (cons (_lower (vla-get-TagString att))
                              (_trim (vla-get-TextString att))) res)))
      (reverse res))
    '()))

(defun _extract-ABC-name (vla / atts val candidates)
  ;; Cherche d'abord dans attributs, puis dans nom de bloc
  (setq atts (_collect-attributes vla))
  (setq candidates '("nom" "name" "point" "code" "matricule"))
  (setq val nil)
  
  ;; Chercher dans les attributs
  (foreach k candidates
    (if (not val)
      (setq val (cdr (assoc k atts)))))
  
  ;; Si pas trouvé dans attributs, utiliser nom de bloc
  (if (or (null val) (= val ""))
    (setq val (_block-name vla)))
  
  ;; Nettoyer et retourner
  (_trim val))

;; retourne (list kind suffix) si matche A_/B_/C_, sinon nil
(defun _parse-abc (s / clean prefix suffix)
  (setq s (_lower (_trim s)))
  ;; Nettoyer : remplacer _ - espaces par _
  (setq clean (vl-string-translate " -" "__" s))
  ;; Chercher pattern A_ B_ C_
  (cond
    ((= (substr clean 1 2) "a_")
     (setq prefix "a" suffix (substr clean 3)))
    ((= (substr clean 1 2) "b_")
     (setq prefix "b" suffix (substr clean 3)))
    ((= (substr clean 1 2) "c_")
     (setq prefix "c" suffix (substr clean 3)))
    (T (setq prefix nil suffix nil)))
  
  ;; Vérifier que le suffixe est numérique (avec point ou virgule)
  (if (and prefix suffix (> (strlen suffix) 0))
    (progn
      (setq suffix (vl-string-translate "," "." suffix))
      ;; Test simple : essayer de convertir en nombre
      (if (numberp (read suffix))
        (list prefix suffix)
        nil))
    nil))

;;; ------------------ Inventaire des points A/B/C ------------------

(defun _pt-of-insert (vla)
  (if (and (_is-vla vla) (vlax-property-available-p vla 'InsertionPoint))
    (trans (vlax-get vla 'InsertionPoint) 0 1)
    nil))

(defun _scan-abc-points (/ ss i e o name pr kind suf p abc-dict found entry)
  (setq abc-dict '())  ; Liste d'association au lieu de hash-table
  (if (setq ss (ssget "_X" '((0 . "INSERT"))))
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq e (ssname ss i)
              o (_ename->vla e)
              name (_extract-ABC-name o)
              pr (_parse-abc name))
        (when pr
          (setq kind (car pr))    ; "a", "b" ou "c"
          (setq suf  (cadr pr))   ; "16.55"
          (setq p    (_pt-of-insert o))
          (if (and p suf kind)
            (progn
              ;; Chercher si ce suffixe existe déjà
              (setq found (assoc suf abc-dict))
              (if (not found)
                ;; Créer nouvelle entrée
                (setq abc-dict (cons (cons suf (list (cons "a" nil) (cons "b" nil) (cons "c" nil))) abc-dict)))
              
              ;; Mettre à jour l'entrée
              (setq entry (assoc suf abc-dict))
              (cond
                ((= kind "a") 
                 (setq abc-dict (subst (cons suf (subst (cons "a" p) (assoc "a" (cdr entry)) (cdr entry))) entry abc-dict)))
                ((= kind "b") 
                 (setq abc-dict (subst (cons suf (subst (cons "b" p) (assoc "b" (cdr entry)) (cdr entry))) entry abc-dict)))
                ((= kind "c") 
                 (setq abc-dict (subst (cons suf (subst (cons "c" p) (assoc "c" (cdr entry)) (cdr entry))) entry abc-dict)))))))
        (setq i (1+ i)))))
  abc-dict)

;;; ------------------ Sélection circulaire & exclusions ------------------

(defun _nearest-A-distance (suf abc-dict / keys best d a other entry)
  ;; distance au plus proche autre A_ (pour auto-rayon)
  (setq keys (mapcar 'car abc-dict))  ; Extraire les clés
  (foreach k keys
    (if (and (not (equal k suf))
             (setq entry (assoc k abc-dict))
             (setq a (cdr (assoc "a" (cdr entry))))
             (setq other (cdr (assoc "a" (cdr (assoc suf abc-dict))))))
      (progn
        (setq d (_dist a other))
        (if (or (not best) (< d best)) (setq best d)))))
  best)

(defun _remove-ABC-from-ss (ss suf / out i e o name pr)
  (if (not ss) 
    nil
    (progn
      (setq out (ssadd))
      (setq i 0)
      (while (< i (sslength ss))
        (setq e (ssname ss i)
              o (_ename->vla e)
              name (_extract-ABC-name o)
              pr (_parse-abc name))
        (if (and pr (equal (vl-string-translate "," "." (cadr pr)) suf))
          ;; C'est un A_/B_/C_ avec le même suffixe -> on exclut
          nil
          (setq out (ssadd e out)))
        (setq i (1+ i)))
      out)))

;;; ------------------ Commande principale ------------------

(defun c:COUPE_ID_ALL (/ abc-dict keys appid rDefault rMin suffix aPt dNN r ss ss2 enames gname entry)
  (setq appid "COUPE_TAG")
  (setq rDefault 9.5)  ;; rayon nominal
  (setq rMin     6.0)  ;; plancher si dNN plus petit que prévu

  (prompt "\n[COUPE_ID_ALL] Indexation des points A/B/C...")
  (setq abc-dict (_scan-abc-points))
  (setq keys (mapcar 'car abc-dict))  ; Extraire les clés

  (if (not keys)
    (progn (prompt "\nAucun point A_/B_/C_ trouvé.") (princ))
    (progn
      (prompt (strcat "\n" (itoa (length keys)) " coupe(s) détectée(s)."))
      (foreach suffix keys
        (setq entry (assoc suffix abc-dict))
        (setq aPt (cdr (assoc "a" (cdr entry))))
        (if (not aPt)
          (prompt (strcat "\n- " suffix " : A_ manquant -> ignoré."))
          (progn
            ;; calcul auto-rayon
            (setq dNN (_nearest-A-distance suffix abc-dict))
            (setq r (cond
                      ((and dNN (> dNN 0.0)) (min rDefault (max rMin (* 0.45 dNN))))
                      (T rDefault)))
            ;; sélection rectangulaire (approximation du cercle)
            (setq ss (ssget "_C" 
                           (list (- (car aPt) r) (- (cadr aPt) r)) 
                           (list (+ (car aPt) r) (+ (cadr aPt) r))))
            ;; exclusions A/B/C du même suffixe
            (setq ss2 (_remove-ABC-from-ss ss suffix))

            (if (or (not ss2) (= (sslength ss2) 0))
              (prompt (strcat "\n- " suffix " : aucune entité capturée (r=" (rtos r 2 2) "m)."))
              (progn
                ;; XDATA + GROUP (sans changer de calque)
                (setq enames '())
                (repeat (sslength ss2)
                  (setq enames (cons (ssname ss2 0) enames))
                  (setq ss2 (ssdel (ssname ss2 0) ss2)))
                (foreach e enames
                  (_set-xdata e appid suffix))
                (setq gname (strcat "COUPE_" suffix))
                (_make-group gname enames)
                (prompt (strcat "\n- " suffix " : " (itoa (length enames)) " entité(s) groupée(s) → " gname
                                " (rayon " (rtos r 2 2) "m)."))
                )))))
      (prompt "\nTerminé.")
      ))
  (princ))

;; Messages de chargement
(princ "\n=== COUPE_ID_ALL.LSP v1.1 chargé ===")
(princ "\nCommande disponible : COUPE_ID_ALL")
(princ)
