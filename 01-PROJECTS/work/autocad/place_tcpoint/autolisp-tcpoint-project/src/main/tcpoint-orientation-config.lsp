;; TCPOINT-ORIENTATION-CONFIG.LSP v1.0
;; =============================================================================
;; Configuration pour le correcteur d'orientation TCPOINT
;; =============================================================================

;; ======================= PARAMETRES DE CONFIGURATION =======================

;; Noms de blocs TCPOINT reconnus (insensible à la casse)
(setq *TCPOINT_BLOCKS* '("TCPOINT" "tcpoint" "POINT" "point" "PT" "pt" "TC_POINT" "tc_point"))

;; Mode de fonctionnement
(setq *DEBUG_MODE* T)                    ; T = affiche les détails, nil = mode silencieux
(setq *USE_RECREATION_METHOD* T)         ; T = recréer les blocs, nil = rotation en place

;; Tolérance pour la détection d'orientation
(setq *ORIENTATION_TOLERANCE* 0.05)      ; Tolérance pour considérer deux vecteurs comme parallèles

;; Calques spécifiques Covadis (pour filtrage optionnel)
(setq *COVADIS_LAYERS* '(
  "_CALAGE_PT"           ; Points de calage
  "_CALAGE_3D_CI"        ; Points 3D Covadis
  "_INTERSEC_AXE_2D"     ; Points d'intersection
  "TCPOINT_LAYER"        ; Calque standard TCPOINT
  "TOPO_POINTS"          ; Points topographiques
))

;; Options de sauvegarde
(setq *BACKUP_ENABLED* T)                ; Créer une sauvegarde avant correction
(setq *LOG_CORRECTIONS* T)               ; Enregistrer les corrections dans un fichier log

;; ======================= FONCTIONS D'AIDE A LA CONFIGURATION =======================

(defun tcp-config:add-block-type (blockname)
  "Ajoute un nouveau type de bloc TCPOINT à reconnaître"
  (if (not (member (strcase blockname) (mapcar 'strcase *TCPOINT_BLOCKS*)))
    (setq *TCPOINT_BLOCKS* (cons blockname *TCPOINT_BLOCKS*)))
  (princ (strcat "\nType de bloc ajouté: " blockname)))

(defun tcp-config:remove-block-type (blockname)
  "Retire un type de bloc TCPOINT de la liste"
  (setq *TCPOINT_BLOCKS* 
    (vl-remove-if 
      '(lambda (x) (= (strcase x) (strcase blockname))) 
      *TCPOINT_BLOCKS*))
  (princ (strcat "\nType de bloc retiré: " blockname)))

(defun tcp-config:set-tolerance (tolerance)
  "Définit la tolérance de détection d'orientation"
  (if (and (numberp tolerance) (> tolerance 0) (< tolerance 1))
    (progn
      (setq *ORIENTATION_TOLERANCE* tolerance)
      (princ (strcat "\nTolérance définie à: " (rtos tolerance))))
    (princ "\nErreur: La tolérance doit être un nombre entre 0 et 1")))

(defun tcp-config:toggle-debug ()
  "Bascule le mode debug"
  (setq *DEBUG_MODE* (not *DEBUG_MODE*))
  (princ (strcat "\nMode debug: " (if *DEBUG_MODE* "ACTIF" "INACTIF"))))

(defun tcp-config:toggle-method ()
  "Bascule entre recréation et rotation"
  (setq *USE_RECREATION_METHOD* (not *USE_RECREATION_METHOD*))
  (princ (strcat "\nMéthode: " (if *USE_RECREATION_METHOD* "RECREATION" "ROTATION"))))

;; ======================= COMMANDES DE CONFIGURATION =======================

(defun c:TCP-CONFIG ()
  "Affiche la configuration actuelle"
  (princ "\n=== CONFIGURATION TCPOINT-ORIENTATION-FIXER ===")
  (princ (strcat "\nTypes de blocs reconnus: " (vl-string-join *TCPOINT_BLOCKS* ", ")))
  (princ (strcat "\nMode debug: " (if *DEBUG_MODE* "ACTIF" "INACTIF")))
  (princ (strcat "\nMéthode: " (if *USE_RECREATION_METHOD* "RECREATION" "ROTATION")))
  (princ (strcat "\nTolérance: " (rtos *ORIENTATION_TOLERANCE*)))
  (princ "\n=== Commandes de configuration ===")
  (princ "\n- TCP-CONFIG-ADD-BLOCK    : Ajouter un type de bloc")
  (princ "\n- TCP-CONFIG-REMOVE-BLOCK : Retirer un type de bloc") 
  (princ "\n- TCP-CONFIG-TOLERANCE    : Définir la tolérance")
  (princ "\n- TCP-CONFIG-DEBUG        : Basculer le mode debug")
  (princ "\n- TCP-CONFIG-METHOD       : Basculer la méthode")
  (princ))

(defun c:TCP-CONFIG-ADD-BLOCK ()
  "Ajoute un nouveau type de bloc TCPOINT"
  (let ((blockname (getstring "\nNom du type de bloc à ajouter: ")))
    (if (/= blockname "")
      (tcp-config:add-block-type blockname)
      (princ "\nAnnulé."))))

(defun c:TCP-CONFIG-REMOVE-BLOCK ()
  "Retire un type de bloc TCPOINT"
  (let ((blockname (getstring "\nNom du type de bloc à retirer: ")))
    (if (/= blockname "")
      (tcp-config:remove-block-type blockname)
      (princ "\nAnnulé."))))

(defun c:TCP-CONFIG-TOLERANCE ()
  "Définit la tolérance de détection"
  (let ((tolerance (getreal "\nTolérance (0.01 à 0.5, défaut 0.05): ")))
    (if tolerance
      (tcp-config:set-tolerance tolerance)
      (princ "\nAnnulé."))))

(defun c:TCP-CONFIG-DEBUG ()
  "Bascule le mode debug"
  (tcp-config:toggle-debug))

(defun c:TCP-CONFIG-METHOD ()
  "Bascule la méthode de correction"
  (tcp-config:toggle-method))

(princ "\n=== CONFIG TCPOINT-ORIENTATION chargée ===")
(princ "\nTapez TCP-CONFIG pour voir la configuration actuelle")
