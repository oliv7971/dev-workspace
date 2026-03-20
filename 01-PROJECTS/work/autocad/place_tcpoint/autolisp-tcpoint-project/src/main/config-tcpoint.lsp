;; CONFIG-TCPOINT.LSP v2.1
;; Ce fichier gère les paramètres de configuration pour le placement des blocs TCPOINT.
;; Les utilisateurs peuvent modifier des paramètres tels que le nom du bloc, le suffixe de calque et le rayon de proximité.

;; ===== PARAMETRES A MODIFIER =====
(setq *NOM-BLOC-TCPOINT* "TCPOINT")     ;; Nom du bloc à insérer
(setq *SUFFIXE-CALQUE* "_tete")         ;; Suffixe ajouté au calque de la ligne
(setq *CALQUE-CENTRES* "_INTERSEC_AXE_2D")       ;; Calque des points centres
(setq *CALQUE-AXES* "INS_GC_GAL_Galeries_Axes") ;; Calque des axes pour intersection
(setq *RAYON-PROXIMITE* 10.0)           ;; Rayon de proximité par défaut (m)
(setq *AFFICHAGE-DEBUG* T)              ;; T = affiche détails, nil = silencieux
(setq *MODE-AUTO* T)                    ;; T = détection auto centres, nil = sélection manuelle

(princ "\n=== CONFIG-TCPOINT.LSP v2.1 chargé ===")
(princ "\nLes paramètres de configuration ont été initialisés.")
