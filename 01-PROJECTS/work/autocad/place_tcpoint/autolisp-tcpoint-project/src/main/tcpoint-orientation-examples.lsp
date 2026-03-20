;; TCPOINT-ORIENTATION-EXAMPLES.LSP v1.0
;; =============================================================================
;; Exemples d'utilisation et tests pour le correcteur d'orientation TCPOINT
;; =============================================================================

;; ======================= EXEMPLES D'UTILISATION =======================

(defun example:fix-all-tcpoints ()
  "Exemple: Corriger tous les TCPOINT du dessin"
  (princ "\n=== EXEMPLE: Correction de tous les TCPOINT ===")
  (princ "\nCette fonction va:")
  (princ "\n1. Rechercher tous les blocs TCPOINT dans le dessin")
  (princ "\n2. Vérifier leur orientation par rapport au SCU courant")  
  (princ "\n3. Corriger ceux qui sont mal orientés")
  (princ "\n")
  
  ; Activer le mode debug pour voir les détails
  (setq old-debug *DEBUG_MODE*)
  (setq *DEBUG_MODE* T)
  
  ; Lancer la correction
  (c:TCPOINT-FIX-ALL)
  
  ; Restaurer le mode debug
  (setq *DEBUG_MODE* old-debug)
  
  (princ "\n=== Exemple terminé ==="))

