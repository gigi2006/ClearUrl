#!/usr/bin/env python3
# coding=UTF-8

import os
import sys

# Stelle sicher, dass das rules-Verzeichnis existiert
rules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules")
os.makedirs(rules_dir, exist_ok=True)

# Import der Hauptklassen
try:
    from .clearurl import Filter, Url
except ImportError:
    # In Fall eines Import-Fehlers, warten wir und versuchen es nochmal
    import time
    time.sleep(0.5)  # Kurz warten
    from .clearurl import Filter, Url

__version__ = "0.2.0"
__all__ = ["Filter", "Url"]