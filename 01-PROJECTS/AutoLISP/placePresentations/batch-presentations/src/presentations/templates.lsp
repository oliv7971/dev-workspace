(defun load-template (template-name)
  "Load a presentation template by name."
  (let ((template-path (strcat "templates/" template-name ".lsp")))
    (if (findfile template-path)
      (load template-path)
      (error (strcat "Template not found: " template-name)))))

(defun apply-template (presentation template-name)
  "Apply a specified template to a given presentation."
  (let ((template (load-template template-name)))
    (if template
      (progn
        ;; Assuming template has a function to apply it
        (template-apply presentation template))
      (error (strcat "Failed to apply template: " template-name)))))

(defun list-templates ()
  "List all available presentation templates."
  (let ((template-files (vl-directory-files "templates" "*.lsp")))
    (mapcar 'vl-filename-base template-files)))

(defun save-template (template-name template-content)
  "Save a new presentation template."
  (let ((template-path (strcat "templates/" template-name ".lsp")))
    (with-open-file template-path "w"
      (lambda (file)
        (write-line template-content file)))))

(defun delete-template (template-name)
  "Delete a specified presentation template."
  (let ((template-path (strcat "templates/" template-name ".lsp")))
    (if (findfile template-path)
      (vl-file-delete template-path)
      (error (strcat "Template not found: " template-name)))))