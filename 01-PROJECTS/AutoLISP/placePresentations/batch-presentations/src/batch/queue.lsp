(defun Queue ()
  (setq presentations '()))

(defun add-presentation (presentation)
  (setq presentations (append presentations (list presentation))))

(defun remove-presentation ()
  (if presentations
    (progn
      (setq removed (car presentations))
      (setq presentations (cdr presentations))
      removed)
    nil))

(defun get-presentations ()
  presentations)

(defun queue-size ()
  (length presentations))

(defun clear-queue ()
  (setq presentations '()))

(defun print-queue ()
  (if presentations
    (progn
      (princ "Current Queue: ")
      (dolist (presentation presentations)
        (princ (strcat presentation " "))
      )
      (terpri))
    (princ "Queue is empty.\n")))