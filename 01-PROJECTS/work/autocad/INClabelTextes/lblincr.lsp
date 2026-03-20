;; LBLINCR.LSP — Pose de libellés avec incrément auto (L01B/L01H, etc.)
;; v1.3 — MTEXT 1-clic via ActiveX (AddMText), plus de 2e coin demandé
;; Commandes : LBLSETUP (init), LBLINCR (pose), LBLBACK (décrément), LBLTOGGLE (H/B), LBLSTATE

(vl-load-com)


;; =======================
;; ======  ÉTAT  =========
;; =======================
(setq *LBL:prefix* "L"
      *LBL:num*    1
      *LBL:width*  2
      *LBL:suffix* "B"      ;; “B” ou “H”
      *LBL:type*   "MTEXT"  ;; "MTEXT" ou "TEXT"
      *LBL:height* nil)     ;; nil -> (getvar "TEXTSIZE")

;; =======================
;; ====== UTILS ==========
;; =======================

(defun LBL:ZeroPad (n w / s out k)
  (setq n (if (numberp n) n 0))
  (setq w (if (and (numberp w) (> w 0)) w 1))
  (setq s (itoa (max 0 n)))
  (setq k (- w (strlen s)) out "")
  (repeat (max 0 k) (setq out (strcat "0" out)))
  (strcat out s)
)

(defun LBL:SplitCode (s / i j len ch prefix numstr suffix)
  (if (not (and s (= (type s) 'STR))) (setq s "L01B"))
  (setq len (strlen s) i 0)
  (while (< i len)
    (setq ch (substr s (1+ i) 1))
    (if (wcmatch ch "[A-Za-z]") (setq i (1+ i)) (setq i i len len))
  )
  (setq prefix (substr s 1 i))
  (setq j i)
  (while (< j (strlen s))
    (setq ch (substr s (1+ j) 1))
    (if (wcmatch ch "[0-9]") (setq j (1+ j)) (setq j j len (strlen s)))
  )
  (setq numstr (substr s (1+ i) (- j i)))
  (setq suffix (substr s (1+ j)))
  (list prefix numstr suffix)
)

(defun LBL:SetFromCode (code / parts numstr)
  (setq parts        (LBL:SplitCode code)
        *LBL:prefix* (nth 0 parts)
        numstr       (nth 1 parts)
        *LBL:suffix* (nth 2 parts)
  )
  (setq *LBL:width* (max 1 (strlen (if (> (strlen numstr) 0) numstr "1"))))
  (setq *LBL:num*   (if (> (strlen numstr) 0) (atoi numstr) 1))
)

(defun LBL:CurrentCode ( / )
  (strcat *LBL:prefix* (LBL:ZeroPad *LBL:num* *LBL:width*) *LBL:suffix*)
)

(defun LBL:ReadTextString (ent / e)
  (if (and ent (setq e (entget ent))) (cdr (assoc 1 e)))
)

(defun LBL:_safe-rtos (v)
  (cond
    ((numberp v) (rtos v 2 2))
    ((and v (not (eq v nil))) (vl-princ-to-string v))
    (T "")
  )
)

(defun LBL:NormalizeType (s)
  (cond
    ((null s) *LBL:type*)
    ((wcmatch (strcase s) "T*") "TEXT")
    ((wcmatch (strcase s) "M*") "MTEXT")
    (T "MTEXT")
  )
)

(defun LBL:_height-get ( / )
  (if (numberp *LBL:height*) *LBL:height* (getvar "TEXTSIZE"))
)

(defun LBL:EchoState ( / h)
  (setq h (LBL:_height-get))
  (princ (strcat
    "\n[LBL] Type=" (LBL:NormalizeType *LBL:type*)
    "  Hauteur=" (LBL:_safe-rtos h)
    "  Code courant=" (LBL:CurrentCode)
    "  (prefix=" *LBL:prefix* ", #=" (vl-princ-to-string *LBL:num*)
    " (w=" (vl-princ-to-string *LBL:width*) "), suffix=" *LBL:suffix* ")"
  ))
  (princ)
)


;; Espace courant (Model/Paper) pour ActiveX — version robuste
(defun LBL:_active-space ( / app doc)
  (setq app (vlax-get-acad-object))
  (setq doc (vla-get-ActiveDocument app))
  (if (= 1 (getvar "CVPORT"))
    (vla-get-PaperSpace doc)   ;; onglet présentation actif
    (vla-get-ModelSpace doc)   ;; espace objet
  )
)


;; =======================
;; === CRÉATION OBJETS ===
;; =======================
;; MTEXT 1-clic : ActiveX avec try/catch + double fallback
(defun LBL:PlaceMTEXT (pt value / h w sp sty res obj p2 ent)
  (setq h  (LBL:_height-get))
  (setq w  (* h (max 6 (strlen value))))   ;; largeur raisonnable
  (setq sp (LBL:_active-space))
  (setq sty (getvar "TEXTSTYLE"))

  ;; 1) Tentative ActiveX avec gestion d’exception
  (setq res (vl-catch-all-apply
              'vlax-invoke (list sp 'AddMText (vlax-3d-point pt) w value)))
  (if (not (vl-catch-all-error-p res))
    (progn
      (setq obj res)
      (vla-put-Height obj h)
      (vla-put-AttachmentPoint obj 5)  ;; MiddleCenter
      (vla-put-DrawingDirection obj 1) ;; LeftToRight
      (vla-put-Rotation obj 0.0)
      (vla-put-Layer obj (getvar "CLAYER"))
      (vla-put-StyleName obj sty)
      (vlax-vla-object->ename obj)
    )
    ;; 2) Fallback ENTMAKEX
    (progn
      (setq ent
        (entmakex
          (list
            (cons 0  "MTEXT")
            (cons 8  (getvar "CLAYER"))
            (cons 7  sty)
            (cons 10 pt)
            (cons 40 h)
            (cons 41 w)
            (cons 71 5)   ;; Middle Center
            (cons 72 1)   ;; Left-to-right
            (cons 50 0.0)
            (cons 1  value)
          )
        )
      )
      (if ent
        ent
        ;; 3) Super-fallback : commande -MTEXT avec 2e coin calculé (toujours 1 clic pour toi)
        (progn
          (setq p2 (list (+ (car pt) (* h 8.0))
                         (+ (cadr pt) (* h 2.0))
                         (caddr pt)))
          (command "._-MTEXT" pt p2 value "")
          (entlast)
        )
      )
    )
  )
)


