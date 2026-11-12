"""Outils partages par les scripts d'exploration."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # pas de fenetre : on enregistre les figures en PNG
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
REPORT_DIR = ROOT / "report"

MATCH_KEY = ["date", "home_team", "away_team"]


def load(name):
    """Charge data/<name>.csv avec la colonne date parsee."""
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        raise SystemExit(f"{path} introuvable : lancer d'abord python scripts/download_data.py")
    date_cols = ["start_date", "end_date"] if name == "former_names" else ["date"]
    return pd.read_csv(path, parse_dates=date_cols)


class Report:
    """Affiche le texte a l'ecran et le sauvegarde dans report/<name>.txt."""

    def __init__(self, name):
        self.name = name
        self.lines = []

    def log(self, msg=""):
        print(msg)
        self.lines.append(str(msg))

    def section(self, title):
        self.log()
        self.log("=" * 70)
        self.log(title)
        self.log("=" * 70)

    def save(self):
        REPORT_DIR.mkdir(exist_ok=True)
        path = REPORT_DIR / f"{self.name}.txt"
        path.write_text("\n".join(self.lines), encoding="utf-8")
        print(f"\nResume texte enregistre dans {path}")


def save_fig(fig, filename):
    FIG_DIR.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=120)
    plt.close(fig)
