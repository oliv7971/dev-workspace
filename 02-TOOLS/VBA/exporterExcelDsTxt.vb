Sub ExporterExcelVersTexte()
    Dim CheminFichier As String
    Dim FichierTexte As Integer
    Dim DerniereLigne As Integer
    Dim DerniereColonne As Integer
    Dim Ligne As Integer
    Dim Colonne As Integer

    ' Sélectionnez l'emplacement et le nom du fichier texte de destination
    CheminFichier = Application.GetSaveAsFilename(FileFilter:="Fichiers texte (*.txt), *.txt", Title:="Enregistrer sous")

    If CheminFichier = "Faux" Then
        MsgBox "Opération annulée."
        Exit Sub
    End If

    ' Ouvrir le fichier texte pour écriture
    FichierTexte = FreeFile
    Open CheminFichier For Output As #FichierTexte

    ' Activer la première feuille Excel
    Sheets(1).Activate

    ' Trouver la dernière ligne et la dernière colonne utilisée dans la feuille Excel
    DerniereLigne = Cells(Rows.Count, 1).End(xlUp).Row
    DerniereColonne = Cells(1, Columns.Count).End(xlToLeft).Column

    ' Écrire le contenu de la feuille Excel dans le fichier texte
    For Ligne = 1 To DerniereLigne
        For Colonne = 1 To DerniereColonne
            If Colonne <> DerniereColonne Then
                Print #FichierTexte, Cells(Ligne, Colonne).Value & ";";
            Else
                Print #FichierTexte, Cells(Ligne, Colonne).Value;
            End If
        Next Colonne
        Print #FichierTexte,  ' Aller à la ligne suivante dans le fichier texte
    Next Ligne

    ' Fermer le fichier texte
    Close #FichierTexte

    MsgBox "Le contenu de la feuille Excel a été exporté avec succès vers le fichier texte."
End Sub