;; layer-management.lsp
;; This file contains functions for managing layers in the drawing,
;; including creating new layers and checking for existing layers.

(vl-load-com)

;; Ensure a layer exists in the drawing
(defun ensure-layer (doc name / layers layer)
  (setq layers (vla-get-Layers doc))
  (if (not (tblsearch "LAYER" name))
    (progn 
      (setq layer (vla-Add layers name)) 
      (vla-put-Color layer 3)  ;; Set layer color to red
      (princ (strcat "\nLayer '" name "' created"))
    )
    (setq layer (vla-Item layers name)))
  layer)

;; Check if a layer exists
(defun layer-exists? (name /)
  (if (tblsearch "LAYER" name) T nil))

;; Set the current layer
(defun set-current-layer (name /)
  (if (layer-exists? name)
    (setvar "CLAYER" name)
    (princ (strcat "\nLayer '" name "' does not exist."))))

;; Get the current layer
(defun get-current-layer (/)
  (getvar "CLAYER"))

;; List all layers in the drawing
(defun list-layers (/ layers layer-names)
  (setq layers (vla-get-Layers (vla-get-ActiveDocument (vlax-get-acad-object))))
  (setq layer-names '())
  (vlax-for layer layers
    (setq layer-names (cons (vla-get-Name layer) layer-names)))
  (reverse layer-names))

(princ "\nLayer management functions loaded.")