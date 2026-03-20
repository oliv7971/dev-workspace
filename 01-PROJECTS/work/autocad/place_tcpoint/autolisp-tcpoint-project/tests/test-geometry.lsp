;; Test cases for geometry utility functions

(defun test-distance-calculation ()
  (setq point1 (list 0 0 0)
        point2 (list 3 4 0)
        expected-distance 5.0
        calculated-distance (_dist2d point1 point2))
  
  (if (= calculated-distance expected-distance)
    (princ "\nTest passed: Distance calculation is correct.")
    (princ (strcat "\nTest failed: Expected " (rtos expected-distance 2 2) ", got " (rtos calculated-distance 2 2) "."))))

(defun test-point-normalization ()
  (setq point2d (list 3 4)
        normalized-point (_pt3 point2d))
  
  (if (and (= (length normalized-point) 3) (= (caddr normalized-point) 0.0))
    (princ "\nTest passed: Point normalization is correct.")
    (princ "\nTest failed: Point normalization is incorrect.")))

(defun run-geometry-tests ()
  (princ "\n=== Running Geometry Tests ===")
  (test-distance-calculation)
  (test-point-normalization)
  (princ "\n=== Geometry Tests Completed ==="))

(run-geometry-tests)