(defun PresentationParameters ( / parameters)
  (setq parameters '())

  (defun set-parameter (key value)
    (setq parameters (cons (cons key value) parameters)))

  (defun get-parameter (key)
    (cdr (assoc key parameters)))

  (defun list-parameters ()
    parameters)

  (defun clear-parameters ()
    (setq parameters '()))

  (list 'set-parameter 'get-parameter 'list-parameters 'clear-parameters)
)