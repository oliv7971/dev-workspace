Imports System.Globalization
Imports System.IO
Imports System.Net.Mime.MediaTypeNames
Imports System.Text.RegularExpressions
Imports Autodesk.AutoCAD.ApplicationServices
Imports Autodesk.AutoCAD.DatabaseServices
Imports Autodesk.AutoCAD.EditorInput
Imports Autodesk.AutoCAD.Geometry
Imports Autodesk.AutoCAD.Runtime

Public Class ImporteurPoints

    <CommandMethod("IMPORTTCPOINT")>
    Public Sub ImporterTCPointsDepuisDossier()

        Dim ed = Application.DocumentManager.MdiActiveDocument.Editor
        Dim doc = Application.DocumentManager.MdiActiveDocument
        Dim db = doc.Database

        ' Demande à l'utilisateur de choisir un dossier
        Dim fbd As New Windows.Forms.FolderBrowserDialog()
        fbd.Description = "Sélectionne le dossier contenant les fichiers DWG"
        If fbd.ShowDialog() <> Windows.Forms.DialogResult.OK Then Return

        Dim dossier As String = fbd.SelectedPath
        Dim fichiers = Directory.GetFiles(dossier, "GGS-S4-C*-leve Boulons radiaux.dwg")

        Using tr As Transaction = db.TransactionManager.StartTransaction()
            For Each fichier In fichiers

                ' Extraction du numéro de coupe
                Dim m = Regex.Match(fichier, "C(\d\d)")
                If Not m.Success Then Continue For
                Dim numeroCoupe As Integer = Integer.Parse(m.Groups(1).Value)
                Dim decalageX As Double = 240 + (numeroCoupe - 3) * 20

                ' Créer une base de données temporaire pour charger le DWG source
                Using dbSource As New Database(False, True)
                    dbSource.ReadDwgFile(fichier, FileShare.Read, True, "")

                    ' Dictionnaire de blocs source
                    Dim btSource As BlockTable = tr.GetObject(dbSource.BlockTableId, OpenMode.ForRead)

                    ' Recherche des blocs TCPOINT
                    Dim btRecordSource As BlockTableRecord = tr.GetObject(btSource(BlockTableRecord.ModelSpace), OpenMode.ForRead)
                    For Each entId In btRecordSource
                        Dim ent = dbSource.TransactionManager.GetObject(entId, OpenMode.ForRead)
                        If TypeOf ent Is BlockReference Then
                            Dim br = DirectCast(ent, BlockReference)
                            Dim bname = br.Name.ToUpper()
                            If bname.Contains("TCPOINT") Then

                                ' Appliquer décalage
                                Dim newPos = New Point3d(br.Position.X + decalageX, br.Position.Y, br.Position.Z)

                                ' Cloner le bloc dans le dessin actif
                                Dim idMap As New IdMapping()
                                Dim ids As New ObjectIdCollection()
                                ids.Add(br.ObjectId)
                                db.WblockCloneObjects(ids, db.CurrentSpaceId, idMap, DuplicateRecordCloning.Ignore, False)

                                ' Repositionner le bloc cloné (nécessite une mise à jour si besoin)
                                ' À ce stade, c’est une copie brute, à affiner selon Covadis
                            End If
                        End If
                    Next
                End Using
            Next

            tr.Commit()
        End Using

        ed.WriteMessage(vbLf & "Importation terminée.")
    End Sub

End Class
