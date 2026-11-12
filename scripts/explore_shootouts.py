"""Exploration de data/shootouts.csv (seances de tirs au but).

Colonnes : date, home_team, away_team, winner, first_shooter
Sorties : report/exploration_shootouts.txt + figures/shootouts_*.png
"""

import matplotlib.pyplot as plt
import pandas as pd

from common import MATCH_KEY, Report, load, save_fig

# On prépare le rapport, puis on charge les séances de tirs au but et les
# résultats des matchs (pour savoir dans quel tournoi et sur quel terrain
# chaque séance a eu lieu).
r = Report("exploration_shootouts")
s = load("shootouts")
res = load("results")

# Vue d'ensemble : combien de séances, sur quelle période, et le type de
# chaque colonne.
r.section("1. Apercu general")
r.log(f"Nombre de seances de tirs au but : {len(s)}")
r.log(f"Periode couverte : {s['date'].min().date()} -> {s['date'].max().date()}")
r.log()
r.log(s.dtypes.to_string())

# On repère les cases vides. On sait rarement quelle équipe a tiré en premier,
# et on précise donc pour quelle part des séances cette info existe.
r.section("2. Valeurs manquantes")
na = s.isna().sum()
r.log(na[na > 0].to_string() if na.sum() else "Aucune valeur manquante.")
r.log(f"-> 'first_shooter' renseigne pour {s['first_shooter'].notna().mean():.1%} des seances.")

# Contrôles de qualité : pas de doublons, et un vainqueur qui est bien l'une
# des deux équipes du match.
r.section("3. Coherence")
r.log(f"Doublons : {s.duplicated().sum()}")
bad_winner = s[(s["winner"] != s["home_team"]) & (s["winner"] != s["away_team"])]
r.log(f"Vainqueur qui n'est ni home ni away : {len(bad_winner)}")
if len(bad_winner):
    r.log(bad_winner.to_string())

# On relie chaque séance au match correspondant dans results.csv. Si une séance
# n'a pas de match associé, on l'affiche pour pouvoir la corriger ou l'ignorer.
m = s.merge(res, on=MATCH_KEY, how="left", indicator=True)
r.log(f"Seances sans match correspondant dans results.csv : {(m['_merge'] == 'left_only').sum()}")
if (m["_merge"] == "left_only").any():
    r.log(m.loc[m["_merge"] == "left_only", MATCH_KEY + ["winner"]].to_string())

# On ne garde que les séances reliées à un match. Normalement, des tirs au but
# suivent un match nul : on compte les cas où ce n'est pas le cas.
matched = m[m["_merge"] == "both"].copy()
matched["neutral"] = matched["neutral"].astype(bool)  # le merge left l'a passe en object
not_draw = matched[matched["home_score"] != matched["away_score"]]
r.log(f"Seances dont le match n'est pas un nul dans results : {len(not_draw)} "
      "(ex. match retour / score cumule)")

# Les 15 compétitions où il y a eu le plus de séances de tirs au but.
r.section("4. Seances par tournoi (top 15)")
r.log(matched["tournament"].value_counts().head(15).to_string())

# Est-ce un avantage de tirer en premier ? On ne regarde que les séances où on
# connaît le premier tireur et on calcule à quelle fréquence il gagne.
r.section("5. Avantage du premier tireur")
known = s.dropna(subset=["first_shooter"])
first_wins = (known["first_shooter"] == known["winner"]).mean()
r.log(f"Seances avec premier tireur connu : {len(known)}")
r.log(f"L'equipe qui tire en premier gagne dans {first_wins:.1%} des cas")

# Est-ce un avantage de jouer chez soi aux tirs au but ? On écarte les matchs
# sur terrain neutre, où il n'y a pas vraiment d'équipe "à domicile".
r.section("6. Avantage domicile (hors terrain neutre)")
non_neutral = matched[~matched["neutral"]]
r.log(f"Seances sur terrain non neutre : {len(non_neutral)}")
if len(non_neutral):
    r.log(f"Victoire de l'equipe a domicile : {(non_neutral['winner'] == non_neutral['home_team']).mean():.1%}")

# Bilan de chaque équipe aux tirs au but. On met toutes les équipes dans une
# seule colonne (qu'elles aient joué à domicile ou à l'extérieur), puis on
# compte séances et victoires. On ne garde que les équipes avec au moins 8
# séances, pour que le pourcentage veuille dire quelque chose.
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

# La liste des séances de tirs au but en phase finale de Coupe du monde.
r.section("8. Tirs au but en Coupe du monde")
wc = matched[matched["tournament"] == "FIFA World Cup"]
r.log(f"Nombre : {len(wc)}")
r.log(wc[MATCH_KEY + ["winner"]].to_string(index=False))

# --- Figures ---
# Graphique 1 : nombre de séances de tirs au but par décennie.
fig, ax = plt.subplots(figsize=(9, 4))
(s["date"].dt.year // 10 * 10).value_counts().sort_index().plot(kind="bar", ax=ax, color="#a5543b")
ax.set_title("Seances de tirs au but par decennie")
ax.set_xlabel("Decennie")
ax.set_ylabel("Nombre")
save_fig(fig, "shootouts_par_decennie.png")

# Graphique 2 : un camembert qui compare les victoires de l'équipe qui tire en
# premier et de celle qui tire en second.
fig, ax = plt.subplots(figsize=(5, 5))
pd.Series({"Premier tireur gagne": first_wins, "Second tireur gagne": 1 - first_wins}).plot(
    kind="pie", autopct="%1.1f%%", ax=ax, ylabel="", colors=["#a5543b", "#d9b38c"])
ax.set_title(f"Avantage du premier tireur (n={len(known)})")
save_fig(fig, "shootouts_premier_tireur.png")

# On rappelle où sont les graphiques, puis on enregistre le rapport texte.
r.log()
r.log("Figures : figures/shootouts_par_decennie.png, shootouts_premier_tireur.png")
r.save()
