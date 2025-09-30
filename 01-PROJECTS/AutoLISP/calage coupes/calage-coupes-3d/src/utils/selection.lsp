;;; SELECTION.LSP
;;; Functions for selecting objects

;; Fonction pour sélectionner TOUS les objets d'un PM spécifique
;; EXCLUT ABSOLUMENT les calques _CALAGE_PT et _CALAGE_3D_CI
(defun select-all-objects-for-pm (pm-ref / ss ss-filtered i ent bloc mat calque)
  ;; Créer un jeu de sélection vide
  (setq ss-filtered (ssadd))
  
  ;; 1. Sélectionner tous les blocs avec attributs du bon PM
  (if (setq ss (ssget "X" '((0 . "INSERT"))))
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq calque (cdr (assoc 8 (entget ent))))
        
        ;; EXCLURE ABSOLUMENT les calques de calage !
        (if (and 
              (not (equal calque "_CALAGE_PT"))      ; PAS les points source
              (not (equal calque "_CALAGE_3D_CI"))   ; PAS les points destination
              (not (wcmatch calque "*CALAGE*"))      ; PAS de calque avec CALAGE dedans
            )
          (progn
            (setq bloc (vlax-ename->vla-object ent))
            (setq mat (get-matricule bloc))
            ;; Si le bloc a un matricule avec le bon PM
            (if (and mat (wcmatch mat (strcat "*_" pm-ref)))
              (ssadd ent ss-filtered)
            )
          )
        )
        (setq i (1+ i))
      )
    )
  )
  
  ;; 2. Ajouter tous les objets GRAPHIQUES dans la zone (lignes, polylignes, etc.)
  ;; D'abord récupérer les points de calage pour ce PM pour définir la zone
  (setq pts-calage (collect-blocks "_CALAGE_PT"))
  (setq pts-pm '())
  (foreach pt pts-calage
    (if (wcmatch (car pt) (strcat "*_" pm-ref))
      (setq pts-pm (cons (cadr pt) pts-pm))
    )
  )
  
  ;; Si on a des points, sélectionner dans leur zone élargie
  (if pts-pm
    (progn
      (setq xmin (apply 'min (mapcar 'car pts-pm)))
      (setq xmax (apply 'max (mapcar 'car pts-pm)))
      (setq ymin (apply 'min (mapcar 'cadr pts-pm)))
      (setq ymax (apply 'max (mapcar 'cadr pts-pm)))
      
      ;; Extension pour couvrir toute la coupe
      (setq largeur (- xmax xmin))
      (setq hauteur (- ymax ymin))
      (setq xmin (- xmin (* 1.5 largeur)))
      (setq xmax (+ xmax (* 1.5 largeur)))
      (setq ymin (- ymin (* 1.5 hauteur)))
      (setq ymax (+ ymax (* 1.5 hauteur)))
      
      ;; Sélectionner avec un filtre STRICT
      (if (setq ss (ssget "_C" 
                     (list xmin ymin) 
                     (list xmax ymax)
                     '((-4 . "<NOT")
                       (-4 . "<OR")
                         (8 . "_CALAGE_PT")
                         (8 . "_CALAGE_3D_CI")
                         (8 . "*CALAGE*")
                       (-4 . "OR>")
                       (-4 . "NOT>")
                     )))
        (progn
          (setq i 0)
          (repeat (sslength ss)
            (setq ent (ssname ss i))
            ;; Double vérification pour être sûr
            (setq calque (cdr (assoc 8 (entget ent))))
            (if (and 
                  (not (equal calque "_CALAGE_PT"))
                  (not (equal calque "_CALAGE_3D_CI"))
                  (not (wcmatch calque "*CALAGE*"))
                  (not (ssmemb ent ss-filtered)))
              (ssadd ent ss-filtered)
            )
            (setq i (1+ i))
          )
        )
      )
    )
  )
  
  ;; Message de sécurité
  (princ (strcat "\n  Objets sélectionnés : " (itoa (sslength ss-filtered))))
  (princ "\n  (Points de calage EXCLUS)")
  
  ss-filtered
)

