#!/usr/bin/env python3
# coding=UTF-8

from setuptools import setup, find_packages
import os
import sys

# Lese die README.md für die lange Beschreibung
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    try:
        with open("readme.md", "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except FileNotFoundError:
        long_description = "ClearURL - Ein URL-Cleaner zum Entfernen von Tracking-Parametern"

# Sicherstellen, dass das rules-Verzeichnis existiert
os.makedirs("clearurl/rules", exist_ok=True)

# Sicherstellen, dass das bin-Verzeichnis existiert
bin_dir = "bin"
os.makedirs(bin_dir, exist_ok=True)

# Prüfen, ob das clearurl-Skript existiert, andernfalls erstellen
clearurl_script = os.path.join(bin_dir, "clearurl")
if not os.path.exists(clearurl_script):
    with open(clearurl_script, "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
# coding=UTF-8

import sys
import argparse
import json
from clearurl import Filter, __version__
from clearurl.updater import update_adguard_rules

def main():
    parser = argparse.ArgumentParser(description="ClearURL - Entferne Tracking-Parameter aus URLs")
    parser.add_argument("url", nargs="?", help="Die zu bereinigende URL")
    parser.add_argument("-m", "--mode", choices=["rule", "auto", "full"], 
                      help="Filtermodus: 'rule' (nur Regeln), 'auto' (nur automatisch), 'full' (beides)")
    parser.add_argument("-j", "--json", action="store_true", help="Ausgabe als JSON")
    parser.add_argument("-u", "--update", action="store_true", help="AdGuard-Regeln aktualisieren")
    parser.add_argument("-v", "--version", action="store_true", help="Version anzeigen")
    parser.add_argument("--no-adguard", action="store_true", help="Keine AdGuard-Regeln verwenden")
    parser.add_argument("--no-auto-update", action="store_true", help="Keine automatische Aktualisierung der AdGuard-Regeln")
    parser.add_argument("--no-self-study", action="store_true", help="Selbstlernfunktion deaktivieren")
    
    args = parser.parse_args()
    
    # Version anzeigen
    if args.version:
        print(f"ClearURL v{__version__}")
        return 0
        
    # AdGuard-Regeln aktualisieren
    if args.update:
        success = update_adguard_rules(force=True)
        if success:
            print("AdGuard-Regeln wurden erfolgreich aktualisiert.")
        else:
            print("Fehler beim Aktualisieren der AdGuard-Regeln.")
        return 0
        
    # URL bereinigen
    if args.url:
        filter = Filter(
            self_study=not args.no_self_study,
            use_adguard=not args.no_adguard,
            auto_update=not args.no_auto_update
        )
        
        cleaned_url = filter.filter_url(args.url, mode=args.mode)
        
        if args.json:
            result = {
                "original_url": args.url,
                "cleaned_url": cleaned_url,
                "was_cleaned": cleaned_url != args.url
            }
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(cleaned_url)
        
        return 0
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
''')
    # Mache das Skript ausführbar (nur unter Unix-ähnlichen Systemen)
    if sys.platform != "win32":
        os.chmod(clearurl_script, 0o755)

setup(
    name="clearurl",
    version="0.2.0",
    author="tmr, aktualisiert von Giorgo",
    author_email="",
    description="URL-Cleaner zum Entfernen von Tracking-Parametern",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/clearurl",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "clearurl": ["rules/*.yaml"],
    },
    scripts=["bin/clearurl"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "asn1crypto>=1.5.1",
        "certifi>=2024.2.2",
        "cffi>=1.16.0",
        "chardet>=5.2.0",
        "cryptography>=42.0.5",
        "idna>=3.6",
        "pycparser>=2.21",
        "pyOpenSSL>=24.0.0",
        "PySocks>=1.7.1",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "six>=1.16.0",
        "urllib3>=2.1.0",
    ],
)