(defun read-file (file-path)
  (if (findfile file-path)
    (with-open-file (file-path :direction :input)
      (let ((content (read-line file-path nil)))
        (if content
          (progn
            (setq content (cons content (read-file file-path)))
            content)
          nil)))
    (error "File not found: ~A" file-path)))

(defun write-file (file-path content)
  (with-open-file (file-path :direction :output :if-does-not-exist :create :element-type 'character)
    (dolist (line content)
      (write-line line file-path))))

(defun append-to-file (file-path content)
  (with-open-file (file-path :direction :output :if-does-not-exist :create :element-type 'character :if-exists :append)
    (dolist (line content)
      (write-line line file-path))))

(defun file-exists-p (file-path)
  (findfile file-path))

(defun delete-file (file-path)
  (if (file-exists-p file-path)
    (delete-file file-path)
    (error "File not found: ~A" file-path)))