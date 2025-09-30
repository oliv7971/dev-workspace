;;; FUSION-CALQUES-PRO.LSP
;;; Fusionne les calques PRO_INS_*** vers INS_***
;;; Gère la fusion quand le calque cible existe déjà

(defun c:FUSION-PRO ()
  (vl-load-com)
  
  (princ "\n\n=== FUSION DES CALQUES PROJET (PRO_INS_***) ===\n")
  
  ;; Variables
  (setq calques-traites 0)
  (setq objets-deplaces 0)
  (setq erreurs 0)
  
  ;; Obtenir la table des calques
  (setq doc (vla-get-activedocument (vlax-get-acad-object)))
  (setq layers (vla-get-layers doc))
  
  ;; Créer une liste des calques à traiter
  (setq calques-pro '())
  (vlax-for layer layers
    (setq nom-calque (vla-get-name layer))
    (if (wcmatch nom-calque "PRO_INS_*")
      (setq calques-pro (cons nom-calque calques-pro))
    )
  )
  
  ;; Trier la liste
  (setq calques-pro (vl-sort calques-pro '<))
  
  (princ (strcat "\nNombre de calques PRO_INS_*** trouvés : " (itoa (length calques-pro)) "\n"))
  
  ;; Traiter chaque calque PRO_INS_***
  (foreach calque-source calques-pro
    (princ (strcat "\n• Traitement de " calque-source " : "))
    
    ;; Créer le nom du calque cible (enlever "PRO_")
    (setq calque-cible (substr calque-source 5))
    
    ;; Vérifier si le calque cible existe
    (if (tblsearch "LAYER" calque-cible)
      (progn
        ;; Le calque existe - FUSION nécessaire
        (princ (strcat "fusion vers " calque-cible))
        
        ;; Déverrouiller les deux calques
        (command "_-LAYER" "_UNLOCK" calque-source "")
        (command "_-LAYER" "_UNLOCK" calque-cible "")
        
        ;; Dégeler les deux calques
        (command "_-LAYER" "_THAW" calque-source "")
        (command "_-LAYER" "_THAW" calque-cible "")
        
        ;; Activer les deux calques
        (command "_-LAYER" "_ON" calque-source "")
        (command "_-LAYER" "_ON" calque-cible "")
        
        ;; Sélectionner tous les objets du calque source
        (setq ss (ssget "X" (list (cons 8 calque-source))))
        
        (if ss
          (progn
            (setq nb-objets (sslength ss))
            (princ (strcat " (" (itoa nb-objets) " objets) "))
            
            ;; Déplacer les objets vers le calque cible
            (setq i 0)
            (repeat nb-objets
              (setq ent (ssname ss i))
              (setq entdata (entget ent))
              ;; Changer le calque (code 8)
              (setq entdata (subst (cons 8 calque-cible) 
                                   (assoc 8 entdata) 
                                   entdata))
              (entmod entdata)
              (setq i (1+ i))
              (setq objets-deplaces (1+ objets-deplaces))
            )
            
            ;; Supprimer le calque source maintenant vide
            (if (not (equal calque-source (getvar "CLAYER")))
              (progn
                (command "_PURGE" "_LA" calque-source "_N")
                (princ " - Calque supprimé")
                (setq calques-traites (1+ calques-traites))
              )
              (progn
                (princ " - Calque actif, suppression manuelle nécessaire")
                (setq erreurs (1+ erreurs))
              )
            )
          )
          (progn
            ;; Pas d'objets dans le calque source
            (princ " (0 objets) ")
            ;; Essayer de supprimer le calque vide
            (if (not (equal calque-source (getvar "CLAYER")))
              (progn
                (command "_PURGE" "_LA" calque-source "_N")
                (princ " - Calque vide supprimé")
                (setq calques-traites (1+ calques-traites))
              )
              (progn
                (princ " - Calque actif")
                (setq erreurs (1+ erreurs))
              )
            )
          )
        )
      )
      (progn
        ;; Le calque cible n'existe pas - RENOMMAGE simple
        (princ (strcat "renommage en " calque-cible))
        
        ;; Renommer directement
        (command "_-RENAME" "_LA" calque-source calque-cible)
        (princ " - OK")
        (setq calques-traites (1+ calques-traites))
      )
    )
  )
  
  ;; Rapport final
  (princ "\n\n=== RAPPORT DE FUSION ===")
  (princ (strcat "\n• Calques traités : " (itoa calques-traites)))
  (princ (strcat "\n• Objets déplacés : " (itoa objets-deplaces)))
  (if (> erreurs 0)
    (princ (strcat "\n• Erreurs : " (itoa erreurs) " (calques actifs non supprimés)"))
  )
  
  ;; Purger le dessin
  (princ "\n\nPurge finale du dessin...")
  (command "_PURGE" "_ALL" "*" "_N")
  
  (princ "\n\n=== FUSION TERMINÉE ===\n")
  (princ)
)

;;; Commande alternative avec options
(defun c:FUSION-PRO-OPTIONS ( / choix)
  (princ "\n\n=== OPTIONS DE FUSION ===")
  (princ "\n1 - Fusionner PRO_INS_*** vers INS_***")
  (princ "\n2 - Fusionner REC_INS_*** vers INS_***")
  (princ "\n3 - Voir la liste des calques concernés")
  (princ "\n4 - Test sur un seul calque")
  
  (setq choix (getstring "\n\nVotre choix (1-4) : "))
  
  (cond
    ((= choix "1") (fusion-calques "PRO_INS_*" "PRO_"))
    ((= choix "2") (fusion-calques "REC_INS_*" "REC_"))
    ((= choix "3") (lister-calques))
    ((= choix "4") (test-fusion-unique))
    (t (princ "\nChoix invalide"))
  )
  (princ)
)

;;; Fonction générique de fusion
(defun fusion-calques (motif prefixe / doc layers calques-source)
  (vl-load-com)
  
  (princ (strcat "\n\n=== FUSION DES CALQUES " motif " ===\n"))
  
  (setq doc (vla-get-activedocument (vlax-get-acad-object)))
  (setq layers (vla-get-layers doc))
  
  (setq calques-traites 0)
  (setq objets-deplaces 0)
  
  ;; Collecter les calques correspondants
  (setq calques-source '())
  (vlax-for layer layers
    (setq nom-calque (vla-get-name layer))
    (if (wcmatch nom-calque motif)
      (setq calques-source (cons nom-calque calques-source))
    )
  )
  
  ;; Traiter chaque calque
  (foreach calque-source calques-source
    (princ (strcat "\n• " calque-source " : "))
    
    ;; Calculer le nom cible (enlever le préfixe)
    (setq calque-cible (substr calque-source (1+ (strlen prefixe))))
    
    (if (tblsearch "LAYER" calque-cible)
      (progn
        ;; Fusion
        (setq ss (ssget "X" (list (cons 8 calque-source))))
        (if ss
          (progn
            (setq nb (sslength ss))
            (princ (strcat "fusion de " (itoa nb) " objets vers " calque-cible))
            (command "_CHPROP" ss "" "_LA" calque-cible "")
            (setq objets-deplaces (+ objets-deplaces nb))
          )
          (princ "calque vide")
        )
        ;; Purger
        (command "_PURGE" "_LA" calque-source "_N")
        (setq calques-traites (1+ calques-traites))
      )
      (progn
        ;; Renommage simple
        (princ (strcat "renommé en " calque-cible))
        (command "_-RENAME" "_LA" calque-source calque-cible)
        (setq calques-traites (1+ calques-traites))
      )
    )
  )
  
  (princ (strcat "\n\nTerminé : " (itoa calques-traites) " calques, " 
                 (itoa objets-deplaces) " objets déplacés"))
)

;;; Lister tous les calques concernés
(defun lister-calques ( / doc layers)
  (vl-load-com)
  
  (princ "\n\n=== LISTE DES CALQUES ===\n")
  
  (setq doc (vla-get-activedocument (vlax-get-acad-object)))
  (setq layers (vla-get-layers doc))
  
  (princ "\nCalques PRO_INS_*** :")
  (vlax-for layer layers
    (setq nom (vla-get-name layer))
    (if (wcmatch nom "PRO_INS_*")
      (princ (strcat "\n  • " nom " -> " (substr nom 5)))
    )
  )
  
  (princ "\n\nCalques REC_INS_*** :")
  (vlax-for layer layers
    (setq nom (vla-get-name layer))
    (if (wcmatch nom "REC_INS_*")
      (princ (strcat "\n  • " nom " -> " (substr nom 5)))
    )
  )
  
  (princ "\n\nCalques INS_*** (cibles) :")
  (vlax-for layer layers
    (setq nom (vla-get-name layer))
    (if (and (wcmatch nom "INS_*")
             (not (wcmatch nom "PRO_INS_*"))
             (not (wcmatch nom "REC_INS_*")))
      (princ (strcat "\n  • " nom))
    )
  )
)

;;; Test sur un seul calque
(defun test-fusion-unique ( / calque-test calque-cible)
  (setq calque-test (getstring "\nNom du calque PRO_INS_*** à tester : "))
  
  (if (tblsearch "LAYER" calque-test)
    (progn
      (setq calque-cible (substr calque-test 5))
      (princ (strcat "\nTest : " calque-test " -> " calque-cible))
      
      (setq ss (ssget "X" (list (cons 8 calque-test))))
      (if ss
        (princ (strcat "\n  Nombre d'objets : " (itoa (sslength ss))))
        (princ "\n  Calque vide")
      )
      
      (if (tblsearch "LAYER" calque-cible)
        (princ "\n  Le calque cible existe - FUSION nécessaire")
        (princ "\n  Le calque cible n'existe pas - RENOMMAGE simple")
      )
    )
    (princ "\nCalque non trouvé")
  )
)

(princ "\n\nCommandes disponibles :")
(princ "\n  FUSION-PRO         : Fusion automatique PRO_INS_*** vers INS_***")
(princ "\n  FUSION-PRO-OPTIONS : Menu avec options")
(princ "\nChargement terminé.")