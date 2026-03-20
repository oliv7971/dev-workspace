import os
import subprocess

def standardize_pdf_with_ghostscript(input_pdf_path, output_pdf_path, paper_size='a4'):
    gswin_path = r'C:\\Program Files\\gs\\gs10.05.1\\bin\\gswin64.exe'
    # Commande pour Ghostscript pour ajuster la taille de toutes les pages au format A4
    command = [
         gswin_path,
        '-sDEVICE=pdfwrite',
        '-dNOPAUSE',
        '-dBATCH',
        '-dSAFER',
        '-dPDFX',
        f'-dDEVICEWIDTHPOINTS={595}',  # Largeur en points pour A4
        f'-dDEVICEHEIGHTPOINTS={842}', # Hauteur en points pour A4
        f'-sOutputFile={output_pdf_path}',
        f'{input_pdf_path}'
    ]
    subprocess.run(command, check=True)

def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            input_path = os.path.join(directory_path, filename)
            output_path = os.path.join(directory_path, f'standardized_{filename}')

            standardize_pdf_with_ghostscript(input_path, output_path)
            print(f"Traitement terminé pour {filename}, sauvegardé sous standardized_{filename}")

# Exemple d'utilisation
directory_path = 'C:/Temp/exports_pdf'
process_directory(directory_path)
