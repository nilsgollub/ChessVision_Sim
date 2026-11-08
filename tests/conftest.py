import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
# backend.py mountet "static" relativ zum Arbeitsverzeichnis
os.chdir(ROOT)
