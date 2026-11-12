"""Remplace les anciens noms de pays par leur nom actuel grace a data/former_names.csv.

Dans results.csv, les colonnes d'equipes (home_team, away_team) utilisent deja
les noms actuels. Par contre la colonne "country" (pays ou le match a eu lieu)
garde le nom de l'epoque (ex. 'Zaïre', 'Soviet Union', 'Swaziland'). Ce script
la met a jour avec la concordance former -> current.

Usage : python scripts/apply_former_names.py
Le fichier data/results.csv est modifie sur place. Relancer le script ne change
plus rien (les anciens noms ont disparu). Pour revenir aux donnees brutes :
python scripts/download_data.py --force
"""

import pandas as pd

from common import DATA_DIR

# On lit tout en texte (dtype=str) et sans transformer "NA" en valeur manquante
# (keep_default_na=False) : comme ça, le fichier est réécrit à l'identique sauf
# pour les cellules qu'on renomme.
fn = pd.read_csv(DATA_DIR / "former_names.csv", dtype=str, keep_default_na=False, encoding="utf-8")
path = DATA_DIR / "results.csv"
res = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")

# Chaque ancien nom renvoie vers un seul pays actuel, donc un simple
# dictionnaire suffit : {"Zaïre": "DR Congo", "Swaziland": "Eswatini", ...}
mapping = dict(zip(fn["former"], fn["current"]))

# On compte les remplacements avant de les faire, pour afficher un résumé.
counts = res["country"][res["country"].isin(mapping)].value_counts()
res["country"] = res["country"].replace(mapping)

if counts.empty:
    print("Aucun ancien nom trouve dans results.csv (colonne country) : rien a faire.")
else:
    for former, n in counts.items():
        print(f"  {former:<22} -> {mapping[former]:<20} {n:>4} matchs")
    print(f"\nTotal : {counts.sum()} matchs mis a jour ({len(counts)} anciens noms).")
    res.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    print(f"Fichier enregistre : {path}")
