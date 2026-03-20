;; This file contains functions for operations related to blocks,
;; such as inserting blocks into the drawing and managing block references.

(defun insert-block (block-name insertion-point / block-ref)
  (if (tblsearch "BLOCK" block-name)
    (progn
      (setq block-ref (vla-InsertBlock
                        (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-acad-object)))
                        (vlax-3d-point insertion-point)
                        block-name
                        1.0 1.0 1.0 0.0))
      (princ (strcat "\nBlock '" block-name "' inserted at " (vl-princ-to-string insertion-point)))
      block-ref
    )
    (progn
      (princ (strcat "\nError: Block '" block-name "' does not exist."))
      nil
    )
  )
)

(defun delete-block-reference (block-ref /)
  (if block-ref
    (progn
      (vla-delete block-ref)
      (princ "\nBlock reference deleted.")
    )
    (princ "\nError: No valid block reference provided.")
  )
)

(defun get-block-attributes (block-ref / attributes)
  (setq attributes nil)
  (if block-ref
    (progn
      (setq attributes (vla-get-Attributes block-ref))
      (if attributes
        (progn
          (princ "\nBlock attributes:")
          (foreach attr attributes
            (princ (strcat "\n  " (vla-get-TagString attr) ": " (vla-get-TextString attr)))
          )
        )
        (princ "\nNo attributes found for this block.")
      )
    )
    (princ "\nError: No valid block reference provided.")
  )
)

(princ "\nBlock operations functions loaded.")