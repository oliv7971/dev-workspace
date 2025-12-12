Option Explicit

' ===========================
' VARIABLE GLOBALE DEBUG
' ===========================
Public DebugMode As Boolean ' True = avec debug, False = silencieux

' ===========================
' FONCTION HELPER POUR DEBUG
' ===========================
Private Sub DebugLog(msg As String)
    If DebugMode Then Debug.Print msg
End Sub

' ===========================
' MODULE CALCULS OPTIMISÉ
' ===========================

' Remplit Résultats observations depuis DATABASE - OPTIMISÉ
Sub RemplirResultatsObservations()
    DebugMode = True ' Activer debug pour macro individuelle
    
    Dim wsObs As Worksheet, wsDB As Worksheet
    Dim lastRowObs As Long, lastColObs As Long, lastRowDB As Long
    Dim iRow As Long, iCol As Long, r As Long
    Dim dateObs As Variant, cible As String, champ As Long
    Dim dateDB As Variant, cibleDB As String
    Dim dictDB As Object ' Dictionary pour indexer DATABASE
    Dim key As String, colDB As Long
    
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    Set wsDB = ThisWorkbook.Sheets("DATABASE")
    Set dictDB = CreateObject("Scripting.Dictionary")
    
    lastRowObs = wsObs.Cells(wsObs.Rows.Count, "A").End(xlUp).Row
    lastColObs = wsObs.Cells(4, wsObs.Columns.Count).End(xlToLeft).Column
    lastRowDB = wsDB.Cells(wsDB.Rows.Count, 48).End(xlUp).Row ' Colonne AV (48)
    
    ' Indexer DATABASE par (date + cible) → ligne, à partir de la ligne 14
    DebugLog "=== DEBUT INDEXATION DATABASE ==="
    DebugLog "Dernière ligne de données: " & lastRowDB
    
    For r = 14 To lastRowDB ' Données commencent ligne 14
        dateDB = wsDB.Cells(r, 48).Value ' AV = colonne 48
        cibleDB = Trim(wsDB.Cells(r, 49).Value) ' AW = colonne 49
        
        ' Debug pour les 5 premières lignes de données
        If r <= 18 Then
            DebugLog "Ligne " & r & ": dateDB=[" & dateDB & "] IsNumeric=" & IsNumeric(dateDB) & " | cibleDB=[" & cibleDB & "]"
        End If
        
        ' La date est stockée comme NOMBRE dans Excel (avec heure)
        If dateDB <> "" And cibleDB <> "" And IsNumeric(dateDB) Then
            key = CDbl(dateDB) & "|" & UCase(cibleDB) ' Clé = date+heure + cible
            dictDB(key) = r ' Stocker le numéro de ligne
            If r <= 18 Then DebugLog "  -> INDEXE: " & key
        End If
    Next r
    
    DebugLog "=== Total indexé: " & dictDB.Count & " ==="
    
    ' Remplir les observations à partir de la ligne 10
    Dim nbTrouves As Long, nbNonTrouves As Long
    nbTrouves = 0: nbNonTrouves = 0
    
    For iRow = 10 To lastRowObs
        dateObs = wsObs.Cells(iRow, 1).Value ' Colonne A
        ' Forcer conversion en nombre
        If dateObs = "" Or Not IsNumeric(CDbl(dateObs)) Then GoTo NextRow
        
        For iCol = 4 To lastColObs ' Mesures commencent colonne D (4)
            cible = Trim(wsObs.Cells(4, iCol).Value) ' Ligne 4 = cible
            
            If cible <> "" And IsNumeric(wsObs.Cells(5, iCol).Value) Then
                champ = CLng(wsObs.Cells(5, iCol).Value) ' Ligne 5 = code champ
                key = CDbl(dateObs) & "|" & UCase(cible)
                
                If dictDB.Exists(key) Then
                    ' Calculer colonne DATABASE : AV (48) + décalage champ
                    ' Champ 3=X(AX=50), 4=Y(AY=51), 5=Z(AZ=52), 6=PM(BA=53), 7=H(BB=54), 8=V(BC=55)
                    colDB = 48 + champ - 1 ' AV=48, donc champ 3 → col 50 (AX)
                    
                    wsObs.Cells(iRow, iCol).Value = wsDB.Cells(dictDB(key), colDB).Value
                    nbTrouves = nbTrouves + 1
                Else
                    nbNonTrouves = nbNonTrouves + 1
                    If nbNonTrouves <= 5 Then DebugLog "NON TROUVÉ: " & key
                End If
            End If
        Next iCol
NextRow:
    Next iRow
    
    DebugLog "=== RESULTAT: " & nbTrouves & " trouvés, " & nbNonTrouves & " non trouvés ==="
    
    MsgBox "Mise à jour terminée ! (" & dictDB.Count & " entrées indexées, " & nbTrouves & " valeurs remplies)"
End Sub

' ===========================
' CALCUL DES DISTANCES 3D
' ===========================
Sub CalculerDistances3D_MultiBlocs()
    DebugMode = True ' Activer debug pour macro individuelle
    
    Dim wsObs As Worksheet
    Dim lastRowObs As Long
    
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    lastRowObs = wsObs.Cells(wsObs.Rows.Count, "A").End(xlUp).Row
    
    DebugLog ""
    DebugLog "╔════════════════════════════════════════════╗"
    DebugLog "║  CALCUL DISTANCES 3D                      ║"
    DebugLog "╚════════════════════════════════════════════╝"
    DebugLog "Dernière ligne: " & lastRowObs
    DebugLog ""
    
    ' Bloc 1 : FU → HE
    DebugLog "▶ BLOC 1 : FU → HE"
    Call CalculerDistances(wsObs, "FU", "HE", lastRowObs)
    
    DebugLog ""
    ' Bloc 2 : HG → HS
    DebugLog "▶ BLOC 2 : HG → HS"
    Call CalculerDistances(wsObs, "HG", "HS", lastRowObs)
    
    DebugLog ""
    DebugLog "✓ Calcul terminé"
    
    MsgBox "Distances calculées !"
End Sub

Private Sub CalculerDistances(wsObs As Worksheet, colStartObs As String, colEndObs As String, lastRowObs As Long)
    Dim colStart As Long, colEnd As Long, col As Long
    Dim cible1 As String, cible2 As String
    Dim colX1 As Long, colY1 As Long, colZ1 As Long
    Dim colX2 As Long, colY2 As Long, colZ2 As Long
    Dim i As Long, X1 As Double, Y1 As Double, Z1 As Double
    Dim X2 As Double, Y2 As Double, Z2 As Double, dist3D As Double
    Dim dictCoord As Object, c As Long, cible As String
    Dim comp9 As String, comp5 As String
    Dim nbCalcul As Long
    
    nbCalcul = 0
    
    ' Créer un cache des coordonnées pour éviter de parcourir D:BK à chaque fois
    Set dictCoord = CreateObject("Scripting.Dictionary")
    
    DebugLog "  → Construction index coordonnées (D:BK)..."
    For c = wsObs.Range("D1").Column To wsObs.Range("BK1").Column
        cible = UCase(Trim(wsObs.Cells(4, c).Value))
        If cible <> "" Then
            comp9 = UCase(Trim(wsObs.Cells(9, c).Value))
            comp5 = Trim(wsObs.Cells(5, c).Value)
            
            If comp9 = "X" Or comp5 = "3" Then 
                dictCoord(cible & "_X") = c
                If dictCoord.Count <= 10 Then DebugLog "    Index: " & cible & "_X → col " & c
            End If
            If comp9 = "Y" Or comp5 = "4" Then dictCoord(cible & "_Y") = c
            If comp9 = "Z" Or comp5 = "5" Then dictCoord(cible & "_Z") = c
        End If
    Next c
    
    DebugLog "  → Total coordonnées indexées: " & dictCoord.Count
    
    colStart = wsObs.Range(colStartObs & "1").Column
    colEnd = wsObs.Range(colEndObs & "1").Column
    
    DebugLog "  → Parcours colonnes " & colStartObs & " (" & colStart & ") à " & colEndObs & " (" & colEnd & ")"
    
    For col = colStart To colEnd
        ' NOUVEAU : Lire cible1 (ligne 4) et cible2 (ligne 5)
        cible1 = UCase(Trim(wsObs.Cells(4, col).Value))
        cible2 = UCase(Trim(wsObs.Cells(5, col).Value))
        
        ' Debug pour les 3 premières colonnes du bloc
        If col <= colStart + 2 Then
            DebugLog "    Col " & col & " ligne 4: [" & cible1 & "] ligne 5: [" & cible2 & "]"
        End If
        
        ' Ignorer si l'une des cibles est vide
        If cible1 = "" Or cible2 = "" Then 
            If col <= colStart + 2 Then DebugLog "      → Vide, ignoré"
            GoTo NextCol
        End If
        
        If col <= colStart + 2 Then
            DebugLog "      → Paire: " & cible1 & " - " & cible2
        End If
        
        ' Récupérer les colonnes depuis le cache
        colX1 = 0: colY1 = 0: colZ1 = 0
        colX2 = 0: colY2 = 0: colZ2 = 0
        
        If dictCoord.Exists(cible1 & "_X") Then colX1 = dictCoord(cible1 & "_X")
        If dictCoord.Exists(cible1 & "_Y") Then colY1 = dictCoord(cible1 & "_Y")
        If dictCoord.Exists(cible1 & "_Z") Then colZ1 = dictCoord(cible1 & "_Z")
        If dictCoord.Exists(cible2 & "_X") Then colX2 = dictCoord(cible2 & "_X")
        If dictCoord.Exists(cible2 & "_Y") Then colY2 = dictCoord(cible2 & "_Y")
        If dictCoord.Exists(cible2 & "_Z") Then colZ2 = dictCoord(cible2 & "_Z")
        
        If col <= colStart + 2 Then
            DebugLog "      → " & cible1 & " XYZ: " & colX1 & "," & colY1 & "," & colZ1
            DebugLog "      → " & cible2 & " XYZ: " & colX2 & "," & colY2 & "," & colZ2
        End If
        
        If colX1 = 0 Or colY1 = 0 Or colZ1 = 0 Or colX2 = 0 Or colY2 = 0 Or colZ2 = 0 Then
            DebugLog "      → ❌ Coordonnées manquantes pour " & cible1 & " ou " & cible2
            GoTo NextCol
        End If
        
        For i = 10 To lastRowObs
            ' Vérifier que TOUTES les coordonnées existent ET sont numériques ET non vides
            If Not IsEmpty(wsObs.Cells(i, colX1).Value) And Not IsEmpty(wsObs.Cells(i, colY1).Value) And Not IsEmpty(wsObs.Cells(i, colZ1).Value) _
               And Not IsEmpty(wsObs.Cells(i, colX2).Value) And Not IsEmpty(wsObs.Cells(i, colY2).Value) And Not IsEmpty(wsObs.Cells(i, colZ2).Value) Then
                
                If IsNumeric(wsObs.Cells(i, colX1).Value) And IsNumeric(wsObs.Cells(i, colY1).Value) And IsNumeric(wsObs.Cells(i, colZ1).Value) _
                   And IsNumeric(wsObs.Cells(i, colX2).Value) And IsNumeric(wsObs.Cells(i, colY2).Value) And IsNumeric(wsObs.Cells(i, colZ2).Value) Then
                    
                    X1 = wsObs.Cells(i, colX1).Value
                    Y1 = wsObs.Cells(i, colY1).Value
                    Z1 = wsObs.Cells(i, colZ1).Value
                    
                    X2 = wsObs.Cells(i, colX2).Value
                    Y2 = wsObs.Cells(i, colY2).Value
                    Z2 = wsObs.Cells(i, colZ2).Value
                    
                    ' VALIDATION : Ignorer si une coordonnée est nulle (cible abandonnée ou pas de mesure)
                    If (X1 = 0 And Y1 = 0 And Z1 = 0) Or (X2 = 0 And Y2 = 0 And Z2 = 0) Then
                        ' Ne rien écrire - cible abandonnée ou pas de mesure
                    Else
                        dist3D = Sqr((X2 - X1) ^ 2 + (Y2 - Y1) ^ 2 + (Z2 - Z1) ^ 2)
                        wsObs.Cells(i, col).Value = dist3D
                        nbCalcul = nbCalcul + 1
                    End If
                End If
            End If
        Next i
        
