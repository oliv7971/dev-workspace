;;; Configuration des couches pour le projet CALAGE3D
;;; Ce fichier définit les couches à inclure ou exclure lors des opérations

;; Définir les couches de calage
(setq layers-calage
      '("_CALAGE_PT"  ; Couche pour les points de calage
        "_CALAGE_3D_CI"  ; Couche pour les objets 3D à aligner
      )
)

;; Définir les couches à exclure si nécessaire
(setq layers-exclusion
      '("_CALAGE_PT_EXCLURE"  ; Exemple de couche à exclure
      )
)

(princ "\nConfiguration des couches chargée.")