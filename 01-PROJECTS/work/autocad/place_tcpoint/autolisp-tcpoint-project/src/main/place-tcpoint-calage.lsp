;; filepath: c:\data\20-DEVELOPPEMENT\AutoLISP\place_tcpoint\autolisp-tcpoint-project\src\main\place-tcpoint-calage.lsp
;; PLACE-TCPOINT-CALAGE.LSP v1.2 (2025-09-08)
;; Placer des blocs TCPOINT sur les points d'intersection avec matricules A/B/C
;; 
;; FONCTIONNALITES :
;; - Place un TCPOINT sur chaque point du calque _INTERSEC_AXE_2D (matricule A_XX.XX)
;; - Place un TCPOINT 10m à droite de chaque point (matricule B_XX.XX)
;; - Place un TCPOINT 10m au-dessus de chaque point (matricule C_XX.XX)
;; - Recherche automatique du texte XX.XX situé ~12m au-dessus du point
;; - Remplit automatiquement l'attribut ALTITUDE avec Z=0.00
;; - Tous les points créés avec Z=0 sur le calque _CALAGE_PT

(vl-load-com)

;; ===== PARAMETRES =====
(setq *NOM-BLOC-TCPOINT* "TCPOINT")              ;; Nom du bloc à insérer
(setq *CALQUE-CENTRES* "_INTERSEC_AXE_2D")       ;; Calque des points centres
(setq *CALQUE-CALAGE* "_CALAGE_PT")              ;; Calque pour les TCPOINT de calage
(setq *DISTANCE-LATERALE* 10.0)                  ;; Distance à droite en mètres
(setq *DISTANCE-VERTICALE* 10.0)                 ;; Distance au-dessus en mètres
(setq *RAYON-RECHERCHE-TEXTE* 5.0)               ;; Rayon de recherche du texte (m) - augmenté
(setq *DISTANCE-TEXTE-APPROX* 12.0)              ;; Distance approximative du texte au-dessus (m)
(setq *TOLERANCE-VERTICALE* 3.0)                 ;; Tolérance verticale pour la recherche (m)
(setq *AFFICHAGE-DEBUG* T)                       ;; T = affiche détails, nil = silencieux

;; ===== FONCTIONS UTILITAIRES =====