NextCol:
    Next col
    
    DebugLog "  → ✓ " & nbCalcul & " distances calculées"
End Sub

' ===========================
' CALCUL DES ÉCARTS CORDES - CORRIGÉ
' ===========================
Sub CalculerEcartsCordes_MultiBlocs()
    DebugMode = True ' Activer debug pour macro individuelle
    
    Dim wsCordes As Worksheet, wsObs As Worksheet
    Dim lastRowObs As Long
    
    On Error GoTo ErrHandler
    
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    
    lastRowObs = wsObs.Cells(wsObs.Rows.Count, "A").End(xlUp).Row
    
    DebugLog ""
    DebugLog "╔════════════════════════════════════════════╗"
    DebugLog "║  DÉBUT CALCUL ÉCARTS CORDES               ║"
    DebugLog "╚════════════════════════════════════════════╝"
    DebugLog "Dernière ligne Obs: " & lastRowObs
    DebugLog ""
    
    ' Bloc 1 : FU → HE → C → T et X → AO
    DebugLog "▶ BLOC 1A : Cordes C→T vs Obs FU→HE"
    Call CalculerEcarts(wsCordes, wsObs, "C", "T", "FU", "HE", lastRowObs)
    DebugLog "  ✓ Bloc 1A terminé"
    
    DebugLog ""
    DebugLog "▶ BLOC 1B : Cordes X→AO vs Obs FU→HE"
    Call CalculerEcarts(wsCordes, wsObs, "X", "AO", "FU", "HE", lastRowObs)
    DebugLog "  ✓ Bloc 1B terminé"
    
    ' Bloc 2 : HG → HS → AS → BE
    DebugLog ""
    DebugLog "▶ BLOC 2 : Cordes AS→BE vs Obs HG→HS"
    Call CalculerEcarts(wsCordes, wsObs, "AS", "BE", "HG", "HS", lastRowObs)
    DebugLog "  ✓ Bloc 2 terminé"
    
    DebugLog ""
    DebugLog "╔════════════════════════════════════════════╗"
    DebugLog "║  FIN CALCUL ÉCARTS CORDES                 ║"
    DebugLog "╚════════════════════════════════════════════╝"
    
    MsgBox "Écarts calculés !"
    Exit Sub
    
ErrHandler:
    DebugLog "❌ ERREUR dans CalculerEcartsCordes_MultiBlocs: " & Err.Description
    MsgBox "Erreur: " & Err.Description, vbCritical
End Sub

' FONCTION CORRIGÉE : Matcher par paire "cible1-cible2" dans ligne 4 de Résultats observations
Private Sub CalculerEcarts(wsCordes As Worksheet, wsObs As Worksheet, colStartCordes As String, colEndCordes As String, colStartObs As String, colEndObs As String, lastRowObs As Long)
    Dim colStartC As Long, colEndC As Long, colStartO As Long, colEndO As Long
    Dim col As Long, cible1C As String, cible2C As String, colObs As Long, i As Long
    Dim valRef As Double
    
    colStartC = wsCordes.Range(colStartCordes & "1").Column
    colEndC = wsCordes.Range(colEndCordes & "1").Column
    colStartO = wsObs.Range(colStartObs & "1").Column
    colEndO = wsObs.Range(colEndObs & "1").Column
    
    DebugLog "=== Calcul écarts : colonnes " & colStartCordes & " à " & colEndCordes & " ==="
    
    For col = colStartC To colEndC
        ' Lire cible1 (ligne 4) et cible2 (ligne 5) dans Cordes
        cible1C = UCase(Trim(wsCordes.Cells(4, col).Value))
        cible2C = UCase(Trim(wsCordes.Cells(5, col).Value))
        
        DebugLog "Col " & col & " (" & Split(Cells(1, col).Address, "$")(1) & "): cible1=[" & cible1C & "] cible2=[" & cible2C & "]"
        
        If cible1C = "" Or cible2C = "" Then 
            DebugLog "  -> Vide, ignoré"
            GoTo NextCol
        End If
        
        DebugLog "  -> Recherche paire: " & cible1C & " + " & cible2C & " dans Obs colonnes " & colStartObs & ":" & colEndObs
        
        ' Chercher la colonne dans Résultats observations en comparant ligne 4 ET ligne 5
        colObs = 0
        Dim c As Long, cibleObs1 As String, cibleObs2 As String
        For c = colStartO To colEndO
            cibleObs1 = UCase(Trim(wsObs.Cells(4, c).Value))
            cibleObs2 = UCase(Trim(wsObs.Cells(5, c).Value))
            
            ' Debug les 5 premières colonnes pour voir le format
            If col = colStartC And c <= colStartO + 5 Then
                DebugLog "    Obs col " & c & ": L4=[" & cibleObs1 & "] L5=[" & cibleObs2 & "]"
            End If
            
            ' Matcher en comparant ligne 4 ET ligne 5
            If cibleObs1 = cible1C And cibleObs2 = cible2C Then
                colObs = c
                DebugLog "  -> TROUVÉ dans Obs col " & c & " !"
                Exit For
            End If
        Next c
        
        If colObs = 0 Then
            DebugLog "  -> ❌ NON TROUVÉ : " & cible1C & " + " & cible2C
            GoTo NextCol
        End If
        
        ' Récupérer la valeur de référence (ligne 10)
        If IsEmpty(wsObs.Cells(10, colObs).Value) Or Not IsNumeric(wsObs.Cells(10, colObs).Value) Then
            DebugLog "Valeur de référence vide ou non numérique pour : " & cible1C & "-" & cible2C
            GoTo NextCol
        End If
        
        valRef = wsObs.Cells(10, colObs).Value
        
        ' VALIDATION : Si la référence est nulle, ne pas calculer
        If valRef = 0 Then
            DebugLog "Valeur de référence nulle pour : " & cible1C & "-" & cible2C
            GoTo NextCol
        End If
        
        ' Calculer les écarts pour chaque ligne (en mm)
        For i = 10 To lastRowObs
            ' Ne calculer que si la valeur existe, est numérique et non nulle
            If Not IsEmpty(wsObs.Cells(i, colObs).Value) And IsNumeric(wsObs.Cells(i, colObs).Value) Then
                If wsObs.Cells(i, colObs).Value <> 0 Then
                    wsCordes.Cells(i, col).Value = (wsObs.Cells(i, colObs).Value - valRef) * 1000
                End If
            End If
        Next i
        
NextCol:
    Next col
End Sub

' ===========================
' MACRO COMBINÉE
' ===========================
Sub CalculerDistancesEtEcarts()
    Call CalculerDistances3D_MultiBlocs
    Call CalculerEcartsCordes_MultiBlocs
    MsgBox "Distances et écarts calculés !"
End Sub

' ===========================
' WORKFLOW COMPLET - Tout en un
' ===========================
Sub WorkflowComplet()
    Dim reponse As VbMsgBoxResult
    
    ' Confirmation avant de tout effacer
    reponse = MsgBox("Ce workflow va :" & vbCrLf & vbCrLf & _
                     "1. EFFACER toutes les données calculées" & vbCrLf & _
                     "2. Extraire les dates de DATABASE" & vbCrLf & _
                     "3. Remplir les mesures" & vbCrLf & _
                     "4. Calculer les distances" & vbCrLf & _
                     "5. Calculer les écarts" & vbCrLf & _
                     "6. Calculer les déplacements" & vbCrLf & _
                     "7. Calculer les normes" & vbCrLf & _
                     "8. Mettre à jour les axes des graphiques" & vbCrLf & vbCrLf & _
                     "Continuer ?", vbYesNo + vbQuestion, "Workflow complet")
    
    If reponse = vbNo Then Exit Sub
    
    ' DÉSACTIVER LE DEBUG POUR LE WORKFLOW COMPLET
    DebugMode = False
    
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    
    ' 1. Reset
    Call ResetZonesCalcul
    
    ' 2. Initialiser dates
    Call InitialiserDatesObservations
    
    ' 3. Remplir mesures
    Call RemplirResultatsObservations
    
    ' 4. Calculer distances
    Call CalculerDistances3D_MultiBlocs
    
    ' 5. Calculer écarts
    Call CalculerEcartsCordes_MultiBlocs
    
    ' 6. Calculer déplacements
    Call CalculerDeplacementsParRapportPremiereMesure
    
    ' 7. Calculer normes
    Call CalculerNormeDansDeplacementsMM
    
    ' 8. Corriger axes des graphiques (si feuille "graphiques" existe)
    ' DÉSACTIVÉ : La macro écrase toutes les plages de dates des graphiques
    ' On Error Resume Next
    ' Call CorrigerAxeXGraphiques
    ' On Error GoTo 0
    
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    
    MsgBox "✓ Workflow complet terminé !" & vbCrLf & vbCrLf & _
           "Toutes les données ont été recalculées.", vbInformation, "Succès"
