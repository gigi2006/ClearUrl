# ClearURL

Ein effizienter URL-Cleaner zum Entfernen von Tracking-Parametern aus URLs.

## Features

- Entfernt bekannte Tracking-Parameter aus URLs
- Verwendet die aktuellen [AdGuard TrackParam Filter](https://github.com/AdguardTeam/AdguardFilters/tree/master/TrackParamFilter)
- Automatische Erkennung von unnötigen Parametern
- Selbstlernfunktion zur Verbesserung der Regeln
- Einfache Integration als Bibliothek oder Kommandozeilen-Tool

## Installation

```bash
pip install clearurl
```

## Verwendung

### Als Kommandozeilen-Tool

```bash
# Einfache Verwendung
clearurl "https://www.example.com/page?id=123&utm_source=newsletter"

# Mit JSON-Ausgabe
clearurl "https://www.example.com/page?id=123&utm_source=newsletter" --json

# Nur Regeln verwenden
clearurl "https://www.example.com/page?id=123&utm_source=newsletter" --mode rule

# AdGuard-Regeln aktualisieren
clearurl --update
```

### Als Python-Bibliothek

```python
from clearurl import Filter

# Einfache Verwendung
filter = Filter()
clean_url = filter.filter_url("https://www.example.com/page?id=123&utm_source=newsletter")

# Verschiedene Modi
filter.filter_url(url, mode="rule")  # Nur Regeln verwenden
filter.filter_url(url, mode="auto")  # Nur automatisch erkennen
filter.filter_url(url, mode="full")  # Beides verwenden

# AdGuard-Regeln deaktivieren
filter = Filter(use_adguard=False)

# Selbstlernfunktion deaktivieren
filter = Filter(self_study=False)
```

## Regeln

ClearURL verwendet Regeln in YAML-Format. Es gibt drei Arten von Regeln:

1. **Host-spezifische Regeln**: Gelten nur für bestimmte Hosts/Domains
2. **Standardregeln**: Gelten für alle Hosts, wenn keine spezifische Regel gefunden wird
3. **AdGuard-Regeln**: Werden automatisch aus den AdGuard TrackParam-Filtern generiert

Die Regeln werden in folgender Priorität angewendet:
1. Host-spezifische Regeln
2. AdGuard-Regeln
3. Standardregeln
4. Automatische Erkennung (falls aktiviert)

## Entwicklung

### Voraussetzungen

- Python 3.7 oder höher
- Pip für die Installation der Abhängigkeiten

### Setup

```bash
git clone https://github.com/yourusername/clearurl.git
cd clearurl
pip install -e .
```

### Tests ausführen

```bash
pytest
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe die [LICENSE](LICENSE) Datei für Details.