(defun test-batch-processing ()
  (setq presentations (list "presentation1.pptx" "presentation2.pptx" "presentation3.pptx"))
  (setq processor (make-instance 'BatchProcessor))
  
  ;; Test starting the batch process
  (assert (eq (start-batch processor presentations) 'success) "Batch process should start successfully.")
  
  ;; Test queue management
  (let ((queue (get-queue processor)))
    (assert (eq (length queue) 3) "Queue should contain 3 presentations.")
    (assert (eq (dequeue processor) "presentation1.pptx") "First presentation should be dequeued.")
    (assert (eq (length (get-queue processor)) 2) "Queue should contain 2 presentations after dequeue.")
  )
  
  ;; Test stopping the batch process
  (assert (eq (stop-batch processor) 'success) "Batch process should stop successfully.")
  
  ;; Test error handling
  (let ((error-processor (make-instance 'BatchProcessor)))
    (assert (eq (start-batch error-processor nil) 'error) "Starting with nil presentations should return an error.")
  )
  
  (princ "All tests passed successfully.")
)

(test-batch-processing)