;; Convertit VARIANT/SAFEARRAY/LIST -> LIST
(defun _to-list (v / val)
  (cond
    ((= (type v) 'VARIANT)
     (setq val (vlax-variant-value v))
     (cond
       ((= (type val) 'SAFEARRAY) (vlax-safearray->list val))
       ((= (type val) 'LIST)      val)
       (T                         nil)))
    ((= (type v) 'SAFEARRAY) (vlax-safearray->list v))
    ((= (type v) 'LIST)      v)
    (T                       nil)))

;; Vérifie si c'est un point 2D valide
(defun _is-pt2 (p) (and (listp p) (numberp (car p)) (numberp (cadr p))))

;; Vérifie si c'est un point 3D valide
(defun _is-pt3 (p) (and (_is-pt2 p) (numberp (caddr p))))

;; Normalise en (x y z) avec Z=0
(defun _pt3-z0 (v / l)
  (setq l (_to-list v))
  (cond
    ((and l (>= (length l) 2)) (list (car l) (cadr l) 0.0))
    (T (list 0.0 0.0 0.0))))

;; Distance 2D entre deux points
(defun _dist2d (p q)
  (if (and (listp p) (listp q) 
           (numberp (car p)) (numberp (cadr p))
           (numberp (car q)) (numberp (cadr q)))
    (sqrt (+ (expt (- (car p) (car q)) 2)
             (expt (- (cadr p) (cadr q)) 2)))
    1e99))

;; Conversion nombre->string robuste
(defun _safe-rtos (x /)
  (cond
    ((numberp x) (rtos x 2 2))
    ((= x T) "T")
    ((= x nil) "nil")
    (t (vl-princ-to-string x))))

;; ===== COLLECTE DES CENTRES =====
(defun _collect-centers ( / ss n i en vo p lst)
  (setq ss (ssget "_ALL" (list '(0 . "POINT") (cons 8 *CALQUE-CENTRES*))))
  (if ss
    (progn
      (setq n (sslength ss) i 0 lst '())
      (while (< i n)
        (setq en (ssname ss i)
              vo (vlax-ename->vla-object en)
              p  (_to-list (vla-get-Coordinates vo)))
        (if (_is-pt2 p) 
          (progn
            (setq p (_pt3-z0 p))  ;; Force Z=0
            (setq lst (cons p lst))
            (if *AFFICHAGE-DEBUG*
              (princ (strcat "\n  Centre collecté: " (vl-princ-to-string p)))
            )
          )
        )
        (setq i (1+ i)))
      (reverse lst))
    nil))

;; ===== RECHERCHE DU TEXTE AU-DESSUS DU POINT (AMELIOREE) =====
(defun _find-text-above (pt / ss zone-min zone-max n i en data type-obj txt-pt txt-val distance best-txt best-dist txt-y diff-y)
  ;; Définir la zone de recherche élargie
  (setq zone-min (list (- (car pt) *RAYON-RECHERCHE-TEXTE*)
                       (+ (cadr pt) (- *DISTANCE-TEXTE-APPROX* *TOLERANCE-VERTICALE*))
                       -1000.0))
  (setq zone-max (list (+ (car pt) *RAYON-RECHERCHE-TEXTE*)
                       (+ (cadr pt) *DISTANCE-TEXTE-APPROX* *TOLERANCE-VERTICALE*)
                       1000.0))
  
  (if *AFFICHAGE-DEBUG*
    (princ (strcat "\n    Zone recherche: X=" (_safe-rtos (car zone-min)) "-" (_safe-rtos (car zone-max))
                   " Y=" (_safe-rtos (cadr zone-min)) "-" (_safe-rtos (cadr zone-max))))
  )
  
  ;; Rechercher tous les textes dans le dessin
  (setq ss (ssget "_X" '((0 . "TEXT,MTEXT"))))
  
  (if ss
    (progn
      (setq n (sslength ss) i 0 best-txt nil best-dist 1e99)
      (while (< i n)
        (setq en (ssname ss i)
              data (entget en)
              type-obj (cdr (assoc 0 data)))
        
        ;; Récupérer la position et le contenu du texte
        (cond
          ((= type-obj "TEXT")
           (setq txt-pt (cdr (assoc 10 data))
                 txt-val (cdr (assoc 1 data))))
          ((= type-obj "MTEXT")
           (setq txt-pt (cdr (assoc 10 data))
                 txt-val (cdr (assoc 1 data))))
        )
        
        ;; Vérifier si le texte est dans la zone de recherche
        (if txt-pt
          (progn
            (setq txt-y (cadr txt-pt)
                  diff-y (- txt-y (cadr pt)))
            
            ;; Si le texte est au-dessus du point dans la plage attendue
            (if (and (>= (car txt-pt) (car zone-min))
                     (<= (car txt-pt) (car zone-max))
                     (>= txt-y (cadr zone-min))
                     (<= txt-y (cadr zone-max)))
              (progn
                ;; Calculer la distance au point de référence
                (setq distance (_dist2d pt txt-pt))
                
                ;; Nettoyer le texte (enlever les espaces et caractères spéciaux)
                (if txt-val
                  (setq txt-val (vl-string-trim " \t\n" txt-val))
                )
                
                ;; Vérifier si c'est un nombre au format XX.XX
                (if (and txt-val 
                         (or (wcmatch txt-val "#.#")
                             (wcmatch txt-val "#.##")
                             (wcmatch txt-val "##.#")
                             (wcmatch txt-val "##.##")
                             (wcmatch txt-val "###.#")
                             (wcmatch txt-val "###.##")
                             (wcmatch txt-val "#")
                             (wcmatch txt-val "##")
                             (wcmatch txt-val "###"))
                         (< distance best-dist))
                  (progn
                    (setq best-txt txt-val
                          best-dist distance)
                    (if *AFFICHAGE-DEBUG*
                      (princ (strcat "\n    Candidat trouvé: '" txt-val 
                                     "' à " (_safe-rtos distance) "m"
                                     " (Y diff=" (_safe-rtos diff-y) "m)"))
                    )
                  )
                )
              )
            )
          )
        )
        (setq i (1+ i)))
      
      (if (and *AFFICHAGE-DEBUG* best-txt)
        (princ (strcat "\n    >>> Meilleur texte: '" best-txt "'"))
      )
      
      best-txt)
    nil))

;; ===== DIAGNOSTIC DES ATTRIBUTS DU BLOC =====
(defun _check-block-attributes (block-name / blk-def attribs)
  (princ (strcat "\n\n=== ANALYSE DU BLOC '" block-name "' ==="))
  
  (if (tblsearch "BLOCK" block-name)
    (progn
      (setq blk-def (vla-item (vla-get-blocks (vla-get-activedocument (vlax-get-acad-object))) block-name))
      (princ "\nRecherche des attributs...")
      
      (vlax-for obj blk-def
        (if (= (vla-get-objectname obj) "AcDbAttributeDefinition")
          (progn
            (princ (strcat "\n  - Tag: '" (vla-get-tagstring obj) 
                          "' / Prompt: '" (vla-get-promptstring obj)
                          "' / Valeur par défaut: '" (vla-get-textstring obj) "'"))
          )
        )
      )
      T)
    (progn
      (princ (strcat "\nERREUR: Le bloc '" block-name "' n'existe pas!"))
      nil))
)

;; ===== INSERTION DE BLOC AVEC ATTRIBUTS (VERSION ROBUSTE) =====
(defun _insert-tcpoint-with-attrib (space pt layer matricule altitude / br attribs attrib i n tag-found attr-count)
  ;; Créer le calque s'il n'existe pas
  (if (not (tblsearch "LAYER" layer))
    (progn
      (command "._LAYER" "_M" layer "")
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n    Calque '" layer "' créé"))
      )
    )
  )
  
  ;; Insérer le bloc
  (setq br (vla-InsertBlock space (vlax-3d-point pt) *NOM-BLOC-TCPOINT* 1.0 1.0 1.0 0.0))
  (vla-put-Layer br layer)
  
  ;; Mettre à jour les attributs si le bloc en a
  (if (= (vla-get-HasAttributes br) :vlax-true)
    (progn
      (setq attribs (vlax-invoke br 'GetAttributes)
            attr-count 0)
      
      (if *AFFICHAGE-DEBUG*
        (princ (strcat "\n    " (itoa (length attribs)) " attribut(s) trouvé(s)"))
      )
      
      ;; Parcourir tous les attributs
      (foreach attrib attribs
        (setq tag-found (vla-get-TagString attrib))
        
        (if *AFFICHAGE-DEBUG*
          (princ (strcat "\n      Attribut trouvé: '" tag-found "'"))
        )
        
        ;; Chercher les tags possibles (avec et sans underscore, majuscules/minuscules)
        (cond
          ;; Attribut MATRICULE (différentes variations possibles)
          ((or (= (strcase tag-found) "MATRICULE")
               (= (strcase tag-found) "MAT")
               (= (strcase tag-found) "NUMERO")
               (= (strcase tag-found) "NUM")
               (= (strcase tag-found) "ID")
               (= (strcase tag-found) "NAME")
               (= (strcase tag-found) "NOM"))
           (vla-put-TextString attrib matricule)
           (setq attr-count (1+ attr-count))
           (if *AFFICHAGE-DEBUG*
             (princ (strcat " -> Matricule défini: " matricule))
           ))
          
          ;; Attribut ALTITUDE (différentes variations possibles)
          ((or (= (strcase tag-found) "ALTITUDE")
               (= (strcase tag-found) "ALT")
               (= (strcase tag-found) "Z")
               (= (strcase tag-found) "ELEVATION")
               (= (strcase tag-found) "ELEV")
               (= (strcase tag-found) "HAUTEUR"))
           (vla-put-TextString attrib altitude)
           (setq attr-count (1+ attr-count))
           (if *AFFICHAGE-DEBUG*
             (princ (strcat " -> Altitude définie: " altitude))
           ))
          
          ;; Si on n'a trouvé aucun tag connu, on remplit le premier attribut avec le matricule
          (T
           (if (= attr-count 0)
             (progn
               (vla-put-TextString attrib matricule)
               (setq attr-count (1+ attr-count))
               (if *AFFICHAGE-DEBUG*
                 (princ (strcat " -> Valeur par défaut: " matricule))
               )
             )
           ))
        )
      )
      
      ;; Si on n'a rempli aucun attribut, avertir
      (if (= attr-count 0)
        (princ "\n    ATTENTION: Aucun attribut n'a pu être rempli!")
      )
    )
    (if *AFFICHAGE-DEBUG*
      (princ "\n    ATTENTION: Le bloc n'a pas d'attributs!")
    )
  )
  
  br)

;; ===== COMMANDE PRINCIPALE =====
(defun c:place-tcpoint-calage ( / doc ms centres nb-centres i centre txt-num matricule-a matricule-b matricule-c 
                                  pt-a pt-b pt-c total-created altitude-str centres-traites)
  (princ "\n=== PLACEMENT DES TCPOINT DE CALAGE v1.2 ===")
  
  (setq doc (vla-get-ActiveDocument (vlax-get-acad-object))
        ms  (vla-get-ModelSpace doc))
  
  ;; Vérifier que le bloc TCPOINT existe et analyser ses attributs
  (if (not (tblsearch "BLOCK" *NOM-BLOC-TCPOINT*))
    (progn
      (princ (strcat "\nERREUR: Le bloc '" *NOM-BLOC-TCPOINT* "' n'existe pas !"))
      (princ "\nVeuillez créer ou charger le bloc TCPOINT avant d'utiliser cette commande.")
      (exit)
    )
    ;; Analyser le bloc pour afficher ses attributs
    (_check-block-attributes *NOM-BLOC-TCPOINT*)
  )
  
  ;; Collecter les centres
  (setq centres (_collect-centers))
  (if centres
    (progn
      (setq nb-centres (length centres))
      (princ (strcat "\n\n" (itoa nb-centres) " centres trouvés sur calque '" *CALQUE-CENTRES* "'"))
      
      (vl-catch-all-apply 'vla-StartUndoMark (list doc))
      
      (setq i 0 
            total-created 0
            centres-traites 0
            altitude-str "0.00")  ;; Altitude fixe à 0.00
      
      ;; Traiter chaque centre
      (foreach centre centres
        (setq i (1+ i))
        (princ (strcat "\n\n--- Centre " (itoa i) "/" (itoa nb-centres) " ---"))
        (princ (strcat "\n  Position: (" (_safe-rtos (car centre)) ", " (_safe-rtos (cadr centre)) ")"))
        
        ;; Rechercher le texte au-dessus
        (setq txt-num (_find-text-above centre))
        (if txt-num
          (progn
            (princ (strcat "\n  Numéro trouvé: " txt-num))
            (setq centres-traites (1+ centres-traites))
            
            ;; Créer les matricules
            (setq matricule-a (strcat "A_" txt-num)
                  matricule-b (strcat "B_" txt-num)
                  matricule-c (strcat "C_" txt-num))
            
            ;; Calculer les positions (Z=0)
            (setq pt-a (list (car centre) (cadr centre) 0.0)                          ;; Point A: sur le centre
                  pt-b (list (+ (car centre) *DISTANCE-LATERALE*) (cadr centre) 0.0)  ;; Point B: 10m à droite
                  pt-c (list (car centre) (+ (cadr centre) *DISTANCE-VERTICALE*) 0.0));; Point C: 10m au-dessus
            
            ;; Insérer les blocs
            (princ "\n  Insertion des TCPOINT:")
            
            ;; Point A
            (_insert-tcpoint-with-attrib ms pt-a *CALQUE-CALAGE* matricule-a altitude-str)
            (princ (strcat "\n    [OK] " matricule-a " placé à (" (_safe-rtos (car pt-a)) ", " (_safe-rtos (cadr pt-a)) ")"))
            (setq total-created (1+ total-created))
            
            ;; Point B
            (_insert-tcpoint-with-attrib ms pt-b *CALQUE-CALAGE* matricule-b altitude-str)
            (princ (strcat "\n    [OK] " matricule-b " placé à (" (_safe-rtos (car pt-b)) ", " (_safe-rtos (cadr pt-b)) ")"))
            (setq total-created (1+ total-created))
            
            ;; Point C
            (_insert-tcpoint-with-attrib ms pt-c *CALQUE-CALAGE* matricule-c altitude-str)
            (princ (strcat "\n    [OK] " matricule-c " placé à (" (_safe-rtos (car pt-c)) ", " (_safe-rtos (cadr pt-c)) ")"))
            (setq total-created (1+ total-created))
          )
          (princ "\n  [INFO] Aucun texte numérique trouvé au-dessus de ce point")
        )
      )
      
      (vl-catch-all-apply 'vla-EndUndoMark (list doc))
      
      ;; Résumé
      (princ "\n\n=== RÉSUMÉ ===")
      (princ (strcat "\n- Centres trouvés      : " (itoa nb-centres)))
      (princ (strcat "\n- Centres traités      : " (itoa centres-traites)))
      (princ (strcat "\n- TCPOINT créés        : " (itoa total-created)))
      (princ (strcat "\n- Calque utilisé       : " *CALQUE-CALAGE*))
      (princ (strcat "\n- Distance latérale    : " (_safe-rtos *DISTANCE-LATERALE*) "m"))
      (princ (strcat "\n- Distance verticale   : " (_safe-rtos *DISTANCE-VERTICALE*) "m"))
      (princ (strcat "\n- Altitude fixe        : " altitude-str))
      (princ "\n\nTerminé !")
    )
    (princ (strcat "\nAucun centre trouvé sur le calque '" *CALQUE-CENTRES* "'"))
  )
  
  (princ)
)

;; ===== COMMANDE POUR ANALYSER LE BLOC TCPOINT =====
(defun c:check-tcpoint ()
  (princ "\n=== ANALYSE DU BLOC TCPOINT ===")
  (_check-block-attributes *NOM-BLOC-TCPOINT*)
  (princ)
)

;; ===== COMMANDE DE TEST - VISUALISER LES ZONES DE RECHERCHE =====
(defun c:test-zones-texte ( / centres i centre zone-min zone-max)
  (princ "\n=== TEST DES ZONES DE RECHERCHE DE TEXTE ===")
  
  (setq centres (_collect-centers))
  (if centres
    (progn
      (setq i 0)
      (foreach centre centres
        (setq i (1+ i))
        
        ;; Calculer la zone de recherche
        (setq zone-min (list (- (car centre) *RAYON-RECHERCHE-TEXTE*)
                             (+ (cadr centre) (- *DISTANCE-TEXTE-APPROX* *TOLERANCE-VERTICALE*))
                             0.0))
        (setq zone-max (list (+ (car centre) *RAYON-RECHERCHE-TEXTE*)
                             (+ (cadr centre) *DISTANCE-TEXTE-APPROX* *TOLERANCE-VERTICALE*)
                             0.0))
        
        ;; Dessiner un rectangle pour visualiser la zone
        (command "._RECTANGLE" zone-min zone-max)
        
        (princ (strcat "\n  Zone " (itoa i) " créée autour du centre (" 
                       (_safe-rtos (car centre)) ", " (_safe-rtos (cadr centre)) ")"))
      )
      (princ (strcat "\n\n" (itoa (length centres)) " zones de recherche créées"))
      (princ "\nCes rectangles montrent où le programme cherche les textes")
    )
    (princ (strcat "\nAucun centre trouvé sur le calque '" *CALQUE-CENTRES* "'"))
  )
  (princ)
)

;; ===== COMMANDE DE DIAGNOSTIC =====
(defun c:diag-tcpoint-calage ( / centres i centre txt-found)
  (princ "\n=== DIAGNOSTIC RECHERCHE DE TEXTES ===")
  
  (setq centres (_collect-centers))
  (if centres
    (progn
      (setq i 0)
      (foreach centre centres
        (setq i (1+ i))
        (princ (strcat "\n\nCentre " (itoa i) ": (" (_safe-rtos (car centre)) ", " (_safe-rtos (cadr centre)) ")"))
        
        ;; Rechercher le texte
        (setq txt-found (_find-text-above centre))
        (if txt-found
          (princ (strcat "\n  → Texte trouvé: '" txt-found "'"))
          (princ "\n  → AUCUN TEXTE TROUVÉ")
        )
      )
    )
    (princ (strcat "\nAucun centre trouvé sur le calque '" *CALQUE-CENTRES* "'"))
  )
  (princ)
)

;; ===== COMMANDE DE CONFIGURATION =====
(defun c:config-tcpoint-calage ( / new-dist-lat new-dist-vert new-dist-texte new-rayon new-tolerance)
  (princ "\n=== CONFIGURATION TCPOINT-CALAGE ===")
  (princ (strcat "\nBloc TCPOINT         : " *NOM-BLOC-TCPOINT*))
  (princ (strcat "\nCalque centres       : " *CALQUE-CENTRES*))
  (princ (strcat "\nCalque calage        : " *CALQUE-CALAGE*))
  (princ (strcat "\nDistance latérale    : " (_safe-rtos *DISTANCE-LATERALE*) "m"))
  (princ (strcat "\nDistance verticale   : " (_safe-rtos *DISTANCE-VERTICALE*) "m"))
  (princ (strcat "\nDistance texte       : " (_safe-rtos *DISTANCE-TEXTE-APPROX*) "m"))
  (princ (strcat "\nRayon recherche      : " (_safe-rtos *RAYON-RECHERCHE-TEXTE*) "m"))
  (princ (strcat "\nTolérance verticale  : " (_safe-rtos *TOLERANCE-VERTICALE*) "m"))
  
  ;; Permettre de modifier les paramètres
  (princ "\n\nModifier les paramètres:")
  
  (setq new-dist-lat (getreal (strcat "\nDistance latérale (m) <" (_safe-rtos *DISTANCE-LATERALE*) ">: ")))
  (if new-dist-lat (setq *DISTANCE-LATERALE* new-dist-lat))
  
  (setq new-dist-vert (getreal (strcat "\nDistance verticale (m) <" (_safe-rtos *DISTANCE-VERTICALE*) ">: ")))
  (if new-dist-vert (setq *DISTANCE-VERTICALE* new-dist-vert))
  
  (setq new-dist-texte (getreal (strcat "\nDistance approximative du texte (m) <" (_safe-rtos *DISTANCE-TEXTE-APPROX*) ">: ")))
  (if new-dist-texte (setq *DISTANCE-TEXTE-APPROX* new-dist-texte))
  
  (setq new-rayon (getreal (strcat "\nRayon de recherche du texte (m) <" (_safe-rtos *RAYON-RECHERCHE-TEXTE*) ">: ")))
  (if new-rayon (setq *RAYON-RECHERCHE-TEXTE* new-rayon))
  
  (setq new-tolerance (getreal (strcat "\nTolérance verticale (m) <" (_safe-rtos *TOLERANCE-VERTICALE*) ">: ")))
  (if new-tolerance (setq *TOLERANCE-VERTICALE* new-tolerance))
  
  (princ "\n\n--- Configuration mise à jour ---")
  (princ)
)

;; ===== MESSAGES DE CHARGEMENT =====
(princ "\n=== PLACE-TCPOINT-CALAGE.LSP v1.2 chargé ===")
(princ "\n")
(princ "\nCOMMANDES DISPONIBLES :")
(princ "\n- PLACE-TCPOINT-CALAGE   : Placer les TCPOINT de calage (A/B/C)")
(princ "\n- CHECK-TCPOINT          : Analyser les attributs du bloc TCPOINT")
(princ "\n- TEST-ZONES-TEXTE       : Visualiser les zones de recherche des textes")
(princ "\n- DIAG-TCPOINT-CALAGE    : Diagnostic de la recherche de textes")
(princ "\n- CONFIG-TCPOINT-CALAGE  : Configurer les paramètres")
(princ "\n")
(princ "\nFONCTIONNEMENT :")
(princ "\n1. Lit les points sur le calque '_INTERSEC_AXE_2D'")
(princ "\n2. Cherche un texte numérique ~12m au-dessus de chaque point")
(princ "\n3. Crée 3 TCPOINT par centre :")
(princ "\n   - A_XX.XX : sur le point d'intersection")
(princ "\n   - B_XX.XX : 10m à droite")
(princ "\n   - C_XX.XX : 10m au-dessus")
(princ "\n4. Tous les points créés avec Z=0 sur le calque '_CALAGE_PT'")
(princ "\n5. Attribut ALTITUDE rempli avec '0.00'")
(princ "\n")
(princ "\nPARAMÈTRES ACTUELS :")
(princ (strcat "\n- Bloc              : " *NOM-BLOC-TCPOINT*))
(princ (strcat "\n- Calque centres    : " *CALQUE-CENTRES*))
(princ (strcat "\n- Calque calage     : " *CALQUE-CALAGE*))
(princ (strcat "\n- Distance latérale : " (_safe-rtos *DISTANCE-LATERALE*) "m"))
(princ (strcat "\n- Distance verticale: " (_safe-rtos *DISTANCE-VERTICALE*) "m"))
(princ (strcat "\n- Rayon recherche   : " (_safe-rtos *RAYON-RECHERCHE-TEXTE*) "m"))
(princ "\n")
(princ "\nUSAGE : Tapez PLACE-TCPOINT-CALAGE")
(princ)
