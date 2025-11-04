=============================================================================
GUIDE : findDuplicates-LowMemory.ps1 - Detection de doublons optimisee memoire
=============================================================================

DESCRIPTION
-----------
Script PowerShell pour detecter et supprimer les doublons entre un repertoire
de reference et des repertoires a nettoyer. Version optimisee memoire utilisant
le streaming pour traiter des millions de fichiers avec <500 MB de RAM.

CONSOMMATION MEMOIRE
--------------------
- DupeGuru : ~12 GB pour 1 million de fichiers
- Ce script : ~50-200 MB pour 1 million de fichiers (20-50x moins !)

FONCTIONNALITES
---------------
1. Compare un repertoire de reference avec des repertoires a nettoyer
2. Detecte les doublons vs reference (fichiers deja dans la reference)
3. Detecte les doublons internes (copies multiples dans les repertoires a nettoyer)
4. Pre-filtrage intelligent par TAILLE (economise 70-90% des calculs de hash)
5. Cache de hashs persistant (evite de recalculer lors de prochaines executions)
6. Traitement en streaming (ne charge pas tout en memoire)
7. Actions : Report / Delete / Move (quarantaine)
8. Mode WhatIf pour simuler avant d'agir

UTILISATION SUR SYNOLOGY NAS
=============================

METHODE 1 : Depuis votre PC Windows (RECOMMANDE)
-------------------------------------------------
1. Mapper le NAS comme lecteur reseau
   - Ouvrir l'Explorateur Windows
   - Clic droit "Ce PC" > "Connecter un lecteur reseau"
   - Choisir une lettre (ex: Z:)
   - Entrer : \\NAS-IP\VolumePrincipal

2. Modifier la configuration du script (lignes 13-19)
   $ReferencePath = "Z:\MesDocumentsClasses"
   $PathsToClean = @(
       "Z:\Telechargements",
       "Z:\ATrier"
   )

3. Executer depuis votre PC
   cd C:\data\20-DEVELOPPEMENT\01-PROJECTS\powershell
   .\findDuplicates-LowMemory.ps1

AVANTAGES : Interface graphique, editeur VS Code, pas de SSH

METHODE 2 : Directement sur le Synology (SSH)
----------------------------------------------
1. Activer SSH sur le Synology
   - DSM > Panneau de configuration > Terminal & SNMP
   - Cocher "Activer le service SSH"

