"""Exploration de data/shootouts.csv (seances de tirs au but).

Colonnes : date, home_team, away_team, winner, first_shooter
Sorties : report/exploration_shootouts.txt + figures/shootouts_*.png
"""

import matplotlib.pyplot as plt
import pandas as pd

from common import MATCH_KEY, Report, load, save_fig

r = Report("exploration_shootouts")
s = load("shootouts")
res = load("results")

r.section("1. Apercu general")
r.log(f"Nombre de seances de tirs au but : {len(s)}")
r.log(f"Periode couverte : {s['date'].min().date()} -> {s['date'].max().date()}")
r.log()
r.log(s.dtypes.to_string())

r.section("2. Valeurs manquantes")
na = s.isna().sum()
r.log(na[na > 0].to_string() if na.sum() else "Aucune valeur manquante.")
r.log(f"-> 'first_shooter' renseigne pour {s['first_shooter'].notna().mean():.1%} des seances.")

r.section("3. Coherence")
r.log(f"Doublons : {s.duplicated().sum()}")
bad_winner = s[(s["winner"] != s["home_team"]) & (s["winner"] != s["away_team"])]
r.log(f"Vainqueur qui n'est ni home ni away : {len(bad_winner)}")
if len(bad_winner):
    r.log(bad_winner.to_string())

m = s.merge(res, on=MATCH_KEY, how="left", indicator=True)
r.log(f"Seances sans match correspondant dans results.csv : {(m['_merge'] == 'left_only').sum()}")
if (m["_merge"] == "left_only").any():
    r.log(m.loc[m["_merge"] == "left_only", MATCH_KEY + ["winner"]].to_string())
matched = m[m["_merge"] == "both"].copy()
matched["neutral"] = matched["neutral"].astype(bool)  # le merge left l'a passe en object
not_draw = matched[matched["home_score"] != matched["away_score"]]
r.log(f"Seances dont le match n'est pas un nul dans results : {len(not_draw)} "
      "(ex. match retour / score cumule)")

r.section("4. Seances par tournoi (top 15)")
r.log(matched["tournament"].value_counts().head(15).to_string())

r.section("5. Avantage du premier tireur")
known = s.dropna(subset=["first_shooter"])
first_wins = (known["first_shooter"] == known["winner"]).mean()
r.log(f"Seances avec premier tireur connu : {len(known)}")
r.log(f"L'equipe qui tire en premier gagne dans {first_wins:.1%} des cas")

r.section("6. Avantage domicile (hors terrain neutre)")
non_neutral = matched[~matched["neutral"]]
r.log(f"Seances sur terrain non neutre : {len(non_neutral)}")
if len(non_neutral):
    r.log(f"Victoire de l'equipe a domicile : {(non_neutral['winner'] == non_neutral['home_team']).mean():.1%}")

r.section("7. Bilan par equipe (au moins 8 seances)")
long = pd.concat([
    s[["home_team", "winner"]].rename(columns={"home_team": "team"}),
    s[["away_team", "winner"]].rename(columns={"away_team": "team"}),
])
long["won"] = long["team"] == long["winner"]
bilan = long.groupby("team")["won"].agg(seances="size", victoires="sum")
bilan["taux"] = (bilan["victoires"] / bilan["seances"]).round(3)
bilan = bilan[bilan["seances"] >= 8].sort_values(["taux", "seances"], ascending=False)
r.log(bilan.to_string())

r.section("8. Tirs au but en Coupe du monde")
wc = matched[matched["tournament"] == "FIFA World Cup"]
r.log(f"Nombre : {len(wc)}")
r.log(wc[MATCH_KEY + ["winner"]].to_string(index=False))

# --- Figures ---
fig, ax = plt.subplots(figsize=(9, 4))
(s["date"].dt.year // 10 * 10).value_counts().sort_index().plot(kind="bar", ax=ax, color="#a5543b")
ax.set_title("Seances de tirs au but par decennie")
ax.set_xlabel("Decennie")
ax.set_ylabel("Nombre")
save_fig(fig, "shootouts_par_decennie.png")

fig, ax = plt.subplots(figsize=(5, 5))
pd.Series({"Premier tireur gagne": first_wins, "Second tireur gagne": 1 - first_wins}).plot(
    kind="pie", autopct="%1.1f%%", ax=ax, ylabel="", colors=["#a5543b", "#d9b38c"])
ax.set_title(f"Avantage du premier tireur (n={len(known)})")
save_fig(fig, "shootouts_premier_tireur.png")

r.log()
r.log("Figures : figures/shootouts_par_decennie.png, shootouts_premier_tireur.png")
r.save()
