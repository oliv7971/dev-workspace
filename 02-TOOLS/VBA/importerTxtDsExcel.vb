Sub ImporterTexteDansExcel()
    Dim CheminFichier As String
    Dim FichierTexte As Integer
    Dim ContenuLigne As String
    Dim Colonne As Integer
    Dim DerniereLigne As Integer

    ' Sélectionnez le fichier texte à importer
    CheminFichier = Application.GetOpenFilename("Fichiers texte (*.txt), *.txt", , "Sélectionnez le fichier texte à importer")

    If CheminFichier = "Faux" Then
        MsgBox "Opération annulée."
        Exit Sub
    End If

    ' Ouvrir le fichier texte
    FichierTexte = FreeFile
    Open CheminFichier For Input As #FichierTexte

    ' Activer la première feuille Excel
    Sheets(1).Activate

    ' Trouver la dernière ligne utilisée dans la feuille Excel
    DerniereLigne = Cells(Rows.Count, 1).End(xlUp).Row

    ' Lire le contenu du fichier texte ligne par ligne
    Do Until EOF(FichierTexte)
        Line Input #FichierTexte, ContenuLigne
        ' Diviser la ligne en colonnes en utilisant le point-virgule comme séparateur
        Dim ColonneData() As String
        ColonneData = Split(ContenuLigne, ";")
        ' Copier les données dans la feuille Excel
        For Colonne = 0 To UBound(ColonneData)
            Cells(DerniereLigne + 1, Colonne + 1).Value = ColonneData(Colonne)
        Next Colonne
        ' Passer à la ligne suivante dans Excel
        DerniereLigne = DerniereLigne + 1
    Loop

    ' Fermer le fichier texte
    Close #FichierTexte

    MsgBox "Les données ont été importées avec succès dans Excel."

End Sub