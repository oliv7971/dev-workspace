; defaults.lsp
; This file defines default settings and parameters for the batch processing system.

(setq *default-batch-parameters* '(
    (max-retries . 3)
    (timeout . 60)
    (log-level . "INFO")
    (output-directory . "C:\\data\\output")
    (presentation-format . "PDF")
))

(defun get-default-parameter (param)
    (cdr (assoc param *default-batch-parameters*))
)

(defun set-default-parameter (param value)
    (setq *default-batch-parameters* (cons (cons param value) (remove-if (lambda (x) (equal (car x) param)) *default-batch-parameters*)))
)