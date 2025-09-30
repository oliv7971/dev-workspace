;; Test cases for the placement commands in the TCPOINT project

(defun test-placer-tcpoints-auto ()
  (princ "\n=== TEST PLACER TCPOINTS AUTOMATIQUEMENT ===")
  
  ;; Setup test environment
  (setq test-centres '((0 0 0) (10 10 0) (20 20 0)))  ;; Example centres
  (setq test-lignes '((0 0 0) (10 0 0) (20 0 0)))  ;; Example lines
  (setq tolR 5.0)  ;; Proximity radius
  
  ;; Call the function to test
  (let ((result (placer-tcpoints-auto test-lignes test-centres tolR)))
    (if (= result 2)  ;; Assuming we expect 2 TCPOINTs to be placed
      (princ "\n✓ Test réussi : 2 TCPOINTs placés correctement.")
      (princ "\n✗ Test échoué : Nombre de TCPOINTs placés incorrect.")))
)

(defun test-placer-tcpoints ()
  (princ "\n=== TEST PLACER TCPOINTS MANUELLEMENT ===")
  
  ;; Setup test environment
  (setq test-lignes '((0 0 0) (10 0 0)))  ;; Example lines
  (setq test-centre (list 5 0 0))  ;; Example centre
  
  ;; Call the function to test
  (let ((result (placer-tcpoints test-lignes test-centre)))
    (if (= result 1)  ;; Assuming we expect 1 TCPOINT to be placed
      (princ "\n✓ Test réussi : 1 TCPOINT placé correctement.")
      (princ "\n✗ Test échoué : Nombre de TCPOINTs placés incorrect.")))
)

(defun run-all-tests ()
  (test-placer-tcpoints-auto)
  (test-placer-tcpoints)
)

(run-all-tests)

(princ "\n=== TESTS TERMINÉS ===")