# Dieser Ordner enthält die Regelwerke für die Filterung von URLs
import os

# Stelle sicher, dass die Standardregeldateien existieren
rule_files = [
    'default_rules.yaml',
    'adguard_rules.yaml',
    'custom_rules.yaml'
]

current_dir = os.path.dirname(os.path.abspath(__file__))

for rule_file in rule_files:
    file_path = os.path.join(current_dir, rule_file)
    if not os.path.exists(file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Leere {rule_file} Datei\nhosts: {{}}\ndefault: []")
        except Exception:
            pass  # Ignoriere Fehler, wenn wir nicht schreiben können