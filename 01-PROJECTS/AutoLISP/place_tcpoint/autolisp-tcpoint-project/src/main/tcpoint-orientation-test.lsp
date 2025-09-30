;; TCPOINT-ORIENTATION-TEST.LSP v1.0
;; =============================================================================
;; Script de test simple pour valider le système TCPOINT Orientation Fixer
;; =============================================================================

(defun test-tcpoint-system ()
  "Test basique du système TCPOINT Orientation"
  (princ "\n=== TEST DU SYSTEME TCPOINT-ORIENTATION ===")
  
  ; Test 1: Vérifier que les fonctions sont chargées
  (princ "\n1. Test de chargement des fonctions...")
  (if (and (boundp 'tcp:is-tcpoint-block?) tcp:is-tcpoint-block?)
    (princ "\n   [OK] tcp:is-tcpoint-block? disponible")
    (princ "\n   [ERREUR] tcp:is-tcpoint-block? manquante"))
  
  (if (and (boundp 'tcp:block-orientation-ok?) tcp:block-orientation-ok?)
    (princ "\n   [OK] tcp:block-orientation-ok? disponible")
    (princ "\n   [ERREUR] tcp:block-orientation-ok? manquante"))
  
  ; Test 2: Tester la fonction de calcul de normale SCU
  (princ "\n\n2. Test de calcul de normale SCU...")
  (let ((ucs-normal (tcp:get-current-ucs-normal)))
    (if ucs-normal
      (princ (strcat "\n   [OK] Normale SCU calculée: " (vl-princ-to-string ucs-normal)))
      (princ "\n   [ERREUR] Erreur calcul normale SCU")))
  
  ; Test 3: Tester la comparaison de vecteurs
  (princ "\n\n3. Test de comparaison de vecteurs...")
  (if (tcp:vectors-parallel? '(0 0 1) '(0 0 1) 0.01)
    (princ "\n   [OK] Détection vecteurs identiques OK")
    (princ "\n   [ERREUR] Problème détection vecteurs identiques"))
  
  (if (not (tcp:vectors-parallel? '(0 0 1) '(1 0 0) 0.01))
    (princ "\n   [OK] Détection vecteurs différents OK")
    (princ "\n   [ERREUR] Problème détection vecteurs différents"))
  
  ; Test 4: Compter les blocs TCPOINT dans le dessin
  (princ "\n\n4. Test de détection des blocs TCPOINT...")
  (let ((ss (ssget "X" '((0 . "INSERT"))))
        (count-tcpoint 0) (i 0))
    (if ss
      (progn
        (while (< i (sslength ss))
          (if (tcp:is-tcpoint-block? (ssname ss i))
            (setq count-tcpoint (1+ count-tcpoint)))
          (setq i (1+ i)))
        (princ (strcat "\n   [OK] " (itoa count-tcpoint) " blocs TCPOINT trouvés sur " 
                       (itoa (sslength ss)) " blocs INSERT")))
      (princ "\n   [INFO] Aucun bloc INSERT dans le dessin")))
  
  ; Test 5: Vérifier les variables de configuration
  (princ "\n\n5. Test de configuration...")
  (princ (strcat "\n   Types blocs: " (vl-string-join *TCPOINT_BLOCKS* ", ")))
  (princ (strcat "\n   Debug: " (if *DEBUG_MODE* "ON" "OFF")))
  (princ (strcat "\n   Méthode: " (if *USE_RECREATION_METHOD* "RECREATION" "ROTATION")))
  
  (princ "\n\n=== TEST TERMINE ===")
  (princ "\nSi tous les tests passent, le système est prêt à utiliser.")
  (princ))

; Commande pour lancer le test
(defun c:TCP-TEST ()
  "Lance les tests du système"
  (test-tcpoint-system))

(princ "\n=== TEST TCPOINT-ORIENTATION chargé ===")
(princ "\nTapez TCP-TEST pour lancer les tests de validation")
