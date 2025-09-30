;; SIMPLIF-COTES-SEMI-AUTO.LSP
;; Version semi-automatique avec calque specifique et centre defini par l'utilisateur
;; 
;; PRINCIPE :
;; 1. Parametre : calque des cotes a traiter
;; 2. Selection d'une zone (coupe par coupe)
;; 3. L'utilisateur clique pour definir le centre de la coupe
;; 4. Tri par angle depuis ce centre
;; 5. Suppression alternee (1 sur 2)

;; ===== PARAMETRES A MODIFIER =====
(setq *CALQUE-COTES* "REC_INS_GC_GAL_Beton_soutenement_txt")  ;; <-- MODIFIER ICI le nom de votre calque
(setq *AFFICHAGE-DEBUG* T)            ;; T = affiche details, nil = silencieux

;; ===== COMMANDE PRINCIPALE =====
(defun c:simplif-cotes-semi ()
  (princ "\n=== SIMPLIFICATION SEMI-AUTOMATIQUE DES TEXTES DE COTES ===")
  (princ (strcat "\nCalque cible : " *CALQUE-COTES*))
  
  ;; Verification que le calque existe
  (if (not (tblsearch "LAYER" *CALQUE-COTES*))
    (progn
      (princ (strcat "\nATTENTION : Le calque '" *CALQUE-COTES* "' n'existe pas !"))
      (princ "\nCreation du calque...")
      (command "._LAYER" "_M" *CALQUE-COTES* "")
    )
  )
  
  ;; Mode d'emploi
  (princ "\n")
  (princ "\nMODE D'EMPLOI :")
  (princ "\n1. Selectionnez la zone de la coupe (fenetre ou capture)")
  (princ "\n2. Cliquez pour definir le centre de la coupe")
  (princ "\n3. Le script supprime automatiquement 1 texte de cote sur 2")
  (princ "\n")
  
  ;; Etape 1 : Selection de la zone
  (princ "\nETAPE 1 : Selectionnez la zone de la coupe...")
  (setq ss-zone (ssget))
  
  (if ss-zone
    (progn
      ;; Etape 2 : Filtrage par calque
      (setq ss-cotes (filtrer-par-calque ss-zone *CALQUE-COTES*))
      
      (if (and ss-cotes (> (sslength ss-cotes) 1))
        (progn
          (princ (strcat "\n" (itoa (sslength ss-cotes)) " textes de cotes trouvees sur le calque " *CALQUE-COTES*))
          
          ;; Etape 3 : Choix du centre
          (princ "\nETAPE 2 : Cliquez pour definir le centre de la coupe...")
          (setq centre (getpoint "\nCentre de la coupe : "))
          
          (if centre
            (progn
              (if *AFFICHAGE-DEBUG*
                (progn
                  ;; Dessiner temporairement le centre
                  (command "._POINT" centre)
                  (princ (strcat "\nCentre defini : X=" (rtos (car centre) 2 3)))
                  (princ (strcat " Y=" (rtos (cadr centre) 2 3)))
                )
              )
              
              ;; Etape 4 : Traitement
              (traiter-coupe ss-cotes centre)
            )
            (princ "\nAnnule.")
          )
        )
        (progn
          (princ (strcat "\nAucun texte de cote trouve sur le calque " *CALQUE-COTES*))
          (princ "\nVerifiez :")
          (princ "\n- Que vos textes de cotes sont sur le bon calque")
          (princ "\n- Que vous avez selectionne la bonne zone")
        )
      )
    )
    (princ "\nAucune selection.")
  )
  (princ)
)