(defun LBL:PlaceMTEXT (pt value / sty h w ent xdir)
  (setq sty  (getvar "TEXTSTYLE"))
  (setq h    (LBL:_height-get))
  (setq w    (* h (max 6 (strlen value))))     ;; largeur de référence
  (setq xdir (list 1.0 0.0 0.0))               ;; vecteur direction X (obligatoire sur certains AutoCAD)

  ;; MTEXT pur ENTMAKEX avec champs complets (évite toute interaction)
  (setq ent
    (entmakex
      (list
        (cons 0   "MTEXT")
        (cons 8   (getvar "CLAYER"))
        (cons 7   sty)
        (cons 10  pt)                           ;; point d’insertion
        (cons 11  xdir)                         ;; vecteur direction texte (X axis)
        (cons 210 (list 0.0 0.0 1.0))           ;; extrusion Z (plan courant)
        (cons 40  h)                            ;; hauteur
        (cons 41  w)                            ;; largeur
        (cons 71  5)                            ;; AttachmentPoint = MiddleCenter
        (cons 72  1)                            ;; Left-to-right
        (cons 73  1)                            ;; Line spacing style = AtLeast
        (cons 44  1.0)                          ;; Line spacing factor
        (cons 50  0.0)                          ;; rotation
        (cons 1   value)                        ;; contenu
      )
    )
  )
  ent
)


(defun LBL:PlaceOne ( / pt val ent)
  (setq val (LBL:CurrentCode))
  (setq pt (getpoint (strcat "\nPoint d'insertion pour \"" val "\" (Entrée pour finir): ")))
  (if pt
    (progn
      (setq ent
        (if (equal (strcase (LBL:NormalizeType *LBL:type*)) "TEXT")
          (LBL:PlaceTEXT pt val)
          (LBL:PlaceMTEXT pt val)
        )
      )
      (if ent
        (progn (setq *LBL:num* (1+ *LBL:num*)) T)
        (progn (princ "\n⚠️  Échec création du texte.") nil)
      )
    )
    nil
  )
)

;; =======================
;; ===== COMMANDES =======
;; =======================

(defun c:LBLSETUP ( / kw s ent code tp h )
  (princ "\n--- Réglage LBL ---")
  ;; Base : saisir / prendre
  (initget "Saisir Prendre")
  (setq kw (getkword "\nBase [Saisir/Prendre] <Saisir>: "))
  (cond
    ((or (null kw) (= kw "Saisir"))
      (setq s (getstring T (strcat "\nEntrer le code de départ (ex. L01B) <" (LBL:CurrentCode) ">: ")))
      (if (> (strlen s) 0) (LBL:SetFromCode s))
    )
    ((= kw "Prendre")
      (princ "\nSélectionner un TEXT/MTEXT existant contenant un code (ex. L07H) :")
      (setq ent (car (entsel "\nChoisir le texte: ")))
      (if (and ent (setq code (LBL:ReadTextString ent)) (> (strlen code) 0))
        (LBL:SetFromCode code)
        (princ "\nAucun texte valide lu, on garde les réglages courants.")
      )
    )
  )

  ;; Type
  (initget "MTEXT TEXT")
  (setq tp (getkword (strcat "\nType de texte [MTEXT/TEXT] <" *LBL:type* ">: ")))
  (if tp (setq *LBL:type* (LBL:NormalizeType tp)))

  ;; Hauteur
  (setq h (getreal (strcat "\nHauteur (en unités dessin) <" (LBL:_safe-rtos (LBL:_height-get)) ">: ")))
  (if (numberp h) (setq *LBL:height* (abs h)))

  (LBL:EchoState)
  (princ "\nRéglages terminés. Lance `LBLINCR` pour poser en série.")
  (princ)
)

(defun c:LBLINCR ( / )
  (princ "\n--- Pose incrémentée LBL ---")
  (LBL:EchoState)
  (princ "\nClique pour poser, Entrée pour terminer. (Tu peux relancer `LBLSETUP` à tout moment pour changer la base.)")
  (while (LBL:PlaceOne))
  (princ "\nTerminé.")
  (princ)
)

(defun c:LBLBACK ( / )
  (setq *LBL:num* (max 0 (1- *LBL:num*)))
  (princ (strcat "\nDécrément : prochain code = " (LBL:CurrentCode)))
  (princ)
)

(defun c:LBLTOGGLE ( / )
  (cond
    ((wcmatch (strcase *LBL:suffix*) "B") (setq *LBL:suffix* "H"))
    ((wcmatch (strcase *LBL:suffix*) "H") (setq *LBL:suffix* "B"))
    (T (setq *LBL:suffix* "B"))
  )
  (princ (strcat "\nSuffixe basculé : " *LBL:suffix* " — prochain code = " (LBL:CurrentCode)))
  (princ)
)

(defun c:LBLSTATE () (LBL:EchoState))

(princ "\nLBLSuite chargé. Utilise LBLSETUP, LBLINCR, LBLBACK, LBLTOGGLE, LBLSTATE.")
(princ)