End Sub

Sub CalculerDeplacementsParRapportPremiereMesure()
    DebugMode = True ' Activer debug pour macro individuelle
    
    Dim wsObs As Worksheet, wsDep As Worksheet
    Dim lastRowObs As Long, lastRowDep As Long, lastColDep As Long
    Dim iRowDep As Long, iColDep As Long, iRowObs As Long
    Dim cibleDep As String, champDep As String
    Dim colObs As Long, refVal As Double
    Dim dateDep As Variant, dateObs As Variant
    Dim dictDates As Object, c As Long
    Dim key As Double  ' CHANGÉ DE STRING À DOUBLE !
    Dim nbCalcul As Long, nbNonTrouves As Long
    
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    Set dictDates = CreateObject("Scripting.Dictionary")
    
    lastRowObs = wsObs.Cells(wsObs.Rows.Count, "A").End(xlUp).Row
    lastRowDep = wsDep.Cells(wsDep.Rows.Count, "A").End(xlUp).Row
    lastColDep = wsDep.Cells(2, wsDep.Columns.Count).End(xlToLeft).Column
    
    nbCalcul = 0
    nbNonTrouves = 0
    
    DebugLog ""
    DebugLog "╔════════════════════════════════════════════╗"
    DebugLog "║  CALCUL DÉPLACEMENTS                      ║"
    DebugLog "╚════════════════════════════════════════════╝"
    DebugLog "Dernière ligne Obs: " & lastRowObs
    DebugLog "Dernière ligne Dep: " & lastRowDep
    DebugLog "Dernière col Dep: " & lastColDep
    DebugLog ""
    
    ' Indexer les dates de Résultats observations
    DebugLog "=== Indexation dates Obs ==="
    For iRowObs = 10 To lastRowObs
        dateObs = wsObs.Cells(iRowObs, 1).Value
        If iRowObs <= 12 Then
            DebugLog "  Ligne " & iRowObs & ": Value=[" & dateObs & "] TypeName=" & TypeName(dateObs) & " IsNumeric=" & IsNumeric(dateObs) & " Value2=[" & wsObs.Cells(iRowObs, 1).Value2 & "]"
        End If
        If dateObs <> "" And IsNumeric(CDbl(dateObs)) Then
            dictDates(CDbl(dateObs)) = iRowObs
            If iRowObs <= 12 Then DebugLog "    -> INDEXÉ: " & CDbl(dateObs)
        End If
    Next iRowObs
    DebugLog "Total dates indexées: " & dictDates.Count
    DebugLog ""
    
    ' Boucle sur les colonnes de Déplacements
    For iColDep = 2 To lastColDep
        cibleDep = UCase(Trim(wsDep.Cells(2, iColDep).Value)) ' cible ligne 2
        champDep = UCase(Trim(wsDep.Cells(3, iColDep).Value)) ' champ ligne 3
        
        ' Debug pour les 5 premières colonnes
        If iColDep <= 6 Then
            DebugLog "Col " & iColDep & " Dep: cible=[" & cibleDep & "] champ=[" & champDep & "]"
        End If
        
        If cibleDep <> "" And champDep <> "" Then
            ' Trouver la colonne correspondante dans Résultats observations
            colObs = 0
            For c = 2 To wsObs.Cells(4, wsObs.Columns.Count).End(xlToLeft).Column
                ' Debug pour les 3 premières colonnes de la première colonne Dep testée
                If iColDep = 2 And c <= 4 Then
                    DebugLog "    Test col " & c & " Obs: L4=[" & wsObs.Cells(4, c).Value & "] L5=[" & wsObs.Cells(5, c).Value & "] L9=[" & wsObs.Cells(9, c).Value & "]"
                    DebugLog "      vs cibleDep=[" & cibleDep & "] champDep=[" & champDep & "]"
                End If
                
                ' Forcer TOUT en texte pour la comparaison
                If UCase(Trim(CStr(wsObs.Cells(4, c).Value))) = cibleDep And _
                   (UCase(Trim(CStr(wsObs.Cells(5, c).Value))) = champDep Or _
                    UCase(Trim(CStr(wsObs.Cells(9, c).Value))) = champDep) Then
                    colObs = c
                    If iColDep <= 6 Then DebugLog "  -> TROUVÉ dans Obs col " & c
                    Exit For
                End If
            Next c
            
            If colObs > 0 Then
                ' VALIDATION : Vérifier que la référence existe et n'est pas vide
                If IsEmpty(wsObs.Cells(10, colObs).Value) Then
                    If iColDep <= 6 Then DebugLog "  -> Référence vide"
                    GoTo NextColDep
                End If
                
                If Not IsNumeric(wsObs.Cells(10, colObs).Value) Then
                    If iColDep <= 6 Then DebugLog "  -> Référence non numérique"
                    GoTo NextColDep
                End If
                
                refVal = wsObs.Cells(10, colObs).Value ' valeur de référence
                
                ' VALIDATION : Ignorer si la valeur de référence est nulle (cible abandonnée)
                If refVal = 0 Then
                    If iColDep <= 6 Then DebugLog "  -> Référence = 0 (cible abandonnée)"
                    GoTo NextColDep
                End If
                
                If iColDep <= 6 Then DebugLog "  -> Référence OK: " & refVal
                
                ' Parcourir les lignes de Déplacements
                Dim nbLignesTestees As Long
                nbLignesTestees = 0
                
                For iRowDep = 10 To lastRowDep
                    dateDep = wsDep.Cells(iRowDep, 1).Value
                    
                    If iColDep = 3 And iRowDep <= 12 Then
                        DebugLog "    Ligne " & iRowDep & " Dep: Value=[" & dateDep & "] TypeName=" & TypeName(dateDep) & " IsNumeric=" & IsNumeric(dateDep) & " Value2=[" & wsDep.Cells(iRowDep, 1).Value2 & "]"
                    End If
                    
                    If dateDep = "" Or Not IsNumeric(CDbl(dateDep)) Then GoTo NextRowDep
                    
                    ' Chercher la date dans le Dictionary
                    key = CDbl(dateDep)
                    
                    ' DEBUG DÉTAILLÉ pour colonne 3, lignes 10-12
                    If iColDep = 3 And iRowDep <= 12 Then
                        DebugLog "      -> Clé recherchée: " & key & " (type=" & TypeName(key) & ")"
                        DebugLog "      -> Dictionary.Count: " & dictDates.Count
                        DebugLog "      -> Existe dans Dict? " & dictDates.Exists(key)
                        
                        ' Afficher les 3 premières clés du Dictionary pour comparaison
                        If iRowDep = 10 Then
                            Dim debugKey As Variant, debugCount As Long
                            debugCount = 0
                            DebugLog "      -> Premières clés du Dictionary:"
                            For Each debugKey In dictDates.Keys
                                DebugLog "         [" & debugKey & "] (type=" & TypeName(debugKey) & ")"
                                debugCount = debugCount + 1
                                If debugCount >= 3 Then Exit For
                            Next debugKey
                        End If
                    End If
                    
                    If dictDates.Exists(key) Then
                        iRowObs = dictDates(key)
                        
                        If iRowObs = 10 Then
                            wsDep.Cells(iRowDep, iColDep).Value = 0 ' première mesure = 0 mm
                            nbCalcul = nbCalcul + 1
                        ElseIf Not IsEmpty(wsObs.Cells(iRowObs, colObs).Value) And IsNumeric(wsObs.Cells(iRowObs, colObs).Value) Then
                            Dim valActuelle As Double
                            valActuelle = wsObs.Cells(iRowObs, colObs).Value
                            
                            ' VALIDATION : Ignorer si la valeur actuelle est nulle (cible abandonnée ou pas de mesure)
                            If valActuelle <> 0 Then
                                wsDep.Cells(iRowDep, iColDep).Value = (valActuelle - refVal) * 1000 ' en mm
                                nbCalcul = nbCalcul + 1
                            End If
                        End If
                        nbLignesTestees = nbLignesTestees + 1
                    End If
NextRowDep:
                Next iRowDep
                
                If iColDep = 3 Then DebugLog "    -> Lignes testées avec succès: " & nbLignesTestees
            Else
                nbNonTrouves = nbNonTrouves + 1
                If iColDep <= 6 Then DebugLog "  -> ❌ NON TROUVÉ dans Obs"
            End If
        End If
NextColDep:
    Next iColDep
    
    DebugLog ""
    DebugLog "✓ Calcul terminé: " & nbCalcul & " déplacements calculés"
    DebugLog "✗ Colonnes non trouvées: " & nbNonTrouves
    
    MsgBox "Déplacements calculés ! (" & nbCalcul & " valeurs, " & nbNonTrouves & " colonnes non trouvées)"
End Sub

Sub CalculerNormeDansDeplacementsMM()
    Dim wsDep As Worksheet
    Dim lastRowDep As Long, lastColDep As Long
    Dim iRow As Long, iCol As Long
    Dim colPM As Long, colH As Long, colZ As Long
    Dim valPM As Double, valH As Double, valZ As Double
    Dim normeCount As Long
    
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    
    lastRowDep = wsDep.Cells(wsDep.Rows.Count, "A").End(xlUp).Row
    lastColDep = wsDep.Cells(2, wsDep.Columns.Count).End(xlToLeft).Column
    normeCount = 0
    
    For iCol = 2 To lastColDep
        If Trim(wsDep.Cells(3, iCol).Value) = "9" Then
            ' Les trois colonnes précédentes doivent être 6, 7, 8
            colPM = iCol - 3
            colH = iCol - 2
            colZ = iCol - 1
            
            ' Vérifications de sécurité
            If colPM < 2 Or colH < 2 Or colZ < 2 Then
                DebugLog "Erreur : colonne 9 à la position " & iCol & " n'a pas assez de colonnes précédentes"
                GoTo NextCol
            End If
            
            If Trim(wsDep.Cells(3, colPM).Value) = "6" And _
               Trim(wsDep.Cells(3, colH).Value) = "7" And _
               Trim(wsDep.Cells(3, colZ).Value) = "8" Then
               
               ' Calculer la norme pour chaque ligne
               For iRow = 10 To lastRowDep
                   If IsNumeric(wsDep.Cells(iRow, colPM).Value) And _
                      IsNumeric(wsDep.Cells(iRow, colH).Value) And _
                      IsNumeric(wsDep.Cells(iRow, colZ).Value) Then
                      
                      valPM = wsDep.Cells(iRow, colPM).Value
                      valH = wsDep.Cells(iRow, colH).Value
                      valZ = wsDep.Cells(iRow, colZ).Value
                      
                      wsDep.Cells(iRow, iCol).Value = Sqr(valPM ^ 2 + valH ^ 2 + valZ ^ 2)
                      normeCount = normeCount + 1
                   End If
               Next iRow
            Else
                DebugLog "Avertissement : colonne 9 à la position " & iCol & " n'a pas les champs 6, 7, 8 avant elle"
            End If
        End If
