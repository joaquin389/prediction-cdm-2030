"""Telecharge les donnees si besoin puis lance tous les scripts d'exploration.

Usage : python scripts/explore_all.py
"""

import runpy
from pathlib import Path

import download_data

HERE = Path(__file__).resolve().parent
SCRIPTS = [
    "explore_data.py",          # results.csv
    "explore_goalscorers.py",
    "explore_shootouts.py",
    "explore_former_names.py",
]

download_data.main()
for script in SCRIPTS:
    print(f"\n\n######## {script} ########")
    runpy.run_path(str(HERE / script), run_name="__main__")
