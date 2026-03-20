;; ========================================
;; BATCH DWG TO DXF CONVERTER
;; ========================================
;; Convertit tous les fichiers DWG d'un dossier en DXF
;; Usage: (C:DWG2DXF)

(defun C:DWG2DXF (/ source-folder dwg-files dwg-file dxf-file count total)
  (princ "\n=== CONVERSION PAR LOTS DWG -> DXF ===\n")
  
  ;; Demander le dossier source
  (setq source-folder (getfiled "Sélectionnez un fichier DWG du dossier à traiter" "" "dwg" 0))
  
  (if source-folder
    (progn
      ;; Extraire le chemin du dossier
      (setq source-folder (vl-filename-directory source-folder))
      (princ (strcat "\nDossier sélectionné: " source-folder "\n"))
      
      ;; Obtenir la liste des fichiers DWG
      (setq dwg-files (vl-directory-files source-folder "*.dwg" 1))
      (setq total (length dwg-files))
      (setq count 0)
      
      (if (> total 0)
        (progn
          (princ (strcat "\n" (itoa total) " fichier(s) DWG trouvé(s)\n"))
          (princ "Conversion en cours...\n\n")
          
          ;; Traiter chaque fichier
          (foreach dwg dwg-files
            (setq count (1+ count))
            (setq dwg-file (strcat source-folder "\\" dwg))
            (setq dxf-file (strcat source-folder "\\" (vl-filename-base dwg) ".dxf"))
            
            (princ (strcat "[" (itoa count) "/" (itoa total) "] " dwg " -> "))
            
            ;; Ouvrir le fichier DWG
            (if (setq dwg-doc (vl-catch-all-apply 'vla-open (list (vla-get-documents (vlax-get-acad-object)) dwg-file)))
              (if (not (vl-catch-all-error-p dwg-doc))
                (progn
                  ;; Exporter en DXF
                  (if (vl-catch-all-apply 'vla-saveas (list dwg-doc dxf-file ac:acR12_dxf))
                    (princ "OK\n")
                    (princ "ERREUR lors de l'export\n")
                  )
                  ;; Fermer sans sauvegarder
                  (vla-close dwg-doc :vlax-false)
                )
                (princ "ERREUR d'ouverture\n")
              )
              (princ "ERREUR d'ouverture\n")
            )
          )
          
          (princ (strcat "\n=== CONVERSION TERMINÉE ===\n" (itoa count) " fichier(s) traité(s)\n"))
        )
        (princ "\nAucun fichier DWG trouvé dans ce dossier.\n")
      )
    )
    (princ "\nOpération annulée.\n")
  )
  (princ)
)

;; Version simplifiée - Génère un script batch .SCR
(defun C:DWG2DXF-AUTO (/ source-folder dwg-files dwg-file dxf-file scr-file f count total)
  (princ "\n=== CONVERSION PAR LOTS DWG -> DXF (AUTO) ===\n")
  
  ;; Définir le dossier (à modifier selon vos besoins)
  (setq source-folder "c:\\data\\20-DEVELOPPEMENT\\01-PROJECTS\\AutoLISP\\vecteursDep\\vecteurs")
  (princ (strcat "\nDossier: " source-folder "\n"))
  
  ;; Obtenir la liste des fichiers DWG
  (setq dwg-files (vl-directory-files source-folder "*.dwg" 1))
  (setq total (length dwg-files))
  
  (if (> total 0)
    (progn
      (princ (strcat "\n" (itoa total) " fichier(s) DWG trouvé(s)\n"))
      (princ "Génération du script de conversion...\n")
      
      ;; Créer le fichier script
      (setq scr-file (strcat source-folder "\\batch_convert.scr"))
      (setq f (open scr-file "w"))
      
      (setq count 0)
      ;; Écrire les commandes pour chaque fichier
      (foreach dwg dwg-files
        (setq count (1+ count))
        (setq dwg-file (strcat source-folder "\\" dwg))
        (setq dxf-file (strcat source-folder "\\" (vl-filename-base dwg) ".dxf"))
        
        ;; Fermer le document courant s'il y en a un
        (if (> count 1)
          (progn
            (write-line "_.CLOSE" f)
            (write-line "N" f)
          )
        )
        
        ;; Ouvrir le fichier - tout sur une seule ligne
        (write-line (strcat "_.OPEN " dwg-file) f)
        
        ;; Exporter en DXF avec DXFOUT - tout sur une seule ligne
        (write-line (strcat "_.DXFOUT " dxf-file " 16 ") f)
      )
      
      ;; Fermer le dernier fichier
      (write-line "_.CLOSE" f)
      (write-line "N" f)
      
      (close f)
      
      (princ (strcat "\n*** Script créé: " scr-file " ***\n"))
      (princ "\nPour lancer la conversion, tapez:\n")
      (princ (strcat "  SCRIPT " (chr 34) scr-file (chr 34) "\n"))
    )
    (princ "\nAucun fichier DWG trouvé dans ce dossier.\n")
  )
  (princ)
)

(princ "\n*** Script chargé ***")
(princ "\nCommandes disponibles:")
(princ "\n  DWG2DXF      - Convertir DWG en DXF (sélection interactive)")
(princ "\n  DWG2DXF-AUTO - Convertir le dossier vecteurs/ automatiquement")
(princ "\n")
(princ)
