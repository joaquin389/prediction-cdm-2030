"""Telecharge les donnees si besoin puis lance tous les scripts d'exploration.

Usage : python scripts/explore_all.py
"""

import runpy
from pathlib import Path

import download_data

# Le dossier où se trouve ce fichier (scripts/), pour retrouver les autres
# scripts quel que soit l'endroit d'où on lance la commande.
HERE = Path(__file__).resolve().parent

# La liste des scripts d'exploration à exécuter, dans l'ordre.
SCRIPTS = [
    "explore_data.py",          # results.csv
    "explore_goalscorers.py",
    "explore_shootouts.py",
    "explore_former_names.py",
]

# Étape 1 : on s'assure que les CSV sont bien présents dans data/
# (ils ne sont téléchargés que s'ils manquent).
download_data.main()

# Étape 2 : on exécute chaque script comme si on l'avait lancé à la main, en
# affichant un en-tête pour bien voir où commence chacun dans le terminal.
for script in SCRIPTS:
    print(f"\n\n######## {script} ########")
    runpy.run_path(str(HERE / script), run_name="__main__")