;; ===== FILTRAGE PAR CALQUE =====
(defun filtrer-par-calque (ss-source nom-calque)
  (setq ss-filtre (ssadd))
  (setq i 0)
  
  (if *AFFICHAGE-DEBUG* (princ "\nFiltrage par calque..."))
  
  (repeat (sslength ss-source)
    (setq ent (ssname ss-source i))
    (setq data (entget ent))
    (setq type-obj (cdr (assoc 0 data)))
    (setq calque-obj (cdr (assoc 8 data)))
    
    ;; Garder seulement les TEXT/MTEXT du bon calque
    (if (and (or (= type-obj "TEXT") (= type-obj "MTEXT"))
             (= (strcase calque-obj) (strcase nom-calque)))
      (progn
        (ssadd ent ss-filtre)
        (if *AFFICHAGE-DEBUG* 
          (princ (strcat "\n  Garde : " type-obj " sur " calque-obj))
        )
      )
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n  Ignore : " type-obj " sur " calque-obj))
      )
    )
    (setq i (1+ i))
  )
  
  ;; Retourner le selection set filtre (ou nil si vide)
  (if (> (sslength ss-filtre) 0)
    ss-filtre
    nil
  )
)

;; ===== TRAITEMENT D'UNE COUPE =====
(defun traiter-coupe (ss-cotes centre)
  (princ "\nTraitement de la coupe...")
  
  ;; Vérifications préliminaires
  (if (not centre)
    (progn
      (princ "\nERREUR : Centre non défini")
      (exit)
    )
  )
  
  (if (not (= (type centre) 'LIST))
    (progn
      (princ (strcat "\nERREUR : Centre invalide, type=" (vl-princ-to-string (type centre))))
      (exit)
    )
  )
  
  (if *AFFICHAGE-DEBUG*
    (progn
      (princ (strcat "\nCentre reçu : X=" (rtos (car centre) 2 3)))
      (princ (strcat " Y=" (rtos (cadr centre) 2 3)))
    )
  )
  
  ;; 1. Extraire positions et calculer angles
  (setq liste-cotes-angles '())
  (setq i 0)
  (setq nb-traites 0)
  (setq nb-valides 0)
  (setq nb-erreurs 0)
  
  (repeat (sslength ss-cotes)
    (setq ent (ssname ss-cotes i))
    (setq data (entget ent))
    (setq type-obj (cdr (assoc 0 data)))
    (setq nb-traites (1+ nb-traites))
    
    (if *AFFICHAGE-DEBUG*
      (princ (strcat "\n--- Traitement texte " (itoa nb-traites) " (" type-obj ") ---"))
    )
    
    ;; Obtenir position selon le type avec vérifications
    (if (= type-obj "TEXT")
      (setq pos (cdr (assoc 10 data)))     ;; Point d'insertion pour TEXT
      (setq pos (cdr (assoc 10 data)))     ;; Point d'insertion pour MTEXT aussi
    )
    
    ;; Vérifications de sécurité
    (if (and pos centre 
             (= (type pos) 'LIST) 
             (= (type centre) 'LIST)
             (>= (length pos) 2)
             (>= (length centre) 2))
      (progn
        ;; Vérifications supplémentaires des valeurs numériques
        (if (and (numberp (car centre)) (numberp (cadr centre))
                 (numberp (car pos)) (numberp (cadr pos)))
          (progn
            ;; Nettoyer les coordonnées (éliminer les micro-valeurs)
            (setq centre-x (car centre))
            (setq centre-y (cadr centre))
            (setq pos-x (car pos))
            (setq pos-y (cadr pos))
            
            ;; Arrondir à zéro si très petit
            (if (< (abs centre-x) 1e-3) (setq centre-x 0.0))
            (if (< (abs centre-y) 1e-3) (setq centre-y 0.0))
            (if (< (abs pos-x) 1e-3) (setq pos-x 0.0))
            (if (< (abs pos-y) 1e-3) (setq pos-y 0.0))
            
            (setq centre-clean (list centre-x centre-y))
            (setq pos-clean (list pos-x pos-y))
            
            (if *AFFICHAGE-DEBUG*
              (progn
                (princ (strcat "\n    COORDS - centre=(" (rtos centre-x 2 3) "," (rtos centre-y 2 3) ")"))
                (princ (strcat " pos=(" (rtos pos-x 2 3) "," (rtos pos-y 2 3) ")"))
              )
            )
            
            ;; Vérifier que les points ne sont pas identiques
            (if (not (and (= centre-x pos-x) (= centre-y pos-y)))
              (progn
                ;; Calcul d'angle alternatif avec protection
                (setq dx (- pos-x centre-x))
                (setq dy (- pos-y centre-y))
                
                (if *AFFICHAGE-DEBUG*
                  (princ (strcat "\n    Delta: dx=" (rtos dx 2 6) " dy=" (rtos dy 2 6)))
                )
                
                ;; Calcul d'angle par atan2 au lieu de la fonction angle
                (setq angle-rad (atan dy dx))
                (setq angle-deg (* angle-rad 57.2958))  ;; Conversion directe
                
                ;; Ajuster l'angle pour qu'il soit entre 0 et 360
                (if (< angle-deg 0) (setq angle-deg (+ angle-deg 360)))
                
                (setq liste-cotes-angles 
                  (cons (list ent pos angle-deg i) liste-cotes-angles)
                )
                (setq nb-valides (1+ nb-valides))
                
                (if *AFFICHAGE-DEBUG*
                  (progn
                    (princ (strcat "\n  ✓ Texte " (itoa (1+ i)) " (" type-obj ") : "))
                    (princ (strcat "angle=" (rtos angle-deg 2 1) "°"))
                  )
                )
              )
              (progn
                (princ (strcat "\n  ✗ ERREUR - Texte " (itoa (1+ i)) " : points identiques"))
                (setq nb-erreurs (1+ nb-erreurs))
              )
            )
          )
          (progn
            (princ (strcat "\n  ✗ ERREUR - Texte " (itoa (1+ i)) " : valeurs non numériques"))
            (setq nb-erreurs (1+ nb-erreurs))
            (if *AFFICHAGE-DEBUG*
              (progn
                (princ (strcat "\n    Centre X type: " (vl-princ-to-string (type (car centre))) " valeur: " (rtos (car centre) 2 6)))
                (princ (strcat "\n    Centre Y type: " (vl-princ-to-string (type (cadr centre))) " valeur: " (rtos (cadr centre) 2 6)))
                (princ (strcat "\n    Pos X type: " (vl-princ-to-string (type (car pos))) " valeur: " (rtos (car pos) 2 6)))
                (princ (strcat "\n    Pos Y type: " (vl-princ-to-string (type (cadr pos))) " valeur: " (rtos (cadr pos) 2 6)))
              )
            )
          )
        )
      )
      (progn
        (princ (strcat "\n  ✗ ERREUR - Texte " (itoa (1+ i)) " : coordonnées invalides"))
        (setq nb-erreurs (1+ nb-erreurs))
        (if *AFFICHAGE-DEBUG*
          (progn
            (princ (strcat "\n    Type pos: " (vl-princ-to-string (type pos))))
            (princ (strcat "\n    Type centre: " (vl-princ-to-string (type centre))))
            (princ (strcat "\n    Pos: " (vl-princ-to-string pos)))
            (princ (strcat "\n    Centre: " (vl-princ-to-string centre)))
          )
        )
      )
    )
    
    (setq i (1+ i))
  )
  
  ;; STATISTIQUES DE VALIDATION
  (princ "\n")
  (princ "\n=== STATISTIQUES DE VALIDATION ===")
  (princ (strcat "\n- Textes traités : " (itoa nb-traites)))
  (princ (strcat "\n- Textes valides : " (itoa nb-valides)))
  (princ (strcat "\n- Textes erreurs : " (itoa nb-erreurs)))
  (princ (strcat "\n- Taux de succès : " (vl-princ-to-string (/ (* nb-valides 100.0) nb-traites)) "%"))
  
  ;; 2. Trier par angle croissant
  (princ (strcat "\nNombre de textes valides trouvés : " (itoa (length liste-cotes-angles))))
  
  (if (> (length liste-cotes-angles) 0)
    (progn
      (setq liste-triee (tri-par-angle-complet liste-cotes-angles))
      
      ;; 3. Supprimer une cote sur deux
      (supprimer-alternees-detaille liste-triee)
    )
    (princ "\nAucun texte valide trouvé pour la suppression.")
  )
)

;; ===== TRI PAR ANGLE =====
(defun tri-par-angle-complet (liste-avec-angles)
  (if *AFFICHAGE-DEBUG* (princ "\nTri par angle..."))
  
  (setq liste-triee
    (vl-sort liste-avec-angles
      '(lambda (a b) (< (caddr a) (caddr b)))  ;; Compare les angles
    )
  )
  
  (if *AFFICHAGE-DEBUG*
    (progn
      (princ "\nOrdre final (par angle croissant) :")
      (setq compteur 0)
      (foreach item liste-triee
        (setq compteur (1+ compteur))
        (setq angle (caddr item))
        (princ (strcat "\n  " (itoa compteur) ". Angle = " (rtos angle 2 1)))
      )
    )
  )
  
  liste-triee
)

;; ===== SUPPRESSION ALTERNEE DETAILLEE =====
(defun supprimer-alternees-detaille (liste-triee)
  (princ "\n")
  (princ "\nSuppression alternee (1 sur 2)...")
  
  (setq compteur 0)
  (setq nb-gardees 0)
  (setq nb-supprimees 0)
  
  (foreach item liste-triee
    (setq compteur (1+ compteur))
    (setq ent (car item))
    (setq angle (caddr item))
    
    ;; REGLE : positions IMPAIRES gardees, PAIRES supprimees
    (if (= (rem compteur 2) 1)  ;; Position impaire (1,3,5,7...)
      (progn
        (setq nb-gardees (1+ nb-gardees))
        (princ (strcat "\n  " (itoa compteur) ". GARDEE    (angle " (rtos angle 2 1) ")"))
      )
      (progn
        (entdel ent)  ;; Supprimer
        (setq nb-supprimees (1+ nb-supprimees))
        (princ (strcat "\n  " (itoa compteur) ". SUPPRIMEE (angle " (rtos angle 2 1) ")"))
      )
    )
  )
  
  (princ "\n")
  (princ (strcat "\nRESULTAT FINAL :"))
  (princ (strcat "\n- Cotes gardees    : " (itoa nb-gardees)))
  (princ (strcat "\n- Cotes supprimees : " (itoa nb-supprimees)))
  (princ (strcat "\n- Total traite     : " (itoa compteur)))
  (princ "\nTermine !")
)

;; ===== COMMANDE POUR CHANGER LE CALQUE =====
(defun c:set-calque-cotes ()
  (princ (strcat "\nCalque actuel : " *CALQUE-COTES*))
  (setq nouveau-calque (getstring T "\nNouveau calque pour les cotes : "))
  (if (and nouveau-calque (> (strlen nouveau-calque) 0))
    (progn
      (setq *CALQUE-COTES* nouveau-calque)
      (princ (strcat "\nCalque mis a jour : " *CALQUE-COTES*))
    )
    (princ "\nAnnule.")
  )
  (princ)
)

;; ===== MESSAGES DE CHARGEMENT =====
(princ "\n=== SIMPLIF-COTES-SEMI-AUTO.LSP charge ===")
(princ "\n")
(princ "\nCOMMANDES DISPONIBLES :")
(princ "\n- SIMPLIF-COTES-SEMI : Simplification semi-automatique")
(princ "\n- SET-CALQUE-COTES   : Changer le calque cible")
(princ "\n")
(princ (strcat "\nPARAMETRES ACTUELS :"))
(princ (strcat "\n- Calque cible : " *CALQUE-COTES*))
(princ (strcat "\n- Debug        : " (if *AFFICHAGE-DEBUG* "ACTIVE" "DESACTIVE")))
(princ "\n")
(princ "\nUSAGE : Tapez SIMPLIF-COTES-SEMI dans AutoCAD")
(princ)
