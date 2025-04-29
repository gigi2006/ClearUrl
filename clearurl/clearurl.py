#!/usr/bin/env python3
# coding=UTF-8

import os
import yaml
import re
import fnmatch
import json
import requests
import logging
from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from pathlib import Path

from .updater import update_adguard_rules, load_adguard_rules, get_rules_path

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('clearurl')

class Url(object):
    """
    Klasse zur Verarbeitung und Manipulation von URLs
    """
    def __init__(self, url=None):
        self.scheme = None
        self.netloc = None
        self.host = None
        self.path = None
        self.params = None
        self.query = None
        self.fragment = None
        self.query_dict = None
        if url:
            self.original_url = url
            self.parse_url()
            self.parse_query()

    def parse_url(self):
        """Zerlegt die URL in ihre Bestandteile"""
        u = urlparse(self.original_url)
        self.scheme = u.scheme
        self.netloc = u.netloc
        self.host = u.hostname
        self.path = u.path
        self.params = u.params
        self.query = u.query
        self.fragment = u.fragment
        return u

    def parse_query(self):
        """Zerlegt die Query-Parameter in ein Dictionary"""
        self.query_dict = parse_qs(self.query)
        return self.query_dict

    def get_query_by_dict(self):
        """Konvertiert das Query-Dictionary zurück in einen Query-String"""
        return urlencode(self.query_dict, doseq=True)

    def get_url(self):
        """Erstellt die vollständige URL aus allen Komponenten"""
        self.query = self.get_query_by_dict()
        return urlunparse((self.scheme, self.netloc, self.path, self.params, self.query, self.fragment))

    def copy(self):
        """Erstellt eine Kopie des Url-Objekts"""
        return Url(self.get_url())