NextCol:
    Next iCol
    
    MsgBox "Normes calculées ! (" & normeCount & " valeurs)"
End Sub

' ===========================
' TEST DEBUG DATABASE
' ===========================
Sub TestDebugDatabase()
    Dim wsDB As Worksheet
    Dim r As Long, c As Long
    
    Set wsDB = ThisWorkbook.Sheets("DATABASE")
    
    DebugLog "=== ANALYSE TOUTES COLONNES lignes 1-20 ==="
    
    ' Afficher TOUTES les colonnes pour les 20 premières lignes
    For r = 1 To 20
        Dim ligne As String
        ligne = "L" & r & ":"
        For c = 1 To 60
            If wsDB.Cells(r, c).Value <> "" Then
                ligne = ligne & " C" & c & "=[" & Left(wsDB.Cells(r, c).Value, 20) & "]"
            End If
        Next c
        If Len(ligne) > 10 Then DebugLog ligne ' N'afficher que les lignes non vides
    Next r
    
    DebugLog ""
    DebugLog "=== RECHERCHE COLONNES DATE et CIBLE ==="
    
    ' Chercher la colonne qui contient des dates (nombres autour de 45000)
    For c = 1 To 60
        For r = 1 To 20
            If IsNumeric(wsDB.Cells(r, c).Value) Then
                If wsDB.Cells(r, c).Value > 40000 And wsDB.Cells(r, c).Value < 50000 Then
                    DebugLog "DATE potentielle: Ligne " & r & " Col " & c & " = " & wsDB.Cells(r, c).Value
                    Exit For
                End If
            End If
        Next r
    Next c
End Sub

' ===========================
' DIAGNOSTIC - Trouver les colonnes avec des paires
' ===========================
Sub DiagnosticTrouverPaires()
    Dim wsObs As Worksheet, wsCordes As Worksheet
    Dim c As Long, lastCol As Long
    Dim texte As String
    Dim nbPaires As Long, premierePaire As Long
    
    ' VÉRIFIER RÉSULTATS OBSERVATIONS
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    lastCol = wsObs.Cells(4, wsObs.Columns.Count).End(xlToLeft).Column
    
    DebugLog ""
    DebugLog "╔════════════════════════════════════════════╗"
    DebugLog "║  RECHERCHE PAIRES - RÉSULTATS OBS         ║"
    DebugLog "╚════════════════════════════════════════════╝"
    DebugLog "Dernière colonne: " & lastCol
    DebugLog ""
    
    nbPaires = 0
    premierePaire = 0
    
    For c = 1 To lastCol
        texte = Trim(wsObs.Cells(4, c).Value)
        
        If InStr(texte, "-") > 0 Then
            nbPaires = nbPaires + 1
            If premierePaire = 0 Then premierePaire = c
            If nbPaires <= 10 Then
                DebugLog "Col " & c & " (" & Split(wsObs.Cells(1, c).Address, "$")(1) & "): [" & texte & "]"
            End If
        End If
    Next c
    
    DebugLog "✓ Total paires dans Résultats obs: " & nbPaires
    
    ' VÉRIFIER CORDES
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    lastCol = wsCordes.Cells(4, wsCordes.Columns.Count).End(xlToLeft).Column
    
    DebugLog ""
    DebugLog "╔════════════════════════════════════════════╗"
    DebugLog "║  RECHERCHE PAIRES - CORDES                ║"
    DebugLog "╚════════════════════════════════════════════╝"
    DebugLog "Dernière colonne: " & lastCol
    DebugLog ""
    
    nbPaires = 0
    premierePaire = 0
    
    For c = 1 To lastCol
        texte = Trim(wsCordes.Cells(4, c).Value)
        
        If InStr(texte, "-") > 0 Or Trim(wsCordes.Cells(5, c).Value) <> "" Then
            nbPaires = nbPaires + 1
            If premierePaire = 0 Then premierePaire = c
            If nbPaires <= 10 Then
                DebugLog "Col " & c & " (" & Split(wsCordes.Cells(1, c).Address, "$")(1) & "):"
                DebugLog "  Ligne 4: [" & Trim(wsCordes.Cells(4, c).Value) & "]"
                DebugLog "  Ligne 5: [" & Trim(wsCordes.Cells(5, c).Value) & "]"
            End If
        End If
    Next c
    
    DebugLog ""
    DebugLog "═══════════════════════════════════════════"
    DebugLog "✓ Total paires/cordes trouvées: " & nbPaires
    If premierePaire > 0 Then
        DebugLog "✓ Première paire en colonne " & premierePaire & " (" & Split(wsCordes.Cells(1, premierePaire).Address, "$")(1) & ")"
    End If
    
    MsgBox "Analyse terminée ! Consultez la fenêtre Immediate (Ctrl+G)"
End Sub

' ===========================
' NETTOYAGE - Reset zones de calcul
' ===========================
Sub ResetZonesCalcul()
    Dim wsObs As Worksheet, wsDep As Worksheet, wsCordes As Worksheet
    Dim lastRow As Long
    
    Application.ScreenUpdating = False
    
    ' Reset Résultats observations - EFFACER AUSSI LIGNE 10
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    lastRow = wsObs.Cells(wsObs.Rows.Count, "A").End(xlUp).Row
    If lastRow >= 10 Then
        wsObs.Rows("10:" & lastRow).ClearContents
    End If
    
    ' Reset Déplacements - EFFACER AUSSI LIGNE 10
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    lastRow = wsDep.Cells(wsDep.Rows.Count, "A").End(xlUp).Row
    If lastRow >= 10 Then
        wsDep.Rows("10:" & lastRow).ClearContents
    End If
    
    ' Reset Cordes - EFFACER AUSSI LIGNE 10
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    lastRow = wsCordes.Cells(wsCordes.Rows.Count, "A").End(xlUp).Row
    If lastRow >= 10 Then
        wsCordes.Rows("10:" & lastRow).ClearContents
    End If
    
    Application.ScreenUpdating = True
    
    MsgBox "Zones de calcul réinitialisées !"
End Sub

