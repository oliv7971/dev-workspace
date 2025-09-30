; filepath: c:\data\20-DEVELOPPEMENT\AutoLISP\placePresentations\placePresentations.lsp
; placePresentations.lsp
; Script AutoLISP pour associer automatiquement les présentations aux coupes
; et centrer les fenêtres sur les intersections des axes

(vl-load-com)

;; Fonction pour obtenir toutes les intersections des lignes d'un calque
(defun get-intersections-on-layer (layer-name / ss i j ent1 ent2 pts all-pts data1 data2)
  (setq all-pts '())
  ; Rechercher les LIGNES sur le calque spécifié
  (setq ss (ssget "X" (list (cons 0 "LINE") (cons 8 layer-name))))
  
  (if ss
    (progn
      (princ (strcat "\n" (itoa (sslength ss)) " ligne(s) trouvée(s) sur le calque " layer-name))
      (setq i 0)
      (while (< i (sslength ss))
        (setq ent1 (ssname ss i))
        (setq data1 (entget ent1))
        
        ; Vérifier que c'est bien une ligne du bon calque
        (if (equal (cdr (assoc 8 data1)) layer-name)
          (progn
            (setq j (1+ i))
            (while (< j (sslength ss))
              (setq ent2 (ssname ss j))
              (setq data2 (entget ent2))
              
              ; Vérifier que c'est bien une ligne du bon calque
              (if (equal (cdr (assoc 8 data2)) layer-name)
                (progn
                  ; Obtenir l'intersection REELLE uniquement
                  (setq pts (get-strict-line-intersection ent1 ent2))
                  (if pts
                    (setq all-pts (append all-pts (list pts)))
                  )
                )
              )
              (setq j (1+ j))
            )
          )
        )
        (setq i (1+ i))
      )
    )
    (princ (strcat "\nAucune ligne trouvée sur le calque " layer-name))
  )
  
  ; Éliminer les doublons
  (setq all-pts (remove-duplicate-points all-pts 0.1))
  all-pts
)

;; Fonction stricte pour calculer l'intersection REELLE de deux lignes
(defun get-strict-line-intersection (ent1 ent2 / p1 p2 p3 p4 inter x y)
  ; Obtenir les points de début et fin des lignes
  (setq p1 (cdr (assoc 10 (entget ent1))))  ; Point de début ligne 1
  (setq p2 (cdr (assoc 11 (entget ent1))))  ; Point de fin ligne 1
  (setq p3 (cdr (assoc 10 (entget ent2))))  ; Point de début ligne 2
  (setq p4 (cdr (assoc 11 (entget ent2))))  ; Point de fin ligne 2
  
  ; Calculer l'intersection avec segments finis uniquement
  (setq inter (inters p1 p2 p3 p4 T))
  
  ; Double vérification : l'intersection doit être strictement dans les limites
  (if inter
    (progn
      (setq x (car inter))
      (setq y (cadr inter))
      
      ; Vérifier que le point est bien sur le segment 1
      (if (not (and 
                (<= x (+ (max (car p1) (car p2)) 0.01))
                (>= x (- (min (car p1) (car p2)) 0.01))
                (<= y (+ (max (cadr p1) (cadr p2)) 0.01))
                (>= y (- (min (cadr p1) (cadr p2)) 0.01))))
        (setq inter nil)
      )
      
      ; Vérifier que le point est bien sur le segment 2
      (if (and inter
               (not (and 
                     (<= x (+ (max (car p3) (car p4)) 0.01))
                     (>= x (- (min (car p3) (car p4)) 0.01))
                     (<= y (+ (max (cadr p3) (cadr p4)) 0.01))
                     (>= y (- (min (cadr p3) (cadr p4)) 0.01)))))
        (setq inter nil)
      )
      
      ; Si intersection valide, s'assurer qu'elle a 3 coordonnées
      (if inter
        (progn
          (if (= (length inter) 2)
            (setq inter (append inter '(0.0)))
          )
          inter
        )
        nil
      )
    )
    nil
  )
)

;; Fonction pour éliminer les points en double (avec tolérance)
(defun remove-duplicate-points (pts tolerance / unique-pts pt is-duplicate)
  (setq unique-pts '())
  
  (foreach pt pts
    (setq is-duplicate nil)
    
    ; Vérifier si ce point existe déjà dans la liste unique
    (foreach upt unique-pts
      (if (and (equal (car pt) (car upt) tolerance)    ; X
               (equal (cadr pt) (cadr upt) tolerance))  ; Y
        (setq is-duplicate T)
      )
    )
    
    ; Si ce n'est pas un doublon, l'ajouter
    (if (not is-duplicate)
      (setq unique-pts (append unique-pts (list pt)))
    )
  )
  
  unique-pts
)

;; Fonction pour trier les points de gauche à droite, puis de haut en bas
(defun sort-points-left-right-top-bottom (pts / sorted)
  (setq sorted (vl-sort pts
    '(lambda (p1 p2)
      (if (equal (cadr p1) (cadr p2) 1.0) ; Si même Y (tolérance de 1 unité)
        (< (car p1) (car p2))              ; Trier par X (gauche à droite)
        (> (cadr p1) (cadr p2))            ; Sinon trier par Y (haut en bas)
      )
    )
  ))
  sorted
)

;; Fonction pour obtenir toutes les présentations sauf Model et cartouche
(defun get-all-layouts (/ layouts layout-list layout-name parsed sorted)
  (setq layouts (vla-get-layouts (vla-get-activedocument (vlax-get-acad-object))))
  (setq layout-list '())
  
  (vlax-for layout layouts
    (setq layout-name (vla-get-name layout))
    ; Exclure "Model" et "cartouche" (insensible à la casse)
    (if (and (not (equal (strcase layout-name) "MODEL"))
             (not (equal (strcase layout-name) "CARTOUCHE")))
      (setq layout-list (append layout-list (list layout-name)))
    )
  )
  
  ; Trier les présentations par ordre numérique naturel
  (setq layout-list (natural-sort-layouts layout-list))
  layout-list
)

;; Fonction pour déverrouiller toutes les fenêtres d'une présentation
(defun unlock-all-viewports (layout-name / ss i ent)
  (setq ss (ssget "X" (list (cons 0 "VIEWPORT") (cons 410 layout-name))))
  
  (if ss
    (progn
      (setq i 0)
      (while (< i (sslength ss))
        (setq ent (ssname ss i))
        ; Déverrouiller la fenêtre
        (command "_.MVIEW" "_L" "_OFF" ent "")
        (setq i (1+ i))
      )
      T
    )
    nil
  )
)

;; Fonction batch corrigée avec le bon calcul d'échelle XP
(defun setup-viewport-corrected (layout-name center scale / oldcmdecho xp-factor)
  (setq oldcmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  ; Calcul du facteur XP basé sur l'échelle papier 1/1000
  ; Pour une échelle 1/100 : XP = 1000/100 = 10
  ; Pour une échelle 1/50  : XP = 1000/50 = 20
  ; Pour une échelle 1/200 : XP = 1000/200 = 5
  (setq xp-factor (/ 1000.0 scale))
  
  ; Activer la présentation
  (setvar "CTAB" layout-name)
  (command "_.REGEN")
  
  ; DÉVERROUILLER les fenêtres
  (unlock-all-viewports layout-name)
  
  ; Passer en espace objet
  (command "_.MSPACE")
  
  ; CORRECTION: Centrer avec une hauteur spécifiée
  ; Utiliser la valeur XP comme hauteur pour le zoom center
  (command "_.ZOOM" "_C" center (rtos xp-factor 2 8))
  
  ; Appliquer l'échelle XP finale
  (command "_.ZOOM" (strcat (rtos xp-factor 2 8) "xp"))
  
  ; Retour espace papier
  (command "_.PSPACE")
  
  ; Reverrouiller la fenêtre
  (command "_.MVIEW" "_L" "_ON" "_L" "")
  
  ; Restaurer
  (setvar "CMDECHO" oldcmdecho)
  T
)

;; Fonction pour tri numérique naturel
(defun natural-sort-layouts (lst / extract-number)
  ; Fonction pour extraire le nombre d'un nom de présentation
  (defun extract-number (str / i num-str)
    (setq i 1)
    (setq num-str "")
    ; Parcourir la chaîne pour extraire les chiffres
    (while (<= i (strlen str))
      (if (member (substr str i 1) '("0" "1" "2" "3" "4" "5" "6" "7" "8" "9"))
        (setq num-str (strcat num-str (substr str i 1)))
      )
      (setq i (1+ i))
    )
    ; Convertir en nombre, ou retourner 0 si pas de nombre
    (if (> (strlen num-str) 0)
      (atoi num-str)
      0
    )
  )
  
  ; Trier la liste en utilisant l'extraction numérique
  (vl-sort lst
    '(lambda (a b)
      (< (extract-number a) (extract-number b))
    )
  )
)

;; FONCTION PRINCIPALE
(defun c:BATCH-VP-SETUP (/ intersections layouts scale i center layout-name confirm old-ctab success-count)
  (princ "\n=== CONFIGURATION BATCH DES PRÉSENTATIONS ===\n")
  
  ; Obtenir l'échelle souhaitée
  (setq scale (getreal "\nÉchelle des fenêtres (ex: 100 pour 1/100) [100]: "))
  (if (not scale) (setq scale 100.0))
  
  ; Récupérer les intersections des axes
  (princ "\nRecherche des intersections sur le calque INS_GC_GAL_Galeries_Axes...")
  (setq intersections (get-intersections-on-layer "INS_GC_GAL_Galeries_Axes"))
  
  (if intersections
    (progn
      (princ (strcat "\n" (itoa (length intersections)) " intersection(s) trouvée(s)."))
      
      ; Trier les intersections
      (setq intersections (sort-points-left-right-top-bottom intersections))
      
      ; Récupérer toutes les présentations (sans Model et cartouche)
      (setq layouts (get-all-layouts))
      (princ (strcat "\n" (itoa (length layouts)) " présentation(s) trouvée(s) (sans 'cartouche')."))
      
      ; Vérifier la correspondance des nombres
      (if (/= (length intersections) (length layouts))
        (princ (strcat "\n⚠ ATTENTION: " (itoa (length intersections)) 
                      " intersections pour " (itoa (length layouts)) 
                      " présentations !"))
      )
      
      ; Afficher les premières associations
      (princ "\n\nCorrespondance prévue (Coupe -> Présentation):")
      (setq i 0)
      (while (and (< i 5) (< i (length intersections)) (< i (length layouts)))
        (setq center (nth i intersections))
        (setq layout-name (nth i layouts))
        (princ (strcat "\n  Coupe " (itoa (1+ i)) " -> Présentation '" layout-name 
                      "' (X=" (rtos (car center) 2 2) 
                      ", Y=" (rtos (cadr center) 2 2) ")"))
        (setq i (1+ i))
      )
      (if (> (min (length intersections) (length layouts)) 5)
        (princ (strcat "\n  ... et " 
                      (itoa (- (min (length intersections) (length layouts)) 5)) 
                      " autres")))
      
      ; Demander confirmation
      (initget "Oui Non")
      (setq confirm (getkword "\n\nContinuer ? [Oui/Non] <Oui>: "))
      (if (not confirm) (setq confirm "Oui"))
      
      (if (equal confirm "Oui")
        (progn
          ; Sauvegarder la présentation courante
          (setq old-ctab (getvar "CTAB"))
          (setq success-count 0)
          
          ; Traiter chaque présentation
          (setq i 0)
          (while (and (< i (length intersections)) 
                      (< i (length layouts)))
            (setq layout-name (nth i layouts))
            (setq center (nth i intersections))
            
            (princ (strcat "\nCoupe " (itoa (1+ i)) " -> " layout-name))
            
            ; Configurer la fenêtre
            (if (setup-viewport-corrected layout-name center scale)
              (progn
                (princ " ✓")
                (setq success-count (1+ success-count))
              )
              (princ " ✗")
            )
            
            (setq i (1+ i))
          )
          
          ; Restaurer la présentation originale
          (setvar "CTAB" old-ctab)
          
          ; Résumé
          (princ "\n\n=== RÉSUMÉ ===")
          (princ (strcat "\n✓ " (itoa success-count) "/" (itoa i) " présentations configurées"))
          (princ (strcat "\n✓ Échelle appliquée: 1/" (rtos scale 2 0) " (" 
                        (rtos (/ 1000.0 scale) 2 2) "XP)"))
          (princ "\n✓ Les fenêtres ont été reverrouillées")
        )
        (princ "\nAnnulé.")
      )
    )
    (princ "\nAucune intersection trouvée sur le calque spécifié.")
  )
  
  (princ "\n")
  (princ)
)

;; Fonction pour visualiser les intersections
(defun c:SHOW-INTERSECTIONS (/ intersections i pt layouts)
  (princ "\nRecherche des intersections...")
  (setq intersections (get-intersections-on-layer "INS_GC_GAL_Galeries_Axes"))
  
  (if intersections
    (progn
      (princ (strcat "\n" (itoa (length intersections)) " intersection(s) trouvée(s)."))
      (setq intersections (sort-points-left-right-top-bottom intersections))
      
      ; Obtenir aussi les présentations pour info
      (setq layouts (get-all-layouts))
      
      (setq i 1)
      (foreach pt intersections
        ; Créer un cercle temporaire pour visualiser l'intersection
        (entmake (list '(0 . "CIRCLE")
                      (cons 10 pt)
                      (cons 40 10.0) ; Rayon du cercle
                      '(62 . 1))) ; Couleur rouge
        
        ; Ajouter un texte avec le numéro de coupe
        (entmake (list '(0 . "TEXT")
                      (cons 10 pt)
                      (cons 11 pt)
                      (cons 1 (strcat "C" (itoa i))) ; "C" pour Coupe
                      (cons 40 5.0) ; Hauteur du texte
                      '(72 . 1)
                      '(73 . 2)
                      '(62 . 1))) ; Couleur rouge
        
        (princ (strcat "\nCoupe " (itoa i) ": X="
                      (rtos (car pt) 2 2) ", Y=" 
                      (rtos (cadr pt) 2 2)))
        
        ; Afficher la présentation associée si elle existe
        (if (and layouts (< (1- i) (length layouts)))
          (princ (strcat " -> Présentation '" (nth (1- i) layouts) "'"))
          (princ " -> (pas de présentation)")
        )
        
        (setq i (1+ i))
      )
      
      (princ (strcat "\n\n" (itoa (length intersections)) 
                    " coupe(s) marquée(s) en rouge."))
    )
    (princ "\nAucune intersection trouvée.")
  )
  (princ)
)

;; Fonction pour visualiser l'ordre des présentations
(defun c:SHOW-LAYOUT-ORDER (/ layouts i)
  (princ "\n=== ORDRE DES PRÉSENTATIONS ===\n")
  (setq layouts (get-all-layouts))
  (setq i 1)
  (foreach layout layouts
    (princ (strcat "\n" (itoa i) ". " layout))
    (setq i (1+ i))
  )
  (princ (strcat "\n\nTotal: " (itoa (length layouts)) " présentation(s)"))
  (princ)
)

;; Fonction pour nettoyer les marquages
(defun c:CLEAN-MARKS (/ ss)
  (princ "\nNettoyage des marquages...")
  
  (setq ss (ssget "X" '((0 . "CIRCLE") (62 . 1))))
  (if ss
    (progn
      (command "_ERASE" ss "")
      (princ (strcat "\n" (itoa (sslength ss)) " cercle(s) supprimé(s)."))
    )
  )
  
  (setq ss (ssget "X" '((0 . "TEXT") (62 . 1))))
  (if ss
    (progn
      (command "_ERASE" ss "")
      (princ (strcat "\n" (itoa (sslength ss)) " texte(s) supprimé(s)."))
    )
  )
  
  (princ "\nNettoyage terminé.")
  (princ)
)

;; Commande de test pour le calcul XP
(defun c:TEST-XP (/ scale xp)
  (princ "\n=== TEST CALCUL ÉCHELLE XP ===")
  (princ "\n(Base papier: 1/1000)\n")
  
  (princ "\nExemples de conversion:")
  (princ "\n  1/50   -> 20 XP")
  (princ "\n  1/100  -> 10 XP") 
  (princ "\n  1/200  -> 5 XP")
  (princ "\n  1/500  -> 2 XP")
  
  (setq scale (getreal "\n\nÉchelle souhaitée (ex: 100 pour 1/100): "))
  (if scale
    (progn
      (setq xp (/ 1000.0 scale))
      (princ (strcat "\nPour une échelle 1/" (rtos scale 2 0) 
                    " -> " (rtos xp 2 2) " XP"))
    )
  )
  (princ)
)

;; Commande de test simple CORRIGÉE
(defun c:TEST-SIMPLE (/ layout-name center scale xp-factor oldcmdecho)
  (princ "\n=== TEST SIMPLE ===")
  
  ; Obtenir les paramètres
  (setq layout-name (getstring "\nNom de la présentation: "))
  
  ; Obtenir le centre (avec possibilité de cliquer)
  (setq center (getpoint "\nCentre de vue (cliquez ou entrez X,Y): "))
  (if (not center)
    (progn
      (princ "\nAnnulé - Aucun point spécifié")
      (princ)
      (exit)
    )
  )
  
  ; Obtenir l'échelle avec valeur par défaut
  (setq scale (getreal "\nÉchelle (ex: 100 pour 1/100) [100]: "))
  (if (not scale) 
    (setq scale 100.0))  ; Valeur par défaut si rien n'est entré
  
  ; Calcul XP
  (setq xp-factor (/ 1000.0 scale))
  (princ (strcat "\n  Échelle 1/" (rtos scale 2 0) " = " (rtos xp-factor 2 2) "XP"))
  
  (setq oldcmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  ; Activer la présentation
  (setvar "CTAB" layout-name)
  
  ; Déverrouiller
  (unlock-all-viewports layout-name)
  
  ; Passer en espace objet
  (command "_.MSPACE")
  
  ; CORRECTION: Centrer avec une hauteur spécifiée
  ; Utiliser la valeur XP comme hauteur pour le zoom center
  (command "_.ZOOM" "_C" center (rtos xp-factor 2 8))
  
  ; Appliquer l'échelle XP finale
  (command "_.ZOOM" (strcat (rtos xp-factor 2 8) "xp"))
  
  ; Retour et verrouillage
  (command "_.PSPACE")
  (command "_.MVIEW" "_L" "_ON" "_L" "")
  
  (setvar "CMDECHO" oldcmdecho)
  
  (princ "\n✓ Terminé")
  (princ)
)

;; NOUVELLE COMMANDE : Configuration automatique rapide avec échelle 1:70
(defun c:AUTO-VP (/ intersections layouts scale old-ctab success-count i layout-name center)
  
  (princ "\n=== CONFIGURATION AUTOMATIQUE RAPIDE ===\n")
  (princ "\nUtilisation des paramètres par défaut:")
  (princ "\n  - Calque: INS_GC_GAL_Galeries_Axes")
  (princ "\n  - Échelle: 1/70 (14.29 XP)")
  (princ "\n  - Exclusion: Model et cartouche")
  
  ; Échelle par défaut 1/70 (la plus courante sur vos plans)
  (setq scale 70.0)
  
  ; Récupérer les intersections
  (setq intersections (get-intersections-on-layer "INS_GC_GAL_Galeries_Axes"))
  
  (if intersections
    (progn
      (princ (strcat "\n\n" (itoa (length intersections)) " coupe(s) trouvée(s)"))
      
      ; Trier les intersections
      (setq intersections (sort-points-left-right-top-bottom intersections))
      
      ; Récupérer les présentations
      (setq layouts (get-all-layouts))
      (princ (strcat "\n" (itoa (length layouts)) " présentation(s) trouvée(s)"))
      
      ; Traiter automatiquement sans confirmation
      (princ "\n\nTraitement en cours...")
      
      ; Sauvegarder la présentation courante
      (setq old-ctab (getvar "CTAB"))
      (setq success-count 0)
      
      ; Traiter chaque présentation
      (setq i 0)
      (while (and (< i (length intersections)) 
                  (< i (length layouts)))
        (setq layout-name (nth i layouts))
        (setq center (nth i intersections))
        
        (princ (strcat "\n  " (itoa (1+ i)) ". " layout-name))
        
        ; Configurer la fenêtre
        (if (setup-viewport-corrected layout-name center scale)
          (progn
            (princ " ✓")
            (setq success-count (1+ success-count))
          )
          (princ " ✗")
        )
        
        (setq i (1+ i))
      )
      
      ; Restaurer la présentation originale
      (setvar "CTAB" old-ctab)
      
      ; Résumé
      (princ "\n\n=== TERMINÉ ===")
      (princ (strcat "\n✓ " (itoa success-count) "/" (itoa i) " présentations configurées"))
      (princ (strcat "\n✓ Échelle: 1/70 (" (rtos (/ 1000.0 70) 2 2) " XP)"))
      (princ "\n✓ Fenêtres reverrouillées")
    )
    (princ "\n✗ Aucune intersection trouvée")
  )
  
  (princ "\n")
  (princ)
)

;; NOUVELLE COMMANDE : Configuration avec échelle personnalisée
(defun c:AUTO-VP-SCALE (/ scale)
  (princ "\n=== CONFIGURATION AUTOMATIQUE AVEC ÉCHELLE ===\n")
  
  ; Demander uniquement l'échelle avec 70 comme valeur par défaut
  (setq scale (getreal "\nÉchelle (ex: 50, 70, 100, 200) [70]: "))
  (if (not scale) (setq scale 70.0))  ; Valeur par défaut 1:70
  
  (princ (strcat "\nÉchelle choisie: 1/" (rtos scale 2 0) " (" (rtos (/ 1000.0 scale) 2 2) " XP)"))
  
  ; Appeler la fonction principale directement avec l'échelle
  (auto-process-layouts scale)
)

;; Fonction interne pour le traitement automatique
(defun auto-process-layouts (scale / intersections layouts i center layout-name old-ctab success-count)
  ; Récupérer les intersections
  (setq intersections (get-intersections-on-layer "INS_GC_GAL_Galeries_Axes"))
  
  (if intersections
    (progn
      (princ (strcat "\n" (itoa (length intersections)) " coupe(s) trouvée(s)"))
      
      ; Trier les intersections
      (setq intersections (sort-points-left-right-top-bottom intersections))
      
      ; Récupérer les présentations
      (setq layouts (get-all-layouts))
      (princ (strcat "\n" (itoa (length layouts)) " présentation(s) trouvée(s)"))
      
      ; Traiter automatiquement
      (princ "\n\nTraitement...")
      
      ; Sauvegarder la présentation courante
      (setq old-ctab (getvar "CTAB"))
      (setq success-count 0)
      
      ; Traiter chaque présentation
      (setq i 0)
      (while (and (< i (length intersections)) 
                  (< i (length layouts)))
        (setq layout-name (nth i layouts))
        (setq center (nth i intersections))
        
        (princ (strcat "\n  " layout-name))
        
        ; Configurer la fenêtre
        (if (setup-viewport-corrected layout-name center scale)
          (progn
            (princ " ✓")
            (setq success-count (1+ success-count))
          )
          (princ " ✗")
        )
        
        (setq i (1+ i))
      )
      
      ; Restaurer la présentation originale
      (setvar "CTAB" old-ctab)
      
      ; Résumé
      (princ "\n\n✓ Terminé: ")
      (princ (strcat (itoa success-count) "/" (itoa i) " présentations"))
      (princ (strcat "\n✓ Échelle appliquée: 1/" (rtos scale 2 0)))
    )
    (princ "\n✗ Aucune intersection trouvée")
  )
  (princ)
)

;; Message de chargement mis à jour
(princ "\n")
(princ "\n=== COMMANDES DISPONIBLES ===")
(princ "\n")
(princ "\n  COMMANDES AUTOMATIQUES:")
(princ "\n  AUTO-VP            : Configuration automatique (échelle 1/70 par défaut)")
(princ "\n  AUTO-VP-SCALE      : Configuration automatique avec choix d'échelle")
(princ "\n")
(princ "\n  COMMANDES INTERACTIVES:")
(princ "\n  BATCH-VP-SETUP     : Configuration avec confirmation et choix d'échelle")
(princ "\n  TEST-SIMPLE        : Test sur une présentation unique")
(princ "\n")
(princ "\n  VISUALISATION:")
(princ "\n  SHOW-INTERSECTIONS : Affiche les intersections numérotées")
(princ "\n  SHOW-LAYOUT-ORDER  : Affiche l'ordre des présentations")
(princ "\n  CLEAN-MARKS        : Supprime les marquages")
(princ "\n")
(princ "\n  UTILITAIRES:")
(princ "\n  TEST-XP            : Calculateur de conversion échelle -> XP")
(princ "\n")
(princ "\nÉchelles courantes avec base papier 1/1000:")
(princ "\n  1/50  = 20 XP")
(princ "\n  1/70  = 14.29 XP (défaut)")
(princ "\n  1/100 = 10 XP")
(princ "\n  1/200 = 5 XP")
(princ "\n")
