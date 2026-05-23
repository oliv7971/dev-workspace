"""Analyse détaillée du sous-dossier dataroom."""
import os
from collections import defaultdict

with open(r'D:\tmp_devp_files.txt', encoding='utf-8', errors='replace') as f:
    lines = [l.strip() for l in f if l.strip()]

base = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT\dataroom'
files = [l for l in lines if l.startswith(base)]
print(f'dataroom: {len(files)} fichiers')

# Extensions
ext_counts = defaultdict(int)
for fp in files:
    ext = os.path.splitext(fp)[1].lower()
    ext_counts[ext] += 1

print()
print('Extensions:')
for ext, n in sorted(ext_counts.items(), key=lambda x: -x[1])[:40]:
    print(f'  {ext:<15} {n:>6}')

# Sous-dossiers de premier niveau
print()
print('Sous-dossiers top-level:')
sub_counts = defaultdict(int)
for fp in files:
    rel = fp[len(base):].lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine)'
    sub_counts[top] += 1
for folder, n in sorted(sub_counts.items(), key=lambda x: -x[1])[:25]:
    print(f'  {folder:<45} {n:>6}')

# Y a-t-il du code ?
CODE_EXTS = {'.py', '.pyw', '.lsp', '.bas', '.cls', '.java', '.php', '.js',
             '.ts', '.sql', '.rb', '.sh', '.bat', '.cmd', '.ps1', '.vb', '.vbs',
             '.c', '.cpp', '.h', '.hpp'}
code_files = [fp for fp in files if os.path.splitext(fp)[1].lower() in CODE_EXTS]
print()
print(f'Fichiers de code source dans dataroom: {len(code_files)}')
for fp in code_files[:20]:
    print(f'  {fp[len(base):]}')
if len(code_files) > 20:
    print(f'  ... et {len(code_files)-20} autres')