' ===========================
' INITIALISATION - Extraire dates de DATABASE
' ===========================
Sub InitialiserDatesObservations()
    DebugMode = True ' Activer debug pour macro individuelle
    
    Dim wsDB As Worksheet, wsObs As Worksheet, wsDep As Worksheet, wsCordes As Worksheet
    Dim lastRowDB As Long, r As Long
    Dim dateDB As Variant, dateRef As Variant
    Dim dictDates As Object
    Dim dates() As Variant, i As Long, j As Long, temp As Variant
    Dim nbDates As Long
    Dim dateRefVal As Double
    
    Set wsDB = ThisWorkbook.Sheets("DATABASE")
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    Set dictDates = CreateObject("Scripting.Dictionary")
    
    ' Récupérer la date de référence (ligne 7, colonne A)
    dateRef = wsObs.Cells(7, 1).Value
    If Not IsDate(dateRef) And Not IsNumeric(dateRef) Then
        MsgBox "ERREUR : La cellule A7 doit contenir la date de référence !"
        Exit Sub
    End If
    
    ' Parcourir DATABASE et collecter les dates uniques
    lastRowDB = wsDB.Cells(wsDB.Rows.Count, 48).End(xlUp).Row
    
    For r = 14 To lastRowDB
        dateDB = wsDB.Cells(r, 48).Value ' Colonne AV (48)
        If dateDB <> "" And IsNumeric(dateDB) Then
            If Not dictDates.Exists(CDbl(dateDB)) Then
                dictDates.Add CDbl(dateDB), CDbl(dateDB)
            End If
        End If
    Next r
    
    ' Convertir le Dictionary en tableau
    nbDates = dictDates.Count
    If nbDates = 0 Then
        MsgBox "Aucune date trouvée dans DATABASE !"
        Exit Sub
    End If
    
    ReDim dates(1 To nbDates)
    i = 1
    Dim key As Variant
    For Each key In dictDates.Keys
        dates(i) = key
        i = i + 1
    Next key
    
    ' Tri par ordre chronologique (tri à bulles simple)
    For i = 1 To nbDates - 1
        For j = i + 1 To nbDates
            If dates(i) > dates(j) Then
                temp = dates(i)
                dates(i) = dates(j)
                dates(j) = temp
            End If
        Next j
    Next i
    
    ' Date de référence = première date (ligne 10)
    dateRefVal = dates(1)
    
    Application.ScreenUpdating = False
    
    ' DÉSACTIVER COMPLÈTEMENT LE FORMATAGE AUTOMATIQUE D'EXCEL
    Application.AutoCorrect.AutoFillFormulasInLists = False
    Application.EnableEvents = False
    
    ' === REMPLIR RÉSULTATS OBSERVATIONS PAR TABLEAU ===
    ' Préparer les tableaux de données
    Dim arrDatesObs() As Variant, arrJoursObs() As Variant
    ReDim arrDatesObs(1 To nbDates, 1 To 1)
    ReDim arrJoursObs(1 To nbDates, 1 To 1)
    
    For i = 1 To nbDates
        arrDatesObs(i, 1) = CDbl(dates(i))  ' Forcer en Double
        arrJoursObs(i, 1) = dates(i) - dateRefVal
    Next i
    
    ' Écrire en bloc (sans ClearFormats pour préserver la mise en forme)
    wsObs.Range("A10:A" & (9 + nbDates)).NumberFormat = "0.00000000"  ' Format numérique strict
    wsObs.Range("A10:A" & (9 + nbDates)).Value = arrDatesObs
    wsObs.Range("A10:A" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsObs.Range("B10:B" & (9 + nbDates)).Value = arrJoursObs
    
    ' === REMPLIR DÉPLACEMENTS PAR TABLEAU ===
    Dim arrDatesDep() As Variant, arrJoursDep() As Variant
    ReDim arrDatesDep(1 To nbDates, 1 To 1)
    ReDim arrJoursDep(1 To nbDates, 1 To 1)
    
    For i = 1 To nbDates
        arrDatesDep(i, 1) = CDbl(dates(i))  ' Forcer en Double
        arrJoursDep(i, 1) = dates(i) - dateRefVal
    Next i
    
    ' Bloc 1 : Colonnes A et B
    wsDep.Range("A10:A" & (9 + nbDates)).NumberFormat = "0.00000000"
    wsDep.Range("A10:A" & (9 + nbDates)).Value = arrDatesDep
    wsDep.Range("A10:A" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsDep.Range("B10:B" & (9 + nbDates)).Value = arrJoursDep
    
    ' Bloc 2 : Colonnes AD et AE
    wsDep.Range("AD10:AD" & (9 + nbDates)).NumberFormat = "0.00000000"
    wsDep.Range("AD10:AD" & (9 + nbDates)).Value = arrDatesDep
    wsDep.Range("AD10:AD" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsDep.Range("AE10:AE" & (9 + nbDates)).Value = arrJoursDep
    
    ' Bloc 3 : Colonnes BG et BH
    wsDep.Range("BG10:BG" & (9 + nbDates)).NumberFormat = "0.00000000"
    wsDep.Range("BG10:BG" & (9 + nbDates)).Value = arrDatesDep
    wsDep.Range("BG10:BG" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsDep.Range("BH10:BH" & (9 + nbDates)).Value = arrJoursDep
    
    ' === REMPLIR CORDES PAR TABLEAU ===
    Dim arrDatesCordes() As Variant, arrJoursCordes() As Variant
    ReDim arrDatesCordes(1 To nbDates, 1 To 1)
    ReDim arrJoursCordes(1 To nbDates, 1 To 1)
    
    For i = 1 To nbDates
        arrDatesCordes(i, 1) = CDbl(dates(i))  ' Forcer en Double
        arrJoursCordes(i, 1) = dates(i) - dateRefVal
    Next i
    
    ' Bloc 1 : Colonnes A et B
    wsCordes.Range("A10:A" & (9 + nbDates)).NumberFormat = "0.00000000"
    wsCordes.Range("A10:A" & (9 + nbDates)).Value = arrDatesCordes
    wsCordes.Range("A10:A" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsCordes.Range("B10:B" & (9 + nbDates)).Value = arrJoursCordes
    
    ' Bloc 2 : Colonnes V et W
    wsCordes.Range("V10:V" & (9 + nbDates)).NumberFormat = "0.00000000"
    wsCordes.Range("V10:V" & (9 + nbDates)).Value = arrDatesCordes
    wsCordes.Range("V10:V" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsCordes.Range("W10:W" & (9 + nbDates)).Value = arrJoursCordes
    
    ' Bloc 3 : Colonnes AQ et AR
    wsCordes.Range("AQ10:AQ" & (9 + nbDates)).NumberFormat = "0.00000000"
    wsCordes.Range("AQ10:AQ" & (9 + nbDates)).Value = arrDatesCordes
    wsCordes.Range("AQ10:AQ" & (9 + nbDates)).NumberFormat = "dd/mm/yyyy hh:mm:ss"
    wsCordes.Range("AR10:AR" & (9 + nbDates)).Value = arrJoursCordes
    
    ' RÉACTIVER LE FORMATAGE AUTOMATIQUE
    Application.AutoCorrect.AutoFillFormulasInLists = True
    Application.EnableEvents = True
    
    ' === FORMATER LES COLONNES JOURS EN NOMBRE (pas en date) ===
    ' Résultats observations - Colonne B
    wsObs.Range("B10:B" & (9 + nbDates)).NumberFormat = "0.00"
    
    ' Déplacements - Colonnes B, AE, BH
    wsDep.Range("B10:B" & (9 + nbDates)).NumberFormat = "0.00"
    wsDep.Range("AE10:AE" & (9 + nbDates)).NumberFormat = "0.00"
    wsDep.Range("BH10:BH" & (9 + nbDates)).NumberFormat = "0.00"
    
    ' Cordes - Colonnes B, W, AR
    wsCordes.Range("B10:B" & (9 + nbDates)).NumberFormat = "0.00"
    wsCordes.Range("W10:W" & (9 + nbDates)).NumberFormat = "0.00"
    wsCordes.Range("AR10:AR" & (9 + nbDates)).NumberFormat = "0.00"
    
    Application.ScreenUpdating = True
    
    MsgBox nbDates & " dates initialisées dans les 3 feuilles avec calcul des jours !"
End Sub

' ===========================
' CORRECTION GRAPHIQUES - Remplacer colonne X (AUTOMATIQUE)
' ===========================
Sub CorrigerAxeXGraphiques()
    Dim ws As Worksheet, wsCordes As Worksheet
    Dim cht As ChartObject
    Dim ser As Series
    Dim newXRange As String
    Dim nbModif As Long
    Dim lastRowCordes As Long
    
    ' Détection automatique de la plage de dates
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    lastRowCordes = wsCordes.Cells(wsCordes.Rows.Count, "A").End(xlUp).Row
    
    ' Construire la plage de dates (colonne A, à partir de la ligne 10)
    newXRange = "Cordes!$A$10:$A$" & lastRowCordes
    
    ' Feuille contenant les graphiques
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("graphiques")
    If ws Is Nothing Then
        MsgBox "Feuille 'graphiques' non trouvée !", vbExclamation
        Exit Sub
    End If
    On Error GoTo 0
    
    nbModif = 0
    
    ' Parcourir tous les graphiques de la feuille
    For Each cht In ws.ChartObjects
        ' Parcourir toutes les séries du graphique
        For Each ser In cht.Chart.SeriesCollection
            ' Modifier la plage X (abscisses) de chaque série
            On Error Resume Next
            ser.XValues = Range(newXRange)
            If Err.Number = 0 Then nbModif = nbModif + 1
            On Error GoTo 0
        Next ser
    Next cht
    
    MsgBox "Graphiques corrigés ! (" & nbModif & " séries modifiées)" & vbCrLf & _
           "Plage utilisée : " & newXRange
End Sub

' ===========================
' DIAGNOSTIC GRAPHIQUES
' ===========================
Sub ListerTousLesGraphiques()
    Dim ws As Worksheet
    Dim cht As ChartObject
    Dim ser As Series
    Dim i As Long
    Dim msg As String
    
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("graphiques")
    If ws Is Nothing Then
        MsgBox "Feuille 'graphiques' non trouvée !", vbExclamation
        Exit Sub
    End If
    On Error GoTo 0
    
    Debug.Print ""
    Debug.Print "╔══════════════════════════════════════════════════╗"
    Debug.Print "║  INVENTAIRE DES GRAPHIQUES                      ║"
    Debug.Print "╚══════════════════════════════════════════════════╝"
    Debug.Print ""
    
    For Each cht In ws.ChartObjects
        Debug.Print "▶ " & cht.Name
        Debug.Print "  Position: Top=" & cht.Top & " Left=" & cht.Left
        
        ' Titre du graphique
        If cht.Chart.HasTitle Then
            Debug.Print "  Titre: " & cht.Chart.ChartTitle.Text
        Else
            Debug.Print "  Titre: (aucun)"
        End If
        
        ' Séries
        Debug.Print "  Séries (" & cht.Chart.SeriesCollection.Count & "):"
        i = 1
        For Each ser In cht.Chart.SeriesCollection
            Debug.Print "    " & i & ". Nom: " & ser.Name
            Debug.Print "       Formule: " & ser.Formula
            i = i + 1
        Next ser
        Debug.Print ""
    Next cht
    
    Debug.Print "═══════════════════════════════════════════════════"
    Debug.Print "✓ Total: " & ws.ChartObjects.Count & " graphiques"
    
    MsgBox "Inventaire terminé !" & vbCrLf & vbCrLf & _
           ws.ChartObjects.Count & " graphiques analysés" & vbCrLf & vbCrLf & _
           "Consultez la fenêtre Immediate (Ctrl+G)", vbInformation
End Sub

' ===========================
' DIAGNOSTIC AVANCÉ - Vérifier cohérence des graphiques
' ===========================
Sub DiagnostiquerCoherenceGraphiques()
    Dim ws As Worksheet, wsCordes As Worksheet
    Dim cht As ChartObject
    Dim ser As Series
    Dim i As Long, nbIncoh As Long, nbOK As Long
    Dim formula As String, xValPart As String, yValPart As String
    Dim sheetName As String, xRange As String, yRange As String
    
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("graphiques")
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    If ws Is Nothing Or wsCordes Is Nothing Then
        MsgBox "Feuille 'graphiques' ou 'Cordes' non trouvée !", vbExclamation
        Exit Sub
    End If
    On Error GoTo 0
    
    nbIncoh = 0
    nbOK = 0
    
    Debug.Print ""
    Debug.Print "╔══════════════════════════════════════════════════╗"
    Debug.Print "║  DIAGNOSTIC COHÉRENCE GRAPHIQUES                ║"
    Debug.Print "╚══════════════════════════════════════════════════╝"
    Debug.Print ""
    
    For Each cht In ws.ChartObjects
        Debug.Print "▶ " & cht.Name
        If cht.Chart.HasTitle Then
            Debug.Print "  Titre: " & cht.Chart.ChartTitle.Text
        End If
        Debug.Print ""
        
        ' Déterminer les attentes selon le graphique
        Dim xColAttendue As String, yColsAttendues As String
        Dim yDebut As Long, yFin As Long
        
        Select Case cht.Name
            Case "Graphique 30"
                xColAttendue = "AQ"
                yColsAttendues = "AS à AZ"
                yDebut = 45: yFin = 52
            Case "Graphique 31"
                xColAttendue = "A"
                yColsAttendues = "C à O"
                yDebut = 3: yFin = 15
            Case "Graphique 32"
                xColAttendue = "V"
                yColsAttendues = "X à AJ"
                yDebut = 24: yFin = 36
            Case Else
                Debug.Print "  ⚠ Graphique non géré par le diagnostic"
                Debug.Print ""
                GoTo NextChart
        End Select
        
        Debug.Print "  Attendu: X=" & xColAttendue & " | Y=" & yColsAttendues
        Debug.Print ""
        
        ' Analyser chaque série
        i = 1
        For Each ser In cht.Chart.SeriesCollection
            formula = ser.formula
            
            ' Parser la formule SERIES
            ' Format: =SERIES(nom,feuille!$X$10:$X$n,feuille!$Y$10:$Y$n,index)
            Dim parts() As String
            parts = Split(formula, ",")
            
            If UBound(parts) >= 2 Then
                xValPart = Trim(parts(1))
                yValPart = Trim(parts(2))
                
                ' Extraire les plages
                Dim xCol As String, yCol As String
                xCol = ExtraireColonne(xValPart)
                yCol = ExtraireColonne(yValPart)
                
                ' Vérifier la cohérence
                Dim coherent As Boolean
                coherent = True
                Dim erreurs As String
                erreurs = ""
                
                ' Vérifier X
                If xCol <> xColAttendue Then
                    coherent = False
                    erreurs = erreurs & "X incorrect (" & xCol & " au lieu de " & xColAttendue & ") "
                End If
                
                ' Vérifier Y
                Dim yColNum As Long
                yColNum = ColonneVersNumero(yCol)
                If yColNum < yDebut Or yColNum > yFin Then
                    coherent = False
                    erreurs = erreurs & "Y hors plage (" & yCol & " pas dans " & yColsAttendues & ") "
                End If
                
                ' Afficher résultat
                If coherent Then
                    Debug.Print "    ✓ Série " & i & ": " & ser.Name & " OK"
                    nbOK = nbOK + 1
                Else
                    Debug.Print "    ❌ Série " & i & ": " & ser.Name
                    Debug.Print "       Formule: " & formula
                    Debug.Print "       Problème: " & erreurs
                    nbIncoh = nbIncoh + 1
                End If
            Else
                Debug.Print "    ⚠ Série " & i & ": Formule non parsable"
                nbIncoh = nbIncoh + 1
            End If
            
            i = i + 1
        Next ser
        
        Debug.Print ""
NextChart:
    Next cht
    
    Debug.Print "═══════════════════════════════════════════════════"
    Debug.Print "✓ Séries cohérentes: " & nbOK
    Debug.Print "✗ Incohérences trouvées: " & nbIncoh
    Debug.Print ""
    
    If nbIncoh > 0 Then
        MsgBox "⚠ " & nbIncoh & " incohérence(s) détectée(s) !" & vbCrLf & vbCrLf & _
               "Consultez la fenêtre Immediate (Ctrl+G) pour les détails.", vbExclamation
    Else
        MsgBox "✓ Tous les graphiques sont cohérents !" & vbCrLf & vbCrLf & _
               nbOK & " séries vérifiées avec succès.", vbInformation
    End If
End Sub

' Fonction helper pour extraire la colonne d'une référence Excel
Private Function ExtraireColonne(refRange As String) As String
    Dim pos1 As Long, pos2 As Long
    Dim colPart As String
    
    ' Chercher le premier $
    pos1 = InStr(refRange, "$")
    If pos1 = 0 Then
        ExtraireColonne = ""
        Exit Function
    End If
    
    ' Chercher le deuxième $
    pos2 = InStr(pos1 + 1, refRange, "$")
    If pos2 = 0 Then
        ExtraireColonne = ""
        Exit Function
    End If
    
    ' Extraire la colonne (entre les deux $)
    colPart = Mid(refRange, pos1 + 1, pos2 - pos1 - 1)
    ExtraireColonne = colPart
End Function

' Fonction helper pour convertir lettre de colonne en numéro
Private Function ColonneVersNumero(colLettre As String) As Long
    On Error Resume Next
    ColonneVersNumero = Range(colLettre & "1").Column
    If Err.Number <> 0 Then ColonneVersNumero = 0
    On Error GoTo 0
End Function

' ===========================
' CONFIGURATION GRAPHIQUE 30 - Cordes verticales
' ===========================
Sub ConfigurerGraphique30_CordesVerticales()
    Dim wsGraph As Worksheet, wsCordes As Worksheet
    Dim cht As ChartObject
    Dim ser As Series
    Dim lastRow As Long
    Dim col As Long
    Dim seriesName As String
    Dim xRange As String, yRange As String
    Dim nbSeries As Long
    
    ' Feuilles
    On Error Resume Next
    Set wsGraph = ThisWorkbook.Sheets("graphiques")
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    If wsGraph Is Nothing Or wsCordes Is Nothing Then
        MsgBox "Feuille 'graphiques' ou 'Cordes' non trouvée !", vbExclamation
        Exit Sub
    End If
    
    ' Trouver le graphique
    Set cht = wsGraph.ChartObjects("Graphique 30")
    If cht Is Nothing Then
        MsgBox "Graphique 30 non trouvé !", vbExclamation
        Exit Sub
    End If
    On Error GoTo 0
    
    ' Déterminer la dernière ligne de données
    lastRow = wsCordes.Cells(wsCordes.Rows.Count, 43).End(xlUp).Row ' Colonne AQ = 43
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════╗"
    Debug.Print "║  CONFIGURATION GRAPHIQUE 30               ║"
    Debug.Print "╚════════════════════════════════════════════╝"
    Debug.Print "Dernière ligne de données: " & lastRow
    Debug.Print ""
    
    ' Plage X commune (dates) : Colonne AQ (43)
    xRange = "Cordes!$AQ$10:$AQ$" & lastRow
    Debug.Print "Axe X (dates): " & xRange
    Debug.Print ""
    
    ' Supprimer toutes les séries existantes
    Do While cht.Chart.SeriesCollection.Count > 0
        cht.Chart.SeriesCollection(1).Delete
    Loop
    
    ' Créer les séries pour AS à AZ (colonnes 45 à 52)
    nbSeries = 0
    For col = 45 To 52 ' AS=45, AT=46, ..., AZ=52
        ' Lire le nom de la série (entête ligne 9)
        seriesName = Trim(wsCordes.Cells(9, col).Value)
        
        If seriesName <> "" Then
            ' Plage Y pour cette série
            yRange = "Cordes!" & wsCordes.Cells(10, col).Address(True, True) & ":" & _
                     wsCordes.Cells(lastRow, col).Address(True, True)
            
            Debug.Print "Série " & (nbSeries + 1) & ": " & seriesName
            Debug.Print "  Y: " & yRange
            
            ' Ajouter la série
            Set ser = cht.Chart.SeriesCollection.NewSeries
            ser.Name = seriesName
            ser.XValues = wsCordes.Range(xRange)
            ser.Values = wsCordes.Range(yRange)
            
            nbSeries = nbSeries + 1
        End If
    Next col
    
    Debug.Print ""
    Debug.Print "✓ " & nbSeries & " séries configurées"
    
    MsgBox "Graphique 30 configuré !" & vbCrLf & vbCrLf & _
           nbSeries & " séries créées (AS à AZ)" & vbCrLf & _
           "Plage: lignes 10 à " & lastRow, vbInformation
End Sub

' ===========================
' CONFIGURATION GRAPHIQUE 31 - Cordes horizontales (Référence 1)
' ===========================
Sub ConfigurerGraphique31_CordesHorizontalesRef1()
    Dim wsGraph As Worksheet, wsCordes As Worksheet
    Dim cht As ChartObject
    Dim ser As Series
    Dim lastRow As Long
    Dim col As Long
    Dim seriesName As String
    Dim xRange As String, yRange As String
    Dim nbSeries As Long
    
    ' Feuilles
    On Error Resume Next
    Set wsGraph = ThisWorkbook.Sheets("graphiques")
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    If wsGraph Is Nothing Or wsCordes Is Nothing Then
        MsgBox "Feuille 'graphiques' ou 'Cordes' non trouvée !", vbExclamation
        Exit Sub
    End If
    
    ' Trouver le graphique
    Set cht = wsGraph.ChartObjects("Graphique 31")
    If cht Is Nothing Then
        MsgBox "Graphique 31 non trouvé !", vbExclamation
        Exit Sub
    End If
    On Error GoTo 0
    
    ' Déterminer la dernière ligne de données (colonne A)
    lastRow = wsCordes.Cells(wsCordes.Rows.Count, 1).End(xlUp).Row ' Colonne A = 1
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════╗"
    Debug.Print "║  CONFIGURATION GRAPHIQUE 31               ║"
    Debug.Print "╚════════════════════════════════════════════╝"
    Debug.Print "Dernière ligne de données: " & lastRow
    Debug.Print ""
    
    ' Plage X commune (dates) : Colonne A (1)
    xRange = "Cordes!$A$10:$A$" & lastRow
    Debug.Print "Axe X (dates): " & xRange
    Debug.Print ""
    
    ' Supprimer toutes les séries existantes
    Do While cht.Chart.SeriesCollection.Count > 0
        cht.Chart.SeriesCollection(1).Delete
    Loop
    
    ' Créer les séries pour C à O (colonnes 3 à 15)
    nbSeries = 0
    For col = 3 To 15 ' C=3, D=4, ..., O=15
        ' Lire le nom de la série (entête ligne 9)
        seriesName = Trim(wsCordes.Cells(9, col).Value)
        
        If seriesName <> "" Then
            ' Plage Y pour cette série
            yRange = "Cordes!" & wsCordes.Cells(10, col).Address(True, True) & ":" & _
                     wsCordes.Cells(lastRow, col).Address(True, True)
            
            Debug.Print "Série " & (nbSeries + 1) & ": " & seriesName
            Debug.Print "  Y: " & yRange
            
            ' Ajouter la série
            Set ser = cht.Chart.SeriesCollection.NewSeries
            ser.Name = seriesName
            ser.XValues = wsCordes.Range(xRange)
            ser.Values = wsCordes.Range(yRange)
            
            nbSeries = nbSeries + 1
        End If
    Next col
    
    Debug.Print ""
    Debug.Print "✓ " & nbSeries & " séries configurées"
    
    MsgBox "Graphique 31 configuré !" & vbCrLf & vbCrLf & _
           nbSeries & " séries créées (C à O)" & vbCrLf & _
           "Plage: lignes 10 à " & lastRow, vbInformation
End Sub

' ===========================
' CONFIGURATION GRAPHIQUE 32 - Cordes horizontales (Référence 2)
' ===========================
Sub ConfigurerGraphique32_CordesHorizontalesRef2()
    Dim wsGraph As Worksheet, wsCordes As Worksheet
    Dim cht As ChartObject
    Dim ser As Series
    Dim lastRow As Long
    Dim col As Long
    Dim seriesName As String
    Dim xRange As String, yRange As String
    Dim nbSeries As Long
    
    ' Feuilles
    On Error Resume Next
    Set wsGraph = ThisWorkbook.Sheets("graphiques")
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    If wsGraph Is Nothing Or wsCordes Is Nothing Then
        MsgBox "Feuille 'graphiques' ou 'Cordes' non trouvée !", vbExclamation
        Exit Sub
    End If
    
    ' Trouver le graphique
    Set cht = wsGraph.ChartObjects("Graphique 32")
    If cht Is Nothing Then
        MsgBox "Graphique 32 non trouvé !", vbExclamation
        Exit Sub
    End If
    On Error GoTo 0
    
    ' Déterminer la dernière ligne de données (colonne V)
    lastRow = wsCordes.Cells(wsCordes.Rows.Count, 22).End(xlUp).Row ' Colonne V = 22
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════╗"
    Debug.Print "║  CONFIGURATION GRAPHIQUE 32               ║"
    Debug.Print "╚════════════════════════════════════════════╝"
    Debug.Print "Dernière ligne de données: " & lastRow
    Debug.Print ""
    
    ' Plage X commune (dates) : Colonne V (22)
    xRange = "Cordes!$V$10:$V$" & lastRow
    Debug.Print "Axe X (dates): " & xRange
    Debug.Print ""
    
    ' Supprimer toutes les séries existantes
    Do While cht.Chart.SeriesCollection.Count > 0
        cht.Chart.SeriesCollection(1).Delete
    Loop
    
    ' Créer les séries pour X à AJ (colonnes 24 à 36)
    nbSeries = 0
    For col = 24 To 36 ' X=24, Y=25, ..., AJ=36
        ' Lire le nom de la série (entête ligne 9)
        seriesName = Trim(wsCordes.Cells(9, col).Value)
        
        If seriesName <> "" Then
            ' Plage Y pour cette série
            yRange = "Cordes!" & wsCordes.Cells(10, col).Address(True, True) & ":" & _
                     wsCordes.Cells(lastRow, col).Address(True, True)
            
            Debug.Print "Série " & (nbSeries + 1) & ": " & seriesName
            Debug.Print "  Y: " & yRange
            
            ' Ajouter la série
            Set ser = cht.Chart.SeriesCollection.NewSeries
            ser.Name = seriesName
            ser.XValues = wsCordes.Range(xRange)
            ser.Values = wsCordes.Range(yRange)
            
            nbSeries = nbSeries + 1
        End If
    Next col
    
    Debug.Print ""
    Debug.Print "✓ " & nbSeries & " séries configurées"
    
    MsgBox "Graphique 32 configuré !" & vbCrLf & vbCrLf & _
           nbSeries & " séries créées (X à AJ)" & vbCrLf & _
           "Plage: lignes 10 à " & lastRow, vbInformation
End Sub

' ===========================
' CONFIGURATION TOUS LES GRAPHIQUES - Tout en un
' ===========================
Sub ConfigurerTousLesGraphiquesCordes()
    Call ConfigurerGraphique30_CordesVerticales
    Call ConfigurerGraphique31_CordesHorizontalesRef1
    Call ConfigurerGraphique32_CordesHorizontalesRef2
    MsgBox "✓ Tous les graphiques configurés !", vbInformation
End Sub

' ===========================
' DIAGNOSTIC V.3 - Pourquoi les déplacements ne se calculent pas
' ===========================
Sub DiagnostiquerProblemeV3()
    Dim wsObs As Worksheet, wsDep As Worksheet
    Dim c As Long, lastColDep As Long, lastColObs As Long
    Dim cibleDep As String, champDep As String
    Dim cibleObs As String, champObs As String
    Dim refVal As Variant
    
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    
    lastColDep = wsDep.Cells(2, wsDep.Columns.Count).End(xlToLeft).Column
    lastColObs = wsObs.Cells(4, wsObs.Columns.Count).End(xlToLeft).Column
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════════════════════╗"
    Debug.Print "║  DIAGNOSTIC V.3 - ANALYSE DÉTAILLÉE                       ║"
    Debug.Print "╚════════════════════════════════════════════════════════════╝"
    Debug.Print ""
    
    ' 1. Chercher V.3 dans Déplacements
    Debug.Print "=== ÉTAPE 1 : Colonnes V.3 dans DÉPLACEMENTS ==="
    Dim colsV3Dep As String
    colsV3Dep = ""
    
    For c = 2 To lastColDep
        cibleDep = Trim(wsDep.Cells(2, c).Value)
        champDep = Trim(wsDep.Cells(3, c).Value)
        
        If InStr(UCase(cibleDep), "V.3") > 0 Or InStr(UCase(cibleDep), "V3") > 0 Then
            Debug.Print "  Col " & c & " (" & Split(wsDep.Cells(1, c).Address, "$")(1) & "):"
            Debug.Print "    Cible L2: [" & cibleDep & "] (Len=" & Len(cibleDep) & ")"
            Debug.Print "    Champ L3: [" & champDep & "] (Len=" & Len(champDep) & ")"
            Debug.Print "    AscII cible: " & AfficherASCII(cibleDep)
            colsV3Dep = colsV3Dep & c & ","
        End If
    Next c
    
    If colsV3Dep = "" Then
        Debug.Print "  ❌ AUCUNE colonne V.3 trouvée dans Déplacements !"
    End If
    Debug.Print ""
    
    ' 2. Chercher V.3 dans Résultats observations
    Debug.Print "=== ÉTAPE 2 : Colonnes V.3 dans RÉSULTATS OBSERVATIONS ==="
    Dim colsV3Obs As String
    colsV3Obs = ""
    
    For c = 2 To lastColObs
        cibleObs = Trim(wsObs.Cells(4, c).Value)
        champObs = Trim(wsObs.Cells(5, c).Value)
        
        If InStr(UCase(cibleObs), "V.3") > 0 Or InStr(UCase(cibleObs), "V3") > 0 Then
            Debug.Print "  Col " & c & " (" & Split(wsObs.Cells(1, c).Address, "$")(1) & "):"
            Debug.Print "    Cible L4: [" & cibleObs & "] (Len=" & Len(cibleObs) & ")"
            Debug.Print "    Champ L5: [" & champObs & "] (Len=" & Len(champObs) & ")"
            Debug.Print "    AscII cible: " & AfficherASCII(cibleObs)
            
            ' Vérifier la valeur de référence
            refVal = wsObs.Cells(10, c).Value
            Debug.Print "    Ref L10: [" & refVal & "] IsEmpty=" & IsEmpty(refVal) & " IsNumeric=" & IsNumeric(refVal)
            If IsNumeric(refVal) Then Debug.Print "    Ref numérique: " & CDbl(refVal)
            
            colsV3Obs = colsV3Obs & c & ","
        End If
    Next c
    
    If colsV3Obs = "" Then
        Debug.Print "  ❌ AUCUNE colonne V.3 trouvée dans Résultats observations !"
    End If
    Debug.Print ""
    
    ' 3. Test de matching
    Debug.Print "=== ÉTAPE 3 : TEST DE MATCHING ==="
    
    For c = 2 To lastColDep
        cibleDep = Trim(wsDep.Cells(2, c).Value)
        champDep = Trim(wsDep.Cells(3, c).Value)
        
        If InStr(UCase(cibleDep), "V.3") > 0 Or InStr(UCase(cibleDep), "V3") > 0 Then
            Debug.Print "  Recherche match pour: cible=[" & cibleDep & "] champ=[" & champDep & "]"
            
            Dim found As Boolean
            found = False
            Dim cObs As Long
            
            For cObs = 2 To lastColObs
                cibleObs = wsObs.Cells(4, cObs).Value
                champObs = wsObs.Cells(5, cObs).Value
                
                ' Test exact comme dans le code
                If UCase(Trim(CStr(cibleObs))) = UCase(Trim(CStr(cibleDep))) And _
                   UCase(Trim(CStr(champObs))) = UCase(Trim(CStr(champDep))) Then
                    Debug.Print "    ✓ MATCH trouvé en colonne " & cObs & " (" & Split(wsObs.Cells(1, cObs).Address, "$")(1) & ")"
                    
                    ' Vérifier les validations
                    refVal = wsObs.Cells(10, cObs).Value
                    Debug.Print "      Valeur ref L10: [" & refVal & "]"
                    
                    If IsEmpty(refVal) Then
                        Debug.Print "      ❌ BLOQUÉ: Référence vide (IsEmpty=True)"
                    ElseIf Not IsNumeric(refVal) Then
                        Debug.Print "      ❌ BLOQUÉ: Référence non numérique"
                    ElseIf CDbl(refVal) = 0 Then
                        Debug.Print "      ❌ BLOQUÉ: Référence = 0 (cible considérée abandonnée)"
                    Else
                        Debug.Print "      ✓ Référence OK: " & CDbl(refVal)
                    End If
                    
                    found = True
                    Exit For
                End If
            Next cObs
            
            If Not found Then
                Debug.Print "    ❌ AUCUN MATCH - Comparaisons détaillées:"
                For cObs = 2 To lastColObs
                    cibleObs = wsObs.Cells(4, cObs).Value
                    If InStr(UCase(cibleObs), "V") > 0 Then
                        Debug.Print "      Col " & cObs & ": [" & cibleObs & "] vs [" & cibleDep & "] = " & _
                                    (UCase(Trim(CStr(cibleObs))) = UCase(Trim(CStr(cibleDep))))
                    End If
                Next cObs
            End If
        End If
    Next c
    
    Debug.Print ""
    Debug.Print "═══════════════════════════════════════════════════════════"
    Debug.Print "Diagnostic terminé - consultez les détails ci-dessus"
    
    MsgBox "Diagnostic V.3 terminé !" & vbCrLf & vbCrLf & _
           "Consultez la fenêtre Immediate (Ctrl+G) pour les détails.", vbInformation
End Sub

' Helper pour afficher les codes ASCII (détecter caractères invisibles)
Private Function AfficherASCII(texte As String) As String
    Dim i As Long
    Dim result As String
    result = ""
    For i = 1 To Len(texte)
        result = result & Asc(Mid(texte, i, 1)) & " "
    Next i
    AfficherASCII = result
End Function

' ===========================
' DIAGNOSTIC - Vérifier les valeurs calculées pour V.3
' ===========================
Sub VerifierValeursV3()
    Dim wsDep As Worksheet, wsObs As Worksheet
    Dim c As Long, r As Long
    Dim cible As String, champ As String
    
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════════════════════╗"
    Debug.Print "║  VÉRIFICATION VALEURS V.3 DANS DÉPLACEMENTS               ║"
    Debug.Print "╚════════════════════════════════════════════════════════════╝"
    Debug.Print ""
    
    ' Chercher les colonnes V.3 dans Déplacements et afficher leurs valeurs
    For c = 2 To wsDep.Cells(2, wsDep.Columns.Count).End(xlToLeft).Column
        cible = Trim(wsDep.Cells(2, c).Value)
        champ = Trim(wsDep.Cells(3, c).Value)
        
        If UCase(cible) = "V.3" Then
            Debug.Print "Col " & c & " (" & Split(wsDep.Cells(1, c).Address, "$")(1) & "): V.3 champ " & champ
            Debug.Print "  Valeurs lignes 10-15:"
            For r = 10 To 15
                Debug.Print "    L" & r & ": [" & wsDep.Cells(r, c).Value & "] IsEmpty=" & IsEmpty(wsDep.Cells(r, c).Value)
            Next r
            Debug.Print ""
        End If
    Next c
    
    Debug.Print "═══════════════════════════════════════════════════════════"
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════════════════════╗"
    Debug.Print "║  VÉRIFICATION VALEURS V.3 DANS RÉSULTATS OBS (source)     ║"
    Debug.Print "╚════════════════════════════════════════════════════════════╝"
    Debug.Print ""
    
    ' Vérifier aussi les valeurs sources dans Résultats observations
    For c = 2 To wsObs.Cells(4, wsObs.Columns.Count).End(xlToLeft).Column
        cible = Trim(wsObs.Cells(4, c).Value)
        champ = Trim(wsObs.Cells(5, c).Value)
        
        If UCase(cible) = "V.3" And (champ = "6" Or champ = "7" Or champ = "8") Then
            Debug.Print "Col " & c & " (" & Split(wsObs.Cells(1, c).Address, "$")(1) & "): V.3 champ " & champ
            Debug.Print "  Valeurs lignes 10-15:"
            For r = 10 To 15
                Debug.Print "    L" & r & ": [" & wsObs.Cells(r, c).Value & "]"
            Next r
            Debug.Print ""
        End If
    Next c
    
    Debug.Print "═══════════════════════════════════════════════════════════"
    
    MsgBox "Vérification terminée ! Consultez Ctrl+G", vbInformation
End Sub

' ===========================
' DIAGNOSTIC - Structure complète onglet Déplacements
' ===========================
Sub DiagnostiquerStructureDeplacements()
    Dim wsDep As Worksheet
    Dim c As Long, r As Long
    Dim lastCol As Long, lastRow As Long
    Dim cible As String, champ As String
    
    Set wsDep = ThisWorkbook.Sheets("Déplacements")
    
    lastRow = wsDep.Cells(wsDep.Rows.Count, "A").End(xlUp).Row
    lastCol = wsDep.Cells(2, wsDep.Columns.Count).End(xlToLeft).Column
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════════════════════╗"
    Debug.Print "║  STRUCTURE COMPLÈTE ONGLET DÉPLACEMENTS                   ║"
    Debug.Print "╚════════════════════════════════════════════════════════════╝"
    Debug.Print ""
    Debug.Print "Dernière ligne avec données (col A): " & lastRow
    Debug.Print "Dernière colonne avec entête (ligne 2): " & lastCol
    Debug.Print ""
    
    ' Afficher les entêtes des 20 premières colonnes
    Debug.Print "=== ENTÊTES (20 premières colonnes) ==="
    Debug.Print "Col | Lettre | Ligne 2 (Cible) | Ligne 3 (Champ)"
    Debug.Print "----+--------+-----------------+-----------------"
    
    For c = 1 To 20
        If c <= lastCol Then
            cible = Trim(wsDep.Cells(2, c).Value)
            champ = Trim(wsDep.Cells(3, c).Value)
            Debug.Print Format(c, "000") & " | " & Format(Split(wsDep.Cells(1, c).Address, "$")(1), "@@@@@@") & " | " & _
                        Format(cible, "!@@@@@@@@@@@@@@@") & " | " & champ
        End If
    Next c
    
    Debug.Print ""
    Debug.Print "=== DATES (colonne A, lignes 10-" & lastRow & ") ==="
    For r = 10 To lastRow
        Debug.Print "  L" & r & ": [" & wsDep.Cells(r, 1).Value & "] (Value2=" & wsDep.Cells(r, 1).Value2 & ")"
    Next r
    
    Debug.Print ""
    Debug.Print "=== VALEURS V.3 - VÉRIFICATION VISUELLE ==="
    Debug.Print "Les colonnes V.3 sont en K, L, M, N (colonnes 11-14)"
    Debug.Print ""
    Debug.Print "Colonne K (V.3 PM):"
    For r = 10 To lastRow
        Debug.Print "  K" & r & " = " & wsDep.Cells(r, 11).Value & " (NumberFormat=" & wsDep.Cells(r, 11).NumberFormat & ")"
    Next r
    
    Debug.Print ""
    Debug.Print "=== VÉRIFICATION FORMAT CELLULES ==="
    Debug.Print "K10: Font.Color=" & wsDep.Cells(10, 11).Font.Color & " Interior.Color=" & wsDep.Cells(10, 11).Interior.Color
    Debug.Print "K10: Hidden=" & wsDep.Columns(11).Hidden & " ColumnWidth=" & wsDep.Columns(11).ColumnWidth
    
    Debug.Print ""
    Debug.Print "═══════════════════════════════════════════════════════════"
    
    MsgBox "Diagnostic terminé ! Consultez Ctrl+G" & vbCrLf & vbCrLf & _
           "Les valeurs V.3 devraient être en colonnes K, L, M, N" & vbCrLf & _
           "(lignes 10 à " & lastRow & ")", vbInformation
End Sub

' ===========================
' DIAGNOSTIC - Trouver les cordes manquantes (V.3-B.4)
' ===========================
Sub DiagnostiquerCordesV3()
    Dim wsCordes As Worksheet, wsObs As Worksheet
    Dim c As Long, lastCol As Long
    Dim cible1 As String, cible2 As String
    
    Set wsCordes = ThisWorkbook.Sheets("Cordes")
    Set wsObs = ThisWorkbook.Sheets("Résultats observations")
    
    Debug.Print ""
    Debug.Print "╔════════════════════════════════════════════════════════════╗"
    Debug.Print "║  DIAGNOSTIC CORDES V.3                                    ║"
    Debug.Print "╚════════════════════════════════════════════════════════════╝"
    Debug.Print ""
    
    ' 1. Chercher V.3 dans Cordes (ligne 4)
    Debug.Print "=== ÉTAPE 1 : Cordes contenant V.3 dans l'onglet CORDES ==="
    lastCol = wsCordes.Cells(4, wsCordes.Columns.Count).End(xlToLeft).Column
    Debug.Print "Dernière colonne Cordes: " & lastCol
    Debug.Print ""
    
    Dim nbV3 As Long
    nbV3 = 0
    
    For c = 1 To lastCol
        cible1 = Trim(wsCordes.Cells(4, c).Value)
        cible2 = Trim(wsCordes.Cells(5, c).Value)
        
        If InStr(UCase(cible1), "V.3") > 0 Or InStr(UCase(cible1), "V3") > 0 Or _
           InStr(UCase(cible2), "V.3") > 0 Or InStr(UCase(cible2), "V3") > 0 Then
            Debug.Print "  Col " & c & " (" & Split(wsCordes.Cells(1, c).Address, "$")(1) & "):"
            Debug.Print "    Ligne 4 (cible1): [" & cible1 & "]"
            Debug.Print "    Ligne 5 (cible2): [" & cible2 & "]"
            nbV3 = nbV3 + 1
        End If
    Next c
    
    If nbV3 = 0 Then
        Debug.Print "  ❌ AUCUNE corde V.3 trouvée dans l'onglet Cordes !"
    Else
        Debug.Print "  ✓ " & nbV3 & " cordes V.3 trouvées"
    End If
    Debug.Print ""
    
    ' 2. Chercher V.3-B.4 spécifiquement dans Résultats observations
    Debug.Print "=== ÉTAPE 2 : Paire V.3-B.4 dans RÉSULTATS OBSERVATIONS ==="
    lastCol = wsObs.Cells(4, wsObs.Columns.Count).End(xlToLeft).Column
    
    Dim foundV3B4 As Boolean
    foundV3B4 = False
    
    For c = 1 To lastCol
        cible1 = UCase(Trim(wsObs.Cells(4, c).Value))
        cible2 = UCase(Trim(wsObs.Cells(5, c).Value))
        
        If (cible1 = "V.3" And cible2 = "B.4") Or (cible1 = "V3" And cible2 = "B4") Then
            Debug.Print "  ✓ TROUVÉ en colonne " & c & " (" & Split(wsObs.Cells(1, c).Address, "$")(1) & ")"
            Debug.Print "    Cible1 L4: [" & wsObs.Cells(4, c).Value & "]"
            Debug.Print "    Cible2 L5: [" & wsObs.Cells(5, c).Value & "]"
            Debug.Print "    Valeur L10: [" & wsObs.Cells(10, c).Value & "]"
            foundV3B4 = True
        End If
    Next c
    
    If Not foundV3B4 Then
        Debug.Print "  ❌ Paire V.3-B.4 NON TROUVÉE dans Résultats observations"
    End If
    Debug.Print ""
    
    ' 3. Afficher les plages de colonnes utilisées par CalculerEcarts
    Debug.Print "=== ÉTAPE 3 : Plages de calcul des écarts cordes ==="
    Debug.Print "  Bloc 1A: Cordes C→T (3-20) vs Obs FU→HE (177-213)"
    Debug.Print "  Bloc 1B: Cordes X→AO (24-41) vs Obs FU→HE (177-213)"
    Debug.Print "  Bloc 2:  Cordes AS→BE (45-57) vs Obs HG→HS (215-227)"
    Debug.Print ""
    Debug.Print "  → V.3-B.4 devrait être dans quelle plage ?"
    Debug.Print "    Si V.3-B.4 est après colonne BE (57) dans Cordes, il ne sera pas traité !"
    Debug.Print ""
    
    ' 4. Chercher B.4 dans Cordes
    Debug.Print "=== ÉTAPE 4 : Cordes contenant B.4 dans l'onglet CORDES ==="
    Dim nbB4 As Long
    nbB4 = 0
    
    For c = 1 To wsCordes.Cells(5, wsCordes.Columns.Count).End(xlToLeft).Column
        cible1 = Trim(wsCordes.Cells(4, c).Value)
        cible2 = Trim(wsCordes.Cells(5, c).Value)
        
        If InStr(UCase(cible1), "B.4") > 0 Or InStr(UCase(cible1), "B4") > 0 Or _
           InStr(UCase(cible2), "B.4") > 0 Or InStr(UCase(cible2), "B4") > 0 Then
            Debug.Print "  Col " & c & " (" & Split(wsCordes.Cells(1, c).Address, "$")(1) & "):"
            Debug.Print "    Ligne 4: [" & cible1 & "]"
            Debug.Print "    Ligne 5: [" & cible2 & "]"
            nbB4 = nbB4 + 1
        End If
    Next c
    
    If nbB4 = 0 Then
        Debug.Print "  ❌ AUCUNE corde B.4 trouvée dans l'onglet Cordes !"
    End If
    
    Debug.Print ""
    Debug.Print "═══════════════════════════════════════════════════════════"
    
    MsgBox "Diagnostic terminé ! Consultez Ctrl+G", vbInformation
End Sub
