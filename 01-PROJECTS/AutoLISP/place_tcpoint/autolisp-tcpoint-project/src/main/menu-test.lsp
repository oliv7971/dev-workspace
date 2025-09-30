;; MENU-TEST.LSP
;; =============================================================================
;; Version de test simplifiée du menu pour diagnostiquer les erreurs
;; =============================================================================

(defun tcp:function-exists-p (func-name)
  "Vérifie si une fonction existe (alternative à fboundp)"
  (and func-name
       (not (null (eval func-name)))))

(defun test-menu-simple ()
  "Menu de test simplifié"
  (princ "\n=== MENU TEST SIMPLIFIE ===")
  (princ "\n1. Test TCFIX")
  (princ "\n2. Test TCCHECK") 
  (princ "\n3. Quitter")
  
  (setq user-input (getstring "\nVotre choix: "))
  (princ (strcat "\nVous avez choisi: " user-input))
  
  (cond
    ((= user-input "1") 
     (princ "\nTest choix 1 - OK"))
    ((= user-input "2") 
     (princ "\nTest choix 2 - OK"))
    ((= user-input "3") 
     (princ "\nAu revoir"))
    (t 
     (princ "\nChoix non reconnu")))
  
  (princ "\n=== FIN TEST ===")
  (princ))

(defun c:MENUTEST ()
  "Commande pour tester le menu"
  (test-menu-simple))

(defun test-variables ()
  "Test des variables et fonctions de base"
  (princ "\n=== TEST VARIABLES ===")
  
  ; Test 1: Variable simple
  (setq test-var "test123")
  (princ (strcat "\nVariable test: " test-var))
  
  ; Test 2: Fonction getstring
  (setq input-test (getstring "\nTapez quelque chose: "))
  (princ (strcat "\nVous avez tape: " input-test))
  
  ; Test 3: Condition simple
  (if (= input-test "test")
    (princ "\n[OK] Test reussi")
    (princ "\n[INFO] Autre valeur"))
  
  (princ "\n=== FIN TEST VARIABLES ===")
  (princ))

(defun c:TESTVAR ()
  "Test des variables"
  (test-variables))

; Information
(princ "\nMenu-test.lsp charge")
(princ "\nCommandes: MENUTEST, TESTVAR")