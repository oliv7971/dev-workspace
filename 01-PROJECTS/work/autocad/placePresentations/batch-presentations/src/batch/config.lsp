; Configuration settings for the batch processing system
; This file exports parameters for processing and resource management

(defun get-config ()
  (list
    (cons 'max-concurrent-processes 5)  ; Maximum number of concurrent processes
    (cons 'default-timeout 300)          ; Default timeout for processing in seconds
    (cons 'log-level 'info)               ; Logging level (info, warning, error)
    (cons 'output-directory "C:\\data\\output") ; Directory for output files
    (cons 'retry-attempts 3)              ; Number of retry attempts for failed processes
  )
)