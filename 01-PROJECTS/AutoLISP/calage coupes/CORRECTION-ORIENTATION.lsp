;;; CORRECTION-ORIENTATION.LSP
;;; Programme pour corriger l'orientation des symboles après transformation 3D
;;; Supprime et recrée les points/tcpoint pour maintenir l'orientation SCU

(vl-load-com)

;; ============================================
;; FONCTIONS UTILITAIRES
;; ============================================

;; Fonction pour récupérer les propriétés d'un bloc avant suppression
(defun get-block-properties (ent / entdata bloc props attrs att-list att)
  (setq entdata (entget ent))
  (setq bloc (vlax-ename->vla-object ent))
  
  ;; Propriétés de base
  (setq props (list
    (cons "Name" (cdr (assoc 2 entdata)))           ; Nom du bloc
    (cons "Layer" (cdr (assoc 8 entdata)))          ; Calque
    (cons "InsertionPoint" (cdr (assoc 10 entdata))) ; Point d'insertion
    (cons "Scale" (list 
      (cdr (assoc 41 entdata))                      ; Échelle X
      (cdr (assoc 42 entdata))                      ; Échelle Y
      (cdr (assoc 43 entdata))))                    ; Échelle Z
    (cons "Rotation" (cdr (assoc 50 entdata)))      ; Rotation
  ))
  
  ;; Récupérer les attributs
  (setq att-list '())
  (if (vlax-property-available-p bloc 'HasAttributes)
    (if (= :vlax-true (vla-get-HasAttributes bloc))
      (progn
        (foreach att (vlax-invoke bloc 'GetAttributes)
          (setq att-list (cons 
            (list 
              (vla-get-TagString att)
              (vla-get-TextString att)
              (vla-get-Height att)
              (vla-get-Rotation att)
            ) 
            att-list))
        )
      )
    )
  )
  
  (setq props (cons (cons "Attributes" att-list) props))
  props
)

;; Fonction pour recréer un bloc avec ses propriétés
(defun recreate-block (props / nom calque pt-ins echelles rotation attributs nouveau-bloc att-props tag valeur hauteur rot-att)
  (setq nom (cdr (assoc "Name" props)))
  (setq calque (cdr (assoc "Layer" props)))
  (setq pt-ins (cdr (assoc "InsertionPoint" props)))
  (setq echelles (cdr (assoc "Scale" props)))
  (setq rotation (cdr (assoc "Rotation" props)))
  (setq attributs (cdr (assoc "Attributes" props)))
  
  ;; Créer le nouveau bloc
  (command "_INSERT" nom pt-ins 
           (if (car echelles) (car echelles) 1.0)    ; Échelle X
           (if (cadr echelles) (cadr echelles) 1.0)  ; Échelle Y
           0.0)                                      ; Rotation = 0 pour orientation SCU
  
  ;; Récupérer le bloc créé
  (setq nouveau-bloc (vlax-ename->vla-object (entlast)))
  
  ;; Définir le calque
  (vla-put-Layer nouveau-bloc calque)
  
  ;; Mettre à jour les attributs avec rotation 0
  (if (and attributs (vlax-property-available-p nouveau-bloc 'HasAttributes))
    (if (= :vlax-true (vla-get-HasAttributes nouveau-bloc))
      (progn
        (foreach att (vlax-invoke nouveau-bloc 'GetAttributes)
          (setq tag (vla-get-TagString att))
          (setq att-props (assoc tag attributs))
          (if att-props
            (progn
              (setq valeur (cadr att-props))
              (setq hauteur (caddr att-props))
              ; Rotation = 0 pour maintenir orientation SCU
              (vla-put-TextString att valeur)
              (if hauteur (vla-put-Height att hauteur))
              (vla-put-Rotation att 0.0)  ; ORIENTATION SCU !
            )
          )
        )
        (vla-Update nouveau-bloc)
      )
    )
  )
  
  nouveau-bloc
)

;; ============================================
;; FONCTION PRINCIPALE
;; ============================================

;; Fonction pour corriger l'orientation des symboles dans une sélection
(defun corriger-orientation-selection (ss / i ent entdata type-obj props nouveau-bloc liste-props)
  (if ss
    (progn
      (princ (strcat "\nCorrection de l'orientation de " (itoa (sslength ss)) " objets..."))
      
      ;; 1. Collecter les propriétés de tous les blocs
      (setq liste-props '())
      (setq i 0)
      (repeat (sslength ss)
        (setq ent (ssname ss i))
        (setq entdata (entget ent))
        (setq type-obj (cdr (assoc 0 entdata)))
        
        ;; Ne traiter que les INSERTs (blocs)
        (if (= type-obj "INSERT")
          (progn
            (setq props (get-block-properties ent))
            (setq liste-props (cons (cons ent props) liste-props))
          )
        )
        (setq i (1+ i))
      )
      
      (princ (strcat "\n" (itoa (length liste-props)) " blocs à corriger..."))
      
      ;; 2. Supprimer tous les blocs d'origine
      (foreach item liste-props
        (entdel (car item))
      )
      
      (princ "\nBlocs supprimés. Recréation en cours...")
      
      ;; 3. Recréer tous les blocs avec orientation SCU
      (foreach item liste-props
        (setq props (cdr item))
        (recreate-block props)
      )
      
      (princ "\n✓ Correction d'orientation terminée !")
    )
    (princ "\nAucun objet sélectionné.")
  )
)

;; ============================================
;; COMMANDES UTILISATEUR
;; ============================================

;; Commande pour corriger l'orientation des objets sélectionnés
(defun c:CORRIGER-ORIENTATION ( / ss)
  (princ "\nSélectionnez les blocs à corriger (points, tcpoint, symboles) : ")
  (setq ss (ssget '((0 . "INSERT"))))
  
  (if ss
    (corriger-orientation-selection ss)
    (princ "\nAucun bloc sélectionné.")
  )
  
  (princ)
)

;; Commande pour corriger automatiquement tous les points des calques spécifiés
(defun c:CORRIGER-POINTS-AUTO ( / ss calques-cibles calque)
  (setq calques-cibles '("_CALAGE_PT" "_CALAGE_3D_CI" "POINTS" "TCPOINT"))
  
  (princ "\nCorrection automatique des points sur les calques :")
  (foreach calque calques-cibles
    (princ (strcat "\n  - " calque))
  )
  
  ;; Sélectionner tous les blocs des calques cibles
  (setq ss (ssget "X" (list 
    (cons 0 "INSERT")
    (cons 8 (strcat (car calques-cibles) "," 
                    (cadr calques-cibles) ","
                    (caddr calques-cibles) ","
                    (cadddr calques-cibles)))
  )))
  
  (if ss
    (corriger-orientation-selection ss)
    (princ "\nAucun point trouvé sur ces calques.")
  )
  
  (princ)
)

;; Commande pour corriger les points d'un calque spécifique
(defun c:CORRIGER-CALQUE ( / nom-calque ss)
  (initget 1)
  (setq nom-calque (getstring "\nNom du calque à corriger : "))
  
  (setq ss (ssget "X" (list 
    (cons 0 "INSERT")
    (cons 8 nom-calque)
  )))
  
  (if ss
    (progn
      (princ (strcat "\nTrouvé " (itoa (sslength ss)) " blocs sur le calque " nom-calque))
      (corriger-orientation-selection ss)
    )
    (princ (strcat "\nAucun bloc trouvé sur le calque " nom-calque))
  )
  
  (princ)
)

;; Commande pour corriger uniquement les points de calage après CALAGE3D
(defun c:CORRIGER-APRES-CALAGE ( / ss-pt ss-3d ss-total)
  (princ "\nCorrection spécifique après CALAGE3D...")
  
  ;; Sélectionner les points des calques de calage
  (setq ss-pt (ssget "X" '((0 . "INSERT") (8 . "_CALAGE_PT"))))
  (setq ss-3d (ssget "X" '((0 . "INSERT") (8 . "_CALAGE_3D_CI"))))
  
  ;; Combiner les sélections
  (setq ss-total (ssadd))
  (if ss-pt
    (progn
      (setq i 0)
      (repeat (sslength ss-pt)
        (ssadd (ssname ss-pt i) ss-total)
        (setq i (1+ i))
      )
    )
  )
  (if ss-3d
    (progn
      (setq i 0)
      (repeat (sslength ss-3d)
        (ssadd (ssname ss-3d i) ss-total)
        (setq i (1+ i))
      )
    )
  )
  
  (if (> (sslength ss-total) 0)
    (corriger-orientation-selection ss-total)
    (princ "\nAucun point de calage trouvé.")
  )
  
  (princ)
)

;; ============================================
;; FONCTION D'INTEGRATION AVEC CALAGE3D
;; ============================================

;; Fonction modifiée de calage avec correction automatique
(defun calage-avec-correction (liste-calage-pm liste-3d pm-nom / resultat ss-correction)
  ;; Effectuer le calage normal
  (setq resultat (calage-une-coupe liste-calage-pm liste-3d pm-nom))
  
  ;; Si le calage a réussi, corriger l'orientation
  (if resultat
    (progn
      (princ "\n  📐 Correction de l'orientation des symboles...")
      
      ;; Sélectionner tous les blocs dans la zone de la coupe
      (setq ss-correction (ssget "X" (list 
        (cons 0 "INSERT")
        (cons -4 "<NOT")
        (cons -4 "<OR")
          (cons 8 "_CALAGE_PT")
          (cons 8 "_CALAGE_3D_CI")
        (cons -4 "OR>")
        (cons -4 "NOT>")
      )))
      
      ;; Corriger uniquement dans la zone concernée
      (if ss-correction
        (progn
          ;; Ici on pourrait filtrer par zone si nécessaire
          (corriger-orientation-selection ss-correction)
        )
      )
    )
  )
  
  resultat
)

(princ "\nCORRECTION-ORIENTATION.LSP chargé")
(princ "\nCommandes disponibles :")
(princ "\n  CORRIGER-ORIENTATION     - Corrige les objets sélectionnés")
(princ "\n  CORRIGER-POINTS-AUTO     - Corrige tous les points automatiquement")
(princ "\n  CORRIGER-CALQUE         - Corrige un calque spécifique")
(princ "\n  CORRIGER-APRES-CALAGE   - Corrige après un CALAGE3D")
(princ)