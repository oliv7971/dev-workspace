;;; blocks.lsp
;;; Utility functions for handling blocks in the 3D alignment process

;; Function to extract attributes from a block
(defun get-block-attributes (block / attributes)
  (setq attributes nil)
  (foreach att (vlax-invoke block 'GetAttributes)
    (setq attributes (cons (list (vla-get-TagString att) (vla-get-TextString att)) attributes))
  )
  attributes
)

;; Function to get the insertion point of a block
(defun get-insertion-point (block)
  (vlax-get block 'InsertionPoint)
)

;; Function to collect blocks from a specific layer
(defun collect-blocks-from-layer (layer-name / ss i block attributes insertion-point blocks-list)
  (setq blocks-list '())
  (if (setq ss (ssget "X" (list (cons 0 "INSERT") (cons 8 layer-name))))
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq block (vlax-ename->vla-object (ssname ss i)))
        (setq attributes (get-block-attributes block))
        (setq insertion-point (get-insertion-point block))
        (setq blocks-list (cons (list attributes insertion-point block) blocks-list))
        (setq i (1+ i))
      )
    )
  )
  blocks-list
)


;; filepath: c:\data\20-DEVELOPPEMENT\AutoLISP\calage coupes\calage-coupes-3d\src\utils\blocks.lsp
;;; BLOCKS.LSP
;;; Utility functions for working with blocks

(vl-load-com)

;; Fonction pour extraire le matricule d'un bloc
(defun get-matricule (bloc / att mat)
  (setq mat nil)
  (foreach att (vlax-invoke bloc 'GetAttributes)
    (if (= (vla-get-TagString att) "MAT")
      (setq mat (vla-get-TextString att))
    )
  )
  mat
)

;; Fonction pour obtenir le point d'insertion d'un bloc
(defun get-point (bloc)
  (vlax-get bloc 'InsertionPoint)
)

;; Fonction pour collecter les blocs d'un calque avec leurs matricules
(defun collect-blocks (calque / ss i bloc mat pt liste)
  (setq liste '())
  (if (setq ss (ssget "X" (list (cons 0 "INSERT") (cons 8 calque))))
    (progn
      (setq i 0)
      (repeat (sslength ss)
        (setq bloc (vlax-ename->vla-object (ssname ss i)))
        (setq mat (get-matricule bloc))
        (setq pt (get-point bloc))
        (if mat
          (setq liste (cons (list mat pt bloc) liste))
        )
        (setq i (1+ i))
      )
    )
  )
  liste
)

;; Fonction pour trouver les correspondances entre les listes
(defun find-pairs (liste-calage liste-3d / paires mat1 item2)
  (setq paires '())
  (foreach item1 liste-calage
    (setq mat1 (car item1))
    (setq item2 (assoc mat1 liste-3d))
    (if item2
      (setq paires (cons (list item1 item2) paires))
    )
  )
  paires
)

(princ "\nBLOCKS.LSP loaded")


(princ "\nUtility functions for block handling loaded.")