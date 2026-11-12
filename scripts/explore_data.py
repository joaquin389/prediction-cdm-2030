"""Exploration du dataset international_results (martj42/international_results).

Charge data/results.csv, inspecte sa structure et sa qualite, et produit:
- un resume texte (stdout + report/exploration_summary.txt)
- quelques figures de reference (figures/*.png)
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# On repère la racine du projet, puis l'emplacement du fichier de résultats et
# des dossiers où on rangera les graphiques et le rapport texte.
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "results.csv"
FIG_DIR = ROOT / "figures"
REPORT_DIR = ROOT / "report"

# Toutes les lignes affichées sont aussi gardées ici, pour être écrites dans
# le fichier de rapport à la fin du script.
lines = []


# Affiche un message à l'écran et le mémorise pour le rapport.
def log(msg=""):
    print(msg)
    lines.append(str(msg))


# Affiche un titre de section bien visible, encadré de lignes de "=".
def section(title):
    log()
    log("=" * 70)
    log(title)
    log("=" * 70)


# On charge le fichier des résultats de matchs. La colonne "date" est
# convertie en vraie date pour pouvoir en extraire l'année, la décennie, etc.
df = pd.read_csv(DATA, parse_dates=["date"])

# Première prise de contact avec les données : combien de matchs, sur quelle
# période, quelles colonnes et de quel type (texte, nombre, date...).
section("1. Apercu general")
log(f"Nombre de matchs : {len(df)}")
log(f"Periode couverte : {df['date'].min().date()} -> {df['date'].max().date()}")
log(f"Colonnes : {list(df.columns)}")
log()
log(df.dtypes.to_string())

# On compte les cases vides colonne par colonne, et on n'affiche que les
# colonnes concernées. S'il n'y en a aucune, on le dit simplement.
section("2. Valeurs manquantes")
na = df.isna().sum()
log(na[na > 0].to_string() if na.sum() > 0 else "Aucune valeur manquante.")

# On vérifie qu'aucun match n'apparaît deux fois à l'identique.
section("3. Doublons")
log(f"Lignes dupliquees (toutes colonnes) : {df.duplicated().sum()}")

# On rassemble les équipes qui ont joué à domicile et à l'extérieur pour
# obtenir la liste complète des sélections présentes dans le dataset.
section("4. Equipes")
teams = pd.concat([df["home_team"], df["away_team"]]).unique()
log(f"Nombre d'equipes distinctes (home + away) : {len(teams)}")
log("Remarque : inclut des equipes disparues/renommees (ex: 'West Germany', "
    "'Yugoslavia', 'Czechoslovakia') -> necessite une normalisation des noms "
    "avant de construire un historique Elo continu par pays.")

# Les 15 compétitions qui comptent le plus de matchs (amicaux, qualifications...).
section("5. Types de tournois (top 15)")
log(df["tournament"].value_counts().head(15).to_string())

# Combien de matchs se sont joués sur terrain neutre (ni chez l'un ni chez
# l'autre), ce qui compte pour mesurer l'avantage du terrain.
section("6. Matchs 'neutral' (terrain neutre)")
log(df["neutral"].value_counts(dropna=False).to_string())

# Statistiques de base sur les scores (moyenne, minimum, maximum...), puis on
# s'assure qu'il n'y a pas de score impossible (négatif) ou absent.
section("7. Scores")
log(df[["home_score", "away_score"]].describe().to_string())
log(f"Scores negatifs ou NaN : "
    f"{((df['home_score'] < 0) | (df['away_score'] < 0) | df['home_score'].isna() | df['away_score'].isna()).sum()}")

# On compte les victoires à domicile, les nuls et les victoires à l'extérieur,
# avec leur pourcentage, pour mesurer l'avantage de jouer chez soi.
section("8. Distribution des resultats (perspective equipe a domicile)")
home_win = (df["home_score"] > df["away_score"]).sum()
draw = (df["home_score"] == df["away_score"]).sum()
away_win = (df["home_score"] < df["away_score"]).sum()
total = len(df)
log(f"Victoire domicile : {home_win} ({home_win/total:.1%})")
log(f"Match nul         : {draw} ({draw/total:.1%})")
log(f"Victoire exterieur: {away_win} ({away_win/total:.1%})")

# On ramène chaque année à sa décennie (1987 -> 1980) et on compte les matchs
# par décennie, pour voir comment le volume de données évolue dans le temps.
section("9. Matchs par decennie")
decade = (df["date"].dt.year // 10 * 10)
log(decade.value_counts().sort_index().to_string())

# On isole tout ce qui touche à la Coupe du monde (phase finale et
# qualifications) et on vérifie jusqu'à quelle date vont les données.
section("10. Couverture Coupe du monde")
wc = df[df["tournament"].str.contains("FIFA World Cup", case=False, na=False)]
log(f"Matchs taggues 'FIFA World Cup*' : {len(wc)}")
log(wc["tournament"].value_counts().to_string())
log(f"Derniere date presente dans le dataset : {df['date'].max().date()} "
    f"(a verifier : doit couvrir au moins la Coupe du monde 2026 selon le sujet)")

# Les 10 pays qui ont accueilli le plus de matchs.
section("11. Pays hotes (top 10)")
log(df["country"].value_counts().head(10).to_string())

# --- Figures ---
# On crée le dossier des graphiques s'il n'existe pas encore.
FIG_DIR.mkdir(exist_ok=True)

# Graphique 1 : un diagramme en barres du nombre de matchs par décennie.
fig, ax = plt.subplots(figsize=(9, 4))
decade.value_counts().sort_index().plot(kind="bar", ax=ax)
ax.set_title("Nombre de matchs internationaux par decennie")
ax.set_xlabel("Decennie")
ax.set_ylabel("Nombre de matchs")
fig.tight_layout()
fig.savefig(FIG_DIR / "matchs_par_decennie.png", dpi=120)
plt.close(fig)

# Graphique 2 : un camembert de la répartition victoire domicile / nul /
# victoire extérieur.
fig, ax = plt.subplots(figsize=(5, 5))
pd.Series(
    {"Domicile": home_win, "Nul": draw, "Exterieur": away_win}
).plot(kind="pie", autopct="%1.1f%%", ax=ax, ylabel="")
ax.set_title("Issue des matchs (perspective domicile)")
fig.tight_layout()
fig.savefig(FIG_DIR / "issues_matchs.png", dpi=120)
plt.close(fig)

log()
log(f"Figures enregistrees dans {FIG_DIR}")

# Pour finir, on écrit tout ce qui a été affiché dans un fichier texte, pour
# pouvoir relire le résumé sans relancer le script.
REPORT_DIR.mkdir(exist_ok=True)
(REPORT_DIR / "exploration_summary.txt").write_text("\n".join(lines), encoding="utf-8")
log(f"Resume texte enregistre dans {REPORT_DIR / 'exploration_summary.txt'}")
