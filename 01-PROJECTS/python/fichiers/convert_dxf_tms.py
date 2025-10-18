import os
import ezdxf

input_folder = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/2025/03/2025-03-13-c-projets TMS galeries/GET2/dxf_recents/"
output_folder = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/2025/03/2025-03-13-c-projets TMS galeries/GET2/dxf_r12/"

# Vérification si le dossier de sortie existe, sinon on le crée
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Vérifier les fichiers dans le dossier source
files_in_folder = [f for f in os.listdir(input_folder) if f.lower().endswith(".dxf")]

# S'il n'y a pas de fichiers DXF dans le dossier source, affiche un message
if not files_in_folder:
    print("Aucun fichier DXF trouvé dans le dossier source.")
else:
    print(f"Fichiers DXF trouvés : {files_in_folder}")

# Conversion de tous les fichiers DXF dans le dossier source
for filename in files_in_folder:
    input_file = os.path.join(input_folder, filename)
    output_file = os.path.join(output_folder, filename)

    try:
        # Charger le fichier DXF source
        doc = ezdxf.readfile(input_file)
        print(f"Chargement réussi du fichier : {filename}")

        # Créer un nouveau fichier DXF au format R12
        new_doc = ezdxf.new('R12')

        # Accéder à l'espace modèle du fichier R12
        new_modelspace = new_doc.modelspace()

        # Vérifier et copier les entités de type LINE, POLYLINE, et CIRCLE
        for entity in doc.modelspace():
            try:
                if entity.dxftype() == 'LINE':
                    print(f"Copie d'une ligne: {entity.dxf.start}, {entity.dxf.end}")
                    new_modelspace.add_line(entity.dxf.start, entity.dxf.end)
                elif entity.dxftype() == 'POLYLINE':  # Gérer les POLYLINE
                    print(f"Copie d'une POLYLINE avec {len(entity.vertices)} sommets")
                    points = [(vertex.x, vertex.y) for vertex in entity.vertices]  # Extraire les points (x, y)
                    # Ajouter la polyligne 2D dans l'espace modèle (R12 n'accepte que 2D)
                    new_modelspace.add_lwpolyline(points, close=entity.is_closed)
                elif entity.dxftype() == 'CIRCLE':
                    print(f"Copie d'un cercle: {entity.dxf.center}, {entity.dxf.radius}")
                    new_modelspace.add_circle(entity.dxf.center, entity.dxf.radius)
                else:
                    print(f"Entité ignorée: {entity.dxftype()}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'entité {entity.dxftype()}: {e}")

        # Sauvegarder le fichier DXF en version R12
        new_doc.saveas(output_file)
        print(f"Fichier converti avec succès: {output_file}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier {filename}: {e}")

print("Conversion terminée !")