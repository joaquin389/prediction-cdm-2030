"""Exploration de data/former_names.csv (anciens noms des selections).

Colonnes : current, former, start_date, end_date
Sert a normaliser les noms d'equipes avant de construire un historique par pays.
Sorties : report/exploration_former_names.txt
"""

import pandas as pd

from common import Report, load

r = Report("exploration_former_names")
fn = load("former_names")
res = load("results")

r.section("1. Contenu complet")
r.log(f"Nombre de correspondances : {len(fn)}")
r.log(f"Pays actuels concernes : {fn['current'].nunique()}")
r.log()
r.log(fn.sort_values("current").to_string(index=False))

r.section("2. Coherence des dates")
bad = fn[fn["start_date"] > fn["end_date"]]
r.log(f"Periodes avec start_date > end_date : {len(bad)}")
r.log(f"Anciens noms utilises par plusieurs pays actuels : "
      f"{fn.groupby('former')['current'].nunique().gt(1).sum()}")
multi = fn["current"].value_counts()
r.log("Pays ayant eu plusieurs anciens noms :")
r.log(multi[multi > 1].to_string() if (multi > 1).any() else "  aucun")

r.section("3. Utilisation des anciens noms dans results.csv")
long = pd.concat([
    res[["date", "home_team"]].rename(columns={"home_team": "team"}),
    res[["date", "away_team"]].rename(columns={"away_team": "team"}),
])
rows = []
for _, row in fn.iterrows():
    played = long[long["team"] == row["former"]]
    in_period = played["date"].between(row["start_date"], row["end_date"])
    rows.append({
        "former": row["former"],
        "current": row["current"],
        "matchs": len(played),
        "hors_periode": int((~in_period).sum()),
    })
usage = pd.DataFrame(rows).sort_values("matchs", ascending=False)
r.log(usage.to_string(index=False))
r.log()
r.log(f"Anciens noms jamais rencontres dans results : {(usage['matchs'] == 0).sum()}")
r.log(f"Matchs joues sous un ancien nom hors de sa periode officielle : {usage['hors_periode'].sum()}")
if (usage["matchs"] == 0).all():
    r.log("-> results.csv utilise DEJA les noms actuels (ex. 'Soviet Union' y est compte "
          "comme 'Russia') : former_names.csv sert de reference, pas de mapping a appliquer.")

r.section("4. Equipes historiques NON couvertes par former_names")
# Etats dissous / scindes : pas un simple renommage, donc absents du fichier.
candidates = ["West Germany", "German DR", "Soviet Union", "Yugoslavia", "Czechoslovakia",
              "Serbia and Montenegro", "CIS", "Saar", "Vietnam Republic", "Yemen DPR"]
teams = set(long["team"])
for t in candidates:
    if t in teams and t not in set(fn["former"]):
        n = (long["team"] == t).sum()
        r.log(f"  {t:<22} {n:>4} matchs -> decision de mapping a prendre manuellement")
r.log()
r.log("-> Ces equipes restent separees dans results.csv. Pour un modele Coupe du monde 2030, "
      "il faut decider si on les rattache a un successeur (ex. Czechoslovakia -> Czech Republic, "
      "Yugoslavia -> Serbia) ou si on les laisse de cote (impact faible : equipes disparues).")

r.save()
