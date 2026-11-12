"""Outils partages par les scripts d'exploration."""

from pathlib import Path

# On dit à matplotlib de ne jamais ouvrir de fenêtre : les graphiques sont
# directement enregistrés en images PNG. Ça doit être fait AVANT d'importer
# pyplot, d'où cet ordre un peu inhabituel dans les imports.
import matplotlib

matplotlib.use("Agg")  # pas de fenetre : on enregistre les figures en PNG
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Les chemins utilisés par tous les scripts, calculés une seule fois ici :
# la racine du projet, puis les dossiers des données, des graphiques et des
# rapports texte.
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
REPORT_DIR = ROOT / "report"

# Un match est identifié de façon unique par sa date et ses deux équipes.
# On s'en sert pour relier les fichiers entre eux (buteurs <-> résultats, etc.).
MATCH_KEY = ["date", "home_team", "away_team"]


def load(name):
    """Charge data/<name>.csv avec la colonne date parsee."""
    path = DATA_DIR / f"{name}.csv"

    # Si le fichier n'a pas encore été téléchargé, on arrête tout avec un
    # message clair qui explique quoi faire, plutôt qu'une erreur obscure.
    if not path.exists():
        raise SystemExit(f"{path} introuvable : lancer d'abord python scripts/download_data.py")

    # La plupart des fichiers ont une colonne "date". former_names.csv est
    # l'exception : il a une date de début et une date de fin. On demande à
    # pandas de les convertir en vraies dates pour pouvoir les comparer.
    date_cols = ["start_date", "end_date"] if name == "former_names" else ["date"]
    return pd.read_csv(path, parse_dates=date_cols)


class Report:
    """Affiche le texte a l'ecran et le sauvegarde dans report/<name>.txt."""

    # On donne un nom au rapport (il servira de nom de fichier) et on prépare
    # une liste vide qui va accumuler toutes les lignes écrites.
    def __init__(self, name):
        self.name = name
        self.lines = []

    # Écrit une ligne : on l'affiche dans le terminal ET on la garde en mémoire
    # pour pouvoir la sauvegarder dans le fichier à la fin.
    def log(self, msg=""):
        print(msg)
        self.lines.append(str(msg))

    # Écrit un titre de section encadré par des lignes de "=", pour que le
    # rapport soit facile à parcourir.
    def section(self, title):
        self.log()
        self.log("=" * 70)
        self.log(title)
        self.log("=" * 70)

    # À la fin du script, on écrit toutes les lignes accumulées dans
    # report/<nom>.txt (en créant le dossier si besoin).
    def save(self):
        REPORT_DIR.mkdir(exist_ok=True)
        path = REPORT_DIR / f"{self.name}.txt"
        path.write_text("\n".join(self.lines), encoding="utf-8")
        print(f"\nResume texte enregistre dans {path}")


# Enregistre un graphique dans figures/ : on ajuste les marges pour que rien ne
# soit coupé, on sauvegarde l'image, puis on ferme la figure pour libérer la
# mémoire.
def save_fig(fig, filename):
    FIG_DIR.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=120)
    plt.close(fig)
