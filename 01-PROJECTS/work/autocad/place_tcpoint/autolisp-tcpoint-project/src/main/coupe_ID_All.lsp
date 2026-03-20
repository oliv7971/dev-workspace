;; COUPE_ID_ALL.lsp — v1.2 (2025-09-08)
;; - Repère A_/B_/C_ via l'attribut MAT de blocs INSERT sur calques dédiés
;; - Côté coupes (par défaut calque "_CALAGE_PT"), côté 3D (par défaut "_CALAGE_3D_CI")
;; - COUPE_ID_ALL : groupe les objets autour de A_suffixe (côté coupes uniquement)
;; - PAIR_REPORT  : tableau d’appairage A/B/C entre coupes et 3D (par suffixe)
;; - Fenêtre WINDOW (UCS), XDATA sans doublons, exclusions A/B/C (INSERT + TEXT/MTEXT/ATTRIB)

(vl-load-com)

;;; ------------------ Paramètres par défaut ------------------

(setq *calques_coupes* '("_CALAGE_PT"))     ;; calques où se trouvent les TCPOINT des coupes
(setq *calques_3d*    '("_CALAGE_3D_CI"))  ;; calques où se trouvent les points 3D
(setq *tags_mat*      '("mat"))            ;; tags d'attribut acceptés pour le code (A_.., B_.., C_..)
(setq *block_whitelist_coupes* '("TCPOINT" "point" "pt")) ;; tolérant : ne filtre pas strictement
(setq *block_whitelist_3d*     '("pt" "TCPOINT" "point"))

;;; ------------------ Helpers ------------------

(defun _is-vla (x) (and x (eq (type x) 'VLA-OBJECT)))
(defun _ename->vla (e) (if (and e (= (type e) 'ENAME)) (vlax-ename->vla-object e)))
(defun _safe-str (x) (cond ((null x) "") ((= (type x) 'STR) x) (T (vl-princ-to-string x))))
(defun _lower (s) (vl-string-translate "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" s))
(defun _trim (s) (vl-string-trim " \t\r\n" (_safe-str s)))
(defun _dist (p q) (if (and (= (type p) 'LIST) (= (type q) 'LIST)) (distance p q) 0.0))
(defun _ename-type (e) (cdr (assoc 0 (entget e))))

(defun _in-list-ci? (s lst) ; membre insensible à la casse
  (setq s (_lower (_safe-str s)))
  (if (vl-some '(lambda (x) (eq s (_lower (_safe-str x)))) lst) T nil))

(defun _layer-of (vla) (if (_is-vla vla) (vla-get-Layer vla)))

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

;;; ------------------ Lecture blocs / attributs ------------------

(defun _block-name (vla)
  (if (_is-vla vla)
    (cond
      ((vlax-property-available-p vla 'EffectiveName) (vla-get-EffectiveName vla))
      ((vlax-property-available-p vla 'Name)          (vla-get-Name vla))
      (T ""))
    ""))

(defun _collect-attributes (vla)
  (if (and (_is-vla vla)
           (vlax-property-available-p vla 'HasAttributes)
           (vla-get-HasAttributes vla))
    (mapcar '(lambda (att) (cons (_lower (vla-get-TagString att))
                                 (_trim  (vla-get-TextString att))))
            (vlax-safearray->list (vlax-variant-value (vla-GetAttributes vla))))
    '()))

(defun _get-attr (atts tags-ci / v)
  (setq v nil)
  (foreach t tags-ci
    (if (and (not v) (setq v (cdr (assoc (_lower t) atts)))))
  )
  v)

(defun _parse-abc (s / m)
  (setq s (_lower (_trim s)))
  (setq m (vl-regexp-match "^(a|b|c)[ _-]*([0-9]+(?:[.,][0-9]+)?)$" s))
  (if m (list (nth 1 m) (vl-string-translate "," "." (nth 2 m))) nil))

(defun _pt-of-insert (vla) ; point en UCS
  (if (and (_is-vla vla) (vlax-property-available-p vla 'InsertionPoint))
    (trans (vlax-get vla 'InsertionPoint) 0 0)))

;;; ------------------ Scan de points A/B/C par CALQUES (INSERT + MAT) ------------------

(defun _scan-abc-on-calques (calques block-whitelist / ss n i e o lay name atts mat pr kind suf p dict found entry)
  (setq dict '()) ; alist: ( (suf . (("a".ptA) ("b".ptB) ("c".ptC))) ... )
  ;; On scanne tous les INSERT, puis on filtre par calque et attribut MAT
  (if (setq ss (ssget "_X" '((0 . "INSERT"))))
    (progn
      (setq n (sslength ss) i 0)
      (while (< i n)
        (setq e   (ssname ss i)
              o   (_ename->vla e)
              lay (_layer-of o)
              name (_block-name o))
        (if (and lay
                 (vl-some '(lambda (L) (wcmatch lay L)) calques)) ; autorise motifs * si tu en mets
          (progn
            ;; (option) si tu veux filtrer aussi par nom de bloc :
            (if (or (not block-whitelist) (_in-list-ci? name block-whitelist)) ; tolérant
              (progn
                (setq atts (_collect-attributes o))
                (setq mat (_get-attr atts *tags_mat*))
                (setq pr (_parse-abc mat))
                (if pr
                  (progn
                    (setq kind (car pr)  suf (cadr pr)  p (_pt-of-insert o))
                    (if (and p suf kind)
                      (progn
                        (setq found (assoc suf dict))
                        (if (not found)
                          (setq dict (cons (cons suf (list (cons "a" nil) (cons "b" nil) (cons "c" nil))) dict)))
                        (setq entry (assoc suf dict))
                        (cond
                          ((equal kind "a") (setq dict (subst (cons suf (subst (cons "a" p) (assoc "a" (cdr entry)) (cdr entry))) entry dict)))
                          ((equal kind "b") (setq dict (subst (cons suf (subst (cons "b" p) (assoc "b" (cdr entry)) (cdr entry))) entry dict)))
                          ((equal kind "c") (setq dict (subst (cons suf (subst (cons "c" p) (assoc "c" (cdr entry)) (cdr entry))) entry dict)))
                        ))))))
          ))
        (setq i (1+ i)))))
  dict)

;;; ------------------ Sélection & exclusions ------------------

(defun _nearest-A-distance (suf dict / keys best a entryS aK)
  (setq entryS (assoc suf dict))
  (setq a     (cdr (assoc "a" (cdr entryS))))
  (setq keys  (mapcar 'car dict))
  (foreach k keys
    (if (and (not (equal k suf))
             (setq aK (cdr (assoc "a" (cdr (assoc k dict)))))
             a)
      (setq best (if best (min best (_dist a aK)) (_dist a aK)))))
  best)

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
        ;; Texte selon type
        (cond
          ((equal typ "INSERT")
           (setq s (_get-attr (_collect-attributes o) *tags_mat*))
           (if (or (null s) (= s "")) (setq s (_block-name o))))
          ((or (equal typ "TEXT") (equal typ "MTEXT") (equal typ "ATTRIB"))
           (setq s (_get-textstring o)))
          (T (setq s "")))
        (setq pr (_parse-abc s))
        (if (and pr (equal (vl-string-translate "," "." (cadr pr)) suf))
          nil ; exclure A/B/C du même suffixe
          (setq out (ssadd e out)))
        (setq i (1+ i)))
      out)))

;;; ------------------ Commandes ------------------

;; 1) Identifier & grouper côté COUPES uniquement (autour des A_suffixe)
(defun c:COUPE_ID_ALL (/ appid rDefault rMin dict keys suffix entry aPt dNN r ss ss2 enames gname total)
  (setq appid    "COUPE_TAG")
  (setq rDefault 9.5)
  (setq rMin     6.0)

  (prompt "\n[COUPE_ID_ALL] Scan des A/B/C côté COUPES (calques *calques_coupes*)...")
  (setq dict (_scan-abc-on-calques *calques_coupes* *block_whitelist_coupes*))
  (setq keys (mapcar 'car dict))

  (if (not keys)
    (progn (prompt "\nAucun TCPOINT (MAT=A_/B_/C_) trouvé sur calques COUPES.") (princ))
    (progn
      (setq total 0)
      (prompt (strcat "\n" (itoa (length keys)) " coupe(s) détectée(s) (côté COUPES)."))
      (foreach suffix keys
        (setq entry (assoc suffix dict))
        (setq aPt (cdr (assoc "a" (cdr entry))))
        (if (not aPt)
          (prompt (strcat "\n- " suffix " : A_ manquant -> ignoré."))
          (progn
            ;; rayon auto (anti-chevauchement entre A côté coupes)
            (setq dNN (_nearest-A-distance suffix dict))
            (setq r (cond
                      ((and dNN (> dNN 0.0)) (min rDefault (max rMin (* 0.45 dNN))))
                      (T rDefault)))
            ;; sélection WINDOW (carré centré sur A, côté = 2r)
            (setq ss (ssget "_W"
                            (list (- (car aPt) r) (- (cadr aPt) r))
                            (list (+ (car aPt) r) (+ (cadr aPt) r))))
            ;; exclusions A/B/C du même suffixe
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

;; 2) Rapport d’appairage COUPES vs 3D (par suffixe)
(defun c:PAIR_REPORT (/ dS dT keysS keysT allkeys k eS eT okA okB okC nOK)
  (prompt "\n[PAIR_REPORT] Scan COUPES...")
  (setq dS (_scan-abc-on-calques *calques_coupes* *block_whitelist_coupes*))
  (prompt "\n[PAIR_REPORT] Scan 3D...")
  (setq dT (_scan-abc-on-calques *calques_3d*    *block_whitelist_3d*))
  (setq keysS (mapcar 'car dS))
  (setq keysT (mapcar 'car dT))
  ;; union des clés
  (setq allkeys keysS)
  (foreach k keysT (if (not (assoc k allkeys)) (setq allkeys (cons k allkeys))))
  (setq allkeys (vl-sort allkeys '(lambda (a b) (< (atof a) (atof b))))) ; tri numérique de suffixes

  (if (not allkeys)
    (prompt "\nAucun suffixe détecté ni côté coupes ni côté 3D.")
    (progn
      (prompt "\nSuffixe | Coups(A,B,C) | 3D(A,B,C)")
      (prompt "\n-----------------------------------")
      (foreach k allkeys
        (setq eS (assoc k dS)  eT (assoc k dT))
        (setq okA (if (and eS (cdr (assoc "a" (cdr eS)))) "A" "-"))
        (setq okB (if (and eS (cdr (assoc "b" (cdr eS)))) "B" "-"))
        (setq okC (if (and eS (cdr (assoc "c" (cdr eS)))) "C" "-"))
        (setq sL (strcat okA okB okC))

        (setq okA (if (and eT (cdr (assoc "a" (cdr eT)))) "A" "-"))
        (setq okB (if (and eT (cdr (assoc "b" (cdr eT)))) "B" "-"))
        (setq okC (if (and eT (cdr (assoc "c" (cdr eT)))) "C" "-"))
        (setq tL (strcat okA okB okC))

        (prompt (strcat "\n" k " | " sL " | " tL))
      )
      (prompt "\n-----------------------------------")
      (prompt "\nLégende: chaque triplet 'ABC' indique la présence des points sur chaque côté ( '-' = absent ).")
    ))
  (princ))

(princ "\n=== COUPE_ID_ALL.LSP v1.2 chargé ===")
(princ "\nCommandes: COUPE_ID_ALL (grouper coupes), PAIR_REPORT (vérifier appairage)")
(princ)
;;; ================== ALIGNEMENTS 3D A->A, B->B, C->C ==================

;; Sélection par XDATA COUPE_TAG (si la coupe a été “taguée” avant)
(defun _ss_by_xdata (suf / flt)
  (setq flt (list (list -3 (list "COUPE_TAG" (cons 1000 suf)))))
  (ssget "_X" flt))

;; Fallback: petite fenêtre autour de A (comme COUPE_ID_ALL), si pas de XDATA
(defun _ss_window_autour_de_A (suf dict / aPt dNN r rDefault rMin ss ss2)
  (setq rDefault 9.5  rMin 6.0)
  (setq aPt (cdr (assoc "a" (cdr (assoc suf dict)))))
  (if aPt
    (progn
      (setq dNN (_nearest-A-distance suf dict))
      (setq r (cond ((and dNN (> dNN 0.0)) (min rDefault (max rMin (* 0.45 dNN))))
                    (T rDefault)))
      (setq ss (ssget "_W"
                      (list (- (car aPt) r) (- (cadr aPt) r))
                      (list (+ (car aPt) r) (+ (cadr aPt) r))))
      ;; Exclure A/B/C du même suffixe
      (setq ss2 (_remove-ABC-from-ss ss suf))
      ss2)))

;; Aligne UNE coupe par son suffixe avec 3DALIGN (A->A, B->B, C->C)
(defun _align_one_suffix (suf allowScale / dS dT eS eT A1 A2 B1 B2 C1 C2 ss oldCE ans)
  ;; dS = coupes ; dT = 3D
  (setq dS (_scan-abc-on-calques *calques_coupes* *block_whitelist_coupes*))
  (setq dT (_scan-abc-on-calques *calques_3d*    *block_whitelist_3d*))
  (setq eS (assoc suf dS)  eT (assoc suf dT))
  (if (and eS eT
           (setq A1 (cdr (assoc "a" (cdr eS))))
           (setq B1 (cdr (assoc "b" (cdr eS))))
           (setq C1 (cdr (assoc "c" (cdr eS))))
           (setq A2 (cdr (assoc "a" (cdr eT))))
           (setq B2 (cdr (assoc "b" (cdr eT))))
           (setq C2 (cdr (assoc "c" (cdr eT)))))
    (progn
      ;; sélection: XDATA si dispo, sinon fallback fenêtre autour de A
      (setq ss (_ss_by_xdata suf))
      (if (or (not ss) (= (sslength ss) 0))
        (setq ss (_ss_window_autour_de_A suf dS)))
      (if (or (not ss) (= (sslength ss) 0))
        (prompt (strcat "\n[" suf "] rien à aligner (pas de sélection)."))
        (progn
          (setq oldCE (getvar "CMDECHO"))
          (setvar "CMDECHO" 0)
          ;; 3DALIGN : sélection -> "" -> paires source/destination -> "" -> scale (Y/N)
          (command "._3DALIGN" ss "" A1 A2 B1 B2 C1 C2 "" (if allowScale "Y" "N"))
          (setvar "CMDECHO" oldCE)
          (prompt (strcat "\n[" suf "] aligné (A->A, B->B, C->C, scale=" (if allowScale "Y" "N") ")."))
        )))
    (prompt (strcat "\n[" suf "] A/B/C manquants d’un côté -> ignoré."))))

;; Commande: aligne TOUTES les coupes qui ont A/B/C des deux côtés
(defun c:COUPE_ALIGN_ALL (/ dS dT keysS keysT commons sc kw allowScale)
  (prompt "\n[COUPE_ALIGN_ALL] Vérification des points A/B/C des deux côtés...")
  (setq dS (_scan-abc-on-calques *calques_coupes* *block_whitelist_coupes*))
  (setq dT (_scan-abc-on-calques *calques_3d*    *block_whitelist_3d*))
  (setq keysS (mapcar 'car dS))
  (setq keysT (mapcar 'car dT))
  ;; intersection sur les suffixes présents des deux côtés
  (setq commons '())
  (foreach k keysS (if (assoc k dT) (setq commons (cons k commons))))
  (if (not commons)
    (progn (prompt "\nAucun suffixe commun trouvé (ou A/B/C manquants).") (princ))
    (progn
      ;; option scale
      (initget "No Yes")
      (setq kw (getkword "\nMise à l’échelle basée sur les points ? [No/Yes] <No>: "))
      (setq allowScale (eq kw "Yes"))
      (prompt (strcat "\nSuffixes à traiter: " (itoa (length commons))))
      ;; trier numériquement (optionnel)
      (setq commons (vl-sort commons '(lambda (a b) (< (atof a) (atof b)))))
      (foreach suf commons
        (_align_one_suffix suf allowScale))
      (prompt "\nCOUPE_ALIGN_ALL terminé.")
    ))
  (princ))

;; (Option) Aligner UNE coupe (utile pour tester un suffixe)
(defun c:COUPE_ALIGN_ONE (/ dS keys suf kw allowScale)
  (setq dS (_scan-abc-on-calques *calques_coupes* *block_whitelist_coupes*))
  (setq keys (mapcar 'car dS))
  (if (not keys)
    (progn (prompt "\nAucun suffixe côté coupes.") (princ))
    (progn
      (setq suf (getstring T (strcat "\nSuffixe à aligner (" (car keys) "…): ")))
      (if (= suf "") (setq suf (car keys)))
      (initget "No Yes")
      (setq kw (getkword "\nMise à l’échelle basée sur les points ? [No/Yes] <No>: "))
      (setq allowScale (eq kw "Yes"))
      (_align_one_suffix suf allowScale)
    )))
