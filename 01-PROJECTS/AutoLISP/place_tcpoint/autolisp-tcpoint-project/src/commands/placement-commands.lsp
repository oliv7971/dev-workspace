;; placement-commands.lsp
;; This file defines commands related to the placement of TCPOINT blocks,
;; including automatic and manual placement modes.

(defun c:place-tcpoint-auto (/ doc ms centres entities)
  (princ "\n=== PLACEMENT AUTOMATIQUE DE BLOCS TCPOINT ===")
  
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        ms  (vla-get-ModelSpace doc))
  
  ;; Collecter les centres
  (setq centres (_collect-centers))
  (if centres
    (progn
      (princ (strcat "\n" (itoa (length centres)) " centres trouvés."))
      ;; Collecter les entités
      (setq entities (_collect-entities))
      (if entities
        (progn
          (princ (strcat "\n" (itoa (length entities)) " entités trouvées."))
          (placer-tcpoints-auto entities centres *RAYON-PROXIMITE*)
        )
        (princ "\nAucune entité trouvée.")
      )
    )
    (princ "\nAucun centre trouvé.")
  )
  
  (princ)
)

(defun c:place-tcpoint-manual (/ doc ms centre entities)
  (princ "\n=== PLACEMENT MANUEL DE BLOCS TCPOINT ===")
  
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        ms  (vla-get-ModelSpace doc))
  
  ;; Sélectionner les entités
  (setq entities (ssget))
  (if entities
    (progn
      (princ (strcat "\n" (itoa (sslength entities)) " entités sélectionnées."))
      (setq centre (getpoint "\nCliquez pour définir le centre de référence : "))
      (if centre
        (placer-tcpoints entities centre)
        (princ "\nAnnulé.")
      )
    )
    (princ "\nAucune sélection.")
  )
  
  (princ)
)

;; Autres commandes peuvent être ajoutées ici pour gérer des fonctionnalités supplémentaires.