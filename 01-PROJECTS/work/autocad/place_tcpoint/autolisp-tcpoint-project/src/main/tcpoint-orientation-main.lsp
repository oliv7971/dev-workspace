;; TCPOINT-ORIENTATION-MAIN.LSP v1.0
;; =============================================================================
;; Fichier principal pour charger le système de correction d'orientation TCPOINT
;; =============================================================================

;; ======================= FONCTIONS DE COMPATIBILITÉ =======================

(defun tcp:function-exists-p (func-name)
  "Vérifie si une fonction existe (alternative à fboundp)"
  (and func-name
       (not (null (eval func-name)))))

;; ======================= CHARGEMENT SYSTÈME =======================

(defun load-tcpoint-orientation-system ()
  "Charge tous les composants du système"
  
  ; Charger Visual LISP si nécessaire
  (if (not (boundp 'vl-load-com))
    (vl-load-com))
  
  ; Charger la configuration (depuis le répertoire courant)
  (if (findfile "tcpoint-orientation-config.lsp")
    (progn
      (load "tcpoint-orientation-config.lsp")
      (princ "\n[OK] Configuration chargee"))
    (princ "\n[ERREUR] Fichier tcpoint-orientation-config.lsp non trouve"))
  
  ; Charger le module principal
  (if (findfile "tcpoint-orientation-fixer.lsp")
    (progn
      (load "tcpoint-orientation-fixer.lsp")
      (princ "\n[OK] Module principal charge"))
    (princ "\n[ERREUR] Fichier tcpoint-orientation-fixer.lsp non trouve"))
  
  ; Charger les exemples (optionnel)
  (if (findfile "tcpoint-orientation-examples.lsp")
    (progn
      (load "tcpoint-orientation-examples.lsp")
      (princ "\n[OK] Exemples charges"))
    (princ "\n[INFO] Fichier tcpoint-orientation-examples.lsp non trouve (optionnel)"))
  
  (princ "\n=== SYSTÈME TCPOINT-ORIENTATION PRÊT ==="))

; Charger automatiquement le système au démarrage
(load-tcpoint-orientation-system)

; Message de confirmation de chargement
(princ "\n\n╔══════════════════════════════════════════════╗")
(princ "\n║ SYSTÈME TCPOINT-ORIENTATION v1.0 - CHARGÉ   ║")
(princ "\n╚══════════════════════════════════════════════╝\n")

;; ======================= COMMANDES RAPIDES =======================

(defun c:TCFIX ()
  "Raccourci: Correction rapide de la sélection"
  (if (not (tcp:function-exists-p 'c:TCPOINT-FIX-SELECTION))
    (progn
      (princ "\n[INFO] Systeme non charge ! Chargement en cours...")
      (load-tcpoint-orientation-system)))
  (if (tcp:function-exists-p 'c:TCPOINT-FIX-SELECTION)
    (progn
      (princ "\n[INFO] Lancement de la correction...")
      (c:TCPOINT-FIX-SELECTION))
    (princ "\n[ERREUR] Impossible de charger le systeme TCPOINT"))
  (princ))

(defun c:TCFIXALL ()
  "Raccourci: Correction de tous les TCPOINT"
  (if (not (tcp:function-exists-p 'c:TCPOINT-FIX-ALL))
    (progn
      (princ "\n[INFO] Systeme non charge ! Chargement en cours...")
      (load-tcpoint-orientation-system)))
  (if (tcp:function-exists-p 'c:TCPOINT-FIX-ALL)
    (progn
      (princ "\n[INFO] Correction de tous les TCPOINT...")
      (c:TCPOINT-FIX-ALL))
    (princ "\n[ERREUR] Impossible de charger le systeme TCPOINT"))
  (princ))

(defun c:TCCHECK ()
  "Raccourci: Vérification rapide"
  (if (not (tcp:function-exists-p 'c:TCPOINT-CHECK-ORIENTATION))
    (progn
      (princ "\n[INFO] Systeme non charge ! Chargement en cours...")
      (load-tcpoint-orientation-system)))
  (if (tcp:function-exists-p 'c:TCPOINT-CHECK-ORIENTATION)
    (progn
      (princ "\n[INFO] Verification de l'orientation...")
      (c:TCPOINT-CHECK-ORIENTATION))
    (princ "\n[ERREUR] Impossible de charger le systeme TCPOINT"))
  (princ))

;; ======================= MENU INTERACTIF =======================

(defun c:TCPOINT-MENU ()
  "Menu interactif pour le système TCPOINT"
  (princ "\n╔══════════════════════════════════════════════╗")
  (princ "\n║          MENU TCPOINT-ORIENTATION            ║")
  (princ "\n╠══════════════════════════════════════════════╣")
  (princ "\n║ 1. TCFIX     - Corriger sélection           ║")
  (princ "\n║ 2. TCFIXALL  - Corriger tous les TCPOINT    ║")
  (princ "\n║ 3. TCCHECK   - Vérifier orientation         ║")
  (princ "\n║ 4. TCP-CONFIG - Configuration               ║")
  (princ "\n║ 5. Quitter                                   ║")
  (princ "\n╚══════════════════════════════════════════════╝")
  
  (setq user-choice (getstring "\nVotre choix (1-5): "))
  (cond
    ((= user-choice "1") 
     (princ "\nExecution de TCFIX...")
     (c:TCFIX))
    ((= user-choice "2") 
     (princ "\nExecution de TCFIXALL...")
     (c:TCFIXALL))
    ((= user-choice "3") 
     (princ "\nExecution de TCCHECK...")
     (c:TCCHECK))
    ((= user-choice "4") 
     (if (tcp:function-exists-p 'c:TCP-CONFIG)
       (progn
         (princ "\nOuverture de la configuration...")
         (c:TCP-CONFIG))
       (princ "\n[ERREUR] Configuration non disponible")))
    ((= user-choice "5") 
     (princ "\nAu revoir !"))
    (t 
     (princ "\nChoix invalide. Tapez TCPOINT-MENU pour recommencer.")))
  (princ))

(defun c:TCP-MENU ()
  "Alias pour le menu"
  (c:TCPOINT-MENU))

; Message d'information
(princ "\n\nSystème TCPOINT-ORIENTATION chargé !")
(princ "\nTapez TCPOINT-MENU pour commencer.")
(princ)