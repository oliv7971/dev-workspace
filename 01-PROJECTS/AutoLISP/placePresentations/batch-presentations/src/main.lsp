; main.lsp
; Entry point of the batch processing application
; Initializes the batch processing system and manages the execution flow

(defun main ()
  (load "batch/config/config.lsp")
  (load "batch/processor.lsp")
  (load "batch/queue.lsp")
  (load "presentations/manager.lsp")
  (load "presentations/parameters.lsp")
  (load "presentations/templates.lsp")
  (load "utils/file-handler.lsp")
  (load "utils/error-handler.lsp")
  (load "utils/logger.lsp")
  (load "ui/interface.lsp")

  (let ((processor (make-instance 'BatchProcessor))
        (queue (make-instance 'Queue)))
    (batch-processor:start processor)
    (queue:process-queue queue)
    (batch-processor:stop processor)))

(main)