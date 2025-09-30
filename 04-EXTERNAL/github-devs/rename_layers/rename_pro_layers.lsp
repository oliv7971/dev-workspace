;;; Who Uses Layer? — Trouver les blocs liés à un calque
;;; - Blocs dont le contenu (direct ou imbriqué) contient des entités sur ce calque
;;; - Références de blocs (INSERT) placées sur ce calque
;;; Cmd: WHO_USES_LAYER
(vl-load-com)

(defun _doc () (vla-get-ActiveDocument (vlax-get-acad-object)))
(defun _db ()  (vla-get-Database (_doc)))
(defun _blocks () (vla-get-Blocks (_doc)))
(defun _layers () (vla-get-Layers (_doc)))

(defun _strcase-eq (a b) (= (strcase a) (strcase b)))

(defun _layer-exists-p (name / err)
  (not (vl-catch-all-error-p
        (vl-catch-all-apply 'vla-Item (list (_layers) name)))))

(defun _btr-skip-p (btr)
  ;; Vrai si BTR à ignorer (xref, layout, anonyme *Model_Space/*Paper_Space/*…)
  (or (vla-get-IsXref btr)
      (vla-get-IsLayout btr)
      (wcmatch (vla-get-Name btr) "*`**"))) ; noms commençant par *
)

(defun _get-effective-name (br)
  ;; Nom “effectif” (dynablocs), fallback sur Name
  (if (vlax-property-available-p br 'EffectiveName)
    (vla-get-EffectiveName br)
    (vla-get-Name br)))

(defun _btr-by-name (nm)
  (vl-catch-all-apply 'vla-Item (list (_blocks) nm)))

(defun _btr-uses-layer-p (btr lname / it ent used childNm childBtr visited)
  ;; Test récursif : ce BTR contient-il des entités sur LAYER (direct ou via INSERT imbriqué) ?
  (setq used nil)
  (vlax-for ent btr
    (if (not used)
      (progn
        ;; Objet interne sur le calque ?
        (if (and (vlax-property-available-p ent 'Layer)
                 (_strcase-eq (vla-get-Layer ent) lname))
          (setq used T)
        )
        ;; INSERT imbriqué : descendre dans le bloc référencé
        (if (and (not used)
                 (eq (vla-get-ObjectName ent) "AcDbBlockReference"))
          (progn
            (setq childNm (_get-effective-name ent))
            (setq childBtr (vl-catch-all-apply '_btr-by-name (list childNm)))
            (if (and (not (vl-catch-all-error-p childBtr))
                     (setq childBtr (vl-catch-all-apply 'vlax-variant-value (list childBtr)))
                     (not (_btr-skip-p childBtr)))
              (if (_btr-uses-layer-p childBtr lname)
                (setq used T)))))
      )
    )
  )
  used
)

(defun _collect-block-defs-using-layer (lname / res)
  (setq res '())
  (vlax-for btr (_blocks)
    (if (not (_btr-skip-p btr))
      (if (_btr-uses-layer-p btr lname)
        (setq res (cons (vla-get-Name btr) res)))))
  (acad_strlsort res)
)

(defun _collect-inserts-on-layer (lname / res ms ps e s h nm sp)
  (setq res '())
  ;; ModelSpace + PaperSpace
  (foreach spc (list (vla-get-ModelSpace (_doc)) (vla-get-PaperSpace (_doc)))
    (vlax-for e spc
      (if (eq (vla-get-ObjectName e) "AcDbBlockReference")
        (if (_strcase-eq (vla-get-Layer e) lname)
          (progn
            (setq nm (_get-effective-name e))
            (setq h  (if (vlax-property-available-p e 'Handle) (vla-get-Handle e) ""))
            (setq s  (strcat nm "  (handle " h ")"))
            (setq res (cons s res)))))))
  (acad_strlsort res)
)

(defun _print-list (title items)
  (princ (strcat "\n" title))
  (if items
    (foreach x items (princ (strcat "\n  - " x)))
    (princ "\n  (aucun)"))
)

(defun C:WHO_USES_LAYER ( / lname defs refs)
  (princ "\nCalque à analyser: ")
  (setq lname (getstring T))
  (if (or (null lname) (= lname ""))
    (princ "\n✗ Nom de calque invalide.")
    (progn
      (if (not (_layer-exists-p lname))
        (princ "\n✗ Ce calque n'existe pas dans le dessin.")
        (progn
          (princ (strcat "\nAnalyse des références au calque \"" lname "\" …"))
          (setq defs (_collect-block-defs-using-layer lname))
          (setq refs (_collect-inserts-on-layer lname))
          (_print-list (strcat "Blocs dont le CONTENU utilise le calque \"" lname "\" :") defs)
          (_print-list (strcat "INSERTs posés sur le calque \"" lname "\" :") refs)
          (princ
            "\n\nAstuce: pour supprimer le calque, il faut d'abord corriger ces blocs (ouvrir la définition et changer le calque des objets),\n"
          )
        )
      )
    )
  )
  (princ)
)
