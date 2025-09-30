;;------------ Ordre de tracé ------------;;

;; gc:GetSortentsTable
;; Retourne la table d'ordre de tracé du block record (bloc ou espace)
;;
;; Argument
;; block : le block record
;; 
;; Fonctions requises :
;; - gc:GetObject (gc_AutomationHelpers.lsp))
(defun gc:GetSortentsTable (block / sort)
  (cond
    ((gc:GetObject (vla-GetExtensionDictionary block) "ACAD_SORTENTS"))
    ((vla-AddObject (vla-GetExtensionDictionary block) "ACAD_SORTENTS" "AcDbSortentsTable"))
  )
)

;; gc:MoveToTop
;; Place les objets en avant (draworder)
;;
;; Argument
;; blk : le block record auquel appartiennent les objets
;; olst : liste des objets à placer en avant (vla-objects)
(defun gc:MoveToTop (blk olst)
  (vlax-invoke (gc:GetSortentsTable blk) 'MoveToTop olst)
)

;; gc:MoveToBottom
;; Place les objets en arrière (draworder)
;;
;; Argument
;; blk : le block record auquel appartiennent les objets
;; olst : liste des objets à placer en arrière (vla-objects)
(defun gc:MoveToBottom (blk olst)
  (vlax-invoke (gc:GetSortentsTable blk) 'MoveToBottom olst)
)

;; gc:MoveAbove
;; Place les objets devant l'objet cible (draworder)
;;
;; Argument
;; blk : le block record auquel appartiennent les objets
;; olst : liste des objets à placer devant (vla-objects)
;; targ : objet cible (vla-object)
(defun gc:MoveAbove (blk olst targ)
  (vlax-invoke (gc:GetSortentsTable blk) 'MoveAbove olst targ)
)

;; gc:MoveBelow
;; Place les objets derrière l'objet cible (draworder)
;;
;; Argument
;; blk : le block record auquel appartiennent les objets
;; olst : liste des objets à placer derrière (vla-objects)
;; targ : objet cible (vla-object)
(defun gc:MoveBelow (blk olst targ)
  (vlax-invoke (gc:GetSortentsTable blk) 'MoveBelow olst targ)
)

;; gc:SetRelativeDrawOrder
;; Place les objets dans l'ordre de la liste
;;
;; Argument
;; blk : le block record auquel appartiennent les objets
;; olst : liste des objets à trier (vla-objects)
(defun gc:SetRelativeDrawOrder (blk olst)
  (vlax-invoke (gc:GetSortentsTable blk) 'SetRelativeDrawOrder olst)
)