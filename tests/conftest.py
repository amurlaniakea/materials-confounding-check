import sys
from pathlib import Path

# make `tests` package importable when running pytest from repo root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
