"""Exploration de data/goalscorers.csv (un but = une ligne).

Colonnes : date, home_team, away_team, team, scorer, minute, own_goal, penalty, assist
Sorties : report/exploration_goalscorers.txt + figures/goals_*.png
"""

import matplotlib.pyplot as plt
import pandas as pd

from common import MATCH_KEY, Report, load, save_fig

# On prépare le rapport, puis on charge les buteurs et les résultats des
# matchs (ces derniers servent à vérifier et compléter les infos des buts).
r = Report("exploration_goalscorers")
g = load("goalscorers")
res = load("results")

# Vue d'ensemble : combien de buts, sur quelle période, dans combien de matchs
# différents, et le type de chaque colonne.
r.section("1. Apercu general")
r.log(f"Nombre de buts : {len(g)}")
r.log(f"Periode couverte : {g['date'].min().date()} -> {g['date'].max().date()}")
r.log(f"Matchs distincts : {g.drop_duplicates(MATCH_KEY).shape[0]}")
r.log()
r.log(g.dtypes.to_string())

# On repère les cases vides. La colonne "assist" (le passeur décisif) est
# presque toujours vide : on le signale pour ne pas s'en servir par erreur.
r.section("2. Valeurs manquantes")
na = g.isna().sum()
r.log(na[na > 0].to_string() if na.sum() else "Aucune valeur manquante.")
r.log(f"-> 'assist' n'est renseigne que pour {g['assist'].notna().mean():.1%} des buts "
      "(colonne recente, inexploitable sur l'historique).")

# On vérifie qu'aucun but n'a été saisi deux fois à l'identique.
r.section("3. Doublons")
r.log(f"Lignes strictement dupliquees : {g.duplicated().sum()}")

# On compare avec le fichier des résultats : parmi les matchs où il y a eu au
# moins un but, combien ont le détail de qui a marqué ? On regarde aussi
# l'inverse : des buts rattachés à un match qui n'existerait pas.
r.section("4. Couverture par rapport a results.csv")
res_scored = res[(res["home_score"] + res["away_score"]) > 0]
detailed = g.drop_duplicates(MATCH_KEY)[MATCH_KEY]
cov = res_scored.merge(detailed, on=MATCH_KEY, how="left", indicator=True)
cov["year"] = cov["date"].dt.year
r.log(f"Matchs avec au moins 1 but dans results.csv : {len(res_scored)}")
r.log(f"... dont avec detail des buteurs : {(cov['_merge'] == 'both').sum()} "
      f"({(cov['_merge'] == 'both').mean():.1%})")
orphans = detailed.merge(res, on=MATCH_KEY, how="left", indicator=True)
r.log(f"Matchs de goalscorers absents de results : {(orphans['_merge'] == 'left_only').sum()}")

# Coherence : nombre de lignes vs score final
# Pour chaque match, on compte le nombre de buts listés et on le compare au
# score final. Si un match a fini 3-1, on s'attend à trouver 4 buteurs.
goals_per_match = g.groupby(MATCH_KEY).size().rename("n_lines").reset_index()
chk = goals_per_match.merge(res, on=MATCH_KEY)
chk["total"] = chk["home_score"] + chk["away_score"]
mismatch = chk[chk["n_lines"] != chk["total"]]
r.log(f"Matchs ou nb de buteurs != score final : {len(mismatch)} / {len(chk)}")
if len(mismatch):
    r.log(mismatch[MATCH_KEY + ["home_score", "away_score", "n_lines"]].head(10).to_string(index=False))

# Quelle part des buts vient d'un penalty, et quelle part est marquée contre
# son camp.
r.section("5. Types de buts")
r.log(f"Penaltys     : {g['penalty'].sum()} ({g['penalty'].mean():.1%})")
r.log(f"Contre son camp : {g['own_goal'].sum()} ({g['own_goal'].mean():.1%})")

