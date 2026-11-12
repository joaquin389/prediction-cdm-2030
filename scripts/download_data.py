"""Telecharge les CSV du dataset martj42/international_results dans data/.

Usage : python scripts/download_data.py [--force]
"""

import sys
import urllib.request
from pathlib import Path

# On repère où se trouve le projet : le dossier parent de "scripts/".
# Les données seront rangées dans un sous-dossier "data/" à la racine.
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# Adresse "brute" du dépôt GitHub : elle renvoie directement le contenu des
# fichiers (et pas la page web GitHub qui les affiche).
BASE_URL = "https://raw.githubusercontent.com/martj42/international_results/master/"

# Les quatre fichiers du dataset qu'on veut récupérer.
FILES = ["results.csv", "goalscorers.csv", "shootouts.csv", "former_names.csv"]


def main(force=False):
    # On crée le dossier data/ s'il n'existe pas encore (sinon on ne fait rien).
    DATA_DIR.mkdir(exist_ok=True)

    # On passe les fichiers un par un.
    for name in FILES:
        dest = DATA_DIR / name

        # Si le fichier est déjà là, on ne le retélécharge pas pour gagner du
        # temps, sauf si l'utilisateur a demandé explicitement --force.
        if dest.exists() and not force:
            print(f"[skip] {name} deja present (utiliser --force pour re-telecharger)")
            continue

        # Sinon on le télécharge depuis GitHub et on affiche sa taille pour
        # vérifier d'un coup d'œil que tout s'est bien passé.
        print(f"[get ] {name} ...", end=" ", flush=True)
        urllib.request.urlretrieve(BASE_URL + name, dest)
        print(f"{dest.stat().st_size / 1024:.0f} Ko")


# Ce bloc ne s'exécute que si on lance le fichier directement
# (python scripts/download_data.py), pas quand un autre script l'importe.
# On regarde si "--force" a été tapé dans la ligne de commande.
if __name__ == "__main__":
    main(force="--force" in sys.argv)
