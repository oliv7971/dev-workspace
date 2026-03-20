;; This file contains test commands for verifying the functionality of the TCPOINT placement and other related features.

(defun c:test-tcpoint-placement ()
  (princ "\n=== TEST DE PLACEMENT TCPOINT ===")
  
  ;; Test de placement automatique
  (command "PLACE-TCPOINT" "1")  ;; Mode automatique
  (princ "\nPlacement automatique effectué.")
  
  ;; Test de placement semi-automatique
  (command "PLACE-TCPOINT" "2")  ;; Mode semi-automatique
  (princ "\nPlacement semi-automatique effectué.")
  
  ;; Test de placement manuel
  (command "PLACE-TCPOINT" "3")  ;; Mode manuel
  (princ "\nPlacement manuel effectué.")
  
  ;; Test de création de centres
  (command "CREATE-CENTRES")
  (princ "\nCentres créés.")
  
  (princ "\n=== TEST TERMINÉ ===")
)

(defun c:test-geometry ()
  (princ "\n=== TEST DES FONCTIONS GÉOMÉTRIQUES ===")
  
  ;; Exemple de test de distance
  (setq pt1 (list 0 0 0))
  (setq pt2 (list 3 4 0))
  (setq distance (_dist2d pt1 pt2))
  
  (princ (strcat "\nDistance entre " (vl-princ-to-string pt1) " et " (vl-princ-to-string pt2) " : " (rtos distance 2 2)))
  
  (princ "\n=== TEST TERMINÉ ===")
)

(princ "\n=== COMMANDES DE TEST CHARGÉES ===")
(princ "\nUtilisez les commandes :")
(princ "\n- TEST-TCPOINT-PLACEMENT : Pour tester le placement des blocs TCPOINT.")
(princ "\n- TEST-GEOMETRY : Pour tester les fonctions géométriques.")
(princ)