# À quel moment du match les buts sont-ils marqués ? On donne les statistiques
# générales, puis on range les buts par tranche de 15 minutes.
r.section("6. Minute des buts")
r.log(g["minute"].describe().to_string())
r.log(f"Buts apres la 90e (prolongations / temps additionnel) : {(g['minute'] > 90).sum()}")
bins = [0, 15, 30, 45, 60, 75, 90, 200]
labels = ["1-15", "16-30", "31-45", "46-60", "61-75", "76-90", "90+"]
by_slot = pd.cut(g["minute"], bins=bins, labels=labels).value_counts().sort_index()
r.log()
r.log(by_slot.to_string())

# Classement des 20 meilleurs buteurs. On enlève les buts contre son camp :
# ils sont comptés pour l'équipe adverse, ce ne sont pas de "vrais" buts du joueur.
r.section("7. Meilleurs buteurs (hors CSC, top 20)")
real = g[~g["own_goal"]]
top_scorers = real.groupby(["scorer", "team"]).size().sort_values(ascending=False).head(20)
r.log(top_scorers.to_string())

# Les 15 sélections qui ont marqué le plus de buts (parmi les matchs détaillés).
r.section("8. Equipes ayant le plus marque (selon goalscorers, top 15)")
r.log(g["team"].value_counts().head(15).to_string())

# On ne garde que les buts marqués en phase finale de Coupe du monde, puis on
# établit le classement des meilleurs buteurs de la compétition.
r.section("9. Coupe du monde : meilleurs buteurs")
wc_matches = res[res["tournament"] == "FIFA World Cup"][MATCH_KEY]
wc_goals = real.merge(wc_matches, on=MATCH_KEY)
r.log(f"Buts en phase finale de Coupe du monde avec buteur connu : {len(wc_goals)}")
r.log(wc_goals.groupby(["scorer", "team"]).size().sort_values(ascending=False).head(15).to_string())

# Quelle part des buts est marquée par l'équipe qui reçoit ? Au-dessus de 50 %,
# cela confirme un avantage à jouer à domicile.
r.section("10. Avantage domicile dans les buts detailles")
g_home = (g["team"] == g["home_team"]).mean()
r.log(f"Part des buts marques par l'equipe a domicile : {g_home:.1%}")

# --- Figures ---
# Graphique 1 : nombre de buts par tranche de 15 minutes.
fig, ax = plt.subplots(figsize=(8, 4))
by_slot.plot(kind="bar", ax=ax, color="#3b6ea5")
ax.set_title("Repartition des buts par tranche de 15 minutes")
ax.set_xlabel("Minute")
ax.set_ylabel("Nombre de buts")
save_fig(fig, "goals_par_minute.png")

# Graphique 2 : pour chaque décennie, le pourcentage de matchs dont on connaît
# les buteurs. Ça montre que le détail est surtout disponible pour les matchs récents.
fig, ax = plt.subplots(figsize=(9, 4))
cov_year = cov.groupby(cov["year"] // 10 * 10)["_merge"].apply(lambda s: (s == "both").mean() * 100)
cov_year.plot(kind="bar", ax=ax, color="#3b6ea5")
ax.set_title("% de matchs avec detail des buteurs, par decennie")
ax.set_xlabel("Decennie")
ax.set_ylabel("% couverture")
ax.set_ylim(0, 100)
save_fig(fig, "goals_couverture_decennie.png")

# Graphique 3 : les 15 meilleurs buteurs en barres horizontales. On inverse
# l'ordre pour que le numéro 1 apparaisse en haut.
fig, ax = plt.subplots(figsize=(8, 6))
top_scorers.head(15).iloc[::-1].plot(kind="barh", ax=ax, color="#3b6ea5")
ax.set_title("Top 15 buteurs internationaux")
ax.set_xlabel("Buts")
ax.set_ylabel("")
save_fig(fig, "goals_top_buteurs.png")

# On rappelle où sont les graphiques, puis on enregistre le rapport texte.
r.log()
r.log("Figures : figures/goals_par_minute.png, goals_couverture_decennie.png, goals_top_buteurs.png")
r.save()