;; Fonction simplifiée pour la sélection par zone
(defun select-in-bounds-for-pm (pt-list pm-ref / xmin xmax ymin ymax pts ss calque xcenter ycenter largeur hauteur)
  (setq pts (mapcar 'cadr pt-list))
  
  ;; Calculer l'emprise des points
  (setq xmin (apply 'min (mapcar 'car pts)))
  (setq xmax (apply 'max (mapcar 'car pts)))
  (setq ymin (apply 'min (mapcar 'cadr pts)))
  (setq ymax (apply 'max (mapcar 'cadr pts)))
  
  ;; Extension pour couvrir toute la coupe
  (setq largeur (- xmax xmin))
  (setq hauteur (- ymax ymin))
  (setq xmin (- xmin (* 1.5 largeur)))
  (setq xmax (+ xmax (* 1.5 largeur)))
  (setq ymin (- ymin (* 1.5 hauteur)))
  (setq ymax (+ ymax (* 1.5 hauteur)))
  
  ;; Sélectionner avec filtre STRICT excluant les calques de calage
  (setq ss (ssget "_C" 
           (list xmin ymin) 
           (list xmax ymax)
           '((-4 . "<NOT")
             (-4 . "<OR")
               (8 . "_CALAGE_PT")      ; Exclure points source
               (8 . "_CALAGE_3D_CI")   ; Exclure points destination  
               (8 . "*CALAGE*")        ; Exclure tout calque avec CALAGE
             (-4 . "OR>")
             (-4 . "NOT>")
           )))
  
  ss  ; Retourner directement le selection set filtré
)

;; Fonction générique
(defun select-in-bounds (pt-list)
  (select-in-bounds-for-pm pt-list nil)
)

;; Fonction pour sélectionner les objets d'une coupe spécifique
;; EXCLUT ABSOLUMENT les points de calage
(defun select-objects-for-coupe (pt-list pm-ref / pt-a xcenter ycenter rayon xmin xmax ymin ymax ss)
  ;; Chercher le point A de ce PM comme centre de sélection
  (setq pt-a nil)
  (setq matricule-a (strcat "A_" pm-ref))
  
  (foreach item pt-list
    (if (equal (car item) matricule-a)
      (setq pt-a (cadr item))
    )
  )
  
  ;; Si pas de point A, prendre le centre de tous les points
  (if (not pt-a)
    (progn
      (setq pts (mapcar 'cadr pt-list))
      (setq xcenter (/ (+ (apply 'min (mapcar 'car pts)) 
                         (apply 'max (mapcar 'car pts))) 2.0))
      (setq ycenter (/ (+ (apply 'min (mapcar 'cadr pts)) 
                         (apply 'max (mapcar 'cadr pts))) 2.0))
      (if pm-ref (princ (strcat "\n    ⚠ Point A_" pm-ref " non trouvé, utilisation du centre")))
    )
    (progn
      (setq xcenter (car pt-a))
      (setq ycenter (cadr pt-a))
      (if pm-ref (princ (strcat "\n    ✓ Centre sur point A_" pm-ref)))
    )
  )
  
  ;; Zone de sélection : 10m autour du centre (point A ou centre calculé)
  (setq rayon 10.0)
  (setq xmin (- xcenter rayon))
  (setq xmax (+ xcenter rayon))
  (setq ymin (- ycenter rayon))
  (setq ymax (+ ycenter rayon))
  
  ;; Debug : afficher la zone de sélection
  (if pm-ref
    (princ (strcat "\n    Zone sélection PM " pm-ref ": "
                  "X=" (rtos xmin 2 1) " à " (rtos xmax 2 1)
                  " Y=" (rtos ymin 2 1) " à " (rtos ymax 2 1)))
  )
  
  ;; Sélectionner avec filtre strict excluant ABSOLUMENT tous les points de calage
  ;; CRITIQUE : Exclure les points A, B, C de TOUTES les coupes (pas seulement celle-ci)
  (setq ss (ssget "_C" 
    (list xmin ymin) 
    (list xmax ymax)
    '((-4 . "<NOT")
      (-4 . "<OR")
        (8 . "_CALAGE_PT")      ; Exclure TOUS les points source (A, B, C de toutes coupes)
        (8 . "_CALAGE_3D_CI")   ; Exclure TOUS les points destination 3D
        (8 . "*CALAGE*")        ; Exclure tout calque contenant CALAGE
        (-4 . "<AND")           ; ET exclure les blocs avec matricules A_, B_, C_
          (0 . "INSERT")
          (-4 . "<OR")
            (2 . "A_*")         ; Blocs commençant par A_
            (2 . "B_*")         ; Blocs commençant par B_  
            (2 . "C_*")         ; Blocs commençant par C_
          (-4 . "OR>")
        (-4 . "AND>")
      (-4 . "OR>")
      (-4 . "NOT>")
    )
  ))
  
  ;; Si aucun objet trouvé avec le filtre strict, essayer sans le filtre wildcard
  (if (not ss)
    (progn
      (if pm-ref (princ "\n    Aucun objet avec filtre strict, essai filtre simple..."))
      (setq ss (ssget "_C" 
        (list xmin ymin) 
        (list xmax ymax)
        '((-4 . "<NOT")
          (-4 . "<OR")
            (8 . "_CALAGE_PT")      ; Exclure seulement les calques connus
            (8 . "_CALAGE_3D_CI")   
          (-4 . "OR>")
          (-4 . "NOT>")
        )
      ))
    )
  )
  
  ss
)

