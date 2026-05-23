"""
Vérifie par MD5 si les fichiers dans _doublons sont vraiment des doublons
de ceux dans USINE-VOUSSOIRS-SMLP (SESSIONS CONTROLES + RAPPORTS).
Échantillonne les N plus gros fichiers par sous-dossier.
"""
import os, hashlib, sys
from collections import defaultdict

NAS = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4"
DOUBLONS = os.path.join(NAS, "_doublons")
USINE    = os.path.join(NAS, "USINE-VOUSSOIRS-SMLP")

SAMPLE_PER_FOLDER = int(sys.argv[1]) if len(sys.argv) > 1 else 20  # fichiers testés par dossier

def human_size(n):
    for u in ["o","Ko","Mo","Go"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

def md5(path, chunk=1024*1024):
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while True:
                data = f.read(chunk)
                if not data: break
                h.update(data)
        return h.hexdigest()
    except Exception:
        return None

# Indexer les fichiers dans USINE-VOUSSOIRS-SMLP : {(filename, size): [path, ...]}
print("Indexation de USINE-VOUSSOIRS-SMLP...")
usine_index = defaultdict(list)
for root, dirs, files in os.walk(USINE):
    # Ne pas indexer _doublons s'il est là par erreur
    dirs[:] = [d for d in dirs if d not in ("_doublons",)]
    for f in files:
        fp = os.path.join(root, f)
        try:
            sz = os.path.getsize(fp)
            usine_index[(f, sz)].append(fp)
        except Exception:
            pass

print(f"  {sum(len(v) for v in usine_index.values())} fichiers indexés dans USINE-VOUSSOIRS-SMLP")

# Parcourir _doublons dossier par dossier
print(f"\nVérification MD5 (échantillon de {SAMPLE_PER_FOLDER} fichiers par sous-dossier)...\n")

grand_total = {"tested": 0, "confirmed": 0, "different": 0, "no_match": 0, "error": 0}
folder_results = {}

top_folders = [d for d in os.listdir(DOUBLONS)
               if os.path.isdir(os.path.join(DOUBLONS, d))]

for top in sorted(top_folders):
    top_path = os.path.join(DOUBLONS, top)

    # Collecter tous les fichiers du sous-dossier, triés par taille desc
    candidates = []
    for root, dirs, files in os.walk(top_path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                candidates.append((sz, fp, f))
            except Exception:
                pass

    if not candidates:
        continue

    candidates.sort(reverse=True)
    sample = candidates[:SAMPLE_PER_FOLDER]

    res = {"confirmed": 0, "different": 0, "no_match": 0, "error": 0, "tested": 0}
    different_examples = []

    for sz, fp, fn in sample:
        res["tested"] += 1
        key = (fn, sz)
        if key not in usine_index:
            res["no_match"] += 1
            continue

        h1 = md5(fp)
        if h1 is None:
            res["error"] += 1
            continue

        # Comparer avec tous les correspondants dans USINE
        matched = False
        for usine_fp in usine_index[key]:
            h2 = md5(usine_fp)
            if h2 == h1:
                matched = True
                break

        if matched:
            res["confirmed"] += 1
        else:
            res["different"] += 1
            different_examples.append((fn, sz, fp))

    folder_results[top] = (res, different_examples, len(candidates))
    for k in grand_total:
        grand_total[k] += res.get(k, 0)

# ─── Rapport ──────────────────────────────────────────────────────────────────
print("=" * 80)
print("RÉSULTAT PAR DOSSIER")
print("=" * 80)
print(f"  {'Dossier':<45} {'Total':>6}  {'Testés':>6}  {'✅Idem':>6}  {'❌Diff':>6}  {'⚠️NoRef':>7}  Verdict")
print("-" * 80)

unsafe = []

for top in sorted(folder_results.keys()):
    res, different_examples, total = folder_results[top]
    t = res["tested"]
    if t == 0:
        verdict = "vide"
    else:
        dup_rate = res["confirmed"] / t
        diff_rate = res["different"] / t
        if diff_rate > 0.1:
            verdict = "⚠️  ATTENTION"
            unsafe.append((top, different_examples, res))
        elif res["no_match"] > t * 0.3:
            verdict = "⚠️  REFS MANQUANTES"
            unsafe.append((top, different_examples, res))
        elif dup_rate >= 0.8:
            verdict = "✅ doublon confirmé"
        else:
            verdict = "~ partiel"
            unsafe.append((top, different_examples, res))

    print(f"  {top[:44]:<45} {total:>6}  {t:>6}  {res['confirmed']:>6}  "
          f"{res['different']:>6}  {res['no_match']:>7}  {verdict}")

print("-" * 80)
print(f"  {'TOTAL':<45} {'':>6}  {grand_total['tested']:>6}  {grand_total['confirmed']:>6}  "
      f"{grand_total['different']:>6}  {grand_total['no_match']:>7}")

if unsafe:
    print("\n" + "=" * 80)
    print("DOSSIERS À EXAMINER (différents ou sans référence)")
    print("=" * 80)
    for top, diff_ex, res in unsafe:
        print(f"\n  📁 {top}")
        print(f"     Différents={res['different']}  Sans_ref={res['no_match']}  Erreurs={res['error']}")
        for fn, sz, fp in diff_ex[:5]:
            rel = fp[len(DOUBLONS)+1:]
            print(f"     ❌ {human_size(sz):>9}  {rel[:70]}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
t = grand_total["tested"]
if t > 0:
    safe_pct = grand_total["confirmed"] / t * 100
    diff_pct = grand_total["different"] / t * 100
    nomatch_pct = grand_total["no_match"] / t * 100
    print(f"  Identiques (vrais doublons) : {grand_total['confirmed']:>5} / {t}  ({safe_pct:.1f}%)")
    print(f"  Différents (faux doublons)  : {grand_total['different']:>5} / {t}  ({diff_pct:.1f}%)")
    print(f"  Sans correspondance         : {grand_total['no_match']:>5} / {t}  ({nomatch_pct:.1f}%)")
    if diff_pct < 5 and nomatch_pct < 10:
        print("\n  ✅ Les _doublons sont globalement sûrs à supprimer.")
        print("     Vérifier les cas signalés ci-dessus avant suppression.")
    else:
        print("\n  ⚠️  Attention — certains fichiers ne sont PAS de vrais doublons.")
        print("     Ne PAS supprimer sans vérifier les cas signalés.")
