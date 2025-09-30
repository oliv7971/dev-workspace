;; TEST-CHARGEMENT-DIRECT.LSP
;; =============================================================================
;; Test direct de chargement des fichiers
;; =============================================================================

(defun test-fichiers-directs ()
  "Test de chargement direct des fichiers"
  
  (princ "\n=== TEST CHARGEMENT DIRECT ===")
  
  ; Test 1: Vérifier la présence des fichiers
  (princ "\n\n1. Vérification des fichiers:")
  
  (if (findfile "tcpoint-orientation-config.lsp")
    (princ "\n[OK] tcpoint-orientation-config.lsp trouve")
    (princ "\n[ERREUR] tcpoint-orientation-config.lsp manquant"))
    
  (if (findfile "tcpoint-orientation-fixer.lsp")
    (princ "\n[OK] tcpoint-orientation-fixer.lsp trouve")
    (princ "\n[ERREUR] tcpoint-orientation-fixer.lsp manquant"))
    
  (if (findfile "tcpoint-orientation-examples.lsp")
    (princ "\n[OK] tcpoint-orientation-examples.lsp trouve")
    (princ "\n[INFO] tcpoint-orientation-examples.lsp trouve"))
  
  ; Test 2: Essayer de charger chaque fichier
  (princ "\n\n2. Test de chargement:")
  
  ; Configuration
  (princ "\n- Chargement configuration...")
  (if (findfile "tcpoint-orientation-config.lsp")
    (progn
      (load "tcpoint-orientation-config.lsp")
      (princ " [OK]"))
    (princ " [ERREUR]"))
  
  ; Module principal
  (princ "\n- Chargement module principal...")
  (if (findfile "tcpoint-orientation-fixer.lsp")
    (progn
      (load "tcpoint-orientation-fixer.lsp")
      (princ " [OK]"))
    (princ " [ERREUR]"))
  
  ; Test 3: Vérifier quelques fonctions
  (princ "\n\n3. Vérification des fonctions:")
  
  (if (and (boundp 'tcp:is-tcpoint-block?) tcp:is-tcpoint-block?)
    (princ "\n[OK] tcp:is-tcpoint-block? disponible")
    (princ "\n[ERREUR] tcp:is-tcpoint-block? manquante"))
    
  (if (and (boundp 'c:TCPOINT-FIX-SELECTION) c:TCPOINT-FIX-SELECTION)
    (princ "\n[OK] c:TCPOINT-FIX-SELECTION disponible")
    (princ "\n[ERREUR] c:TCPOINT-FIX-SELECTION manquante"))
  
  (princ "\n\n=== FIN TEST ===")
  (princ))

(defun c:TESTDIR ()
  "Test direct des fichiers"
  (test-fichiers-directs))

; Information
(princ "\nTest-chargement-direct.lsp charge")
(princ "\nTapez TESTDIR pour tester")