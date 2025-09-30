;; Utility functions for geometric calculations

;; Calculate the distance between two points
(defun distance (pt1 pt2)
  (sqrt (+ (expt (- (car pt1) (car pt2)) 2)
           (expt (- (cadr pt1) (cadr pt2)) 2))))

;; Normalize a point to ensure it has three coordinates
(defun normalize-point (pt)
  (if (= (length pt) 2)
    (append pt (list 0.0))
    pt))

;; Calculate the distance from a point to a line segment
(defun distance-point-to-segment (point segment-start segment-end)
  (let* ((a segment-start)
         (b segment-end)
         (p point)
         (ab (distance a b))
         (ap (distance a p))
         (bp (distance b p))
         (dot-product (dot-product (list (- (car b) (car a)) (- (cadr b) (cadr a)))
                                   (list (- (car p) (car a)) (- (cadr p) (cadr a))))))
         (t (if (> ab 0) (/ dot-product (expt ab 2)) 0)))
    (if (< t 0)
      ap
      (if (> t 1)
        bp
        (let ((projection (list (+ (car a) (* t (- (car b) (car a))))
                                 (+ (cadr a) (* t (- (cadr b) (cadr a)))))))
          (distance p projection))))))

;; Calculate the dot product of two vectors
(defun dot-product (vec1 vec2)
  (+ (* (car vec1) (car vec2))
     (* (cadr vec1) (cadr vec2))))