class Filter(object):
    """
    Hauptklasse zum Filtern von URLs basierend auf Regeln
    """
    def __init__(self, rule_file=None, self_study=True, use_adguard=True, auto_update=True):
        """
        Initialisiert den Filter mit den gegebenen Regeln
        
        Args:
            rule_file: Pfad zur Regeldatei (YAML)
            self_study: Ob der Filter automatisch neue Regeln lernen soll
            use_adguard: Ob AdGuard-Regeln verwendet werden sollen
            auto_update: Ob AdGuard-Regeln automatisch aktualisiert werden sollen
        """
        self.study = self_study
        self.use_adguard = use_adguard
        
        # Bestimme Standard-Regeldatei, falls keine angegeben
        if rule_file is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            self.rule_file = os.path.join(package_dir, "rules", "default_rules.yaml")
            
            # Falls default_rules.yaml nicht existiert, kopiere die vorhandene rule.yaml
            if not os.path.exists(self.rule_file) and os.path.exists("rule.yaml"):
                from shutil import copyfile
                os.makedirs(os.path.dirname(self.rule_file), exist_ok=True)
                copyfile("rule.yaml", self.rule_file)
                logger.info(f"rule.yaml nach {self.rule_file} kopiert")
        else:
            self.rule_file = rule_file
        
        # Lade Regeln
        self.load_rule_file(self.rule_file)
        
        # Aktualisiere und lade AdGuard-Regeln, falls aktiviert
        if self.use_adguard:
            if auto_update:
                update_adguard_rules()
            self.adguard_rules = load_adguard_rules()
            if self.adguard_rules:
                logger.info("AdGuard-Regeln erfolgreich geladen")
                self.merge_adguard_rules()
            else:
                logger.warning("Keine AdGuard-Regeln gefunden oder laden fehlgeschlagen")

    def load_rule_file(self, rule_filename):
        """Lädt die Regeln aus einer YAML-Datei"""
        try:
            if os.path.exists(rule_filename):
                with open(rule_filename, 'r', encoding='utf-8') as f:
                    self.rules = yaml.safe_load(f)
                logger.info(f"Regeln aus {rule_filename} geladen")
            else:
                logger.warning(f"Regeldatei {rule_filename} nicht gefunden, verwende leere Regeln")
                self.rules = {"hosts": {}, "default": [], "sets": {}}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Regeldatei: {e}")
            self.rules = {"hosts": {}, "default": [], "sets": {}}

    def reload_rule(self):
        """Lädt die Regeln neu"""
        self.load_rule_file(self.rule_file)

    def dump_rule_file(self, rule_filename):
        """Speichert die Regeln in einer YAML-Datei"""
        try:
            with open(rule_filename, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.rules, f, sort_keys=False, allow_unicode=True)
            logger.info(f"Regeln in {rule_filename} gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Regeldatei: {e}")

    def save_rule(self):
        """Speichert die aktuellen Regeln"""
        self.dump_rule_file(self.rule_file)

    def add_to_rule(self, host, remove_list):
        """Fügt neue Parameter zur Regel für einen Host hinzu"""
        if not host:
            return
            
        if self.rules.get('hosts') is None:
            self.rules['hosts'] = {}
            
        if self.rules['hosts'].get(host):
            existing_list = self.rules['hosts'][host].get('query', [])
            # Füge neue Parameter hinzu und entferne Duplikate
            updated_list = list(set(existing_list + remove_list))
            self.rules['hosts'][host]['query'] = updated_list
        else:
            self.rules['hosts'][host] = {"query": remove_list}

    def merge_adguard_rules(self):
        """Führt die AdGuard-Regeln mit den benutzerdefinierten Regeln zusammen"""
        if not self.adguard_rules:
            return
            
        # Füge die Standard-Parameter hinzu
        if 'default' in self.adguard_rules:
            default_set = set(self.rules.get('default', []))
            default_set.update(self.adguard_rules['default'])
            self.rules['default'] = list(default_set)
            
        # Füge die Host-spezifischen Regeln hinzu
        if 'hosts' in self.adguard_rules:
            for host, host_rules in self.adguard_rules['hosts'].items():
                query_params = host_rules.get('query', [])
                self.add_to_rule(host, query_params)

    def filter_url(self, url, mode=None):
        """
        Filtert eine URL basierend auf den Regeln
        
        Args:
            url: Die zu filternde URL
            mode: Der Filtermodus ('rule', 'auto', 'full' oder None für automatische Auswahl)
            
        Returns:
            Die gefilterte URL
        """
        if not url:
            return url
            
        self.url = Url(url)
        
        if not self.url.host:
            return url

        if mode == "rule":
            self.filter_by_rule()
        elif mode == "auto":
            self.filter_auto()
        elif mode == "full":
            self.filter_by_rule()
            self.filter_auto()
        else:
            if not self.filter_by_rule():
                self.filter_auto()
        return self.url.get_url()

    def filter_by_rule(self):
        """
        Filtert die URL basierend auf den vordefinierten Regeln
        
        Returns:
            True, wenn die URL geändert wurde, sonst False
        """
        remove_list = []
        # Standardmäßig Fragment behalten
        keep_fragment = True

        # Lade hostbasierte Regeln (mit Wildcard-Unterstützung)
        host_flag = False
        for host in self.rules.get("hosts", {}):
            if fnmatch.fnmatch(self.url.host, host):
                host_flag = True
                host_rules = self.rules["hosts"].get(host, {})
                remove_list = host_rules.get("query", [])
                keep_fragment = host_rules.get("fragment", True)
                break
                
        # Wenn kein Host-Match, verwende Standardregeln
        if not host_flag:
            remove_list = self.rules.get("default", [])
            
        # Entferne die Parameter aus der URL
        for k in remove_list:
            if self.url.query_dict.get(k):
                self.url.query_dict.pop(k)
                
        # Entferne Fragment, falls konfiguriert
        if not keep_fragment:
            self.url.fragment = None
            
        # Prüfe, ob die URL geändert wurde
        if self.url.get_url() == self.url.original_url:
            return False
        else:
            return True

    def filter_auto(self):
        """
        Versucht automatisch unnötige Parameter zu erkennen und zu entfernen
        
        Returns:
            True, wenn die URL geändert wurde, sonst False
        """
        try:
            # Hole den Inhalt der ursprünglichen URL
            original_content = get_url_content(self.url.get_url())
            differ = SequenceMatcher()
            differ.set_seq1(original_content)
            
            # Prüfe jeden Parameter einzeln
            remove_list = []
            for k in list(self.url.query_dict.keys()):
                # Erstelle eine URL ohne diesen Parameter
                select_query_dict = self.url.query_dict.copy()
                select_query_dict.pop(k)
                select_url = self.url.copy()
                select_url.query_dict = select_query_dict
                
                # Hole den Inhalt der modifizierten URL
                select_content = get_url_content(select_url.get_url())
                differ.set_seq2(select_content)
                
                # Wenn die Seiten ähnlich genug sind, ist der Parameter nicht notwendig
                # Ein Schwellenwert von 0.95 erfordert eine sehr hohe Ähnlichkeit
                if differ.ratio() > 0.95:
                    remove_list.append(k)
                    
            # Entferne die identifizierten Parameter
            for k in remove_list:
                if k in self.url.query_dict:
                    self.url.query_dict.pop(k)
                
            # Lerne neue Regeln, falls aktiviert
            if self.study and remove_list:
                self.add_to_rule(self.url.host, remove_list)
                self.save_rule()
                self.reload_rule()
                
            # Prüfe, ob die URL geändert wurde
            if self.url.get_url() == self.url.original_url:
                return False
            else:
                return True
        except Exception as e:
            logger.error(f"Fehler im Auto-Filter-Modus: {e}")
            return False


def get_url_content(url):
    """
    Ruft den Inhalt einer URL ab
    
    Args:
        url: Die URL, deren Inhalt abgerufen werden soll
        
    Returns:
        Der Inhalt der URL als Bytes
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.content
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der URL {url}: {e}")
        return b""