(defun example:fix-specific-layer ()
  "Exemple: Corriger les TCPOINT d'un calque spécifique"
  (princ "\n=== EXEMPLE: Correction par calque ===")
  (princ "\nCet exemple corrige les TCPOINT sur le calque '_CALAGE_PT'")
  
  ; Forcer le nom du calque pour l'exemple
  (let ((ss (ssget "X" '((0 . "INSERT") (8 . "_CALAGE_PT")))))
    (if ss
      (progn
        (princ (strcat "\n" (itoa (sslength ss)) " blocs trouvés sur le calque _CALAGE_PT"))
        (tcp:fix-selected-blocks ss))
      (princ "\nAucun bloc trouvé sur le calque _CALAGE_PT")))
  
  (princ "\n=== Exemple terminé ==="))

;; ======================= TESTS DE VALIDATION =======================

(defun test:create-test-scenario ()
  "Crée un scénario de test avec des TCPOINT mal orientés"
  (princ "\n=== TEST: Création de scénario ===")
  
  ; Créer quelques blocs TCPOINT pour tester
  ; (Cette fonction nécessiterait que le bloc TCPOINT existe dans le dessin)
  
  (let ((doc (vla-get-ActiveDocument (vlax-get-acad-object)))
        (mspace (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-acad-object)))))
    
    ; Vérifier si le bloc TCPOINT existe
    (if (tblsearch "BLOCK" "TCPOINT")
      (progn
        (princ "\nCréation de blocs TCPOINT de test...")
        
        ; Insérer quelques blocs à différentes positions
        (vla-InsertBlock mspace (vlax-3d-point '(0 0 0)) "TCPOINT" 1.0 1.0 1.0 0.0)
        (vla-InsertBlock mspace (vlax-3d-point '(100 0 0)) "TCPOINT" 1.0 1.0 1.0 0.0)
        (vla-InsertBlock mspace (vlax-3d-point '(0 100 0)) "TCPOINT" 1.0 1.0 1.0 0.0)
        
        (princ "\n3 blocs TCPOINT créés pour test")
        (princ "\nMaintenez changez le SCU et testez la correction"))
      (princ "\nErreur: Le bloc TCPOINT n'existe pas dans ce dessin")))
  
  (princ "\n=== Test setup terminé ==="))

(defun test:orientation-detection ()
  "Test de détection d'orientation"
  (princ "\n=== TEST: Détection d'orientation ===")
  
  (let ((ss (ssget "X" '((0 . "INSERT"))))
        (count-total 0) (count-ok 0) (count-bad 0) (i 0))
    
    (if ss
      (progn
        (princ (strcat "\nAnalyse de " (itoa (sslength ss)) " blocs INSERT..."))
        
        (setq i 0)
        (while (< i (sslength ss))
          (let ((ename (ssname ss i)))
            (if (tcp:is-tcpoint-block? ename)
              (progn
                (setq count-total (1+ count-total))
                (if (tcp:block-orientation-ok? ename)
                  (setq count-ok (1+ count-ok))
                  (setq count-bad (1+ count-bad))))))
          (setq i (1+ i)))
        
        (princ (strcat "\nRésultats:"))
        (princ (strcat "\n- Total TCPOINT: " (itoa count-total)))
        (princ (strcat "\n- Bien orientés: " (itoa count-ok)))
        (princ (strcat "\n- Mal orientés: " (itoa count-bad))))
      (princ "\nAucun bloc INSERT trouvé")))
  
  (princ "\n=== Test terminé ==="))

(defun test:performance ()
  "Test de performance sur un grand nombre de blocs"
  (princ "\n=== TEST: Performance ===")
  
  (let ((start-time (getvar "MILLISECS"))
        (ss (ssget "X" '((0 . "INSERT"))))
        (end-time nil) (elapsed nil) (i 0))
    
    (if ss
      (progn
        (princ (strcat "\nTest de performance sur " (itoa (sslength ss)) " blocs..."))
        
        ; Simuler le processus de vérification sans correction
        (setq i 0)
        (while (< i (sslength ss))
          (let ((ename (ssname ss i)))
            (if (tcp:is-tcpoint-block? ename)
              (tcp:block-orientation-ok? ename)))
          (setq i (1+ i)))
        
        (setq end-time (getvar "MILLISECS")
              elapsed (- end-time start-time))
        
        (princ (strcat "\nTemps écoulé: " (itoa elapsed) " millisecondes"))
        (princ (strcat "\nMoyenne: " (rtos (/ elapsed (sslength ss)) 2 3) " ms par bloc")))
      (princ "\nAucun bloc pour le test"))
    
    (princ "\n=== Test terminé ===")))

;; ======================= UTILITAIRES DE DIAGNOSTIC =======================

(defun diag:ucs-info ()
  "Affiche des informations sur le SCU courant"
  (princ "\n=== DIAGNOSTIC: Informations SCU ===")
  
  (let ((ucs-origin (getvar "UCSORG"))
        (ucs-xdir (getvar "UCSXDIR"))
        (ucs-ydir (getvar "UCSYDIR"))
        (ucs-name (getvar "UCSNAME")))
    
    (princ (strcat "\nNom du SCU: " (if ucs-name ucs-name "WORLD")))
    (princ (strcat "\nOrigine: " (vl-princ-to-string ucs-origin)))
    (princ (strcat "\nDirection X: " (vl-princ-to-string ucs-xdir)))
    (princ (strcat "\nDirection Y: " (vl-princ-to-string ucs-ydir)))
    (princ (strcat "\nNormale Z: " (vl-princ-to-string (tcp:get-current-ucs-normal)))))
  
  (princ "\n=== Diagnostic terminé ==="))

(defun diag:block-info (ename)
  "Diagnostic détaillé d'un bloc spécifique"
  (princ "\n=== DIAGNOSTIC: Information bloc ===")
  
  (if (and ename (tcp:is-tcpoint-block? ename))
    (let ((props (tcp:get-block-properties ename))
          (block-normal (tcp:get-block-normal ename))
          (ucs-normal (tcp:get-current-ucs-normal)))
      
      (princ (strcat "\nNom du bloc: " (cdr (assoc 'blockname props))))
      (princ (strcat "\nCalque: " (cdr (assoc 'layer props))))
      (princ (strcat "\nPosition: " (vl-princ-to-string (cdr (assoc 'insertion-point props)))))
      (princ (strcat "\nRotation: " (rtos (or (cdr (assoc 'rotation props)) 0.0))))
      (princ (strcat "\nNormale du bloc: " (vl-princ-to-string block-normal)))
      (princ (strcat "\nNormale SCU: " (vl-princ-to-string ucs-normal)))
      (princ (strcat "\nOrientation correcte: " (if (tcp:block-orientation-ok? ename) "OUI" "NON")))
      
      (if (assoc 'attributes props)
        (progn
          (princ "\nAttributs:")
          (foreach attr (cdr (assoc 'attributes props))
            (princ (strcat "\n  " (car attr) " = " (cdr attr)))))))
    (princ "\nErreur: Entité invalide ou pas un bloc TCPOINT"))
  
  (princ "\n=== Diagnostic terminé ==="))

;; ======================= COMMANDES DE TEST =======================

(defun c:TCP-EXAMPLE-ALL ()
  "Lance l'exemple de correction complète"
  (example:fix-all-tcpoints))

(defun c:TCP-EXAMPLE-LAYER ()
  "Lance l'exemple de correction par calque"
  (example:fix-specific-layer))

(defun c:TCP-TEST-SETUP ()
  "Crée un scénario de test"
  (test:create-test-scenario))

(defun c:TCP-TEST-DETECTION ()
  "Lance le test de détection"
  (test:orientation-detection))

(defun c:TCP-TEST-PERFORMANCE ()
  "Lance le test de performance"
  (test:performance))

(defun c:TCP-DIAG-UCS ()
  "Affiche le diagnostic SCU"
  (diag:ucs-info))

(defun c:TCP-DIAG-BLOCK ()
  "Diagnostic d'un bloc sélectionné"
  (let ((ename (car (entsel "\nSélectionnez un bloc TCPOINT: "))))
    (if ename
      (diag:block-info ename)
      (princ "\nAnnulé."))))

;; ======================= AIDE =======================

(defun c:TCP-HELP ()
  "Affiche l'aide complète"
  (princ "\n=== AIDE TCPOINT-ORIENTATION-FIXER ===")
  (princ "\n")
  (princ "\n== COMMANDES PRINCIPALES ==")
  (princ "\n- TCPOINT-FIX-SELECTION      : Corriger la sélection")
  (princ "\n- TCPOINT-FIX-ALL            : Corriger tous les blocs")
  (princ "\n- TCPOINT-FIX-LAYER          : Corriger un calque")
  (princ "\n- TCPOINT-CHECK-ORIENTATION  : Vérifier sans corriger")
  (princ "\n")
  (princ "\n== CONFIGURATION ==")
  (princ "\n- TCP-CONFIG                 : Afficher la configuration")
  (princ "\n- TCP-CONFIG-DEBUG           : Mode debug on/off")
  (princ "\n- TCP-CONFIG-METHOD          : Méthode recréation/rotation")
  (princ "\n")
  (princ "\n== EXEMPLES ET TESTS ==")
  (princ "\n- TCP-EXAMPLE-ALL            : Exemple complet")
  (princ "\n- TCP-TEST-DETECTION         : Test de détection")
  (princ "\n- TCP-DIAG-UCS               : Info SCU courant")
  (princ "\n- TCP-DIAG-BLOCK             : Info bloc sélectionné")
  (princ "\n")
  (princ "\n== PROBLEMES COURANTS ==")
  (princ "\nSi les TCPOINT apparaissent de profil après 3DALIGN ou")
  (princ "\nchangement de SCU, utilisez TCPOINT-FIX-ALL pour les corriger.")
  (princ))

(princ "\n=== EXEMPLES TCPOINT-ORIENTATION chargés ===")
(princ "\nTapez TCP-HELP pour l'aide complète")
