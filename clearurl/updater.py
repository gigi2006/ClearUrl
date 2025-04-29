#!/usr/bin/env python3
# coding=UTF-8

import os
import re
import yaml
import requests
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('clearurl.updater')

# URLs für AdGuard-Filterlisten
ADGUARD_SPECIFIC_URL = "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/TrackParamFilter/sections/specific.txt"
ADGUARD_GENERAL_URL = "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/TrackParamFilter/sections/general_url.txt"

# Pfad zur AdGuard-Regeldatei
def get_rules_path():
    # Versuche zuerst den installierten Paket-Pfad
    package_dir = os.path.dirname(os.path.abspath(__file__))
    rules_dir = os.path.join(package_dir, "rules")
    
    # Stelle sicher, dass das Verzeichnis existiert
    os.makedirs(rules_dir, exist_ok=True)
    
    return os.path.join(rules_dir, "adguard_rules.yaml")

def download_adguard_lists():
    """
    Lädt die AdGuard-Filterlisten herunter und gibt sie als Liste zurück
    """
    try:
        specific_response = requests.get(ADGUARD_SPECIFIC_URL)
        specific_response.raise_for_status()
        
        general_response = requests.get(ADGUARD_GENERAL_URL)
        general_response.raise_for_status()
        
        return specific_response.text.splitlines(), general_response.text.splitlines()
    except requests.RequestException as e:
        logger.error(f"Fehler beim Herunterladen der AdGuard-Listen: {e}")
        return [], []

def parse_adguard_rules(specific_lines, general_lines):
    """
    Parst die AdGuard-Filterlisten und konvertiert sie in das ClearURL-Format
    """
    hosts = {}
    default_params = set()
    
    # Reguläre Ausdrücke für das Parsen
    host_param_re = re.compile(r'^\|\|([\w\.\-]+)\^.*?(?:removeparam|tracking-\w+)=(.+)$')
    general_param_re = re.compile(r'^(?:\$|@@\$)(?:~?(?:xmlhttprequest|third-party|document|popup|cookie),)*?(?:removeparam|tracking-\w+)=(.+?)(?:,|$)')
    
    # Spezifische Regeln parsen (host-basiert)
    for line in specific_lines:
        line = line.strip()
        if line and not line.startswith('!'):  # Ignoriere Kommentare
            match = host_param_re.match(line)
            if match:
                host, params_str = match.groups()
                params = [p.strip() for p in params_str.split(',')]
                
                if host in hosts:
                    hosts[host]['query'].extend(params)
                    # Entferne Duplikate
                    hosts[host]['query'] = list(set(hosts[host]['query']))
                else:
                    hosts[host] = {'query': params, 'fragment': True}
    
    # Allgemeine Regeln parsen
    for line in general_lines:
        line = line.strip()
        if line and not line.startswith('!'):  # Ignoriere Kommentare
            match = general_param_re.match(line)
            if match:
                params_str = match.group(1)
                params = [p.strip() for p in params_str.split(',')]
                default_params.update(params)
    
    # Erstelle das Regeln-Dictionary
    rules = {
        'hosts': hosts,
        'default': list(default_params),
        'sets': {
            'adguard-trackparams': {
                'ref': 'adguard-trackparams',
                'list': list(default_params)
            }
        },
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return rules

def save_adguard_rules(rules, file_path=None):
    """
    Speichert die konvertierten AdGuard-Regeln in einer YAML-Datei
    """
    if file_path is None:
        file_path = get_rules_path()
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(rules, f, sort_keys=False, allow_unicode=True)
        logger.info(f"AdGuard-Regeln wurden erfolgreich in {file_path} gespeichert")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der AdGuard-Regeln: {e}")
        return False

def load_adguard_rules(file_path=None):
    """
    Lädt die AdGuard-Regeln aus einer YAML-Datei
    """
    if file_path is None:
        file_path = get_rules_path()
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Keine AdGuard-Regeldatei gefunden unter {file_path}")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Laden der AdGuard-Regeln: {e}")
        return None

def should_update_rules(file_path=None, days=1):
    """
    Überprüft, ob die Regeln aktualisiert werden sollten (älter als X Tage)
    """
    if file_path is None:
        file_path = get_rules_path()
    
    # Wenn die Datei nicht existiert, sollte sie erstellt werden
    if not os.path.exists(file_path):
        return True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        if not rules or 'last_updated' not in rules:
            return True
        
        last_updated = datetime.strptime(rules['last_updated'], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - last_updated) > timedelta(days=days)
    except Exception as e:
        logger.error(f"Fehler bei der Überprüfung, ob Regeln aktualisiert werden sollten: {e}")
        return True

def update_adguard_rules(force=False, file_path=None):
    """
    Aktualisiert die AdGuard-Regeln, wenn sie veraltet sind oder bei erzwungener Aktualisierung
    """
    if file_path is None:
        file_path = get_rules_path()
    
    if force or should_update_rules(file_path):
        logger.info("Aktualisiere AdGuard-Regeln...")
        specific_lines, general_lines = download_adguard_lists()
        
        if not specific_lines and not general_lines:
            logger.warning("Konnte keine AdGuard-Listen herunterladen, verwende bestehende Regeln")
            return False
        
        rules = parse_adguard_rules(specific_lines, general_lines)
        return save_adguard_rules(rules, file_path)
    else:
        logger.info("AdGuard-Regeln sind aktuell, keine Aktualisierung notwendig")
        return True

if __name__ == "__main__":
    # Manuelles Update bei direkter Ausführung des Skripts
    update_adguard_rules(force=True)