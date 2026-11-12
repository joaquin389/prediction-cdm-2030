"""Telecharge les CSV du dataset martj42/international_results dans data/.

Usage : python scripts/download_data.py [--force]
"""

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
BASE_URL = "https://raw.githubusercontent.com/martj42/international_results/master/"
FILES = ["results.csv", "goalscorers.csv", "shootouts.csv", "former_names.csv"]


def main(force=False):
    DATA_DIR.mkdir(exist_ok=True)
    for name in FILES:
        dest = DATA_DIR / name
        if dest.exists() and not force:
            print(f"[skip] {name} deja present (utiliser --force pour re-telecharger)")
            continue
        print(f"[get ] {name} ...", end=" ", flush=True)
        urllib.request.urlretrieve(BASE_URL + name, dest)
        print(f"{dest.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
