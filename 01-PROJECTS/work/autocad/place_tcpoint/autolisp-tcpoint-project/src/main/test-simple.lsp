;; TEST-SIMPLE.LSP
;; =============================================================================
;; Test simple pour vérifier le chargement sans erreurs
;; =============================================================================

(defun tcp:function-exists-p (func-name)
  "Vérifie si une fonction existe (alternative à fboundp)"
  (and func-name
       (not (null (eval func-name)))))

(defun test-chargement-simple ()
  "Test de chargement minimal"
  
  (princ "\n===========================================")
  (princ "\n        TEST DE CHARGEMENT SIMPLE")
  (princ "\n===========================================")
  
  ; Test 1: Charger le système principal
  (princ "\n\n1. Chargement du fichier principal...")
  
  ; Utiliser un try-catch pour capturer les erreurs
  (if (vl-catch-all-error-p 
        (vl-catch-all-apply 'load '("tcpoint-orientation-main.lsp")))
    (princ "\n[ERREUR] Erreur lors du chargement du fichier principal")
    (princ "\n[OK] Fichier principal charge sans erreur"))
  
  ; Test 2: Vérifier les commandes de base
  (princ "\n\n2. Test des commandes de base...")
  
  (if (tcp:function-exists-p 'c:TCFIX)
    (princ "\n[OK] TCFIX disponible")
    (princ "\n[ERREUR] TCFIX non disponible"))
    
  (if (tcp:function-exists-p 'c:TCCHECK)
    (princ "\n[OK] TCCHECK disponible")
    (princ "\n[ERREUR] TCCHECK non disponible"))
  
  (princ "\n\n===========================================")
  (princ "\n           TEST TERMINE")
  (princ "\n===========================================\n")
  
  (princ))

(defun c:TEST ()
  "Commande rapide pour le test"
  (test-chargement-simple))

; Message de chargement
(princ "\nTest-simple.lsp charge - Tapez TEST pour lancer le test")