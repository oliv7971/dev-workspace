;;; main.lsp
;;; Main entry point for the CALAGE 3D program

;; Obtenir le chemin du répertoire actuel
(setq *calage3d-base-path* 
  (if (findfile "main.lsp")
    (vl-filename-directory (findfile "main.lsp"))
    "c:/data/20-DEVELOPPEMENT/AutoLISP/calage coupes/calage-coupes-3d/src"
  )
)

;; Fonction pour charger un fichier avec gestion d'erreur
(defun load-calage3d-file (filename)
  (setq full-path (strcat *calage3d-base-path* "/" filename))
  (if (findfile full-path)
    (progn
      (princ (strcat "\nLoading " filename "..."))
      (load full-path)
      (princ " OK")
      T
    )
    (progn
      (princ (strcat "\nERROR: Cannot find " full-path))
      nil
    )
  )
)

;; Load necessary utility functions
(load-calage3d-file "utils/blocks.lsp")
(load-calage3d-file "utils/selection.lsp")
(load-calage3d-file "utils/alignment.lsp")

;; Load command definitions
(load-calage3d-file "commands/calage3d.lsp")
(load-calage3d-file "commands/calage3d-info.lsp")
(load-calage3d-file "commands/calage3d-auto.lsp")

(princ "\n\nCALAGE 3D program initialized.")
(princ "\nCommands loaded: CALAGE3D, CALAGE3D-INFO, CALAGE3D-AUTO")
(princ "\nBase path: ")
(princ *calage3d-base-path*)
(princ)