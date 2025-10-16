import sys
from pathlib import Path


# Add the app/ directory to PYTHONPATH for tests
APP_DIR = Path(__file__).resolve().parent / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
