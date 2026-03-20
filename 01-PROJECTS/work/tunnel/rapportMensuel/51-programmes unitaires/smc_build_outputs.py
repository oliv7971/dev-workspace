# smc_build_outputs.py
import argparse, os
import pandas as pd

def french_join(ddmmyyyy_list):
    if not ddmmyyyy_list:
        return "aucune mesure"
    # on retire l’année dans le texte pour l’alléger (reste JJ/MM)
    short = [d[:5] for d in ddmmyyyy_list]
    if len(short) == 1:
        return short[0]
    return ", ".join(short[:-1]) + " et le " + short[-1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-csv", required=True, help="CSV produit par smc_batch_extract.py")
    ap.add_argument("--out-csv", required=True, help="CSV des phrases à insérer")
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--month", type=int, required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv)
    rows = []
    for _, r in df.iterrows():
        dates = [d for d in str(r.get("dates_all_in_month","")).split(";") if d]
        phrase = f"Ce mois-ci, les mesures ont été effectuées les {french_join(dates)} et le {args.year}."
        # si une seule date => pas de “et le …”, on garde naturel
        if len(dates) <= 1:
            phrase = f"Ce mois-ci, la mesure a été effectuée le {french_join(dates)} {args.year}."
        rows.append({
            "filepath": r["filepath"],
            "dates_list": ";".join(dates),
            "sentence": phrase
        })

    out = os.path.abspath(args.out_csv)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8")
    print(f"OK : {out}")

if __name__ == "__main__":
    main()
