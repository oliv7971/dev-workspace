(defun log-message (message)
  (princ (strcat (rtos (getvar "cdate") 2 2) ": " message))
  (princ "\n")
)

(defun log-error (error-message)
  (princ (strcat (rtos (getvar "cdate") 2 2) ": ERROR: " error-message))
  (princ "\n")
)

(defun log-info (info-message)
  (princ (strcat (rtos (getvar "cdate") 2 2) ": INFO: " info-message))
  (princ "\n")
)

(defun log-warning (warning-message)
  (princ (strcat (rtos (getvar "cdate") 2 2) ": WARNING: " warning-message))
  (princ "\n")
)

(defun clear-log ()
  (princ "Log cleared.\n")
)