#!/usr/bin/env python3
# coding=UTF-8

from setuptools import setup, find_packages
import os

# Lese die README.md für die lange Beschreibung
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Sicherstellen, dass das rules-Verzeichnis existiert
os.makedirs("clearurl/rules", exist_ok=True)

setup(
    name="clearurl",
    version="0.2.0",
    author="Aktualisiert von gigi2006",
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