;; Fonction SÉCURISÉE pour sélectionner UNIQUEMENT les objets de la coupe
(defun select-coupe-objects-only (pm-ref / ss ss-final i ent calque bloc mat)
  ;; Créer une sélection vide
  (setq ss-final (ssadd))
  
  ;; Sélectionner UNIQUEMENT :
  ;; - Les lignes, polylignes, textes, etc. (pas de blocs de calage)
  ;; - Les blocs qui ont le bon PM mais qui ne sont PAS sur les calques de calage
  
  ;; 1. Objets graphiques simples
  (if (setq ss (ssget "X" '((0 . "LINE,LWPOLYLINE,POLYLINE,TEXT,MTEXT,ARC,CIRCLE,ELLIPSE"))))
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq calque (cdr (assoc 8 (entget ent))))
        ;; Vérifier que ce n'est pas un calque de calage
        (if (and 
              (not (equal calque "_CALAGE_PT"))
              (not (equal calque "_CALAGE_3D_CI"))
              (not (wcmatch calque "*CALAGE*")))
          (ssadd ent ss-final)
        )
        (setq i (1+ i))
      )
    )
  )
  
  ;; 2. Blocs avec le bon PM (mais pas sur les calques de calage)
  (if (setq ss (ssget "X" '((0 . "INSERT"))))
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq calque (cdr (assoc 8 (entget ent))))
        ;; Si ce n'est pas un calque de calage
        (if (and 
              (not (equal calque "_CALAGE_PT"))
              (not (equal calque "_CALAGE_3D_CI"))
              (not (wcmatch calque "*CALAGE*")))
          (progn
            (setq bloc (vlax-ename->vla-object ent))
            (setq mat (get-matricule bloc))
            ;; Si le bloc a le bon PM
            (if (and mat (wcmatch mat (strcat "*_" pm-ref)))
              (ssadd ent ss-final)
            )
          )
        )
        (setq i (1+ i))
      )
    )
  )
  
  ss-final
)

(princ "\nSELECTION.LSP loaded - Version sécurisée")