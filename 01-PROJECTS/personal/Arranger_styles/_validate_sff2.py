"""Validation de tools/sff2_reader.py sur tous les fichiers de styles Yamaha."""
import glob, os, sys, re, traceback
sys.path.insert(0, '.')
from tools.sff2_reader import read_style, dump_style

all_files = sorted(
    glob.glob(r'données etude\YAMAHA (TYROS3)\**\*.prs', recursive=True) +
    glob.glob(r'données etude\YAMAHA (TYROS5)\**\*.prs', recursive=True) +
    glob.glob(r'données etude\YAMAHA (TYROS5)\**\*.sst', recursive=True)
)

print(f"Fichiers à valider : {len(all_files)}\n")

errors = []
ok_count = 0
stats_by_ver = {}   # ver -> {sections_set, cseg_counts, etc.}

for path in all_files:
    name = os.path.basename(path)
    m = re.search(r'\.(T|S)(\d+)\.', name)
    ver = (m.group(1) + m.group(2)) if m else 'unknown'
    
    try:
        style = read_style(path)
        ok_count += 1
        
        section_names = {s.name for s in style.sections}
        total_events  = sum(len(s.events) for s in style.sections)
        
        if ver not in stats_by_ver:
            stats_by_ver[ver] = {
                'count': 0, 'section_sets': [], 'cseg_counts': [],
                'total_events': [], 'empty_sections': [],
            }
        v = stats_by_ver[ver]
        v['count'] += 1
        v['section_sets'].append(frozenset(section_names))
        v['cseg_counts'].append(len(style.casm))
        v['total_events'].append(total_events)
        empty = [s.name for s in style.sections if len(s.events) == 0]
        v['empty_sections'].extend(empty)
        
    except Exception as e:
        errors.append((name, str(e)))
        traceback.print_exc()

print(f"OK : {ok_count}/{len(all_files)}")
if errors:
    print(f"\nERREURS ({len(errors)}):")
    for name, msg in errors:
        print(f"  {name}: {msg}")

print(f"\n{'='*70}")
print("RÉSUMÉ PAR VERSION")
print('='*70)
for ver in sorted(stats_by_ver):
    v = stats_by_ver[ver]
    n = v['count']
    all_section_sets = v['section_sets']
    unique_sets = len(set(all_section_sets))
    avg_events  = sum(v['total_events']) / n if n else 0
    cseg_vals   = v['cseg_counts']
    cseg_range  = f"{min(cseg_vals)}-{max(cseg_vals)}"
    
    # Sections communes à tous les fichiers de cette version
    if all_section_sets:
        common = set.intersection(*[set(s) for s in all_section_sets])
        all_s  = set.union(*[set(s) for s in all_section_sets])
    else:
        common = all_s = set()
    
    print(f"\nVersion {ver} ({n} fichier(s)):")
    print(f"  CSEGs       : {cseg_range}")
    print(f"  Sections communes ({len(common)}) : {sorted(common)}")
    if all_s - common:
        print(f"  Sections variables : {sorted(all_s - common)}")
    print(f"  Moy. events/style : {avg_events:.0f}")
    if v['empty_sections']:
        from collections import Counter
        emp = Counter(v['empty_sections'])
        print(f"  Sections vides    : {dict(emp)}")

# Afficher un exemple détaillé pour T160 et T108
print(f"\n{'='*70}")
print("EXEMPLE DÉTAILLÉ")
print('='*70)
for target_ver in ('T160', 'T108'):
    candidates = [f for f in all_files if f'.{target_ver}.' in f]
    if candidates:
        style = read_style(candidates[0])
        print(f"\n--- {os.path.basename(candidates[0])} ---")
        dump_style(style)
