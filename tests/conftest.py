import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
# backend.py mountet "static" relativ zum Arbeitsverzeichnis
os.chdir(ROOT)

import tempfile

# Gespeicherte Partien der Tests in einen Wegwerf-Ordner, nie in data/
os.environ.setdefault("BRETT_DATA_DIR", tempfile.mkdtemp(prefix="brett-test-"))
