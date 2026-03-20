;; COUPE_ID_ALL.lsp — v1.1b (2025-09-08)
;; - Traite toutes les coupes d’un coup
;; - Sélection rectangulaire (WINDOW) centrée sur A_suffixe (rayon 9.5 m par défaut, auto ≤ 0.45*dNN)
;; - Exclut A_/B_/C_ de la sélection (on ne transfère pas les points de calage)
;; - Conserve les calques d’origine ; ajoute XDATA + GROUP "COUPE_<suffixe>"
;; Corrections clés:
;;   * UCS cohérent (trans … 0 0)
;;   * ssget "_W" (pas "_C")
;;   * Parsing suffixe via atof / wcmatch (pas de read)
;;   * XDATA: remplace si déjà présent (pas de doublons)
;;   * Option: exclusion des TEXT/MTEXT A_/B_/C_ du même suffixe

(vl-load-com)

;;; ------------------ Helpers ------------------

(defun _is-vla (x) (and x (eq (type x) 'VLA-OBJECT)))
(defun _ename->vla (e) (if (and e (= (type e) 'ENAME)) (vlax-ename->vla-object e)))
(defun _safe-str (x) (cond ((null x) "") ((= (type x) 'STR) x) (T (vl-princ-to-string x))))
(defun _lower (s) (vl-string-translate "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" s))
(defun _trim (s) (vl-string-trim " \t\r\n" (_safe-str s)))

(defun _dist (p q) (if (and (= (type p) 'LIST) (= (type q) 'LIST)) (distance p q) 0.0))

(defun _add-appid (appid / doc dict)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq dict (vla-get-RegisteredApplications (vla-get-Database doc)))
  (if (vl-catch-all-error-p (vl-catch-all-apply 'vla-Item (list dict appid)))
    (vla-Add dict appid))
  T)

(defun _set-xdata (ename appid key / ed old) ; remplace si présent
  (if (and ename appid key)
    (progn
      (_add-appid appid) (regapp appid)
      (setq ed  (entget ename '("COUPE_TAG")))
      (setq old (assoc -3 ed))
      (if old
        (entmod (subst (list -3 (list appid (list 1000 key))) old ed))
        (entmod (append ed (list (list -3 (list appid (list 1000 key)))))))
      T)))

(defun _make-group (gname enames / doc groups g)
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object)))
  (setq groups (vla-get-Groups doc))
  (if (vl-catch-all-error-p (vl-catch-all-apply 'vla-Item (list groups gname)))
    (setq g (vla-Add groups gname))
    (progn (setq g (vla-Item groups gname)) (vla-RemoveAll g)))
  (foreach e enames
    (if (= (type e) 'ENAME)
      (vla-AppendItem g (vlax-ename->vla-object e))))
  g)

;;; ------------------ Extraction nom A_/B_/C_ ------------------

(defun _block-name (vla)
  (if (_is-vla vla)
    (cond
      ((vlax-property-available-p vla 'EffectiveName) (vla-get-EffectiveName vla))
      ((vlax-property-available-p vla 'Name)          (vla-get-Name vla))
      (T ""))
    ""))

(defun _collect-attributes (vla / res)
  (if (and (_is-vla vla)
           (vlax-property-available-p vla 'HasAttributes)
           (vla-get-HasAttributes vla))
    (mapcar '(lambda (att) (cons (_lower (vla-get-TagString att))
                                 (_trim  (vla-get-TextString att))))
            (vlax-safearray->list (vlax-variant-value (vla-GetAttributes vla))))
    '()))

(defun _extract-ABC-name (vla / atts val)
  ;; Attributs (priorité), sinon nom de bloc
  (setq atts (_collect-attributes vla))
  (foreach k '("nom" "name" "point" "code" "matricule")
    (if (and (not val) (setq val (cdr (assoc k atts)))))
  )
  (if (or (null val) (= val "")) (setq val (_block-name vla)))
  (_trim val))

;; retourne (list kind suffix) si matche A_/B_/C_, sinon nil
(defun _parse-abc (s / clean prefix suffix)
  (setq s (_lower (_trim s)))
  (setq clean (vl-string-translate " -" "__" s)) ; espaces/tirets -> underscore
  (cond
    ((= (substr clean 1 2) "a_") (setq prefix "a" suffix (substr clean 3)))
    ((= (substr clean 1 2) "b_") (setq prefix "b" suffix (substr clean 3)))
    ((= (substr clean 1 2) "c_") (setq prefix "c" suffix (substr clean 3)))
    (T (setq prefix nil suffix nil)))
  (if (and prefix suffix (> (strlen suffix) 0))
    (progn
      (setq suffix (vl-string-translate "," "." suffix))
      ;; Test tolérant : atof ne jette pas, et on accepte aussi "0", "0.0", etc.
      (if (or (/= (atof suffix) 0.0) (wcmatch suffix "#*"))
        (list prefix suffix)
        nil))
    nil))

;;; ------------------ Inventaire des points A/B/C ------------------

(defun _pt-of-insert (vla) ; point en UCS (important pour ssget)
  (if (and (_is-vla vla) (vlax-property-available-p vla 'InsertionPoint))
    (trans (vlax-get vla 'InsertionPoint) 0 0)
    nil))

(defun _scan-abc-points (/ ss i e o name pr kind suf p abc-dict found entry)
  (setq abc-dict '())  ; alist: ( (suf . (("a".ptA) ("b".ptB) ("c".ptC))) ... )
  (if (setq ss (ssget "_X" '((0 . "INSERT"))))
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq e (ssname ss i)
              o (_ename->vla e)
              name (_extract-ABC-name o)
              pr (_parse-abc name))
        (if pr
          (progn
            (setq kind (car pr)  suf (cadr pr)  p (_pt-of-insert o))
            (if (and p suf kind)
              (progn
                (setq found (assoc suf abc-dict))
                (if (not found)
                  (setq abc-dict (cons (cons suf (list (cons "a" nil) (cons "b" nil) (cons "c" nil))) abc-dict)))
                (setq entry (assoc suf abc-dict))
                (cond
                  ((= kind "a") (setq abc-dict (subst (cons suf (subst (cons "a" p) (assoc "a" (cdr entry)) (cdr entry))) entry abc-dict)))
                  ((= kind "b") (setq abc-dict (subst (cons suf (subst (cons "b" p) (assoc "b" (cdr entry)) (cdr entry))) entry abc-dict)))
                  ((= kind "c") (setq abc-dict (subst (cons suf (subst (cons "c" p) (assoc "c" (cdr entry)) (cdr entry))) entry abc-dict)))
                )))))
        (setq i (1+ i)))))
  abc-dict)

;;; ------------------ Sélection & exclusions ------------------

(defun _nearest-A-distance (suf abc-dict / keys best a other entryS aK)
  (setq entryS (assoc suf abc-dict))
  (setq a     (cdr (assoc "a" (cdr entryS))))
  (setq keys  (mapcar 'car abc-dict))
  (foreach k keys
    (if (and (not (equal k suf))
             (setq aK (cdr (assoc "a" (cdr (assoc k abc-dict)))))
             a)
      (setq best (if best (min best (_dist a aK)) (_dist a aK)))))
  best)

(defun _ename-type (e) (cdr (assoc 0 (entget e))))
(defun _get-textstring (vla)
  (if (and (_is-vla vla) (vlax-property-available-p vla 'TextString))
    (_trim (vla-get-TextString vla))))

(defun _remove-ABC-from-ss (ss suf / out i e o typ s pr)
  (if (not ss) nil
    (progn
      (setq out (ssadd) i 0)
      (while (< i (sslength ss))
        (setq e   (ssname ss i)
              o   (_ename->vla e)
              typ (_ename-type e))
        ;; Nom à parser selon type
        (cond
          ((= typ "INSERT") (setq s (_extract-ABC-name o)))
          ((or (= typ "TEXT") (= typ "MTEXT") (= typ "ATTRIB")) (setq s (_get-textstring o)))
          (T (setq s "")))
        (setq pr (_parse-abc s))
        (if (and pr (= (vl-string-translate "," "." (cadr pr)) suf))
          nil ; exclure ce A/B/C du même suffixe
          (setq out (ssadd e out)))
        (setq i (1+ i)))
      out)))

;;; ------------------ Commande principale ------------------

(defun c:COUPE_ID_ALL (/ abc-dict keys appid rDefault rMin suffix aPt dNN r ss ss2 enames gname entry total)
  (setq appid    "COUPE_TAG")
  (setq rDefault 9.5)  ;; rayon nominal
  (setq rMin     6.0)  ;; plancher si dNN plus petit que prévu

  (prompt "\n[COUPE_ID_ALL] Indexation des points A/B/C...")
  (setq abc-dict (_scan-abc-points))
  (setq keys (mapcar 'car abc-dict))

  (if (not keys)
    (progn (prompt "\nAucun point A_/B_/C_ trouvé.") (princ))
    (progn
      (setq total 0)
      (prompt (strcat "\n" (itoa (length keys)) " coupe(s) détectée(s)."))
      (foreach suffix keys
        (setq entry (assoc suffix abc-dict))
        (setq aPt (cdr (assoc "a" (cdr entry))))
        (if (not aPt)
          (prompt (strcat "\n- " suffix " : A_ manquant -> ignoré."))
          (progn
            ;; rayon auto (anti-chevauchement)
            (setq dNN (_nearest-A-distance suffix abc-dict))
            (setq r (cond
                      ((and dNN (> dNN 0.0)) (min rDefault (max rMin (* 0.45 dNN))))
                      (T rDefault)))
            ;; sélection WINDOW (rectangle centré sur A, côté = 2r)
            (setq ss (ssget "_W"
                            (list (- (car aPt) r) (- (cadr aPt) r))
                            (list (+ (car aPt) r) (+ (cadr aPt) r))))
            ;; exclusions A/B/C du même suffixe (INSERT + TEXT/MTEXT/ATTRIB)
            (setq ss2 (_remove-ABC-from-ss ss suffix))

            (if (or (not ss2) (= (sslength ss2) 0))
              (prompt (strcat "\n- " suffix " : aucune entité capturée (r=" (rtos r 2 2) "m)."))
              (progn
                ;; XDATA + GROUP
                (setq enames '())
                (repeat (sslength ss2)
                  (setq enames (cons (ssname ss2 0) enames))
                  (setq ss2 (ssdel (ssname ss2 0) ss2)))
                (foreach e enames (_set-xdata e appid suffix))
                (setq gname (strcat "COUPE_" suffix))
                (_make-group gname enames)
                (setq total (+ total (length enames)))
                (prompt (strcat "\n- " suffix " : " (itoa (length enames)) " entité(s) groupée(s) → " gname
                                " (rayon " (rtos r 2 2) "m)."))
                )))))
      (prompt (strcat "\nTerminé. Total tagué : " (itoa total) " entité(s)."))
      ))
  (princ))

(princ "\n=== COUPE_ID_ALL.LSP v1.1b chargé ===")
(princ "\nCommande disponible : COUPE_ID_ALL")
(princ)