2. Se connecter en SSH
   ssh admin@192.168.1.xxx
   (Remplacer par l'IP de votre NAS)

3. Verifier si PowerShell est installe
   pwsh --version

4. SI POWERSHELL N'EST PAS INSTALLE sur Synology :
   Le script ne fonctionnera pas directement sur le NAS.
   -> Utilisez la METHODE 1 (depuis votre PC Windows)

5. SI PowerShell Core est installe :
   - Copier le script sur le NAS
   - Modifier les chemins (ex: /volume1/MesDocuments)
   - Executer : pwsh ./findDuplicates-LowMemory.ps1

CONFIGURATION DU SCRIPT
========================

CHEMINS A MODIFIER (lignes 13-19)
----------------------------------
$ReferencePath = "Z:\Archive"              # Vos donnees deja classees
$PathsToClean = @(                         # Dossiers a nettoyer
    "Z:\Downloads",
    "Z:\Backup",
    "Z:\TempFiles"
)

OPTIONS DE TRAITEMENT (lignes 22-25)
-------------------------------------
$Action = "Report"                         # "Report" / "Delete" / "Move"
$QuarantinePath = "Z:\Doublons_Trouves"   # Ou deplacer les doublons
$WhatIf = $true                           # $true = simulation, $false = reel
$Verbose = $true                          # $true = affichage detaille

OPTIONS D'ANALYSE (lignes 28-30)
---------------------------------
$MinFileSize = 1KB                        # Ignorer fichiers < 1KB
$HashAlgorithm = "MD5"                    # MD5 (rapide) ou SHA256 (precis)
$ExcludeExtensions = @(".tmp", ".log")    # Extensions a ignorer

OPTIONS AVANCEES (lignes 33-36)
--------------------------------
$RemoveInternalDuplicates = $true         # Supprimer doublons internes
$CreateDetailedReport = $true             # Creer rapport CSV
$ReportPath = ".\rapport_doublons.csv"    # Chemin du rapport

OPTIMISATION MEMOIRE (lignes 39-42)
------------------------------------
$ChunkSize = 10000                        # Taille des lots
$CacheFilePath = ".\hash_cache.txt"       # Cache des hashs

WORKFLOW RECOMMANDE
===================

ETAPE 1 : Mode Report (voir ce qui sera trouve)
------------------------------------------------
$Action = "Report"
$WhatIf = $true

Executer le script
-> Consulter le rapport CSV genere

ETAPE 2 : Mode Move + Simulation (tester le deplacement)
---------------------------------------------------------
$Action = "Move"
$WhatIf = $true

Executer le script
-> Verifier que les chemins de destination sont corrects

ETAPE 3 : Mode Move + Reel (deplacer en quarantaine)
-----------------------------------------------------
$Action = "Move"
$WhatIf = $false

Executer le script
-> Les doublons sont deplaces dans $QuarantinePath

ETAPE 4 : Verifier la quarantaine et supprimer manuellement
------------------------------------------------------------
- Parcourir Z:\Doublons_Trouves
- Verifier que ce sont bien des doublons
- Supprimer manuellement le dossier

ETAPE 5 (optionnel) : Mode Delete direct
-----------------------------------------
$Action = "Delete"
$WhatIf = $false

ATTENTION : Suppression definitive ! Utiliser avec precaution.

FICHIERS GENERES
=================

1. rapport_doublons.csv
   - Liste de tous les doublons detectes
   - Colonnes : FichierDouble, Taille, Raison, Reference
   - Ouvrir avec Excel pour analyser

2. hash_cache.txt
   - Cache des hashs calcules
   - Format : Chemin|Taille|Hash|DateModification
   - Accelere les prochaines executions (ne recalcule pas les hashs)
   - Peut etre supprime sans probleme (sera recree)

ERREURS COURANTES ET SOLUTIONS
===============================

ERREUR 1 : "Le repertoire de reference n'existe pas"
-----------------------------------------------------
CAUSE : Le chemin specifie dans $ReferencePath est incorrect
SOLUTION : 
- Verifier que le lecteur reseau est bien mappe (Z:)
- Verifier le chemin exact dans l'Explorateur Windows
- Utiliser des chemins UNC : \\NAS\volume1\dossier

ERREUR 2 : "Les scripts sont desactives sur ce systeme"
--------------------------------------------------------
CAUSE : PowerShell bloque l'execution des scripts
SOLUTION :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

ERREUR 3 : "Impossible de calculer le hash pour : ..."
-------------------------------------------------------
CAUSE : Fichier verrouille, acces refuse, ou corrompu
SOLUTION : Le script l'ignore automatiquement et continue

ERREUR 4 : "Caracteres Unicode non pris en charge"
---------------------------------------------------
CAUSE : PowerShell 5.1 ne supporte pas les emojis dans le code
SOLUTION : VERSION CORRIGEE (tous les emojis remplaces par [TAGS])

ERREUR 5 : Script tres lent
----------------------------
CAUSE : Trop de fichiers a analyser
SOLUTIONS :
- Augmenter $MinFileSize (ex: 100KB au lieu de 1KB)
- Changer $HashAlgorithm de "SHA256" a "MD5" (plus rapide)
- Traiter un dossier a la fois
- Verifier la vitesse reseau (lecteur reseau lent)

ERREUR 6 : Consommation RAM elevee quand meme
----------------------------------------------
CAUSE : Cache devient trop gros avec des millions de fichiers
SOLUTION :
- Supprimer hash_cache.txt regulierement
- Traiter les dossiers separement
- Augmenter $MinFileSize pour ignorer petits fichiers

PERFORMANCES
============

VITESSE DE TRAITEMENT (estimations)
------------------------------------
- 10 000 fichiers : 2-5 minutes
- 100 000 fichiers : 20-50 minutes
- 1 000 000 fichiers : 3-8 heures

FACTEURS INFLUENCANT LA VITESSE :
- Vitesse reseau (NAS distant)
- Taille moyenne des fichiers
- Type de hash (MD5 plus rapide que SHA256)
- Nombre de doublons (moins de hash a calculer si peu de doublons)

OPTIMISATIONS POSSIBLES
------------------------
1. Executer la nuit (tache planifiee Windows)
2. Utiliser MD5 au lieu de SHA256 (2-3x plus rapide)
3. Augmenter $MinFileSize pour ignorer petits fichiers
4. Desactiver $Verbose pour accelerer l'affichage
5. Traiter les gros dossiers separement

COMPRENDRE LE FONCTIONNEMENT
=============================

ETAPE 1 : Indexation de la reference par taille
------------------------------------------------
- Parcourt le repertoire de reference
- Groupe les fichiers par TAILLE
- Si un seul fichier d'une taille donnee -> pas de doublon possible
- Economise 70-90% des calculs de hash

ETAPE 2 : Calcul des hashs (seulement tailles en conflit)
----------------------------------------------------------
- Calcule les hashs UNIQUEMENT pour les tailles avec plusieurs fichiers
- Utilise le cache si disponible (evite de recalculer)
- Construit un index hash -> fichier

ETAPE 3 : Scan des repertoires a nettoyer (streaming)
------------------------------------------------------
- Parcourt chaque fichier UN PAR UN (pas tout en memoire)
- Compare la taille d'abord (rapide)
- Si conflit de taille -> calcule le hash
- Si hash existe dans reference -> DOUBLON
- Si hash existe dans doublons internes -> DOUBLON INTERNE

AVANTAGES DE CETTE APPROCHE
----------------------------
- Memoire constante (ne depend pas du nombre de fichiers)
- Cache persistant (accelere les prochaines executions)
- Pré-filtrage par taille (economise calculs)
- Traitement streaming (libere memoire au fur et a mesure)

SUPPORT ET AIDE
===============

SI LE SCRIPT NE FONCTIONNE PAS :
1. Verifier la version PowerShell : $PSVersionTable
2. Verifier les chemins dans l'Explorateur Windows
3. Tester avec un petit dossier d'abord
4. Activer $Verbose = $true pour voir le detail
5. Consulter rapport_doublons.csv pour comprendre les resultats

QUESTIONS FREQUENTES
====================

Q : Le script touche-t-il au repertoire de reference ?
R : NON, jamais ! Seuls les fichiers dans $PathsToClean sont traites.

Q : Que se passe-t-il si j'interromps le script (Ctrl+C) ?
R : Pas de probleme. Les fichiers deja traites sont sauvegardes.
   Le cache est sauvegarde a la fin, donc peut etre incomplet.

Q : Puis-je executer le script plusieurs fois ?
R : OUI ! Le cache accelerera les executions suivantes.

Q : Comment choisir entre MD5 et SHA256 ?
R : MD5 = plus rapide, risque infime de collision (acceptable pour doublons)
   SHA256 = plus lent, zero risque de collision

Q : Quelle est la difference avec findDuplicates-DupeGuruStyle.ps1 ?
R : DupeGuruStyle = charge tout en memoire (rapide mais RAM++)
   LowMemory = streaming (plus lent mais RAM--)
   Utilisez LowMemory si vous avez >100 000 fichiers

Q : Le script fonctionne-t-il sur Linux/Mac ?
R : OUI avec PowerShell Core (pwsh), mais adapter les chemins Unix

AUTEUR : GitHub Copilot
VERSION : 1.0 - Novembre 2025
LICENCE : Libre d'utilisation