"""Outils partages par les scripts d'exploration."""

from pathlib import Path

<<<<<<< HEAD
# On dit à matplotlib de ne jamais ouvrir de fenêtre : les graphiques sont
# directement enregistrés en images PNG. Ça doit être fait AVANT d'importer
# pyplot, d'où cet ordre un peu inhabituel dans les imports.
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
import matplotlib

matplotlib.use("Agg")  # pas de fenetre : on enregistre les figures en PNG
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

<<<<<<< HEAD
# Les chemins utilisés par tous les scripts, calculés une seule fois ici :
# la racine du projet, puis les dossiers des données, des graphiques et des
# rapports texte.
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
REPORT_DIR = ROOT / "report"

<<<<<<< HEAD
# Un match est identifié de façon unique par sa date et ses deux équipes.
# On s'en sert pour relier les fichiers entre eux (buteurs <-> résultats, etc.).
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
MATCH_KEY = ["date", "home_team", "away_team"]


def load(name):
    """Charge data/<name>.csv avec la colonne date parsee."""
    path = DATA_DIR / f"{name}.csv"
<<<<<<< HEAD

    # Si le fichier n'a pas encore été téléchargé, on arrête tout avec un
    # message clair qui explique quoi faire, plutôt qu'une erreur obscure.
    if not path.exists():
        raise SystemExit(f"{path} introuvable : lancer d'abord python scripts/download_data.py")

    # La plupart des fichiers ont une colonne "date". former_names.csv est
    # l'exception : il a une date de début et une date de fin. On demande à
    # pandas de les convertir en vraies dates pour pouvoir les comparer.
=======
    if not path.exists():
        raise SystemExit(f"{path} introuvable : lancer d'abord python scripts/download_data.py")
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
    date_cols = ["start_date", "end_date"] if name == "former_names" else ["date"]
    return pd.read_csv(path, parse_dates=date_cols)


class Report:
    """Affiche le texte a l'ecran et le sauvegarde dans report/<name>.txt."""

<<<<<<< HEAD
    # On donne un nom au rapport (il servira de nom de fichier) et on prépare
    # une liste vide qui va accumuler toutes les lignes écrites.
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
    def __init__(self, name):
        self.name = name
        self.lines = []

<<<<<<< HEAD
    # Écrit une ligne : on l'affiche dans le terminal ET on la garde en mémoire
    # pour pouvoir la sauvegarder dans le fichier à la fin.
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
    def log(self, msg=""):
        print(msg)
        self.lines.append(str(msg))

<<<<<<< HEAD
    # Écrit un titre de section encadré par des lignes de "=", pour que le
    # rapport soit facile à parcourir.
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
    def section(self, title):
        self.log()
        self.log("=" * 70)
        self.log(title)
        self.log("=" * 70)

<<<<<<< HEAD
    # À la fin du script, on écrit toutes les lignes accumulées dans
    # report/<nom>.txt (en créant le dossier si besoin).
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
    def save(self):
        REPORT_DIR.mkdir(exist_ok=True)
        path = REPORT_DIR / f"{self.name}.txt"
        path.write_text("\n".join(self.lines), encoding="utf-8")
        print(f"\nResume texte enregistre dans {path}")


<<<<<<< HEAD
# Enregistre un graphique dans figures/ : on ajuste les marges pour que rien ne
# soit coupé, on sauvegarde l'image, puis on ferme la figure pour libérer la
# mémoire.
=======
>>>>>>> 4a223f12641bf536b5dd4b73a919de01c64f4758
def save_fig(fig, filename):
    FIG_DIR.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=120)
    plt.close(fig)
