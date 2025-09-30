;; Script AutoLISP pour renommer les calques PRO_ vers leur équivalent sans préfixe
;; et fusionner avec les calques existants si nécessaire
;; 
;; Auteur: GitHub Copilot
;; Date: Septembre 2025
;; 
;; Usage: Charger le script et taper RENAMEPRO dans AutoCAD

(defun C:RENAMEPRO (/ layer-list pro-layers target-layer new-name result-msg current-name old-cmdecho *error*)
  
  ;; Fonction de gestion d'erreur locale
  (defun *error* (msg)
    (if old-cmdecho (setvar "CMDECHO" old-cmdecho))
    (princ (strcat "\nErreur: " msg))
    (princ "\nTraitement interrompu.")
    (princ)
  )
  
  (princ "\nDébut du traitement des calques PRO_...")
  
  ;; Sauvegarde et désactivation de CMDECHO
  (setq old-cmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  ;; Initialisation des variables
  (setq result-msg "")
  (setq pro-layers '())
  
  ;; Récupération de tous les calques du dessin
  (setq layer-list (vla-get-layers (vla-get-activedocument (vlax-get-acad-object))))
  
  ;; Recherche des calques commençant par "PRO_" - on stocke les NOMS, pas les objets
  (vlax-for layer layer-list
    (if (and (= (substr (vla-get-name layer) 1 4) "PRO_")
             (> (strlen (vla-get-name layer)) 4))
      (setq pro-layers (cons (vla-get-name layer) pro-layers))
    )
  )
  
  ;; Traitement de chaque calque PRO_
  (if pro-layers
    (progn
      (princ (strcat "\nTrouvé " (itoa (length pro-layers)) " calque(s) PRO_ à traiter:"))
      
      (foreach pro-layer-name pro-layers
        (setq current-name pro-layer-name)
        (setq new-name (substr current-name 5)) ; Supprime "PRO_"
        
        (princ (strcat "\n  Traitement: " current-name " -> " new-name))
        
        ;; Vérification si le calque source existe encore (pas supprimé)
        (if (tblsearch "LAYER" current-name)
          (progn
            ;; Vérification si le calque cible existe déjà
            (if (tblsearch "LAYER" new-name)
              ;; Cas 2: Le calque cible existe - fusion nécessaire
              (if (merge-layers current-name new-name)
                (progn
                  ;; Vérification si la fusion est complète
                  (if (tblsearch "LAYER" current-name)
                    (setq result-msg (strcat result-msg "\n    ⚠ " current-name " fusionné mais calque conservé (blocs?)"))
                    (setq result-msg (strcat result-msg "\n    ✓ " current-name " fusionné avec " new-name))
                  )
                )
                (setq result-msg (strcat result-msg "\n    ✗ Erreur lors de la fusion de " current-name))
              )
              ;; Cas 1: Le calque cible n'existe pas - renommage simple
              (progn
                (command "._-layer" "_rename" current-name new-name "")
                (while (> (getvar "CMDACTIVE") 0) (princ)) ; Attente fin commande
                (setq result-msg (strcat result-msg "\n    ✓ " current-name " renommé en " new-name))
              )
            )
          )
          (setq result-msg (strcat result-msg "\n    - " current-name " déjà supprimé"))
        )
      )
      
      ;; Affichage du résumé
      (princ "\n\nRésumé des opérations:")
      (princ result-msg)
      (princ "\nTraitement terminé.")
    )
    (princ "\nAucun calque PRO_ trouvé dans le dessin.")
  )
  
  ;; Restauration de CMDECHO
  (setvar "CMDECHO" old-cmdecho)
  
  (princ)
)

;; Fonction auxiliaire pour fusionner les calques
(defun merge-layers (source-name target-name / ss obj-count i ent old-cmdecho ent-data new-ent-data success-count)
  (princ (strcat "\n      Fusion de " source-name " vers " target-name "..."))
  
  ;; Sauvegarde et désactivation de CMDECHO
  (setq old-cmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  ;; Sélection de tous les objets sur le calque source
  (setq ss (ssget "X" (list (cons 8 source-name))))
  
  (if ss
    (progn
      (setq obj-count (sslength ss))
      (setq success-count 0)
      (princ (strcat "\n      Déplacement de " (itoa obj-count) " objet(s)..."))
      
      ;; Méthode robuste : déplacement objet par objet avec entmod
      (setq i 0)
      (while (< i obj-count)
        (setq ent (ssname ss i))
        (setq ent-data (entget ent))
        
        (if ent-data
          (progn
            (setq new-ent-data (subst (cons 8 target-name) (assoc 8 ent-data) ent-data))
            (if (entmod new-ent-data)
              (setq success-count (1+ success-count))
            )
          )
        )
        (setq i (1+ i))
      )
      
      (princ (strcat "\n      " (itoa success-count) "/" (itoa obj-count) " objet(s) déplacé(s)"))
      
      ;; Suppression du calque source si tous les objets ont été déplacés
      (if (= success-count obj-count)
        (progn
          (if (tblsearch "LAYER" source-name)
            (progn
              (command "._-layer" "_delete" source-name "")
              (while (> (getvar "CMDACTIVE") 0) (princ))
              
              ;; Vérification si le calque a bien été supprimé
              (if (tblsearch "LAYER" source-name)
                (princ "\n      ⚠️ Calque non supprimé (probablement utilisé dans des blocs)")
                (princ "\n      ✓ Calque supprimé avec succès")
              )
            )
          )
          ;; Restauration de CMDECHO
          (setvar "CMDECHO" old-cmdecho)
          T ; Retourne True si succès complet
        )
        (progn
          ;; Restauration de CMDECHO
          (setvar "CMDECHO" old-cmdecho)
          (princ "\n      ⚠️ Fusion partielle - calque source non supprimé")
          nil ; Retourne nil si échec partiel
        )
      )
    )
    (progn
      ;; Aucun objet sur le calque, suppression directe
      (princ "\n      Calque vide, suppression directe...")
      (if (tblsearch "LAYER" source-name)
        (command "._-layer" "_delete" source-name "")
      )
      
      ;; Restauration de CMDECHO
      (setvar "CMDECHO" old-cmdecho)
      T
    )
  )
)

;; Fonction pour diagnostiquer une paire de calques (source PRO_ et cible)
(defun C:DIAGPAIR (/ layer-name target-name layer-data target-data ss)
  (setq layer-name (getstring "\nNom du calque PRO_ à diagnostiquer: "))
  
  (if (and layer-name (/= layer-name ""))
    (progn
      (setq target-name (substr layer-name 5)) ; Supprime "PRO_"
      
      (princ (strcat "\n=== DIAGNOSTIC PAIRE DE CALQUES ==="))
      (princ (strcat "\nSource: " layer-name))
      (princ (strcat "\nCible:  " target-name))
      (princ "\n")
      
      ;; Diagnostic du calque source
      (princ "\n--- CALQUE SOURCE ---")
      (setq layer-data (tblsearch "LAYER" layer-name))
      (if layer-data
        (progn
          (princ "\n✓ Calque source trouvé")
          (setq ss (ssget "X" (list (cons 8 layer-name))))
          (if ss
            (princ (strcat "\n  " (itoa (sslength ss)) " objet(s) à déplacer"))
            (princ "\n  Aucun objet à déplacer")
          )
        )
        (princ "\n✗ Calque source NON TROUVÉ")
      )
      
      ;; Diagnostic du calque cible
      (princ "\n\n--- CALQUE CIBLE ---")
      (setq target-data (tblsearch "LAYER" target-name))
      (if target-data
        (progn
          (princ "\n✓ Calque cible EXISTE (fusion nécessaire)")
          (setq flags (cdr (assoc 70 target-data)))
          (princ (strcat "\n  Flags: " (itoa flags)))
          
          ;; Vérification des problèmes potentiels
          (if (= (logand flags 1) 1) (princ "\n  ⚠️ Calque cible GELÉ"))
          (if (= (logand flags 2) 2) (princ "\n  ⚠️ Calque cible VERROUILLÉ"))
          (if (= (logand flags 4) 4) (princ "\n  ⚠️ Calque cible dépendant d'une XREF"))
          (if (= (logand flags 16) 16) (princ "\n  ⚠️ Calque cible résolu de XREF"))
          
          ;; Vérification si c'est le calque courant
          (if (= (strcase target-name) (strcase (getvar "CLAYER")))
            (princ "\n  ⚠️ CALQUE CIBLE EST LE CALQUE COURANT")
          )
          
          ;; Objets existants sur le calque cible
          (setq ss (ssget "X" (list (cons 8 target-name))))
          (if ss
            (princ (strcat "\n  " (itoa (sslength ss)) " objet(s) déjà présent(s)"))
            (princ "\n  Aucun objet sur le calque cible")
          )
          
          ;; Test de fusion simulée
          (princ "\n\n--- TEST DE FUSION SIMULÉE ---")
          (setq ss-source (ssget "X" (list (cons 8 layer-name))))
          (if ss-source
            (progn
              (princ (strcat "\n  Tentative de déplacement de " (itoa (sslength ss-source)) " objet(s)..."))
              
              ;; Test avec le premier objet seulement
              (setq test-ent (ssname ss-source 0))
              (princ "\n  Test de changement de calque sur le premier objet...")
              
              ;; Sauvegarde du calque original
              (setq orig-layer (cdr (assoc 8 (entget test-ent))))
              
              ;; Test de changement avec entmod (plus sûr)
              (setq ent-data (entget test-ent))
              (setq new-ent-data (subst (cons 8 target-name) (assoc 8 ent-data) ent-data))
              
              (if (entmod new-ent-data)
                (progn
                  (princ "\n  ✓ Test réussi - l'objet peut être déplacé")
                  ;; Remettre sur le calque original
                  (setq restore-data (subst (cons 8 orig-layer) (assoc 8 new-ent-data) new-ent-data))
                  (entmod restore-data)
                  (princ "\n  ✓ Objet remis sur le calque original")
                )
                (princ "\n  ✗ Test échoué - l'objet ne peut pas être déplacé")
              )
            )
            (princ "\n  Aucun objet à tester")
          )
        )
        (princ "\n✓ Calque cible N'EXISTE PAS (renommage simple possible)")
      )
    )
    (princ "\nOpération annulée")
  )
  (princ)
)
(defun C:DIAGLAYER (/ layer-name layer-data layer-obj)
  (setq layer-name (getstring "\nNom du calque à diagnostiquer: "))
  
  (if (and layer-name (/= layer-name ""))
    (progn
      (princ (strcat "\n=== DIAGNOSTIC DU CALQUE: " layer-name " ==="))
      
      ;; Vérification existence avec tblsearch
      (setq layer-data (tblsearch "LAYER" layer-name))
      (if layer-data
        (progn
          (princ "\n✓ Calque trouvé avec tblsearch")
          (princ (strcat "\n  Nom: " (cdr (assoc 2 layer-data))))
          (princ (strcat "\n  Flags: " (itoa (cdr (assoc 70 layer-data)))))
          (princ (strcat "\n  Couleur: " (itoa (cdr (assoc 62 layer-data)))))
          (princ (strcat "\n  Type de ligne: " (cdr (assoc 6 layer-data))))
          
          ;; Vérification des flags spéciaux
          (setq flags (cdr (assoc 70 layer-data)))
          (if (= (logand flags 1) 1) (princ "\n  ⚠️ Calque GELÉ"))
          (if (= (logand flags 2) 2) (princ "\n  ⚠️ Calque VERROUILLÉ"))
          (if (= (logand flags 4) 4) (princ "\n  ⚠️ Calque dépendant d'une XREF"))
          (if (= (logand flags 16) 16) (princ "\n  ⚠️ Calque résolu de XREF"))
          
          ;; Vérification si c'est le calque courant
          (if (= (strcase layer-name) (strcase (getvar "CLAYER")))
            (princ "\n  ⚠️ C'EST LE CALQUE COURANT")
          )
          
          ;; Comptage des objets sur ce calque
          (setq ss (ssget "X" (list (cons 8 layer-name))))
          (if ss
            (princ (strcat "\n  Objets sur le calque: " (itoa (sslength ss))))
            (princ "\n  Aucun objet sur le calque")
          )
          
          ;; Test de renommage
          (princ "\n\n--- TEST DE RENOMMAGE ---")
          (setq test-name (strcat layer-name "_TEST"))
          (princ (strcat "\nTest de renommage vers: " test-name))
          
          (if (tblsearch "LAYER" test-name)
            (princ "\n  ⚠️ Le nom de test existe déjà")
            (progn
              (command "._-layer" "_rename" layer-name test-name "")
              (if (tblsearch "LAYER" test-name)
                (progn
                  (princ "\n  ✓ Renommage réussi")
                  ;; Remettre le nom original
                  (command "._-layer" "_rename" test-name layer-name "")
                  (princ "\n  ✓ Nom original restauré")
                )
                (princ "\n  ✗ ÉCHEC du renommage")
              )
            )
          )
        )
        (princ "\n✗ Calque NON TROUVÉ")
      )
    )
    (princ "\nOpération annulée")
  )
  (princ)
)

;; Fonction pour lister tous les calques PRO_ (utilitaire)
;; Fonction pour lister tous les calques PRO_ avec détails (utilitaire)
(defun C:LISTPRO (/ layer-list pro-count layer-name flags ss)
  (princ "\nCalques PRO_ présents dans le dessin:")
  (setq layer-list (vla-get-layers (vla-get-activedocument (vlax-get-acad-object))))
  (setq pro-count 0)
  
  (vlax-for layer layer-list
    (setq layer-name (vla-get-name layer))
    (if (= (substr layer-name 1 4) "PRO_")
      (progn
        (setq pro-count (1+ pro-count))
        (princ (strcat "\n  " layer-name))
        
        ;; Informations supplémentaires
        (setq layer-data (tblsearch "LAYER" layer-name))
        (if layer-data
          (progn
            (setq flags (cdr (assoc 70 layer-data)))
            (if (= (logand flags 1) 1) (princ " [GELÉ]"))
            (if (= (logand flags 2) 2) (princ " [VERROUILLÉ]"))
            (if (= (logand flags 4) 4) (princ " [XREF]"))
            (if (= (strcase layer-name) (strcase (getvar "CLAYER"))) (princ " [COURANT]"))
            
            ;; Comptage des objets
            (setq ss (ssget "X" (list (cons 8 layer-name))))
            (if ss
              (princ (strcat " (" (itoa (sslength ss)) " obj)"))
              (princ " (vide)")
            )
            
            ;; Vérification si le calque cible existe
            (setq target-name (substr layer-name 5))
            (if (tblsearch "LAYER" target-name)
              (princ (strcat " → " target-name " [EXISTE]"))
              (princ (strcat " → " target-name " [LIBRE]"))
            )
          )
        )
      )
    )
  )
  
  (princ (strcat "\n\nTotal: " (itoa pro-count) " calque(s) PRO_"))
  (princ)
)

;; Fonction pour traiter UN SEUL calque PRO_ spécifique (test)
(defun C:TESTPRO (/ layer-name target-name old-cmdecho *error*)
  
  ;; Fonction de gestion d'erreur locale
  (defun *error* (msg)
    (if old-cmdecho (setvar "CMDECHO" old-cmdecho))
    (princ (strcat "\nErreur: " msg))
    (princ)
  )
  
  (setq layer-name (getstring "\nNom du calque PRO_ à traiter: "))
  
  (if (and layer-name (/= layer-name ""))
    (progn
      ;; Sauvegarde et désactivation de CMDECHO
      (setq old-cmdecho (getvar "CMDECHO"))
      (setvar "CMDECHO" 0)
      
      (setq target-name (substr layer-name 5)) ; Supprime "PRO_"
      
      (princ (strcat "\n=== TRAITEMENT DU CALQUE ==="))
      (princ (strcat "\nSource: " layer-name))
      (princ (strcat "\nCible:  " target-name))
      
      ;; Vérification si le calque source existe
      (if (tblsearch "LAYER" layer-name)
        (progn
          ;; Vérification si le calque cible existe déjà
          (if (tblsearch "LAYER" target-name)
            ;; Cas fusion
            (progn
              (princ "\n\n--- FUSION ---")
              (if (merge-layers layer-name target-name)
                (princ (strcat "\n✓ " layer-name " fusionné avec " target-name))
                (princ (strcat "\n✗ Erreur lors de la fusion de " layer-name))
              )
            )
            ;; Cas renommage simple
            (progn
              (princ "\n\n--- RENOMMAGE ---")
              (command "._-layer" "_rename" layer-name target-name "")
              (while (> (getvar "CMDACTIVE") 0) (princ))
              (if (tblsearch "LAYER" target-name)
                (princ (strcat "\n✓ " layer-name " renommé en " target-name))
                (princ (strcat "\n✗ Erreur lors du renommage de " layer-name))
              )
            )
          )
        )
        (princ (strcat "\n✗ Calque " layer-name " non trouvé"))
      )
      
      ;; Restauration de CMDECHO
      (setvar "CMDECHO" old-cmdecho)
    )
    (princ "\nOpération annulée")
  )
  (princ)
)

;; Messages d'information
(princ "\n*** Script de gestion des calques PRO_ chargé ***")
(princ "\nCommandes disponibles:")
(princ "\n  RENAMEPRO - Traite tous les calques PRO_")
(princ "\n  LISTPRO   - Liste tous les calques PRO_ avec détails")
(princ "\n  DIAGLAYER - Diagnostic détaillé d'un calque spécifique")
(princ "\n  DIAGPAIR  - Diagnostic d'une paire source/cible")
(princ "\n  TESTPRO   - Traite UN SEUL calque PRO_ (test)")
(princ "\n")
